# ARCHITEKTUR (alles geplant, nichts umgesetzt)

Keine Ordnerstruktur festgelegt; sie ergibt sich bei der Umsetzung.

- **Pod-Startskript** (geplant): richtet einen frischen RunPod-Pod ein – Repo klonen, ComfyUI installieren, Modelle und LoRAs laden, rclone konfigurieren.
- **ComfyUI headless** (geplant): läuft ohne eigene Oberfläche als Bildmotor und wird über die ComfyUI-API angesprochen.
- **DreamDeck-Backend** (geplant): vermittelt zwischen Oberfläche und ComfyUI-API, verwaltet Verlauf und Metadaten, liest Secrets nur aus Umgebungsvariablen.
- **Oberfläche** (geplant): nach Entwurf „Variante B“ – Pipeline-Boxen 1–5, Prompt-Leiste, Bühne mit Verlauf, Einstellungsseite (zeigt nur den Status der Secrets).
- **rclone-Sync** (geplant): überträgt erzeugte Bilder ins Google Drive, bevor der Pod gelöscht wird.
- **LoRA-Liste** (geplant): Datei im Repo ohne Token; der Pod lädt die Einträge beim Start über das Civitai-Secret.
