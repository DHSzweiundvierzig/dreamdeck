# NOTIZEN – getroffene Entscheidungen

- **Arbeitstitel „DreamDeck“** – Name wird für Repo und Oberfläche genutzt; kann später noch geändert werden.
- **ComfyUI bleibt der Motor, DreamDeck steuert es über die ComfyUI-API** – bewährte Bildpipeline wird nicht neu gebaut, DreamDeck ist nur die Bedienschicht.
- **Pod nur bei Bedarf: starten, arbeiten, löschen; Code kommt per `git clone` aus diesem Repo** – spart Kosten; der Pod ist wegwerfbar, der Zustand liegt im Repo.
- **Bilder wandern per rclone ins Google Drive; LoRA-Training läuft auf Civitai, nicht selbst gehostet** – Ergebnisse überleben das Löschen des Pods; Training selbst zu hosten wäre unnötiger Aufwand.
- **Secrets nur als RunPod-Secrets; die Einstellungsseite zeigt nur den Status, keine Eingabe** – nichts Geheimes im Repo oder in der Oberfläche.
  - Im Repo stehen nur die Namen der Secrets, nie die Werte.
  - Secrets:

    | Name | Zweck | nötig ab |
    |---|---|---|
    | GITHUB_TOKEN | Pod klont das private Repo | Etappe 1 |
    | CIVITAI_TOKEN | LoRAs von Civitai laden | Etappe 1 |
    | RCLONE_DRIVE_TOKEN | Bilder ins Google Drive | Etappe 1 |
    | DASHBOARD_PASSWORD | Schutz der Oberfläche | Etappe 2 |
    | ANTHROPIC_API_KEY | Prompt-Helfer | Etappe 4, optional |

  - GITHUB_TOKEN ist ein eigener fine-grained Token nur für dreamdeck mit nur Lesezugriff (Contents: Read), getrennt vom Token der devbox. Grund: Wird er bekannt, kann niemand etwas verändern.
  - rclone bekommt nur Zugriff auf selbst angelegte Dateien (Drive-Scope `drive.file`). Grund: DreamDeck kann den Rest des Drives weder lesen noch löschen.
  - Kein HF_TOKEN nötig, solange FLUX aus der frei zugänglichen Comfy-Org-Kopie auf Hugging Face geladen wird.
- **LoRA-Bibliothek als Datei im Repo, ohne Token; der Pod lädt beim Start per Civitai-Secret** – Liste ist versionierbar, der Zugang bleibt geheim.
- **Formate als Presets um ca. 1 MP, Auflösung immer durch 16 teilbar, über 2 MP Warnung** – passt zu den Modellen, vermeidet Fehler und Speicherprobleme.
- **Bis zu 6 LoRAs gleichzeitig** – genug Spielraum für Kombinationen, ohne die Oberfläche zu überladen.
- **Oberfläche nach Entwurf „Variante B“** – Pipeline-Boxen 1–5 oben, Prompt-Leiste, Bühne mit Verlauf rechts, Einstellungsseite.
- **Bezeichner im Code auf Englisch, Doku und Kommentare auf Deutsch** – vorläufig, solange nichts anderes kommt.
- **ngrok aus der 1.0 wird nicht mehr genutzt** – Authtoken am 11.11.2026 rotiert.
