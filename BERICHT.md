# Bericht – Etappe 2 · Schritt 2n: Dashboard über den RunPod-Proxy

## Änderungen je Datei
- `pod/start.sh`:
  - `step_start_dashboard`: `--host 0.0.0.0` statt `127.0.0.1`; Kommentar angepasst (alle Schnittstellen, RunPod-Proxy, nur Port 8000 als HTTP-Port, geschützt durch DASHBOARD_PASSWORD). `wait_for_http` prüft weiter `http://127.0.0.1:$DASHBOARD_PORT/api/health`, Name jetzt „Dashboard auf Port $DASHBOARD_PORT“.
  - `step_check_secrets`: DASHBOARD_PASSWORD hinter DREAMDECK_DRIVE_CLIENT_SECRET aufgenommen.
  - `step_start_sync`: `env -u CIVITAI_TOKEN -u DASHBOARD_PASSWORD`, Kommentar angepasst.
  - `step_start_comfyui` unverändert (bleibt auf 127.0.0.1).
- `ANLEITUNG.md`: Vorlage Punkt 4 (HTTP-Port 8000, TCP 22, Hinweis auf DASHBOARD_PORT); neuer Unterabschnitt „Dashboard über den RunPod-Proxy öffnen“ vor dem SSH-Tunnel, dieser umbenannt in „ComfyUI-Oberfläche und Fehlersuche per SSH-Tunnel“ (Inhalt unverändert); Neustart-Befehl mit `--host 0.0.0.0`, `env -u CIVITAI_TOKEN` unverändert.
- `NOTIZEN.md`: Eintrag 16.11.2026 – 2n unter der 2j-Zeile (die Zeile selbst bleibt stehen).
- `ARCHITEKTUR.md`: Satz „lauscht auf 0.0.0.0:8000, erreichbar über den RunPod-Proxy, geschützt durch DASHBOARD_PASSWORD“ ergänzt; dafür den nun falschen Halbsatz „bis zur Freigabe lauscht das Dashboard nur auf 127.0.0.1 (Zugriff per SSH-Tunnel)“ ersetzt.
- `MERKLISTE.md`: 2j abgehakt, 2n umbenannt (offen), 2o neu (offen), Verweis bei den RunPod-Diensten auf „→ 2o“.

## Prüfung
- `bash -n pod/start.sh`: ohne Fehler.
- Noch offen: Test auf dem Pod (Proxy-Adresse, Login, ComfyUI nicht von außen erreichbar).
