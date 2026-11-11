# ARCHITEKTUR (alles geplant, nichts umgesetzt)

Keine Ordnerstruktur festgelegt; sie ergibt sich bei der Umsetzung.

- **Pod-Startskript** (geplant): richtet einen frischen RunPod-Pod ein – Repo klonen, ComfyUI installieren, Modelle und LoRAs laden, rclone konfigurieren.
- **ComfyUI headless** (geplant): läuft ohne eigene Oberfläche als Bildmotor und wird über die ComfyUI-API angesprochen.
- **DreamDeck-Backend** (geplant): vermittelt zwischen Oberfläche und ComfyUI-API, verwaltet Verlauf und Metadaten, liest Secrets nur aus Umgebungsvariablen.
- **Oberfläche** (geplant): nach Entwurf „Variante B“ – Pipeline-Boxen 1–5, Prompt-Leiste, Bühne mit Verlauf, Einstellungsseite (zeigt nur den Status der Secrets).
- **rclone-Sync** (geplant): überträgt erzeugte Bilder ins Google Drive, bevor der Pod gelöscht wird.
- **LoRA-Liste** (geplant): Datei im Repo ohne Token; der Pod lädt die Einträge beim Start über das Civitai-Secret.

## Secrets (geplant)

- Die Secrets liegen als RunPod-Secrets im Konto; die Pod-Vorlage gibt sie beim Start als Umgebungsvariablen weiter.
- Das Startskript nutzt `GITHUB_TOKEN`, `CIVITAI_TOKEN` und `RCLONE_DRIVE_TOKEN`.
- Das Dashboard nutzt `DASHBOARD_PASSWORD` und später (optional) `ANTHROPIC_API_KEY`.
- Im Repo stehen nur die Namen, nie die Werte. Details und Begründungen: NOTIZEN.md.
