% =========================================================================
% CHECKLISTE: LIVE-STREAMING IM LABOR (Verasonics -> FAST)
% =========================================================================
%
% ZIEL: Ultraschallbilder live per LAN-Kabel an den Laptop senden.
%       (Lösung ohne C++/MEX Dateien, nur reine MATLAB-Skripte)
%
% -------------------------------------------------------------------------
% PHASE 1: WINDOWS & NETZWERK (Einmalig einrichten)
% -------------------------------------------------------------------------
% 1. Verbinde Verasonics-PC und Laptop direkt mit einem LAN-Kabel.
%
% 2. Setze STATISCHE IP-ADRESSEN (damit sie sich sicher finden):
%    (Systemsteuerung -> Netzwerk -> Adapteroptionen -> Rechtsklick Ethernet -> IPv4)
%
%    -> Verasonics PC:
%       IP-Adresse:      192.168.1.10
%       Subnetzmaske:    255.255.255.0
%
%    -> Dein Laptop:
%       IP-Adresse:      192.168.1.20
%       Subnetzmaske:    255.255.255.0
%
% 3. Teste die Verbindung (in der Windows Eingabeaufforderung/cmd):
%    Auf dem Laptop tippen:   ping 192.168.1.10
%    -> Wenn "Antwort von..." kommt: Verbindung steht!
%
% -------------------------------------------------------------------------
% PHASE 2: MATLAB BIBLIOTHEK PRÜFEN & BEREITSTELLEN
% -------------------------------------------------------------------------
% 1. Prüfe zuerst, ob OpenIGTLink vielleicht schon installiert ist.
%    Tippe im MATLAB Command Window:
%       which igtlConnect
%
%    -> Ergebnis: Ein Pfad wird angezeigt?  => PERFEKT, weiter zu Phase 3.
%    -> Ergebnis: "not found"?              => BIBLIOTHEK FEHLT (siehe Schritt 2).
%
% 2. Falls "not found" (Bibliothek hinzufügen):
%    - Du benötigst die MATLAB-Skripte für OpenIGTLink.
%      (Das ist die Bibliothek, die "OpenIGTLinkMessageSender.m" enthält).
%
%    - Kopiere ALLE .m Dateien aus dieser Bibliothek direkt in deinen
%      Verasonics-Projektordner (dort wo auch dein Setup-Skript liegt).
%      Dann findet MATLAB sie automatisch.
%
% -------------------------------------------------------------------------
% PHASE 3: DIE ZWEI SKRIPTE ERSTELLEN
% -------------------------------------------------------------------------
% Erstelle diese zwei Dateien im Verasonics-Projektordner.
%
% DATEI 1: "sendUSFrameOverIGTL.m" (Die Hilfsfunktion)
% Kopiere diesen Code exakt hinein:
% -------------------------------------------------
% function sendUSFrameOverIGTL(sender, Img)
%     % 1. Bild aufbereiten (uint8, 0-255)
%     if ~isa(Img, 'uint8')
%         Img = double(Img);
%         % Skalierung auf Maximum (einfache Helligkeitsanpassung)
%         maxValue = max(Img(:));
%         if maxValue > 0
%             Img = uint8((Img / maxValue) * 255);
%         else
%             Img = uint8(Img);
%         end
%     end
%
%     % 2. Metadaten definieren (Dummy-Werte für 2D Streaming)
%     deviceName = 'US_Live_Stream';
%     spacing = [1.0, 1.0, 1.0];
%     origin  = [0, 0, 0];
%     norm_i  = [1, 0, 0];
%     norm_j  = [0, 1, 0];
%     norm_k  = [0, 0, 1];
%
%     % 3. Senden (über die Klasse)
%     sender.igtlSendImageMessage(deviceName, Img, spacing, origin, norm_i, norm_j, norm_k);
% end
% -------------------------------------------------
%
% DATEI 2: "Run_Live_Stream.m" (Dein neues Hauptskript)
% Kopiere diesen Code hinein:
% -------------------------------------------------
% clear all; close all;
%
% % =======================================================================
% % WICHTIG: HIER DEINEN DATEINAMEN EINTRAGEN!
% % =======================================================================
% % Trage hier den Namen deines Verasonics-Setup-Skripts ein (ohne .m).
% % Beispiel: meinSetupSkript = 'SetUpL11_5v_128RyLns';
%
% meinSetupSkript = 'NAME_DEINES_SETUP_SKRIPTS_HIER_EINTRAGEN'; 
%
% % =======================================================================
%
% % 1. Setup laden
% disp(['Lade Setup: ' meinSetupSkript]);
% eval(meinSetupSkript); % Führt dein Setup-Skript aus
%
% % 2. Verbindung zum Laptop aufbauen
% disp('Verbinde mit Laptop (192.168.1.20)...');
%
% % Verbindungsobjekt erstellen
% igtlConnection = igtlConnect('192.168.1.20', 18944);
%
% % Sender-Klasse initialisieren (WICHTIG für die .m Lösung)
% sender = OpenIGTLinkMessageSender(igtlConnection);
%
% % 3. Starten
% % Der Dateiname für VSX ergibt sich meist aus dem Setup-Namen + Pfad
% % Wir nehmen an, das Setup speichert ein .mat File in "MatFiles/"
% filename = ['MatFiles/', meinSetupSkript]; 
%
% VSX(filename); % Initialer Start
%
% disp('Streaming läuft... (Abbruch mit Ctrl+C)');
% while 1
%     % A) Bild holen (das letzte verfügbare)
%     if exist('ImageBuffer','var') && ~isempty(ImageBuffer(1).Data)
%         Img = squeeze(ImageBuffer(1).Data{end});
%
%         % B) Bild senden (mit unserem sender-Objekt)
%         sendUSFrameOverIGTL(sender, Img);
%     end
%
%     % C) VSX fortsetzen (Loop)
%     VSX(filename, 'reuse');
%     pause(0.01); % Kurze Pause für die CPU
% end
%
% % 4. Aufräumen
% igtlDisconnect(igtlConnection);
% -------------------------------------------------
%
% -------------------------------------------------------------------------
% PHASE 4: STARTEN (Reihenfolge wichtig!)
% -------------------------------------------------------------------------
% 1. LAPTOP: Starte dein Python-Skript (Skript-US-Live-OpenIGTLink.py).
%    -> Es wartet jetzt auf Daten.
%
% 2. VERASONICS: Starte "Run_Live_Stream.m" in MATLAB.
%
% 3. ERGEBNIS: Das Bild sollte auf dem Laptop erscheinen.
% =========================================================================