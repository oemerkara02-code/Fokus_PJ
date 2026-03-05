import fast
import os

## =========================================================================
## FAST-Framework: Ultrasound + Microscope Dual View
## Modus: OpenIGTLink (Live-Stream über Netzwerk)
## =========================================================================
##
## ZWECK:
## Dieses Skript dient als EMPFÄNGER (Client) für einen Live-Ultraschall-Stream.
## Es verbindet sich über das Netzwerk (LAN-Kabel oder lokal) mit dem Sender.
##
## SZENARIO:
## 1. PC A (Verasonics/MATLAB): Sendet Bilder via OpenIGTLink.
## 2. PC B (Dieser Laptop): Empfängt Bilder mit diesem Skript.
##
## VORAUSSETZUNG:
## - Die beiden PCs müssen per LAN-Kabel verbunden sein.
## - Du musst die IP-Adresse von PC A kennen.
## - Auf PC A muss MATLAB laufen und senden (siehe MATLAB_Anleitung_OpenIGTLink.m).

# ==== KONFIGURATION ====

# 1. Verbindungseinstellungen für den Ultraschall-Stream (Input 1)
# -------------------------------------------------------------------------
# WICHTIG: Hier musst du die IP-Adresse des Senders (Verasonics-PC) eintragen.
#
# Fall A: Du bist per LAN-Kabel verbunden (Normalfall im Labor)
# -> Trage hier die IP des Verasonics-PCs ein (z.B. "192.168.1.10").
#
# Fall B: Du testest alles auf EINEM Computer (Simulation)
# -> Trage "localhost" ein.
IGTL_IP = "192.168.1.10"  # <--- HIER ÄNDERN! (IP des Verasonics-PCs)
IGTL_PORT = 18944         # Standard-Port für OpenIGTLink (meistens so lassen)

# 2. Pfad zum Mikroskop-Bild (Input 2)
# -------------------------------------------------------------------------
# Aktuell ein statisches Bild. Später kann hier auch ein Streamer hin.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MICROSCOPE_IMAGE_PATH = os.path.join(CURRENT_DIR, "Microscopie.png")


def main():
    print("=================================================")
    print("   FAST Framework - Dual View (US + Microscope)")
    print("=================================================")
    print(f"1. Mikroskop-Bild (Rechts): {MICROSCOPE_IMAGE_PATH}")
    print(f"2. Ultraschall-Stream (Links):")
    print(f"   -> Versuche Verbindung zu: {IGTL_IP}:{IGTL_PORT}")
    print(f"   -> Protokoll: OpenIGTLink")
    print("   -> Status: Warte auf Daten...")
    print("=================================================")

    # --- Pipeline Aufbau ---
    # In FAST bauen wir eine "Pipeline". Daten fließen von oben (Input) nach unten (Renderer -> Window).

    # SCHRITT 1: Datenquellen definieren (Inputs)
    # ---------------------------------------------------------------------
    
    # Input 1: Ultraschall (Live via OpenIGTLink)
    # Der OpenIGTLinkStreamer ist ein aktives Objekt. Er versucht im Hintergrund,
    # die Verbindung zur IP-Adresse aufzubauen.
    # - Wenn die Verbindung klappt: Er empfängt Bilder und schickt sie weiter.
    # - Wenn nicht: Er wartet geduldig. Das Fenster bleibt schwarz, stürzt aber nicht ab.
    us_stream = fast.OpenIGTLinkStreamer.create(
        ipAddress=IGTL_IP,
        port=IGTL_PORT
    )

    # Input 2: Mikroskop (Statisch aus Datei)
    # Der ImageFileImporter liest ein Bild einmalig von der Festplatte.
    # Das ist unser "rechtes Auge" im Fenster.
    # HINWEIS: Falls die Datei fehlt, stürzt FAST hier ab. Bitte sicherstellen, dass sie existiert.
    microscope_import = fast.ImageFileImporter.create(MICROSCOPE_IMAGE_PATH)

    # SCHRITT 2: Daten visualisieren (Renderer)
    # ---------------------------------------------------------------------
    # Ein "Renderer" nimmt Rohdaten (z.B. Pixel-Array) und macht daraus eine Grafik,
    # die die Grafikkarte anzeigen kann.
    
    # Renderer für Ultraschall (verbinden mit us_stream)
    renderer_us = fast.ImageRenderer.create().connect(us_stream)
    
    # Renderer für Mikroskop (verbinden mit microscope_import)
    renderer_microscope = fast.ImageRenderer.create().connect(microscope_import)

    # SCHRITT 3: Fenster erstellen und Layout festlegen
    # ---------------------------------------------------------------------
    # Wir nutzen ein fertiges "DualViewWindow2D". Das teilt den Bildschirm automatisch
    # in zwei Hälften.
    
    window = fast.DualViewWindow2D.create()\
        .connectLeft(renderer_us)\
        .connectRight(renderer_microscope)
        # connectLeft: Was soll links angezeigt werden? -> Unser US-Renderer
        # connectRight: Was soll rechts angezeigt werden? -> Unser Mikroskop-Renderer

    # Fenstertitel setzen (steht oben in der Leiste)
    window.setTitle("FAST - Ultrasound (Live) & Microscope")
    
    # SCHRITT 4: Starten
    # ---------------------------------------------------------------------
    # window.run() startet die Hauptschleife (Event Loop).
    # Das Programm bleibt hier stehen und läuft, bis du das Fenster schließt.
    window.run()


if __name__ == "__main__":
    main()
