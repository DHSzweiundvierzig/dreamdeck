# ARCHITEKTUR (Pod-Startskript als Gerüst umgesetzt, alles andere geplant)

Keine Ordnerstruktur festgelegt; sie ergibt sich bei der Umsetzung.

- **Pod-Startskript** (Gerüst umgesetzt): richtet einen frischen RunPod-Pod ein – Repo klonen, ComfyUI installieren, Modelle und LoRAs laden, rclone konfigurieren. Liegt im Ordner `pod/` (`pod/start.sh`). Der Startbefehl der RunPod-Vorlage klont das Repo und ruft `pod/start.sh` auf. Alle Schritte laufen über die gemeinsame Funktion `run_step` (Protokoll, Dauer, Fehlerbehandlung; nach dem ersten Fehler werden weitere Schritte übersprungen). Protokoll: `/workspace/logs/start.log`. Bei einem Fehler bleibt der Pod erreichbar (`sleep infinity`, RunPod-Dienste laufen im Hintergrund). Versionen stehen nur in `pod/versions.env`. Bisher enthalten: Repo absichern, Secrets prüfen, ComfyUI installieren (Ziel `/workspace/ComfyUI`, Version aus `pod/versions.env`), GPU-Probe nach der Installation, Modelle laden; LoRAs, ComfyUI-Start und rclone folgen in 1e–1g. Modelle: `pod/models.toml` beschreibt die Modell-Sets (Dateien, Ladeart, Prüfsummen), `pod/models.py` ist der Download-Baustein (Quellen-, Platz- und Prüfsummenprüfung; auch fürs Dashboard gedacht). Welche Sets geladen werden, steht in `pod/versions.env` (`DEFAULT_MODEL_SETS`) und ist per `MODEL_SETS` überschreibbar.
- **ComfyUI headless** (geplant): läuft ohne eigene Oberfläche als Bildmotor und wird über die ComfyUI-API angesprochen.
- **DreamDeck-Backend** (geplant): vermittelt zwischen Oberfläche und ComfyUI-API, verwaltet Verlauf und Metadaten, liest Secrets nur aus Umgebungsvariablen. Technik: Python, FastAPI, uvicorn, httpx; ComfyUI per HTTP (Aufträge, Bilder) und Websocket-Client (Fortschritt); Fortschritt an die Oberfläche per Server-Sent Events, sonst fetch; nur DreamDeck von außen erreichbar, ComfyUI nur intern; Tests auf der devbox mit Spiel-ComfyUI (Fake-Bilder).
- **Oberfläche** (geplant): nach Entwurf „Variante B“ – Pipeline-Boxen 1–5, Prompt-Leiste, Bühne mit Verlauf, Einstellungsseite (zeigt nur den Status der Secrets). Technik: schlichtes HTML/CSS/JS ohne Build-Schritt, ES-Module statt globaler Variablen; Alpine.js (fest im Repo, Version in Etappe 2 gepinnt) für Step-Boxen und LoRA-Liste; Live-Fortschritt per Server-Sent Events.
- **rclone-Sync** (geplant): überträgt erzeugte Bilder ins Google Drive, bevor der Pod gelöscht wird.
- **LoRA-Liste** (geplant): Datei im Repo ohne Token; der Pod lädt die Einträge beim Start über das Civitai-Secret.

## Secrets (geplant)

- Die Secrets liegen als RunPod-Secrets im Konto; die Pod-Vorlage gibt sie beim Start als Umgebungsvariablen weiter.
- Das Startskript nutzt `GITHUB_TOKEN`, `CIVITAI_TOKEN` und `RCLONE_DRIVE_TOKEN`.
- Das Dashboard nutzt `DASHBOARD_PASSWORD` und später (optional) `ANTHROPIC_API_KEY`.
- Im Repo stehen nur die Namen, nie die Werte. Details und Begründungen: NOTIZEN.md.
