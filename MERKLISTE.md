# MERKLISTE

## Etappe 0 – Grundlagen
- [x] Repo
- [x] Doku-Gerüst
- [x] Secrets-Konzept
- [x] Alte Zugangsdaten der 1.0 prüfen
- [x] Technik-Entscheidung Dashboard

## Etappe 1 – Pod-Startskript
- [x] GitHub-Lese-Token für dreamdeck anlegen (fine-grained, nur Contents: Read)
- [x] rclone-Drive-Token einmalig lokal erzeugen (Scope drive.file)
- [x] Secrets in RunPod anlegen
- [x] Pod-Startskript (git clone, ComfyUI, Modelle, LoRAs, rclone) – Unterschritte:
  - [x] 1a Doku-Nachträge nach den Vorarbeiten
  - [x] 1b Startskript-Gerüst, Startbefehl für die RunPod-Vorlage
  - [x] 1c Basis-Image und ComfyUI-Version festlegen, ComfyUI installieren
  - [x] 1d Modelle laden (FLUX.1 [dev], T5, CLIP-L, VAE, Upscaler), vorhandene überspringen
  - [x] 1e LoRAs von Civitai laden, Liste im Repo pflegbar
  - [x] 1f ComfyUI im Hintergrund starten (nur intern, Bilder unter /workspace/output)
  - [x] 1g rclone installieren (v1.75.2 mit Prüfsumme) und einrichten (Token auspacken, Ordner DreamDeck/)
  - [x] 1h Sync: pod/sync.sh (Schleife + letzter Sync), Pfade in pod/paths.env, ANLEITUNG „Pod beenden“
  - [x] 1i Erster Testlauf auf RunPod als Abnahme – vorher GPU-Wahl; dabei prüfen, ob der Civitai-Download mit „Read Only“ klappt; gemessene Prüfsummen eintragen, freien Speicher prüfen (df -h); vorher klären, wie die ComfyUI-Oberfläche trotz „nur intern“ erreichbar ist
  - [x] 1j Drive-Secret in DREAMDECK_DRIVE_TOKEN umbenannt (Kollision mit rclones RCLONE_DRIVE_*)
  - [x] 1k Eigene Google-Client-ID für rclone (Secrets DREAMDECK_DRIVE_CLIENT_ID/_SECRET)
  - [x] 1l Gemessene Prüfsummen für t5, clip_l und vae eingetragen
  - [x] 1m ANLEITUNG: Vorlage (Port 22, PUBLIC_KEY, Raw-Editor), Pod-Start, SSH-Tunnel, Google-Zugang
  - [x] 1n Merkliste mit den Funden aus dem Testlauf ergänzt
  - [x] 1o Abschluss-Testlauf mit neuer Vorlage und neuen Secrets, danach etappe-1 nach main mergen
  - [x] 1p ANLEITUNG: Hinweise zum Bearbeiten der Vorlage und zum Drive-Ordner nach Client-Wechsel

## Etappe 2 – Dashboard-MVP
- [x] Dashboard-MVP – Unterschritte:
  - [x] 2a Merkliste und Doku für Etappe 2 neu gegliedert
  - [x] 2b Backend-Gerüst: FastAPI, requirements.txt mit festen Versionen, liest pod/paths.env, Startseite, /api/health
  - [x] 2c Pod: start.sh installiert die Abhängigkeiten und startet das Dashboard (nur 127.0.0.1), ANLEITUNG zum SSH-Tunnel – erster Pod-Test (bestanden am 15.11.2026)
  - [x] 2d ComfyUI-Anbindung: Workflow aus Vorlage (split) mit LoRA-Kette, POST /api/generate, filename_prefix mit Monatsordner und Zeitstempel (Europe/Berlin) – Pod-Test bestanden am 15.11.2026, Bild identisch mit dem ComfyUI-Testbild
  - [x] 2e Fortschritt: ComfyUI-Websocket als Server-Sent Events an die Oberfläche – Pod-Test bestanden am 15.11.2026 (start, fortschritt 1–20, fertig mit Bild, warteschlange)
  - [x] 2f Oberflächen-Gerüst nach Variante B, Alpine.js fest im Repo und gepinnt – Browser-Kontrolle bestanden am 15.11.2026
  - [x] 2g Prompt-Leiste: Prompt, Format-Presets, Seed, Batch-Anzahl – Browser-Kontrolle bestanden am 15.11.2026 (inkl. Seed 2^64 − 1)
  - [x] 2h LoRA-Auswahl (bis 6 gleichzeitig, mit Stärke-Regler) – Browser-Kontrolle bestanden am 15.11.2026 (PsyDreamer-Bild per Dashboard)
  - [x] 2i Backend für die Bühne: GET /api/bild, EventHub merkt letzten Stand (verbindung, warteschlange) – Pod-Test bestanden am 15.11.2026 (Hub sofort mit Stand, /api/bild 200/404/404)
  - [x] 2l Bühne in der Oberfläche: „Modell wird geladen“, Fortschrittsbalken, Bild mit Info-Karte, Verlauf der Sitzung – Browser-Kontrolle bestanden am 15.11.2026
  - [x] 2l Korrektur: Live-Verbindung nur bei sichtbarem Tab oder laufendem Auftrag (Chrome-Grenze 6 Verbindungen) – Stresstest mit 10 Tabs bestanden am 15.11.2026
  - [x] 2m Verlauf vom Pod: GET /api/verlauf (neueste 60 aus dem Output-Ordner), Oberfläche lädt beim Start und beim Sichtbarwerden – Pod-/Browser-Test bestanden am 16.11.2026
  - [x] 2j Passwortschutz (DASHBOARD_PASSWORD): Login-Seite, Sitzungs-Cookie, Schutz aller Wege außer /api/health – Pod-/Browser-Test bestanden am 16.11.2026
  - [x] 2n Dashboard über den RunPod-Proxy (0.0.0.0, HTTP-Port 8000), DASHBOARD_PASSWORD in der Secrets-Prüfung, Sync-Schleife ohne Passwort – Pod-/Browser-Test bestanden am 16.11.2026 (Proxy, SSE über 3 min ohne Abbruch, -8188 = 404, Sync ohne Passwort)
  - [x] 2o RunPod-Dienste: auf dem Pod prüfen, was /start.sh startet (Jupyter, nginx, sshd, Web-Terminal), und entscheiden, was abgeschaltet wird – entschieden am 16.11.2026: nichts abschalten (siehe NOTIZEN)
  - [x] 2k Abnahme auf RunPod: PsyDreamer-Bild ohne ComfyUI-Oberfläche, danach etappe-2 nach main mergen und Vorlage wieder mit DREAMDECK_BRANCH=main anlegen – Abnahme bestanden am 16.11.2026 (PsyDreamer-Bild über den Proxy, ohne ComfyUI-Oberfläche); Merge nach main und neue Vorlage im Anschluss
