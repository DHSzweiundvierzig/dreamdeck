# Bericht – Etappe 2 · Schritt 2m: Verlauf vom Pod

## Änderungen je Datei
- `dashboard/app.py`: Konstante `HISTORY_LIMIT = 60` neben `IMAGE_SUFFIXES`; neuer Endpunkt `GET /api/verlauf` (normales `def`, Threadpool) direkt unter `/api/bild`. Durchsucht `OUTPUT_DIR` rekursiv, nur Dateien mit Endung aus `IMAGE_SUFFIXES`, sortiert nach Änderungszeit absteigend, höchstens 60, Rückgabe `{"bilder": [{"datei", "ordner"}]}`; fehlender Ordner → leere Liste.
- `dashboard/static/js/app.js`: `mergeHistory(entries)` als einzige Schreibstelle für `history` (entdoppelt nach `src`, kürzt auf `HISTORY_MAX`); „fertig“ nutzt sie. Neue `loadHistory()` mit Flag `historyLoading`, Zusammenführen Sitzung/Pod (Sitzungs-Einträge ohne Pod-Treffer nach vorn, bekannte Einträge behalten `promptId`), leere Bühne ohne laufenden Auftrag zeigt das erste Bild; Fehler still. Aufruf einmal in `init()` und im vorhandenen `visibilitychange`-Handler bei sichtbarem Tab (zusammen mit `checkHealth()`). Kommentar über `history` angepasst. Kein neuer Timer, kein neuer Listener.
- `MERKLISTE.md`: „2l Korrektur“ abgehakt, 2m offen eingefügt (vor 2j), neuer Punkt unter Etappe 3 (Galerie aus Google Drive).
- `NOTIZEN.md`: Eintrag zu 2m.
- `index.html`: unverändert.

## Prüfungen
- `node --check dashboard/static/js/app.js`: ohne Fehler.
- `app.py`: Syntaxprüfung nicht möglich (`python3` fehlt in dieser Umgebung); Endpunkt nicht gestartet.
- Browser-Kontrolle auf neuem Pod steht aus.

## Auffälligkeiten
- Das Grep-Werkzeug stand nicht zur Verfügung; gesucht wurde mit `grep` per Bash, nur lesend.
- Der Verlauf zeigt nur Bilder seit Pod-Start; dauerhafte Quelle wird das Drive (Etappe 3).
