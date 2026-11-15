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
    | DREAMDECK_DRIVE_TOKEN | Bilder ins Google Drive | Etappe 1 |
    | DREAMDECK_DRIVE_CLIENT_ID | Eigene Google-Client-ID für rclone | Etappe 1 |
    | DREAMDECK_DRIVE_CLIENT_SECRET | Zugehöriger Clientschlüssel | Etappe 1 |
    | DASHBOARD_PASSWORD | Schutz der Oberfläche | Etappe 2 |
    | ANTHROPIC_API_KEY | Prompt-Helfer | Etappe 4, optional |

  - GITHUB_TOKEN ist ein eigener fine-grained Token nur für dreamdeck mit nur Lesezugriff (Contents: Read), getrennt vom Token der devbox. Grund: Wird er bekannt, kann niemand etwas verändern.
  - rclone bekommt nur Zugriff auf selbst angelegte Dateien (Drive-Scope `drive.file`). Grund: DreamDeck kann den Rest des Drives weder lesen noch löschen.
  - GITHUB_TOKEN läuft am 15.05.2027 ab.
  - CIVITAI_TOKEN nutzt das Civitai-Preset „Read Only“. Grund: Der Pod muss nur LoRAs laden. Für den Upload in Etappe 5 wird ein eigener Key mit passenden Schreibrechten angelegt, dieser hier wird nicht erweitert.
  - DREAMDECK_DRIVE_TOKEN liegt base64-kodiert vor (so gibt `rclone authorize` den Token aus). Das Startskript muss ihn vor der Nutzung auspacken.
  - Kein HF_TOKEN nötig, solange FLUX aus der frei zugänglichen Comfy-Org-Kopie auf Hugging Face geladen wird.
- **LoRA-Bibliothek als Datei im Repo, ohne Token; der Pod lädt beim Start per Civitai-Secret** – Liste ist versionierbar, der Zugang bleibt geheim.
- **Formate als Presets um ca. 1 MP, Auflösung immer durch 16 teilbar, über 2 MP Warnung** – passt zu den Modellen, vermeidet Fehler und Speicherprobleme.
- **Bis zu 6 LoRAs gleichzeitig** – genug Spielraum für Kombinationen, ohne die Oberfläche zu überladen.
- **Oberfläche nach Entwurf „Variante B“** – Pipeline-Boxen 1–5 oben, Prompt-Leiste, Bühne mit Verlauf rechts, Einstellungsseite.
- **Bezeichner im Code auf Englisch, Doku und Kommentare auf Deutsch** – vorläufig, solange nichts anderes kommt.
- **ngrok aus der 1.0 wird nicht mehr genutzt** – Authtoken am 11.11.2026 rotiert.
- **14.11.2026 – Claude Code läuft mit dem Firmenkonto** – bewusste Entscheidung, so gewünscht.
- **14.11.2026 – Ablage im Google Drive: Ordner `DreamDeck/JJJJ-MM/`, Dateinamen `JJJJ-MM-TT_hhmmss_NNNNN_.png`** (ComfyUI hängt immer `_NNNNN_` an) – Gründe: wenige Ordner, chronologische Sortierung, und der Bildzähler von ComfyUI startet bei jedem frischen Pod wieder bei 00001; ohne Zeitstempel würden sich Dateinamen doppeln.
  - Ordner und Zeitstempel stecken im `filename_prefix` beim Speichern (z. B. `2026-11/2026-11-14_153012`). Ab Etappe 2 setzt ihn das Dashboard, im Testlauf werden Platzhalter in der ComfyUI-Oberfläche genutzt. rclone spiegelt nur. Grund: Die Bilder bleiben dort, wo ComfyUI sie kennt (wichtig für Galerie und „Nochmal“).
  - Den Ordner `DreamDeck` legt rclone selbst an. Wegen Scope `drive.file` sieht rclone keine von Hand angelegten Ordner.
