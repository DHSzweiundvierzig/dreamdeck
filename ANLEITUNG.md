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

4. Expose HTTP Ports: `8000` (Dashboard). Expose TCP Ports: `22` mit Label `SSH`. Port 8188 (ComfyUI) nicht eintragen, ComfyUI bleibt intern.
   Hinweis: Der Port muss zu `DASHBOARD_PORT` in `pod/paths.env` passen.
5. Container Disk: 50 GB, Volume Disk: 0 GB.
6. Environment Variables: Auf „Raw editor“ klicken, diesen Block einfügen und mit „Update Variables“ übernehmen:

```
GITHUB_TOKEN={{ RUNPOD_SECRET_GITHUB_TOKEN }}
CIVITAI_TOKEN={{ RUNPOD_SECRET_CIVITAI_TOKEN }}
DREAMDECK_DRIVE_TOKEN={{ RUNPOD_SECRET_DREAMDECK_DRIVE_TOKEN }}
DREAMDECK_DRIVE_CLIENT_ID={{ RUNPOD_SECRET_DREAMDECK_DRIVE_CLIENT_ID }}
DREAMDECK_DRIVE_CLIENT_SECRET={{ RUNPOD_SECRET_DREAMDECK_DRIVE_CLIENT_SECRET }}
DASHBOARD_PASSWORD={{ RUNPOD_SECRET_DASHBOARD_PASSWORD }}
DREAMDECK_BRANCH=main
PUBLIC_KEY=ssh-ed25519 AAAA... (eigene Zeile, siehe unten)
```

   Hinweise:
   - `PUBLIC_KEY` = Inhalt der Datei `id_ed25519.pub` (öffentlicher Schlüssel, kein Geheimnis). Ohne ihn startet RunPod keinen SSH-Dienst und Port 22 bleibt zu. In die Zwischenablage holen mit `Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard`. Nie die Datei `id_ed25519` ohne Endung verwenden (privater Schlüssel).
   - `DASHBOARD_PASSWORD`: Das Secret `DASHBOARD_PASSWORD` vorher in RunPod unter Secrets anlegen (selbst gewähltes Passwort fürs Dashboard). Ohne dieses Secret ist keine Anmeldung am Dashboard möglich.
   - `DREAMDECK_BRANCH`: für Tests vor dem Merge den Branch-Namen eintragen, z. B. `etappe-1`. Der Pod holt den Code nur beim Start. Neuer Stand auf dem Branch → neuen Pod starten.
   - `MODEL_SETS` (optional): Standard `basis fp16`; für fp8 `basis fp8` eintragen (ohne Anführungszeichen eintragen). Nie beide FLUX-Sets zusammen.
   - Die Secrets werden als Verweise angezeigt (lila); die Werte setzt RunPod erst beim Start ein.
   - Achtung: Beim Bearbeiten einer vorhandenen Vorlage speichert RunPod geänderte Umgebungsvariablen nicht (Stand 15.11.2026). Für Änderungen die Vorlage löschen und neu anlegen; die Secrets bleiben dabei erhalten.

### Pod starten (jedes Mal)
1. RunPod → Pods → Deploy.
2. Filter „CUDA Version“: 13.0 oder höher.
3. GPU mit 48 GB: A40, ersatzweise RTX A6000 oder L40S (24 GB reichen für fp16 nicht).
4. „Change Template“ → `dreamdeck` wählen.
5. Instance Pricing: On-Demand (nicht Spot/Interruptible).
6. Deploy, dann Protokoll ansehen (siehe unten).

### Protokoll ansehen
Im Web-Terminal des Pods:

```
tail -f /workspace/logs/start.log
# RunPod-Dienste: tail -f /workspace/logs/runpod.log
# ComfyUI: tail -f /workspace/logs/comfyui.log
# Sync: tail -f /workspace/logs/sync.log
# Dashboard: tail -f /workspace/logs/dashboard.log
```

Hinweis: Prüfsummen, die beim ersten Lauf gemessen werden, stehen im Protokoll mit „bitte eintragen“ (suchen mit `grep "bitte" /workspace/logs/start.log`) und gehören danach in `pod/models.toml`.

### LoRAs beim Start
Welche LoRAs der Pod beim Start lädt, steht in `pod/loras.toml`. Eingetragen wird nur die Civitai-Versionsnummer: auf der Modellseite die Version wählen, die Zahl hinter `modelVersionId=` in der Adresse ist die Versionsnummer; den Namen als Kommentar dahinter schreiben. Dateiname, Größe und Prüfsumme holt der Pod selbst von Civitai. Erlaubt sind nur LoRAs für Flux.1 D im Format SafeTensor. Die Liste bewusst klein halten – weitere LoRAs kommen später übers Dashboard.

## Arbeiten
### Dashboard über den RunPod-Proxy öffnen
RunPod → Pod → Connect → bei „HTTP Services“ Port 8000 anklicken, oder direkt `https://<POD_ID>-8000.proxy.runpod.net` öffnen. Die Anmeldung erfolgt mit `DASHBOARD_PASSWORD`.

