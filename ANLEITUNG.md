# ANLEITUNG

## Pod starten

### RunPod-Vorlage (einmalig anlegen)
1. RunPod-Konsole → Templates → New Template, Name „dreamdeck“.
2. Container Image: wird in Schritt 1c festgelegt.
3. Container Start Command (genau so kopieren):

```
bash -c 'rm -rf /workspace/dreamdeck; git clone --depth 1 -b "${DREAMDECK_BRANCH:-main}" "https://x-access-token:${GITHUB_TOKEN}@github.com/DHSzweiundvierzig/dreamdeck.git" /workspace/dreamdeck && exec bash /workspace/dreamdeck/pod/start.sh || { echo "DreamDeck: Klonen fehlgeschlagen"; /start.sh & sleep infinity; }'
```

4. Environment Variables:
   - `GITHUB_TOKEN` = `{{ RUNPOD_SECRET_GITHUB_TOKEN }}`
   - `CIVITAI_TOKEN` = `{{ RUNPOD_SECRET_CIVITAI_TOKEN }}`
   - `RCLONE_DRIVE_TOKEN` = `{{ RUNPOD_SECRET_RCLONE_DRIVE_TOKEN }}`
   - `DREAMDECK_BRANCH` = `main` (für Tests vor dem Merge den Branch-Namen eintragen, z. B. `etappe-1`)

### Protokoll ansehen
Im Web-Terminal des Pods:

```
tail -f /workspace/logs/start.log
# RunPod-Dienste: tail -f /workspace/logs/runpod.log
```

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
