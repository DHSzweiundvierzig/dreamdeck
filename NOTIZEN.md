# NOTIZEN – getroffene Entscheidungen

- **Arbeitstitel „DreamDeck“** – Name wird für Repo und Oberfläche genutzt; kann später noch geändert werden.
- **ComfyUI bleibt der Motor, DreamDeck steuert es über die ComfyUI-API** – bewährte Bildpipeline wird nicht neu gebaut, DreamDeck ist nur die Bedienschicht.
- **Pod nur bei Bedarf: starten, arbeiten, löschen; Code kommt per `git clone` aus diesem Repo** – spart Kosten; der Pod ist wegwerfbar, der Zustand liegt im Repo.
- **Bilder wandern per rclone ins Google Drive; LoRA-Training läuft auf Civitai, nicht selbst gehostet** – Ergebnisse überleben das Löschen des Pods; Training selbst zu hosten wäre unnötiger Aufwand.
- **Secrets nur als RunPod-Secrets; die Einstellungsseite zeigt nur den Status, keine Eingabe** – nichts Geheimes im Repo oder in der Oberfläche.
- **LoRA-Bibliothek als Datei im Repo, ohne Token; der Pod lädt beim Start per Civitai-Secret** – Liste ist versionierbar, der Zugang bleibt geheim.
- **Formate als Presets um ca. 1 MP, Auflösung immer durch 16 teilbar, über 2 MP Warnung** – passt zu den Modellen, vermeidet Fehler und Speicherprobleme.
- **Bis zu 6 LoRAs gleichzeitig** – genug Spielraum für Kombinationen, ohne die Oberfläche zu überladen.
- **Oberfläche nach Entwurf „Variante B“** – Pipeline-Boxen 1–5 oben, Prompt-Leiste, Bühne mit Verlauf rechts, Einstellungsseite.
- **Bezeichner im Code auf Englisch, Doku und Kommentare auf Deutsch** – vorläufig, solange nichts anderes kommt.