- **Technik Dashboard**
  - Backend: Python mit FastAPI, uvicorn und httpx. Grund: gleiche Sprache wie ComfyUI; FastAPI baut auf Starlette auf, das auch im GW2-Dashboard läuft.
  - Verbindung zu ComfyUI: HTTP für Aufträge und Bilder, Websocket-Client für den Fortschritt. Grund: ComfyUI meldet Fortschritt nur per Websocket.
  - Nur DreamDeck ist von außen erreichbar, ComfyUI nur intern. Grund: Ein Passwort schützt alles.
  - Frontend: schlichtes HTML/CSS/JS ohne Build-Schritt, aufgeteilt in ES-Module statt globaler Variablen. Grund: einfach zu warten; ES-Module vermeiden Namenskonflikte, wenn das Projekt wächst.
  - Alpine.js für die datengetriebenen Bereiche (Step-Boxen, LoRA-Liste). Die Datei liegt fest im Repo statt per CDN, Version wird beim Einbinden in Etappe 2 festgelegt und gepinnt. Grund: Oberfläche aktualisiert sich aus den Daten von selbst; kein Build nötig.
  - Live-Fortschritt per Server-Sent Events, alles andere per fetch. Grund: Fortschritt ändert sich mehrmals pro Sekunde, Polling wäre zu träge.
  - Tests direkt auf dem Pod gegen das echte ComfyUI (15.11.2026, ersetzt den Plan mit Spiel-ComfyUI auf der devbox). Grund: Die Pod-Kosten sind bewusst akzeptiert; getestet wird gegen die echte API, und das Spiel-ComfyUI entfällt als eigener Bauteil.
- **14.11.2026 – Basis-Image: schlankes RunPod-PyTorch-Image, ComfyUI installiert unser Skript selbst in fester Version** (Version in einer Datei im Repo, Update nur bewusst) – Gründe: volle Kontrolle, jeder Schritt lesbar; die Startzeit bestimmen ohnehin die Modelle; fertige ComfyUI-Images machen ComfyUI oft öffentlich erreichbar. Image runpod/pytorch:2.1.0-cu1300-torch2130-ubuntu2404 (PyTorch 2.13.0, CUDA 13.0 statt 13.2, weil 13.2 einen neueren Host-Treiber braucht und die Auswahl einschränkt); ComfyUI v0.45.2; kein eigenes venv, das PyTorch des Images wird genutzt. Eigenes Image als Idee in Etappe 6.
- **14.11.2026 – Branch des Pods über `DREAMDECK_BRANCH`, Standard `main`** – Grund: Testläufe vor dem Merge.
- **14.11.2026 – RunPod-Dienste (Web-Terminal, SSH, Jupyter) laufen in Etappe 1 mit** – Grund: Fehlersuche. Ob sie abgeschaltet werden, wird in Etappe 2 entschieden.
- **14.11.2026 – Token-Hygiene im Startskript** – Das Skript entfernt den Token aus der Git-Adresse und löscht `GITHUB_TOKEN` aus der Umgebung.
  - Reihenfolge: Repo absichern läuft vor den RunPod-Diensten, damit `/start.sh` den Token nicht erbt. Die RunPod-Ausgabe landet in `/workspace/logs/runpod.log`.
  - Schutzziel sind Kindprozesse (ComfyUI, Erweiterungen, Dashboard). Wer per Web-Terminal oder SSH auf dem Pod ist, ist root und kann die Startumgebung ohnehin lesen – das ist bewusst akzeptiert, Zugang hat nur, wer ins RunPod-Konto kommt.
  - Der Fallback im Startbefehl (Klonen fehlgeschlagen) läuft ohne `unset`. Akzeptiert, weil dort nur die RunPod-Dienste laufen, keine Kindprozesse von DreamDeck.
- **14.11.2026 – Modell-Sets: fp16 (Standard) und fp8, immer nur eins pro Start** – fp16 als Einzeldateien von Comfy-Org/comfyanonymous (ohne Token ladbar), fp8 als Komplettpaket. Auswahl über `MODEL_SETS`, Standard in `pod/versions.env`. Ziel: unter 50 GB Container Disk bleiben.
  - Ladeart je Set (`checkpoint` oder `split`) steht in `pod/models.toml`, damit das Dashboard den passenden Lader wählt. Die Einstellungen sind sonst identisch.
  - Reserve bei Platzmangel: T5 als fp8 (`t5xxl_fp8_e4m3fn.safetensors`, ca. 4,9 GB) statt fp16.