### ComfyUI-Oberfläche und Fehlersuche per SSH-Tunnel
1. In RunPod beim Pod → Connect → unter „SSH over exposed TCP“ die IP und den äußeren Port für Port 22 ablesen.
2. In Windows PowerShell (IP und Port einsetzen):
   `ssh -L 8188:127.0.0.1:8188 -L 8000:127.0.0.1:8000 root@<IP> -p <Port> -i $env:USERPROFILE\.ssh\id_ed25519`
   Beim ersten Mal die Frage nach dem Vertrauen mit `yes` beantworten.
3. Fenster offen lassen. Im Browser: Dashboard `http://localhost:8000`, ComfyUI `http://localhost:8188`.
   Das Dashboard fragt nach dem Passwort (`DASHBOARD_PASSWORD`). Die Anmeldung gilt 12 Stunden bzw. bis zum Neustart des Dashboards.
4. Zum Beenden in der SSH-Sitzung `exit`; damit ist auch der Tunnel zu.

#### Neuen Code ohne neuen Pod holen
In der SSH-Sitzung auf dem Pod:
```
cd /workspace/dreamdeck && git pull
pkill -f "uvicorn dashboard.app"; env -u CIVITAI_TOKEN nohup /workspace/venv-dashboard/bin/uvicorn dashboard.app:app --app-dir /workspace/dreamdeck --host 0.0.0.0 --port 8000 > /workspace/logs/dashboard.log 2>&1 &
```
Hinweis: Das gilt für Änderungen am Dashboard. Änderungen an `pod/start.sh` oder den Modell-Listen brauchen weiterhin einen neuen Pod.

## Pod beenden
1. Im Web-Terminal: `bash /workspace/dreamdeck/pod/sync.sh` und auf „Sync fertig“ warten.
2. Im Google Drive im Ordner DreamDeck kurz prüfen, ob die letzten Bilder da sind.
3. Pod in RunPod löschen (Terminate). Alles auf dem Pod ist danach weg.

## Zugänge erneuern
- **GitHub-Token (läuft am 15.05.2027 ab):** Auf GitHub einen neuen fine-grained Token mit denselben Einstellungen anlegen (Owner DHSzweiundvierzig, nur Repo dreamdeck, Contents: Read-only). Dann in RunPod das Secret `GITHUB_TOKEN` aktualisieren.
- **Google-Zugang (rclone):**
  - Grundlage: eigenes Google-Cloud-Projekt `dreamdeck` (Client „rclone“, Typ Desktop-App, App „In Produktion“). Die heruntergeladene Client-Datei liegt auf dem PC unter `C:\Ai\Coding\DreamDeck\google-client.json` – nie ins Repo, nie in den Chat, der Ordner wird nicht in eine Cloud synchronisiert.
  - Die Seite https://dhszweiundvierzig.github.io (Startseite und Datenschutz für Google) nicht löschen, Google verlangt sie für die veröffentlichte App.
  - Client-ID und Client-Secret in RunPod eintragen (einmalig bzw. nach neuem Client). In PowerShell:

    ```
    $c = (Get-Content "C:\Ai\Coding\DreamDeck\google-client.json" -Raw | ConvertFrom-Json).installed
    $c.client_id | Set-Clipboard
    ```

    → in RunPod als Secret `DREAMDECK_DRIVE_CLIENT_ID` einfügen, danach

    ```
    $c.client_secret | Set-Clipboard
    ```

    → als Secret `DREAMDECK_DRIVE_CLIENT_SECRET` einfügen.
  - Token erzeugen (bei neuem Client oder wenn Google den Zugriff ablehnt): PowerShell im Ordner mit `rclone.exe` öffnen und diesen Block ausführen:

    ```
    $c = (Get-Content "C:\Ai\Coding\DreamDeck\google-client.json" -Raw | ConvertFrom-Json).installed
    $cfg = @{ scope = "drive.file"; client_id = $c.client_id; client_secret = $c.client_secret } | ConvertTo-Json -Compress
    $blob = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($cfg)).TrimEnd('=')
    $out = .\rclone.exe authorize "drive" $blob
    $token = ($out | Select-String -SimpleMatch '--->' -Context 0,1).Context.PostContext[0].Trim()
    $token | Set-Clipboard
    "Token in der Zwischenablage: $($token.Length) Zeichen"
    ```

    Im Browser anmelden und zulassen; die Warnung „App nicht überprüft“ über „Erweitert → weiter zu DreamDeck“ bestätigen. Die Kontrollzeile muss einige hundert Zeichen zeigen. Dann in RunPod das Secret `DREAMDECK_DRIVE_TOKEN` mit Strg+V aktualisieren.
  - Danach Zwischenablage leeren mit `Set-Clipboard -Value " "` (ggf. auch im Zwischenablageverlauf Win+V) und das PowerShell-Fenster schließen.
  - Wichtig: Token, Client-ID und Client-Secret gehören zusammen. Wird der Client neu angelegt, muss auch der Token neu erzeugt werden.
  - Nach einem Client-Wechsel legt DreamDeck im Drive einen neuen Ordner „DreamDeck“ an, weil der neue Client (Scope drive.file) die Dateien des alten nicht sieht. Alte Bilder von Hand in den neuen Ordner verschieben und den alten Ordner löschen. Der Sync nutzt rclone copy und löscht im Drive nie etwas.
- **Hinweis:** Im Google Drive keinen DreamDeck-Ordner von Hand anlegen, das macht der Pod.
