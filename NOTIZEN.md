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
  - GITHUB_TOKEN läuft am 15.05.2027 ab.
  - CIVITAI_TOKEN nutzt das Civitai-Preset „Read Only“. Grund: Der Pod muss nur LoRAs laden. Für den Upload in Phase 5 wird ein eigener Key mit passenden Schreibrechten angelegt, dieser hier wird nicht erweitert.
  - RCLONE_DRIVE_TOKEN liegt base64-kodiert vor (so gibt `rclone authorize` den Token aus). Das Startskript muss ihn vor der Nutzung auspacken.
  - Kein HF_TOKEN nötig, solange FLUX aus der frei zugänglichen Comfy-Org-Kopie auf Hugging Face geladen wird.
- **LoRA-Bibliothek als Datei im Repo, ohne Token; der Pod lädt beim Start per Civitai-Secret** – Liste ist versionierbar, der Zugang bleibt geheim.
- **Formate als Presets um ca. 1 MP, Auflösung immer durch 16 teilbar, über 2 MP Warnung** – passt zu den Modellen, vermeidet Fehler und Speicherprobleme.
- **Bis zu 6 LoRAs gleichzeitig** – genug Spielraum für Kombinationen, ohne die Oberfläche zu überladen.
- **Oberfläche nach Entwurf „Variante B“** – Pipeline-Boxen 1–5 oben, Prompt-Leiste, Bühne mit Verlauf rechts, Einstellungsseite.
- **Bezeichner im Code auf Englisch, Doku und Kommentare auf Deutsch** – vorläufig, solange nichts anderes kommt.
- **ngrok aus der 1.0 wird nicht mehr genutzt** – Authtoken am 11.11.2026 rotiert.
- **14.11.2026 – Claude Code läuft mit dem Firmenkonto** – bewusste Entscheidung, so gewünscht.
- **14.11.2026 – Ablage im Google Drive: Ordner `DreamDeck/JJJJ-MM/`, Dateinamen `JJJJ-MM-TT_hhmmss_NNNNN.png`** – Gründe: wenige Ordner, chronologische Sortierung, und der Bildzähler von ComfyUI startet bei jedem frischen Pod wieder bei 00001; ohne Zeitstempel würden sich Dateinamen doppeln.
  - Den Ordner `DreamDeck` legt rclone selbst an. Wegen Scope `drive.file` sieht rclone keine von Hand angelegten Ordner.
- **Technik Dashboard**
  - Backend: Python mit FastAPI, uvicorn und httpx. Grund: gleiche Sprache wie ComfyUI; FastAPI baut auf Starlette auf, das auch im GW2-Dashboard läuft.
  - Verbindung zu ComfyUI: HTTP für Aufträge und Bilder, Websocket-Client für den Fortschritt. Grund: ComfyUI meldet Fortschritt nur per Websocket.
  - Nur DreamDeck ist von außen erreichbar, ComfyUI nur intern. Grund: Ein Passwort schützt alles.
  - Frontend: schlichtes HTML/CSS/JS ohne Build-Schritt, aufgeteilt in ES-Module statt globaler Variablen. Grund: einfach zu warten; ES-Module vermeiden Namenskonflikte, wenn das Projekt wächst.
  - Alpine.js für die datengetriebenen Bereiche (Step-Boxen, LoRA-Liste). Die Datei liegt fest im Repo statt per CDN, Version wird beim Einbinden in Etappe 2 festgelegt und gepinnt. Grund: Oberfläche aktualisiert sich aus den Daten von selbst; kein Build nötig.
  - Live-Fortschritt per Server-Sent Events, alles andere per fetch. Grund: Fortschritt ändert sich mehrmals pro Sekunde, Polling wäre zu träge.
  - Tests auf der devbox ohne GPU mit einem Spiel-ComfyUI, das Fake-Bilder liefert. Grund: Der teure Pod wird erst gebraucht, wenn es ernst wird.