- [x] Entscheiden, ob RunPod-Dienste (Jupyter, SSH) abgeschaltet werden – dabei beachten: RunPod exportiert alle Secrets auch in SSH- und Web-Terminal-Sitzungen (→ 2o) – entschieden in 2o
- [x] Dashboard liest Pfade und Port aus pod/paths.env (→ 2b)
- [x] Zeitzone für Datum/Uhrzeit im Dateinamen festlegen (ComfyUI-Oberfläche nutzt die Ortszeit des Browsers) – entschieden: Europe/Berlin, Umsetzung in 2d

## Etappe 2 – Ausbau (nach dem MVP)
- [ ] Einstellungsseite: Modell-Sets mit Status und Nachladen, evtl. Set tauschen
- [ ] Modell-Dropdown nach Ladeart (checkpoint/split)
- [ ] Bühnenbild per Klick groß anzeigen (Vollbild-Ansicht)
- [ ] Boxen per Klick irgendwo in die geschlossene Box öffnen, Pfeil entfernen; offene Box über die Kopfzeile schließen (Regler-Klicks dürfen nicht schließen)
- [ ] Live-Verbindung (live) in der Kopfzeile anzeigen; Warteschlangen-Position des eigenen Auftrags statt Gesamtlänge
- [ ] LoRA per Civitai-Link oder Versionsnummer nachladen (nutzt civitai_lora/download_file)
- [ ] Klick-Tutorial mit An/Aus-Schalter: Erklär-Boxen an jedem Menü/Dropdown, Schritt für Schritt
- [ ] GPU-Name in der Kopfzeile (aus ComfyUI /system_stats über /api/health durchreichen)
- [ ] Anzeige „Drive-Sync aktiv“ in der Kopfzeile – Datenquelle klären
- [ ] Seed-Modus „+1 je Bild“ / „−1 je Bild“ (braucht mehrere Aufträge statt eines Batches)
- [ ] Deko-Streifen der Boxen näher am Entwurf (schräg, größer, Farbe)
- [ ] Abmelden-Knopf in der Kopfzeile (POST /api/logout)
- [ ] Triggerwörter zu LoRAs anzeigen und per Knopf in den Prompt einfügen (Daten aus Civitai, → Etappe 5) und lesbare Anzeigenamen statt Dateinamen (z. B. FLUX_Psy_Dreamer_Style-000007 → PsyDreamer)

## Etappe 3 – Galerie & Metadaten
- [ ] Galerie & Metadaten
- [ ] Metadaten alter Bilder auslesen (welche LoRAs waren dabei?)
- [ ] Galerie liest Bilder aus Google Drive (Output-Ordner ist mit dem Pod weg) – Weg klären: live per rclone oder beim Pod-Start holen

## Etappe 4 – Prompt-Werkstatt
- [ ] Prompt-Werkstatt

## Etappe 5 – Civitai-Anbindung
- [ ] Civitai-Anbindung

## Etappe 6 – Ideen-Parkplatz
- [ ] Network Volume – dann Modelle und Bilder außerhalb des ComfyUI-Ordners ablegen (extra_model_paths), weil ein ComfyUI-Versionswechsel den Ordner löscht
- [ ] Upscaling-Workflow
- [ ] Bild-zu-Bild
- [ ] Vergleichsansicht
- [ ] Serverless
- [ ] Eigenes Pod-Image (schnellerer Start)
- [ ] Spiel-ComfyUI (Fake-Bilder) für Tests auf der devbox
- [ ] Python in der devbox (für Dashboard und Tests)
- [ ] Tastatur-Kürzel 1–5
- [ ] Markierung geänderter Werte
- [x] Eigene Google-Client-ID für rclone, falls die geteilte Client-ID von rclone gedrosselt wird
- [ ] Vergleich fp8 gegen fp16
- [ ] Speicher im Blick behalten, bevor weitere Modelle dazukommen (Testlauf: Disk 36 von 50 GB, RAM-Spitze 78 % beim Laden)
- [ ] RunPod-MCP prüfen (nur nach ausdrücklicher Freigabe)
