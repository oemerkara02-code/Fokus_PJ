import copy
import os
import numpy as np
import pydicom
from pydicom import examples
from pydicom.uid import ExplicitVRLittleEndian, generate_uid


# ── Konfiguration ──────────────────────────────────────────────────────────────
N_SLICES   = 20    # Anzahl Slices pro Serie (gerade Zahl -> symmetrisch um 0)
SLICE_GAP  = 1.0   # Abstand zwischen Slices in mm
OUTPUT_DIR = "us_dicom_output"


# ── Patienten-Tags (EXAKT so wie Dr. Huber den Test-Slot anlegt) ───────────────
# Fix 1: pydicom-Beispiel-Tags werden durch diese Werte ueberschrieben
# --> Muessen mit dem Test-Patienten-Slot im Medtronic-System uebereinstimmen
PATIENT_NAME      = "Test^Phantom"   # <-- Vorgabe an Dr. Huber
PATIENT_ID        = "TEST001"        # <-- Vorgabe an Dr. Huber
PATIENT_BIRTHDATE = "19000101"       # Platzhalterdatum fuer Testpatient
STUDY_DATE        = "20260522"       # <-- Testdatum anpassen (nicht kritisch fuer Matching)


# ── SOPClassUID fuer MR Image Storage (DICOM Standard 1.2.840.10008.5.1.4.1.1.4) ──
# Fix 2: Explizit setzen, da pydicom-Beispiel eine eigene SOPClassUID hat
# --> Ohne korrekte SOPClassUID wuerde das Medtronic-System den DICOM-Typ nicht erkennen
MR_SOP_CLASS_UID = "1.2.840.10008.5.1.4.1.1.4"


# ── Geometrische Tags pro Achse ────────────────────────────────────────────────
# IOP (0020,0037) = zwei 3D-Einheitsvektoren [Rx,Ry,Rz, Cx,Cy,Cz]:
#   Row-Vektor (erste 3):  Richtung der Bildzeilen im Patientenraum
#   Col-Vektor (letzte 3): Richtung der Bildspalten im Patientenraum
#   Normalvektor der Ebene (= Stapelrichtung) = Kreuzprodukt Row x Col
# axis: welche IPP-Koordinate sich pro Slice verschiebt
# Axial:    Row=X, Col=Y  -> Ebene liegt in XY, Stapel entlang Z
# Coronal:  Row=X, Col=-Z -> Ebene liegt in XZ, Stapel entlang Y
# Sagittal: Row=Y, Col=-Z -> Ebene liegt in YZ, Stapel entlang X
ORIENTATIONS = {
    "axial":    {"iop": [1, 0, 0,  0, 1, 0],  "axis": 2},  # Offset auf Z
    "coronal":  {"iop": [1, 0, 0,  0, 0, -1], "axis": 1},  # Offset auf Y
    "sagittal": {"iop": [0, 1, 0,  0, 0, -1], "axis": 0},  # Offset auf X
}



