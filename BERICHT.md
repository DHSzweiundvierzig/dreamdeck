# BERICHT – Schritt 0e: Technik-Entscheidung Dashboard festhalten

## Geändert
- NOTIZEN.md: neuer Eintrag „Technik Dashboard“ mit den 7 Entscheidungen, je mit Grund.
- ARCHITEKTUR.md: Technik in Stichworten bei „DreamDeck-Backend“ (Python/FastAPI/uvicorn/httpx, HTTP + Websocket zu ComfyUI, SSE, nur DreamDeck extern erreichbar, Spiel-ComfyUI) und „Oberfläche“ (HTML/CSS/JS ohne Build, ES-Module, Alpine.js gepinnt im Repo, SSE) ergänzt. Kein neuer Abschnitt, „geplant“ bleibt.
- MERKLISTE.md: Etappe 0 „Technik-Entscheidung Dashboard“ abgehakt (Etappe 0 komplett); Etappe 2 am Anfang „Spiel-ComfyUI (Fake-Bilder) für Tests auf der devbox“ ergänzt.
- Kein Programmcode geschrieben.

## Zuordnung
- Die Teile hießen wie erwartet („DreamDeck-Backend“, „Oberfläche“), keine abweichende Zuordnung nötig.

## Auffälligkeiten
- Kein Grep-Werkzeug verfügbar, Suche per `grep` über Bash (nur lesend). Die Dateien waren sehr klein.
- Das Spiel-ComfyUI steht in ARCHITEKTUR.md beim Backend (Teststrategie), da kein eigener Teil dafür existiert.
- Es wurde nichts committet.
