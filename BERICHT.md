# Bericht – Schritt 1g: rclone installieren und einrichten

## Geänderte Dateien
- `pod/versions.env`: `RCLONE_VERSION=v1.75.2` und `RCLONE_SHA256` ergänzt, mit Kommentar zur Quelle.
- `pod/start.sh`: Versionsprüfung um die rclone-Werte erweitert; Konstanten `RCLONE_CONF` und `RCLONE_REMOTE`; neue Schritte `step_install_rclone` (Download nach /tmp, Prüfsumme, Entpacken mit python3/zipfile, `install -m 755`) und `step_configure_rclone` (Token nur aus der Umgebung, Konfiguration mit Rechten 600, `unset`, `rclone mkdir` als Verbindungstest); ComfyUI startet mit `env -u CIVITAI_TOKEN`; Ablauf: rclone-Schritte zwischen „LoRAs laden“ und „ComfyUI starten“; Platzhalter-Kommentar verweist auf 1h.
- `NOTIZEN.md`: Eintrag zu rclone-Version, Download-Quelle, Token-Format und Reihenfolge.
- `ARCHITEKTUR.md`: Zeile „Pod-Startskript“ aktualisiert, „rclone-Sync“ unverändert.
- `MERKLISTE.md`: 1g abgehakt, neue 1h (Sync), bisherige 1h jetzt 1i.
- Nachbesserung: fehlendes Leerzeichen in step_start_comfyui (python3 "$COMFY_DIR/main.py").

## Offene Punkte
- Nicht auf einem Pod getestet; Abnahme erst in 1i.
- `step_install_rclone` nutzt `curl`; falls im Image nicht vorhanden, schlägt der Schritt fehl (dann auf python3-Download umstellen).
- Bei einem Fehler im Token-Schritt wird der Token trotzdem aus der Umgebung gelöscht.
- ANLEITUNG-Abschnitt „Zugänge erneuern“ wird in der Fehlermeldung genannt – bitte prüfen, ob er existiert.
- Sync-Schleife und `pod/sync.sh` folgen in 1h.
