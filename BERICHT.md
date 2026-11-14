# BERICHT – Schritt 1h: Sync ins Google Drive

## Dateien
- **pod/paths.env** (neu): gemeinsame Pfade, Port, rclone-Remote und Drive-Ordner als schlichte NAME=Wert-Zeilen; auch für Python lesbar.
- **pod/sync.sh** (neu): `sync_once` ist die einzige Stelle mit dem rclone-Befehl (copy). Ohne Argument: blockierender letzter Sync mit flock, Meldung „Sync fertig“ bzw. Fehlerhinweis, Exit-Code wird durchgereicht. Mit `loop`: alle 30 s, flock -n, `--min-age 15s`, Fehler mit Zeitstempel in sync.log. Unbekanntes Argument: Hilfe, Exit 1.
- **pod/start.sh**: Pfadkonstanten entfernt, stattdessen `source paths.env` (Fallback: Meldung, /start.sh im Hintergrund, sleep infinity). `$DRIVE_FOLDER` statt festem „DreamDeck“. Neuer Schritt `step_start_sync` (ohne CIVITAI_TOKEN) nach dem ComfyUI-Start, Platzhalterkommentar entfernt.
- **ANLEITUNG.md**: Protokollzeilen für ComfyUI und Sync ergänzt; „Pod beenden“ als drei nummerierte Schritte.
- **ARCHITEKTUR.md**: rclone-Sync auf „umgesetzt“, Pod-Startskript-Zeile angepasst.
- **NOTIZEN.md**: zwei Einträge (paths.env, Sync per rclone copy).
- **MERKLISTE.md**: 1h abgehakt, Dashboard-Punkt in Etappe 2 ergänzt.

## Prüfung
- `bash -n` für start.sh und sync.sh ohne Fehler; unbekanntes Argument liefert Hilfe und Exit 1.
- Nicht getestet: echter rclone-Lauf (kein rclone/Drive in der devbox) – das passiert im Testlauf 1i.

## Offen
- Die Sperre nutzt einen Dateideskriptor (fd 9) statt `flock … Befehl`, damit die Umgebung erhalten bleibt; das ist eine kleine Abweichung von der Wortwahl der Vorgabe, aber gleiche Wirkung.
- 1i (Testlauf auf RunPod) steht weiter aus.
