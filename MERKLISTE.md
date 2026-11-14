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
  - [ ] 1b Startskript-Gerüst, Startbefehl für die RunPod-Vorlage (Repo per GITHUB_TOKEN klonen), ComfyUI installieren – vorher Basis-Image entscheiden
  - [ ] 1c Modelle laden (FLUX.1 [dev], T5, CLIP-L, VAE, Upscaler), vorhandene überspringen
  - [ ] 1d LoRAs von Civitai laden, Liste im Repo pflegbar
  - [ ] 1e ComfyUI im Hintergrund starten, rclone einrichten (Token auspacken, Monatsordner, Dateinamen mit Zeitstempel)
  - [ ] 1f Erster Testlauf auf RunPod als Abnahme – vorher GPU-Wahl; dabei prüfen, ob der Civitai-Download mit „Read Only“ klappt

## Etappe 2 – Dashboard-MVP
- [ ] Spiel-ComfyUI (Fake-Bilder) für Tests auf der devbox
- [ ] Dashboard-MVP

## Etappe 3 – Galerie & Metadaten
- [ ] Galerie & Metadaten

## Etappe 4 – Prompt-Werkstatt
- [ ] Prompt-Werkstatt

## Etappe 5 – Civitai-Anbindung
- [ ] Civitai-Anbindung

## Etappe 6 – Ideen-Parkplatz
- [ ] Network Volume
- [ ] Upscaling-Workflow
- [ ] Bild-zu-Bild
- [ ] Vergleichsansicht
- [ ] Serverless
- [ ] Tastatur-Kürzel 1–5
- [ ] Markierung geänderter Werte
- [ ] Eigene Google-Client-ID für rclone, falls die geteilte Client-ID von rclone gedrosselt wird