def us_pixel_in_mr_wrapper(output_dir=OUTPUT_DIR):


    # -- Block 1: Pixelquelle -------------------------------------------------
    us_arr = examples.rgb_color.pixel_array    # --> pixel_array gibt die Pixelwerte zurueck =! Metadaten
    test_image = examples.rgb_color            # --> Gibt das vollstaendige Dicom-Objekt inkl. Metadaten zurueck
    test_image.save_as("test_rgb_color.dcm")   # --> Speichern des Testbildes zur Inspektion der Metadaten


    # SPAETER Option A: Einzelframe vom Frame Grabber (nativ Graustufen, kein cvtColor noetig)
    # import cv2
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # cap.release()
    # if not ret: raise RuntimeError("Kein Signal vom Frame Grabber.")
    # us_arr = frame  # BGR oder Graustufen direkt, wird in Block 2 behandelt


    # SPAETER Option B: Kontinuierlicher Stream
    # import cv2
    # cap = cv2.VideoCapture(0)
    # while True:
    #     ret, frame = cap.read()
    #     if not ret: break
    #     us_arr = frame
    #     us_pixel_in_mr_wrapper(us_arr)
    # cap.release()


    # -- Block 2: Eingabe -> Graustufen ---------------------------------------
    # Fix 3: Zwei Pfade, da US-Geraete oft nativ Graustufen liefern (ndim == 2)
    if us_arr.ndim == 2:
        # Bereits Graustufen (z.B. nativer US-Output vom Frame Grabber)
        gray = us_arr.astype(np.uint8)
    elif us_arr.ndim == 3 and us_arr.shape[-1] == 3:
        # RGB -> Graustufen via ITU-R BT.601 Luminanzformel
        # float32 fuer Zwischenrechnung, danach uint8 als finales 8-bit Ergebnis
        gray = np.round(
            0.299 * us_arr[:, :, 0].astype(np.float32) +   # Rot   Index 0
            0.587 * us_arr[:, :, 1].astype(np.float32) +   # Gruen Index 1
            0.114 * us_arr[:, :, 2].astype(np.float32)     # Blau  Index 2
        ).astype(np.uint8)
    else:
        raise ValueError(f"Unerwartetes Array-Format: {us_arr.shape}")


    # -- Block 3: 8-bit -> 12-bit Skalierung ----------------------------------
    # US liefert 8-bit (0-255), MRI erwartet 12-bit (0-4095)
    # Da DICOM kein natives 12-bit kennt, wird in uint16 gespeichert (BitsAllocated=16, BitsStored=12)
    gray16 = np.round(
        gray.astype(np.float32) * (4095.0 / 255.0)
    ).astype(np.uint16)


    # -- Block 4: MR-Vorlage laden --------------------------------------------
    # examples.mr ist ein pydicom-internes MRI-Beispielbild --> liefert korrektes MR-DICOM-Grundgeruest
    mr_base = copy.deepcopy(examples.mr)


    # -- Block 5: Pixel einsetzen ---------------------------------------------
    mr_base.PixelData        = gray16.tobytes()   # DICOM PixelData erwartet Byte-String
    mr_base["PixelData"].VR  = "OW"               # OW = Other Word, fuer 16-bit Pixeldata (OB waere 8-bit)
    mr_base.Rows, mr_base.Columns = gray16.shape  # Bildgroesse in Metadaten anpassen


    # -- Block 6: Pixelattribute anpassen -------------------------------------
    mr_base.SamplesPerPixel           = 1               # 1 = Graustufen, 3 = RGB
    mr_base.PhotometricInterpretation = "MONOCHROME2"   # Hoeherer Wert = heller (MONOCHROME1 waere invertiert)
    mr_base.BitsAllocated             = 16              # Bits im Speicher pro Pixel
    mr_base.BitsStored                = 12              # Davon genutzte Bits (12-bit MRI-Standard)
    mr_base.HighBit                   = 11              # Hoechstes gesetztes Bit (0-indexiert: Bit 11 = 12 bits)
    mr_base.PixelRepresentation       = 0               # 0 = unsigned integer (kein Vorzeichen fuer Graustufen)
    mr_base.SmallestImagePixelValue   = int(gray16.min())
    mr_base.LargestImagePixelValue    = int(gray16.max())  # Range der Pixelwerte
    mr_base.WindowCenter              = int(gray16.max() // 2)
    mr_base.WindowWidth               = int(gray16.max())  # Fensterbreite fuer Grauwertskalierung bei Anzeige


    # -- Block 7: Metadaten ---------------------------------------------------
    # Study-weite UIDs einmalig generieren, werden per deepcopy an alle Serien weitergegeben
    # StudyInstanceUID:    verbindet alle 3 Serien zur gleichen Untersuchung
    # FrameOfReferenceUID: teilt dem System mit, dass alle 3 Serien im gleichen 3D-Koordinatenraum liegen
    # --> Ohne gleiche FrameOfReferenceUID wuerde das Medtronic-System die Serien nicht zusammenfuehren
    mr_base.StudyInstanceUID    = generate_uid()
    mr_base.FrameOfReferenceUID = generate_uid()
    mr_base.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian  # Standard-Codierung fuer DICOM-Bytes
    mr_base.ImageType     = ["DERIVED", "SECONDARY", "OTHER"]
    mr_base.ImageComments = "US grayscale inserted into MR clone for PoC"


    # Fix 1: Patienten-Tags explizit ueberschreiben
    # --> pydicom-Beispiel hat eigene Patienten-UIDs die nicht mit dem Medtronic-Slot uebereinstimmen
    mr_base.PatientName      = PATIENT_NAME
    mr_base.PatientID        = PATIENT_ID
    mr_base.PatientBirthDate = PATIENT_BIRTHDATE
    mr_base.StudyDate        = STUDY_DATE


    # Fix 2: SOPClassUID explizit auf MR Image Storage setzen
    # --> pydicom-Beispiel hat abweichende SOPClassUID; Medtronic erwartet den MR-Standard
    mr_base.SOPClassUID = MR_SOP_CLASS_UID
    mr_base.file_meta.MediaStorageSOPClassUID = MR_SOP_CLASS_UID


    # -- Block 8: 3 Serien erzeugen (Axial, Coronal, Sagittal) ---------------
    # Jede Achse = eine Serie mit N_SLICES Einzelbildern
    # Alle Serien teilen StudyInstanceUID und FrameOfReferenceUID aus Block 7
    os.makedirs(output_dir, exist_ok=True)


    for ori_name, cfg in ORIENTATIONS.items():


        series_uid = generate_uid()  # Jede Achse bekommt eine eigene SeriesInstanceUID


        # Symmetrischer IPP-Offset um den Ursprung (0,0,0):
        # 20 Slices x 1mm -> laeuft von -10mm bis +10mm
        # --> Slice 11 liegt exakt bei 0mm = Zielschnitt fuer die Segmentation
        offsets = [(i - N_SLICES / 2) * SLICE_GAP for i in range(N_SLICES)]


        for i, offset in enumerate(offsets):
            mr = copy.deepcopy(mr_base)  # Tiefer Copy damit jeder Slice eigene Tags hat


            # Eigene ID pro Slice, muss einzigartig sein
            mr.SOPInstanceUID    = generate_uid()
            mr.SeriesInstanceUID = series_uid       # Gleich fuer alle Slices dieser Achse
            mr.file_meta.MediaStorageSOPInstanceUID = mr.SOPInstanceUID
            mr.InstanceNumber    = str(i + 1)       # Slice-Nummerierung ab 1
            mr.SeriesNumber      = str(list(ORIENTATIONS.keys()).index(ori_name) + 1)
            mr.AcquisitionNumber = "1"
            mr.SeriesDescription = f"US_PoC_{ori_name.upper()}"


            # ── Geometrische Tags (die einzigen 2 die sich zwischen Achsen unterscheiden) ──
            # IOP (0020,0037): definiert WIE das Bild im Patientenraum orientiert ist (Rotation)
            mr.ImageOrientationPatient = cfg["iop"]


            # IPP (0020,0032): definiert WO der Slice im Patientenraum liegt (Translation)
            # Nur die Offset-Achse veraendert sich pro Slice, die anderen 2 bleiben 0
            ipp = [0.0, 0.0, 0.0]
            ipp[cfg["axis"]] = round(offset, 6)
            mr.ImagePositionPatient = ipp


            mr.SliceLocation  = round(offset, 6)  # Skalarer Abstand entlang Normalrichtung
            mr.SliceThickness = str(SLICE_GAP)
            mr.PixelSpacing   = [1.0, 1.0]         # 1mm x 1mm Pixel


            # Speichern
            fname = os.path.join(output_dir, f"us_{ori_name}_{i+1:03d}.dcm")
            mr.save_as(fname, enforce_file_format=True)


        print(f"[OK] {ori_name:10s} -- {N_SLICES} Slices gespeichert in '{output_dir}/'")


    return output_dir



# ── Verifikation ───────────────────────────────────────────────────────────────
def verify_output(output_dir=OUTPUT_DIR):


    files = [f for f in os.listdir(output_dir) if f.endswith(".dcm")]


    # Test 1: Korrekte Anzahl Dateien
    print(f"\n-- Test 1: Dateianzahl ------------------------------------")
    status = "OK" if len(files) == N_SLICES * 3 else "FEHLER"
    print(f"  [{status}] {len(files)} Dateien gefunden (erwartet: {N_SLICES * 3})")


    # Test 2: Konsistenz der Study-weiten UIDs
    # --> Alle 60 Dateien muessen dieselbe StudyInstanceUID und FrameOfReferenceUID haben
    print(f"\n-- Test 2: Study-weite UIDs --------------------------------")
    study_uids = set()
    for_uids   = set()
    for f in files:
        ds = pydicom.dcmread(os.path.join(output_dir, f))
        study_uids.add(str(ds.StudyInstanceUID))
        for_uids.add(str(ds.FrameOfReferenceUID))
    print(f"  {'[OK]' if len(study_uids) == 1 else '[FEHLER]'} StudyInstanceUIDs:    {len(study_uids)} (erwartet: 1)")
    print(f"  {'[OK]' if len(for_uids)   == 1 else '[FEHLER]'} FrameOfReferenceUIDs: {len(for_uids)}   (erwartet: 1)")


    # Test 3: Korrekte Anzahl Serien (eine pro Achse)
    print(f"\n-- Test 3: Serien ------------------------------------------")
    series_uids = set()
    for f in files:
        ds = pydicom.dcmread(os.path.join(output_dir, f))
        series_uids.add(str(ds.SeriesInstanceUID))
    print(f"  {'[OK]' if len(series_uids) == 3 else '[FEHLER]'} SeriesInstanceUIDs: {len(series_uids)} (erwartet: 3)")


    # Test 4: Patienten-Tags und SOPClassUID
    print(f"\n-- Test 4: Patienten-Tags & SOPClassUID --------------------")
    ds = pydicom.dcmread(os.path.join(output_dir, files[0]))
    print(f"  {'[OK]' if str(ds.PatientID)   == PATIENT_ID       else '[FEHLER]'} PatientID:   {ds.PatientID}")
    print(f"  {'[OK]' if str(ds.PatientName) == PATIENT_NAME     else '[FEHLER]'} PatientName: {ds.PatientName}")
    print(f"  {'[OK]' if str(ds.SOPClassUID) == MR_SOP_CLASS_UID else '[FEHLER]'} SOPClassUID: {ds.SOPClassUID}")
    print(f"  {'[OK]' if ds.Modality == 'MR'                     else '[FEHLER]'} Modality:    {ds.Modality}")


    # Test 5: Geometrie-Check Mittelschnitt pro Achse
    print(f"\n-- Test 5: Geometrie Mittelschnitt -------------------------")
    for ori_name, cfg in ORIENTATIONS.items():
        mid_file = os.path.join(output_dir, f"us_{ori_name}_{N_SLICES//2 + 1:03d}.dcm")
        ds = pydicom.dcmread(mid_file)
        iop_ok  = list(int(v) for v in ds.ImageOrientationPatient) == cfg["iop"]
        ipp_mid = round(float(ds.ImagePositionPatient[cfg["axis"]]), 1)
        ipp_ok  = ipp_mid == 0.0  # Mittelschnitt sollte exakt bei 0mm liegen
        print(f"  {ori_name:10s} | IOP {'[OK]' if iop_ok else '[FEHLER]'} | IPP-Mitte {'[OK]' if ipp_ok else '[FEHLER]'} ({ipp_mid}mm) | {ds.Rows}x{ds.Columns}px | BitsStored: {ds.BitsStored}")


    print(f"\n-- Verifikation abgeschlossen ------------------------------\n")



# ── Einstiegspunkt ─────────────────────────────────────────────────────────────
# Wird nur ausgefuehrt wenn das Skript direkt gestartet wird (nicht bei import)
if __name__ == "__main__":
    out = us_pixel_in_mr_wrapper()

    print(f"\nGesamt: {N_SLICES * 3} DICOM-Dateien in '{out}/'")
    print(f"Aufbau: {N_SLICES} Slices x 3 Achsen, +/-{int(N_SLICES/2 * SLICE_GAP)}mm um Ursprung")
    print(f"Zielschnitt fuer Segmentation: Slice {N_SLICES//2 + 1} von {N_SLICES} (bei 0mm)")

    verify_output(out)