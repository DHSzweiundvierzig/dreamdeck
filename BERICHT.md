# BERICHT – ANLEITUNG.md an den Testlauf angepasst

## Geänderte Abschnitte (nur ANLEITUNG.md)
- **RunPod-Vorlage:** Punkte 1–3 unverändert. Punkt 4 (Expose TCP Ports 22/SSH, keine HTTP Ports) und Punkt 5 (Container Disk 50 GB, Volume Disk 0 GB) ersetzt. Neu Punkt 6: Environment Variables per Raw editor mit den fünf Secrets, `DREAMDECK_BRANCH` und `PUBLIC_KEY`, dazu Hinweise (PUBLIC_KEY, BRANCH, MODEL_SETS, lila Verweise).
- **Neu angelegt:** „### Pod starten (jedes Mal)“ (6 Schritte), nach der Vorlage.
- **Arbeiten:** „Folgt in Etappe 2.“ ersetzt durch „### ComfyUI per SSH-Tunnel öffnen (bis Etappe 2)“.
- **Zugänge erneuern:** Punkt „rclone-Token“ ersetzt durch „Google-Zugang (rclone)“ mit eigener Client-ID, Client-Datei, Token-Erzeugung und Aufräumen der Zwischenablage.
- Unverändert: Protokoll ansehen, LoRAs beim Start, Pod beenden, GitHub-Token, Hinweis zum DreamDeck-Ordner.

## Abschlusskontrolle
- `RCLONE_DRIVE_TOKEN` und „Folgt in Etappe 2“: keine Treffer in ANLEITUNG.md.
- Die fünf Secret-Namen (`GITHUB_TOKEN`, `CIVITAI_TOKEN`, `DREAMDECK_DRIVE_TOKEN`, `DREAMDECK_DRIVE_CLIENT_ID`, `DREAMDECK_DRIVE_CLIENT_SECRET`) stehen im Raw-Block je genau einmal und kommen mit gleicher Schreibweise in pod/start.sh vor (nur gegrept, nicht geändert).

## Merkliste
- Kein passender offener Punkt vorhanden, nichts abgehakt.

## Offen
- `PUBLIC_KEY` wird in start.sh nicht ausgewertet (RunPod-eigener Mechanismus), daher nicht in der Namensprüfung enthalten.
