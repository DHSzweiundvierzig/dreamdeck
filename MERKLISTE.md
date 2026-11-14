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
  - [ ] 1c Basis-Image und ComfyUI-Version festlegen, ComfyUI installieren
  - [ ] 1d Modelle laden (FLUX.1 [dev], T5, CLIP-L, VAE, Upscaler), vorhandene überspringen
  - [ ] 1e LoRAs von Civitai laden, Liste im Repo pflegbar
  - [ ] 1f ComfyUI im Hintergrund starten, rclone einrichten (Token auspacken, Monatsordner, Dateinamen mit Zeitstempel)
  - [ ] 1g Erster Testlauf auf RunPod als Abnahme – vorher GPU-Wahl; dabei prüfen, ob der Civitai-Download mit „Read Only“ klappt

## Etappe 2 – Dashboard-MVP
- [ ] Spiel-ComfyUI (Fake-Bilder) für Tests auf der devbox
- [ ] Dashboard-MVP
- [ ] Entscheiden, ob RunPod-Dienste (Jupyter, SSH) abgeschaltet werden

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
- [ ] Eigenes Pod-Image (schnellerer Start)
- [ ] Tastatur-Kürzel 1–5
- [ ] Markierung geänderter Werte
- [ ] Eigene Google-Client-ID für rclone, falls die geteilte Client-ID von rclone gedrosselt wird
