# ANLEITUNG

## Pod starten
Folgt in Etappe 1.

## Arbeiten
Folgt in Etappe 2.

## Pod beenden
Folgt in Etappe 1.

## Zugänge erneuern
- **GitHub-Token (läuft am 15.05.2027 ab):** Auf GitHub einen neuen fine-grained Token mit denselben Einstellungen anlegen (Owner DHSzweiundvierzig, nur Repo dreamdeck, Contents: Read-only). Dann in RunPod das Secret `GITHUB_TOKEN` aktualisieren.
- **rclone-Token:** Falls Google den Zugriff irgendwann ablehnt, auf dem PC `rclone.exe` herunterladen und ausführen:
  `.\rclone.exe authorize "drive" "eyJzY29wZSI6ImRyaXZlLmZpbGUifQ"` (ohne `=` am Ende).
  Alles zwischen „--->“ und „<---End paste“ in das Secret `RCLONE_DRIVE_TOKEN` eintragen.
- **Hinweis:** Im Google Drive keinen DreamDeck-Ordner von Hand anlegen, das macht der Pod.
