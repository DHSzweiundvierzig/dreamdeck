# Bericht – Etappe 2 · Schritt 2b (Backend-Gerüst)

## Neue Dateien
- `dashboard/requirements.txt`: Alle Pakete inkl. Unterabhängigkeiten fest gepinnt (Python 3.12).
- `dashboard/__init__.py`: Macht `dashboard` zum Paket; Start mit `uvicorn dashboard.app:app` aus dem Repo-Ordner.
- `dashboard/config.py`: Einzige Stelle, die `pod/paths.env` liest; stellt `REPO_DIR`, `OUTPUT_DIR`, `COMFY_PORT`, `DASHBOARD_PORT`, `COMFY_URL` bereit, klare deutsche Fehlermeldung bei fehlender Datei.
- `dashboard/app.py`: FastAPI-App mit lifespan (gemeinsamer httpx-Client in `app.state.comfy`), `GET /api/health`, Static-Mount auf `/` nach den API-Routen.
- `dashboard/static/index.html`: Platzhalterseite ohne JavaScript und ohne Netz-CSS, mit Link auf `/api/health`.

## Geänderte Dateien
- `pod/paths.env`: `DASHBOARD_PORT=8000` nach `COMFY_PORT` eingefügt.
- `ARCHITEKTUR.md`: Backend-Punkt auf „Gerüst umgesetzt“ gesetzt und um Ort, Config und Pins ergänzt.
- `NOTIZEN.md`: Eintrag zur eigenen venv und den festen Pins angehängt.
- `MERKLISTE.md`: 2b und „Dashboard liest Pfade und Port“ abgehakt.

## Auffälligkeiten aus der Durchsicht
- Nicht ausgeführt: In der devbox gibt es kein Python, der Code wurde nur gelesen, nicht getestet. Erster Lauf in 2c auf dem Pod.
- Das Grep-Werkzeug war nicht verfügbar; gesucht wurde per `grep` über Bash, nur lesend.
- `config.py` liest die Datei beim Import. Fehlt ein Schlüssel (z. B. `DASHBOARD_PORT` in einer älteren `paths.env`), bricht der Start mit `KeyError` ab; fehlt die Datei, mit der deutschen Fehlermeldung.
- `StaticFiles` prüft beim Anlegen, dass `dashboard/static` existiert; der Ordner ist vorhanden (`index.html`).
- Relative Importe (`from .config`) funktionieren nur beim Start als Paket (`uvicorn dashboard.app:app`), nicht per `python dashboard/app.py`.
- Die Pins (z. B. `opentelemetry-api`, `annotated-doc`) wurden wie vorgegeben übernommen und nicht gegen PyPI geprüft; ob `pip install -r` sauber auflöst, zeigt sich erst in 2c.
