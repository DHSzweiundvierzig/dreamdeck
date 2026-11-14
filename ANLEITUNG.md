# ANLEITUNG

## Pod starten

### RunPod-Vorlage (einmalig anlegen)
1. RunPod-Konsole → Templates → New Template, Name „dreamdeck“.
2. Container Image: runpod/pytorch:2.1.0-cu1300-torch2130-ubuntu2404
   Hinweis: Beim Pod-Start im CUDA-Filter 13.0 oder neuer wählen, sonst sieht PyTorch die GPU nicht (Treiber ab 580 nötig).
3. Container Start Command (genau so kopieren):

```
bash -c 'rm -rf /workspace/dreamdeck; git clone --depth 1 -b "${DREAMDECK_BRANCH:-main}" "https://x-access-token:${GITHUB_TOKEN}@github.com/DHSzweiundvierzig/dreamdeck.git" /workspace/dreamdeck && exec bash /workspace/dreamdeck/pod/start.sh || { echo "DreamDeck: Klonen fehlgeschlagen"; /start.sh & sleep infinity; }'
```

4. Environment Variables:
   - `GITHUB_TOKEN` = `{{ RUNPOD_SECRET_GITHUB_TOKEN }}`
   - `CIVITAI_TOKEN` = `{{ RUNPOD_SECRET_CIVITAI_TOKEN }}`
   - `RCLONE_DRIVE_TOKEN` = `{{ RUNPOD_SECRET_RCLONE_DRIVE_TOKEN }}`
   - `DREAMDECK_BRANCH` = `main` (für Tests vor dem Merge den Branch-Namen eintragen, z. B. `etappe-1`)
   - `MODEL_SETS` (optional) = Standard `basis fp16`; für fp8 `basis fp8` eintragen (ohne Anführungszeichen eintragen). Nie beide FLUX-Sets zusammen.
5. Container Disk: 50 GB

### Protokoll ansehen
Im Web-Terminal des Pods:

```
tail -f /workspace/logs/start.log
# RunPod-Dienste: tail -f /workspace/logs/runpod.log
# ComfyUI: tail -f /workspace/logs/comfyui.log
# Sync: tail -f /workspace/logs/sync.log
```

Hinweis: Prüfsummen, die beim ersten Lauf gemessen werden, stehen im Protokoll mit „bitte eintragen“ (suchen mit `grep "bitte" /workspace/logs/start.log`) und gehören danach in `pod/models.toml`.

### LoRAs beim Start
Welche LoRAs der Pod beim Start lädt, steht in `pod/loras.toml`. Eingetragen wird nur die Civitai-Versionsnummer: auf der Modellseite die Version wählen, die Zahl hinter `modelVersionId=` in der Adresse ist die Versionsnummer; den Namen als Kommentar dahinter schreiben. Dateiname, Größe und Prüfsumme holt der Pod selbst von Civitai. Erlaubt sind nur LoRAs für Flux.1 D im Format SafeTensor. Die Liste bewusst klein halten – weitere LoRAs kommen später übers Dashboard.

## Arbeiten
Folgt in Etappe 2.

## Pod beenden
1. Im Web-Terminal: `bash /workspace/dreamdeck/pod/sync.sh` und auf „Sync fertig“ warten.
2. Im Google Drive im Ordner DreamDeck kurz prüfen, ob die letzten Bilder da sind.
3. Pod in RunPod löschen (Terminate). Alles auf dem Pod ist danach weg.

## Zugänge erneuern
- **GitHub-Token (läuft am 15.05.2027 ab):** Auf GitHub einen neuen fine-grained Token mit denselben Einstellungen anlegen (Owner DHSzweiundvierzig, nur Repo dreamdeck, Contents: Read-only). Dann in RunPod das Secret `GITHUB_TOKEN` aktualisieren.
- **rclone-Token:** Falls Google den Zugriff irgendwann ablehnt, auf dem PC `rclone.exe` herunterladen und ausführen:
  `.\rclone.exe authorize "drive" "eyJzY29wZSI6ImRyaXZlLmZpbGUifQ"` (ohne `=` am Ende).
  Alles zwischen „--->“ und „<---End paste“ in das Secret `RCLONE_DRIVE_TOKEN` eintragen.
- **Hinweis:** Im Google Drive keinen DreamDeck-Ordner von Hand anlegen, das macht der Pod.
