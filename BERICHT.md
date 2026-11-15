# Bericht – Etappe 2 · Schritt 2c (Dashboard startet mit dem Pod)

## Geänderte Dateien
- `pod/paths.env`: Neue Zeile `DASHBOARD_VENV=/workspace/venv-dashboard`; Kopfkommentar nennt jetzt das Dashboard (`dashboard/config.py`) als Leser.
- `pod/start.sh`: Neue Hilfsfunktion `wait_for_http`, `step_start_comfyui` nutzt sie (eigene Warteschleife und `waited` entfallen), neue Schritte `step_install_dashboard` (venv + pip install) und `step_start_dashboard` (uvicorn auf 127.0.0.1, ohne CIVITAI_TOKEN, `--app-dir`, 30 s Wartezeit auf `/api/health`); Konstanten-Kommentar um `DASHBOARD_PORT` und `DASHBOARD_VENV` ergänzt.
- `ANLEITUNG.md`: Tunnel-Abschnitt für ComfyUI und Dashboard (Ports 8188 und 8000), Dashboard-Protokollzeile, Hinweis „Pod holt Code nur beim Start → neuer Pod“.
- `ARCHITEKTUR.md`: update.sh-Satz ersetzt (neuer Code = neuer Pod, Start durch `pod/start.sh`).
- `NOTIZEN.md`: Entwicklungsablauf Etappe 2 auf „neuer Pod mit `DREAMDECK_BRANCH=etappe-2`“ umgestellt (update.sh verworfen), Reihenfolge-Punkt angepasst.
- `MERKLISTE.md`: 2c ohne update.sh-Teil (nicht abgehakt, erst nach Pod-Test); 2k um „Vorlage wieder mit DREAMDECK_BRANCH=main anlegen“ ergänzt.

## Ablauf in start.sh (Reihenfolge der run_step-Aufrufe am Ende)
… rclone einrichten → ComfyUI starten → Sync-Schleife starten → **Dashboard einrichten** → **Dashboard starten**.

## grep „update.sh“ (Punkt 8)
Einziger Treffer: `NOTIZEN.md:77` – „… (update.sh verworfen).“ Wie gefordert.

## Prüfung
- `bash -n pod/start.sh`: Syntax in Ordnung. Nicht auf einem Pod getestet.
- `/api/health` existiert in `dashboard/app.py` (Zeile 27).

## Auffälligkeiten
- `step_install_dashboard` prüft die venv mit `-x` auf `bin/python` (Vorgabe: „fehlt“); bei einem Pod mit bestehendem `/workspace`-Volume wird die venv wiederverwendet und pip installiert nur Fehlendes nach.
- start.sh nutzt bewusst kein `set -e`; schlägt das Dashboard fehl, läuft ComfyUI trotzdem (wie in der Entscheidung vorgesehen).
- Ist `python3-venv` im Image nicht vorhanden, meldet der Schritt das im Protokoll; erst der Pod-Test zeigt es.
- `dashboard/config.py` wurde nicht angefasst; ob es die neue Zeile `DASHBOARD_VENV` in `paths.env` ohne Fehler überliest, ist im Pod-Test (oder per Durchsicht von config.py) zu bestätigen.
