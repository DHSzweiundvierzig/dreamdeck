# Bericht – Etappe 2 · Schritt 2l Korrektur: Live-Verbindung nur bei sichtbarem Tab oder laufendem Auftrag

## Änderungen je Datei
- `dashboard/static/js/app.js`: Neuer Zustand `eventSource`, neue Methode `syncEvents()` als einzige Stelle zum Öffnen und Schließen der SSE-Verbindung (Soll = Tab sichtbar oder Auftrag läuft); `init()` ruft sie auf und hängt `visibilitychange` (mit `checkHealth()` beim Sichtbarwerden) und `pagehide` an; `generate()` ruft sie nach dem Absenden, `onEvent` am Ende von „fertig“ und „fehler“ auf.
- `MERKLISTE.md`: 2l mit „Browser-Kontrolle bestanden am 15.11.2026“ abgehakt, neuer Punkt „2l Korrektur“ darunter, drei neue Ausbau-Punkte in Etappe 2.
- `NOTIZEN.md`: Chrome-Grenze von 6 Verbindungen und die Regel „sichtbar oder eigener Auftrag“ beim Eintrag zum Live-Fortschritt ergänzt.

## Prüfungen
- `node --check dashboard/static/js/app.js`: ohne Fehler.
- Ablauf mit Attrappe (Node, Fake-`EventSource`, Fake-`document`/`window`; Skript im Scratchpad, nicht im Repo) durchgespielt:
  - sichtbar → Verbindung offen ✔
  - versteckt ohne Auftrag → zu ✔
  - wieder sichtbar → neu offen ✔
  - versteckt mit laufendem Auftrag → bleibt offen ✔
  - nach „fertig“ im versteckten Tab → zu ✔
  - `pagehide` → zu, `eventSource` null ✔

## Auffälligkeiten
- Das Grep-Werkzeug stand in dieser Sitzung nicht zur Verfügung; gesucht wurde mit `grep` per Bash, nur lesend (wie in CLAUDE.md vorgesehen).
- Im Hintergrund-Tab ohne Auftrag wird `live` nicht mehr aktualisiert; beim Sichtbarwerden holt der Hub den letzten Stand sofort nach.
- Ein Auftrag, der im versteckten Tab endet, ohne dass „fertig“ oder „fehler“ ankommt (z. B. Verbindungsabbruch), hält die Verbindung offen, bis der Tab wieder sichtbar wird oder die Seite schließt.
- Echte Browser-Kontrolle (mehrere Tabs in Chrome) steht noch aus; deshalb bleibt „2l Korrektur“ in der Merkliste offen.
