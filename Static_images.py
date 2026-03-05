import sys
import os

# Add FAST framework to Python path
fast_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FAST", "fast")
if fast_path not in sys.path:
    sys.path.insert(0, fast_path)

import fast

# =========================================================================
# FAST-Framework: Statischer Dual-View Test
# =========================================================================
# Dieses Skript lädt zwei statische Bilder (US.png und Microscopie.png)
# und zeigt sie nebeneinander an. Ideal zum Testen des Layouts.

# 1. Pfade zu den Bildern definieren
# Wir gehen davon aus, dass die Bilder im gleichen Ordner liegen wie dieses Skript.
current_dir = os.path.dirname(os.path.abspath(__file__))

image_path_us = os.path.join(current_dir, "US.png")
image_path_microscope = os.path.join(current_dir, "Microscopie.png")

print(f"Lade Ultraschall-Bild: {image_path_us}")
print(f"Lade Mikroskop-Bild:   {image_path_microscope}")

# 2. Importer erstellen (Liest die Bilder von der Festplatte)
# Hinweis: Falls die Dateien nicht existieren, wird FAST hier einen Fehler werfen.
importer_us = fast.ImageFileImporter.create(image_path_us)
print(f"US-Importer erstellt")
importer_microscope = fast.ImageFileImporter.create(image_path_microscope)
print(f"Mikroskop-Importer erstellt")

# 3. Renderer erstellen (Macht die Bilder sichtbar)
renderer_us = fast.ImageRenderer.create().connect(importer_us)
print(f"US-Renderer erstellt")
renderer_microscope = fast.ImageRenderer.create().connect(importer_microscope)
print(f"Mikroskop-Renderer erstellt")

# 4. Fenster erstellen (Dual View)
# Links: Ultraschall, Rechts: Mikroskop
window = fast.DualViewWindow2D.create()\
    .connectLeft(renderer_us)\
    .connectRight(renderer_microscope)

print(f"Fenster erstellt")
window.setTitle("FAST - Static Dual View Test")
print(f"Fenstertitel gesetzt")

# 5. Starten
print("Fenster wird gestartet. Schließen zum Beenden.")
window.run()
print("Fenster geschlossen.")
