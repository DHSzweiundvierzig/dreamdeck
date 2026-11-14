# BERICHT – Schritt 1a: Doku-Nachträge nach den Vorarbeiten

## Geändert
- MERKLISTE.md (Etappe 1): GitHub-Lese-Token, rclone-Drive-Token und Secrets in RunPod mit [x] abgehakt.
- MERKLISTE.md: Unterschritte 1a–1f eingefügt, 1a abgehakt, 1b–1f offen.
- MERKLISTE.md (Etappe 6 – Ideen-Parkplatz): Punkt „Eigene Google-Client-ID für rclone“ ergänzt.
- NOTIZEN.md: drei Ergänzungen (GITHUB_TOKEN-Ablauf, CIVITAI_TOKEN „Read Only“, RCLONE_DRIVE_TOKEN base64) und zwei neue Einträge vom 14.11.2026 (Firmenkonto, Drive-Ablage).
- ANLEITUNG.md: neuer Abschnitt „Zugänge erneuern“ (GitHub-Token, rclone-Token, Hinweis zum Drive-Ordner).
- Kein Programmcode geschrieben.

## Ergänzt statt neu angelegt
- NOTIZEN.md: Die drei Token-Punkte stehen als Unterpunkte im bestehenden Eintrag „Secrets nur als RunPod-Secrets“, vor dem HF_TOKEN-Hinweis.
- MERKLISTE.md: Der vorhandene Punkt „Pod-Startskript (git clone, ComfyUI, Modelle, LoRAs, rclone)“ blieb als Oberpunkt stehen (offen); 1b–1f sind als Unterpunkte darunter eingerückt, damit nichts doppelt ist.

## Auffälligkeiten
- Grep nach „Konto“/„Firmenkonto“ in MERKLISTE.md: kein Treffer, also kein offener Punkt zum Claude-Code-Konto, nichts abzuhaken (Schritt 2 entfällt). Die Entscheidung steht nun in NOTIZEN.md.
- ANLEITUNG.md hatte keinen Abschnitt zu Zugängen/Secrets, daher „Zugänge erneuern“ neu angelegt (vor „Pod beenden“ steht weiterhin der Platzhalter, der neue Abschnitt folgt am Ende).
- In der MERKLISTE heißt der Ideen-Abschnitt „Etappe 6 – Ideen-Parkplatz“; in der Vorgabe stand „Phase 6“. Dort eingetragen. Die NOTIZEN-Vorgabe spricht beim Civitai-Upload von „Phase 5“, in der MERKLISTE ist das „Etappe 5 – Civitai-Anbindung“; Wortlaut der Vorgabe übernommen.
- Kein Grep-Werkzeug verfügbar, Suche per `grep` über Bash (nur lesend).
- Es wurde nichts committet.
