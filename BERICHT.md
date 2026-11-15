# BERICHT – Eigene Google-Client-ID für rclone

## Geänderte Stellen
- **pod/start.sh**
  - `step_check_secrets`: Schleife prüft zusätzlich `DREAMDECK_DRIVE_CLIENT_ID` und `DREAMDECK_DRIVE_CLIENT_SECRET` (Werte werden nie ausgegeben).
  - `step_configure_rclone`: liest beide Werte (`.strip()`), Plausibilitätsprüfung (leer oder client_id ohne Endung `.apps.googleusercontent.com` → Meldung „Client-ID oder Client-Secret unbrauchbar (leer oder vertauscht?)“, `exit 1`, ohne Werte auszugeben), conf-Reihenfolge: type, client_id, client_secret, scope, token. Kommentar über der Funktion ergänzt.
  - Beide vorhandenen `unset`-Zeilen erweitert, keine neuen angelegt. Keine neuen Funktionen.
- **ARCHITEKTUR.md**: Aufzählung der Startskript-Secrets um beide Namen ergänzt.
- **NOTIZEN.md**: zwei Zeilen in der Secrets-Tabelle, neuer datierter Eintrag vom 15.11.2026 am Ende der Entscheidungen.
- **MERKLISTE.md**: Punkt „Eigene Google-Client-ID für rclone“ mit `[x]` abgehakt.
- **ANLEITUNG.md**: unverändert (folgt in 1n).

## Abschlusskontrolle (Schritt 6)
- `grep -rn DREAMDECK_DRIVE_CLIENT` (ohne .git): in `start.sh` überall gleich geschrieben (Schleife, Kommentar, beide `os.environ`-Zugriffe, beide `unset`); weitere Treffer nur in ARCHITEKTUR.md und NOTIZEN.md.
- `bash -n pod/start.sh`: ohne Fehler.

## Offen
- In RunPod müssen die Secrets `DREAMDECK_DRIVE_CLIENT_ID` und `DREAMDECK_DRIVE_CLIENT_SECRET` angelegt werden; ohne sie bricht der Pod-Start bei „Secrets prüfen“ ab.
- Der Drive-Token muss mit derselben Client-ID neu erzeugt werden.
- Ein echter Lauf auf RunPod ist nicht getestet.
