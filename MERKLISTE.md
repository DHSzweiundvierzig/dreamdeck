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
  - [ ] 1h Sync: pod/sync.sh für Schleife im Hintergrund und letzten Sync vor dem Löschen; ANLEITUNG „Pod beenden“
  - [ ] 1i Erster Testlauf auf RunPod als Abnahme – vorher GPU-Wahl; dabei prüfen, ob der Civitai-Download mit „Read Only“ klappt; gemessene Prüfsummen eintragen, freien Speicher prüfen (df -h); vorher klären, wie die ComfyUI-Oberfläche trotz „nur intern“ erreichbar ist

## Etappe 2 – Dashboard-MVP
- [ ] Spiel-ComfyUI (Fake-Bilder) für Tests auf der devbox
- [ ] Dashboard-MVP
- [ ] Entscheiden, ob RunPod-Dienste (Jupyter, SSH) abgeschaltet werden
- [ ] Python in der devbox (für Dashboard und Tests)
- [ ] Einstellungsseite: Modell-Sets mit Status und Nachladen, evtl. Set tauschen
- [ ] Modell-Dropdown nach Ladeart (checkpoint/split)
- [ ] LoRA per Civitai-Link oder Versionsnummer nachladen (nutzt civitai_lora/download_file)

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
- [ ] Eigene Google-Client-ID für rclone, falls die geteilte Client-ID von rclone gedrosselt wird
- [ ] Vergleich fp8 gegen fp16
