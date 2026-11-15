# BERICHT – Umbenennung Drive-Secret: RCLONE_DRIVE_TOKEN → DREAMDECK_DRIVE_TOKEN

## Geänderte Stellen
- **pod/start.sh**: 6 Stellen – Schleife in `step_check_secrets`, Kommentar über `step_configure_rclone`, `os.environ[...]` im Python-Block, Fehlermeldung, beide `unset`. Sonst keine Logik-Änderung.
- **ANLEITUNG.md**: Vorlagenzeile der Umgebungsvariable (`DREAMDECK_DRIVE_TOKEN` = `{{ RUNPOD_SECRET_DREAMDECK_DRIVE_TOKEN }}`) und Abschnitt „Zugänge erneuern“.
- **ARCHITEKTUR.md**: Aufzählung der Startskript-Secrets.
- **NOTIZEN.md**: Secrets-Tabelle, Hinweis zur base64-Kodierung, neuer datierter Eintrag vom 15.11.2026 am Ende der Entscheidungen.
- **MERKLISTE.md**: keine Änderung – kein Punkt betrifft die Umbenennung.

## Prüfung
- `bash -n pod/start.sh`: ohne Fehler.
- Abschlusskontrolle: `grep -rn RCLONE_DRIVE_TOKEN` (ohne .git) findet nur noch den Begründungssatz im NOTIZEN-Eintrag vom 15.11.2026.

## Offen
- In RunPod muss das Secret selbst umbenannt bzw. neu angelegt werden: `DREAMDECK_DRIVE_TOKEN` mit dem bisherigen base64-Wert. Das Repo kann das nicht erledigen. Ohne diesen Schritt bricht der nächste Pod-Start mit „fehlt“ ab.
- Vorgabe-Schritte 1–5 sind erledigt; ein echter Lauf auf RunPod ist nicht getestet (Testlauf 1i steht weiter aus).
