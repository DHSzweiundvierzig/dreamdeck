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
- [ ] Pod-Startskript (git clone, ComfyUI, Modelle, LoRAs, rclone) – Unterschritte:
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
  - [ ] 1o Abschluss-Testlauf mit neuer Vorlage und neuen Secrets, danach etappe-1 nach main mergen

## Etappe 2 – Dashboard-MVP
- [ ] Spiel-ComfyUI (Fake-Bilder) für Tests auf der devbox
- [ ] Dashboard-MVP
- [ ] Entscheiden, ob RunPod-Dienste (Jupyter, SSH) abgeschaltet werden – dabei beachten: RunPod exportiert alle Secrets auch in SSH- und Web-Terminal-Sitzungen
- [ ] Python in der devbox (für Dashboard und Tests)
- [ ] Einstellungsseite: Modell-Sets mit Status und Nachladen, evtl. Set tauschen
- [ ] Modell-Dropdown nach Ladeart (checkpoint/split)
- [ ] LoRA per Civitai-Link oder Versionsnummer nachladen (nutzt civitai_lora/download_file)
- [ ] Dashboard liest Pfade und Port aus pod/paths.env
- [ ] Zeitzone für Datum/Uhrzeit im Dateinamen festlegen (ComfyUI-Oberfläche nutzt die Ortszeit des Browsers)

## Etappe 3 – Galerie & Metadaten
- [ ] Galerie & Metadaten
- [ ] Metadaten alter Bilder auslesen (welche LoRAs waren dabei?)

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
- [ ] Tastatur-Kürzel 1–5
- [ ] Markierung geänderter Werte
- [x] Eigene Google-Client-ID für rclone, falls die geteilte Client-ID von rclone gedrosselt wird
- [ ] Vergleich fp8 gegen fp16
- [ ] Speicher im Blick behalten, bevor weitere Modelle dazukommen (Testlauf: Disk 36 von 50 GB, RAM-Spitze 78 % beim Laden)
- [ ] RunPod-MCP prüfen (nur nach ausdrücklicher Freigabe)