- **14.11.2026 – Sicherheitsregeln für Downloads** – nur die Hosts huggingface.co und civitai.com (https); Prüfsummen (sha256) aus `pod/models.toml`, fehlende werden beim ersten Lauf gemessen und protokolliert; Pickle-Dateien (.pth/.pt/.ckpt/.bin) nur mit Prüfsumme; Download erst in eine `.part`-Datei, umbenannt wird nach bestandener Prüfung; Platzprüfung vor dem Laden; Header (Tokens) werden nie ausgegeben.
- **14.11.2026 – Download-Baustein in Python (`pod/models.py`) statt in Bash** – Grund: Das Dashboard verwendet ihn wieder (Nachladen, LoRAs), es gibt nur eine Download-Logik. Nur Standardbibliothek.
- **14.11.2026 – Grundhaltung „DreamDeck gibt nichts vor“** – beim Start wird nur PsyDreamer geladen, alles andere bei Bedarf übers Dashboard.
- **14.11.2026 – LoRA-Liste (`pod/loras.toml`) nur mit Civitai-Versionsnummer** – Dateiname, Größe, Basismodell und Prüfsumme kommen über die Civitai-API; nichts davon wird von Hand gepflegt.
  - Regeln: nur Typ LoRA, nur Basismodell Flux.1 D, nur SafeTensor. Alles andere wird abgelehnt.
  - Der Token kommt nur aus der Umgebung (`CIVITAI_TOKEN`), nie als Argument – Kommandozeilen sind für andere Prozesse sichtbar.
  - Alle Anfragen senden den User-Agent `DreamDeck/1.0`.
- **14.11.2026 – Bildablage außerhalb von ComfyUI: `/workspace/output` per `--output-directory`** – Grund: `step_install_comfyui` löscht `/workspace/ComfyUI` bei einem Versionswechsel.
- **14.11.2026 – rclone fest in v1.75.2 von GitHub-Releases, mit Prüfsumme**
  - Grund Version: mehr als 14 Tage alt (v1.76.0 war erst 8 Tage alt); Prüfsumme gegen die offizielle SHA256SUMS geprüft.
  - github.com ist als Download-Quelle nur für Werkzeuge erlaubt, Modelle weiter nur huggingface.co und civitai.com.
  - Token-Format: base64 ohne Padding, darin JSON mit Feld „token“.
  - Reihenfolge: rclone-Einrichtung vor dem ComfyUI-Start, danach unset, damit ComfyUI den Token nicht erbt. ComfyUI startet ohne CIVITAI_TOKEN.
- **14.11.2026 – Gemeinsame Pfade in `pod/paths.env`** – Grund: eine Stelle für start.sh, sync.sh und später das Dashboard; nur NAME=Wert, damit auch Python sie lesen kann.
- **14.11.2026 – Sync per rclone copy**
  - Schleife alle 30 s mit Mindestalter 15 s, gegen halb geschriebene Bilder.
  - Manueller letzter Sync ohne Mindestalter.
  - flock gegen Überschneidung von Schleife und manuellem Sync.
  - copy statt move, damit ComfyUI die Bilder bis zum Pod-Ende behält.
- **15.11.2026 – Drive-Secret heißt DREAMDECK_DRIVE_TOKEN** – Grund: rclone liest `RCLONE_DRIVE_*` als eigene Optionen (`RCLONE_DRIVE_TOKEN` = Option „token“) und überschreibt damit die Konfiguration; RunPod exportiert Secrets auch in SSH-Sitzungen, dort hat der alte Name den manuellen Sync gestört.
- **15.11.2026 – Eigene Google-Client-ID für rclone** – Grund: rclones geteilte Client-ID wird 2026 abgeschaltet. Google-Cloud-Projekt „dreamdeck“, Client-Typ Desktop-App, App veröffentlicht („In Produktion“), weil Tokens im Testmodus nach 7 Tagen ablaufen. Startseite und Datenschutz als Pflichtangabe auf dhszweiundvierzig.github.io. Der Drive-Token muss mit derselben Client-ID erzeugt werden.
- **15.11.2026 – Entwicklungsablauf in Etappe 2**
  - Neuer Code kommt per `pod/update.sh` auf den laufenden Pod (Branch wechseln, neuen Stand holen, Dashboard neu starten). Die Vorlage bleibt auf `DREAMDECK_BRANCH=main`. Grund: RunPod-Vorlagen lassen sich nicht bearbeiten, gespeicherte Variablen gehen verloren.
  - Das Dashboard lauscht bis Schritt 2j nur auf 127.0.0.1, der Zugriff läuft per SSH-Tunnel. Grund: nichts öffentlich, solange der Passwortschutz fehlt.
  - Reihenfolge je Schritt: Umsetzung → Commit + Sync → update.sh auf dem Pod → Browser-Kontrolle; Befunde als weiterer Commit. Grund: Der Pod holt den Code aus GitHub.
  - Zeitstempel im Dateinamen in Europe/Berlin, gesetzt vom Backend. Grund: unabhängig von der Zeitzone von Browser und Pod.
