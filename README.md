# Fokus-Projekt: FAST Medical Imaging Framework

Dieses Projekt nutzt das **FAST Framework (v4.17.0)** für medizinische Bildverarbeitung und Ultraschallbildverarbeitung.

## ⚠️ WICHTIG: FAST Installation

Das FAST Framework muss **lokal auf Ihrem Computer installiert** werden, da es zu groß für GitHub ist (~300 MB+).

### FAST herunterladen & installieren:
1. Besuchen Sie: https://github.com/smistad/FAST/releases
2. Laden Sie die neueste Release (v4.17.0+) herunter
3. Entpacken Sie sie in den `FAST/` Ordner hier

**Hinweis:** Der `FAST/` Ordner ist lokal, aber NICHT im Git-Repository gespeichert.

## Setup & Installation

### 1. Python Dependencies installieren
```bash
pip install -r requirements.txt
```

Dies installiert automatisch:
- **pyfast** (v4.17.0) - FAST Framework Python Bindings
- Alle weiteren Abhängigkeiten

## Projektstruktur

```
FAST-Framework/
├── Skript-US-Live-OpenIGTLink.py          # Ultraschall-Live-Streaming mit OpenIGTLink
├── Static_images.py                        # Python-Skript für statische Bildverarbeitung
├── Video-Seq.py                            # Video-Sequenz Verarbeitung
├── run_fast.bat                            # Windows Batch-Datei zum Starten
├── requirements.txt                        # Python Dependencies
├── MATLAB_Anleitung_OpenIGTLink.m         # MATLAB-Anleitung für OpenIGTLink
├── README.md                               # Diese Datei
└── FAST/                                   # FAST Framework (NICHT im Git, lokal installiert)
    └── fast/                               # FAST Binaries & Libraries
```

## Scripts

### 1. **Skript-US-Live-OpenIGTLink.py**
Ultraschall-Live-Streaming mit OpenIGTLink-Unterstützung

### 2. **Static_images.py**
Statische Bildverarbeitung

### 3. **Video-Seq.py**
Video-Sequenz Verarbeitung

## Workflow - So arbeitest du mit diesem Projekt

### Erste Schritte (nach Klonen des Repos):

1. **FAST Framework lokal installieren** (siehe oben: "FAST herunterladen & installieren")

2. **Python Dependencies installieren:**
```bash
pip install -r requirements.txt
```

3. **Skripte ausführen:**
```bash
python Skript-US-Live-OpenIGTLink.py
# oder
python Static_images.py
# oder
python Video-Seq.py
```

### Während der Entwicklung:

- Modifizieren Sie die `.py` Dateien
- Testen Sie lokal
- Committen Sie zu Git:
```bash
git add .
git commit -m "Beschreibung der Änderung"
git push origin main
```
# 1. Dateien editieren (Static_images.py, etc.)

# 2. Neue Module brauchst du?
pip install neuesmodul

# 3. requirements.txt aktualisieren (optional, aber empfohlen)
# Entweder manuell editieren oder:
pip freeze | grep -v "^-e" > requirements.txt

# 4. Changes committen
git add Static_images.py MATLAB_Anleitung_OpenIGTLink.m requirements.txt
git commit -m "Beschreibung der Änderungen"
```

## FAST Framework - Wichtige Funktionen

### Importing FAST
```python
import fast
```

### Häufig verwendete Funktionen

#### 1. Bildimport
```python
# Bild aus Datei laden
importer = fast.ImageFileImporter.create('path/to/image.jpg')
```

#### 2. Bildrendering/Visualisierung
```python
# Renderer für die Anzeige
renderer = fast.ImageRenderer.create(importer)
window = fast.SimpleWindow2D.create()
window.addRenderer(renderer)
window.run()
```

#### 3. Bildverarbeitung
```python
# Beispiel: Smoothing Filter
smoother = fast.GaussianSmoothing.create(importer)
```

#### 4. Ultraschall/OpenIGTLink Integration
```python
# Ultrasound-Streamer (z.B. für Live-Daten)
streamer = fast.UltraSoundFileStreamer.create('file.usraw')
```

### Beispiel: Komplettes Skript
```python
import fast

# Bild laden
importer = fast.ImageFileImporter.create('image.jpg')

# Visualisieren
renderer = fast.ImageRenderer.create(importer)
window = fast.SimpleWindow2D.create()
window.addRenderer(renderer)
window.run()
```

## Docs & Ressourcen

- **FAST Dokumentation**: https://fast-imaging.github.io
- **GitHub Repository**: https://github.com/smistad/FAST

## Wichtige Befehle

| Befehl | Zweck |
|--------|-------|
| `pip install -r requirements.txt` | Alle Dependencies installieren |
| `pip install neuesmodul` | Neues Python-Modul installieren |
| `git add .` | Alle Änderungen zum Commit hinzufügen |
| `git commit -m "message"` | Änderungen speichern mit Nachricht |
| `git status` | Status des Repositorys anzeigen |

## Fehlerbehandlung

**Problem: FAST kann nicht importiert werden**
```bash
# Sicherstellen, dass pip install lief:
pip install -r requirements.txt

# Oder direkt:
pip install pyfast
```

**Problem: Virtual Environment nicht aktiviert**
```bash
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate
```

---

**Letzte Aktualisierung**: March 2026  
**Python Version**: 3.12+  
**FAST Version**: v4.17.0
