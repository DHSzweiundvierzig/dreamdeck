# BERICHT – Etappe 2 · Schritt 2l: Bühne in der Oberfläche

## Änderungen je Datei
- `dashboard/static/js/app.js`: neue Zustände (`live`, `queueCount`, `jobs`, `stage`, `history`, Grenze `HISTORY_MAX = 60`), EventSource auf `/api/events` in `init()`, `generate()` hält die Auftragsangaben als Kopie fest und setzt die Bühne auf „wartet“, alle Ereignisse laufen durch `onEvent`, dazu `imageUrl`, `showImage`, `stageInfo`, `stageText` sowie die kleinen Hilfen `isRunning`, `progress` und `strengthText`.
- `dashboard/static/index.html`: Bühne neu aufgebaut (Platzhalter, Statuszeile mit `aria-live`, Fortschrittsbalken, Bild mit Info-Karte und vier gesperrten Knöpfen), Verlauf mit „läuft …“-Kachel und Vorschaubildern als Knöpfe.
- `dashboard/static/css/dreamdeck.css`: Tokens `--dd-cyan-deep` und `--dd-magenta-glow`, Fortschrittsbalken mit `@keyframes dd-stripes`, Bühnenbild mit Schatten, Info-Karte, Knopf-Raster, Verlaufs-Kacheln, unter 900px Bild über der Info-Spalte.
- `MERKLISTE.md`: 2i abgehakt mit Vermerk zum Pod-Test vom 15.11.2026; 2l bleibt offen.
- `ARCHITEKTUR.md`: Zeile „Oberfläche“ um Live-Stand, `/api/bild` und Sitzungs-Verlauf ergänzt.

## Prüfung
- `node --check dashboard/static/js/app.js`: ohne Fehler.
- Ablauf mit nachgebauten Ereignissen durchgespielt (Node-Skript mit Attrappen für Alpine, EventSource und fetch; liegt nur im Scratchpad, nicht im Repo) – alle Prüfungen bestanden:
  - warteschlange 1 → „In der Warteschlange“, warteschlange 3 → „· noch 2 vor dir“
  - start → „Modell wird geladen …“, Balken unbestimmt
  - fortschritt 1–25 → „Schritt X / 25“, Anteil X/25
  - fertig mit 2 Bildern → beide im Verlauf, erstes auf der Bühne, Adresse `/api/bild?ordner=2026-11&datei=a%201.png`; Info-Karte mit Seed, Auflösung, Format, LoRAs, Datei – unverändert, obwohl danach Regler verstellt wurden
  - fehler mit und ohne Meldung („Unbekannter Fehler“), das letzte Bild bleibt stehen
  - fremde prompt_id → wird angezeigt, Info-Karte nur mit Datei
  - Zusatz: ungültiges JSON wird ignoriert, Verlauf endet bei 60, `showImage` wechselt das Bild
- Nicht geprüft: die Darstellung im Browser (HTML/CSS) – hier läuft weder Backend noch Browser. Das steht auf dem Pod noch aus.

## Auffälligkeiten
- Das Grep-Werkzeug war nicht verfügbar; gesucht wurde mit `grep` per Bash (nur lesend).
- Reihenfolge SSE/Antwort: Kommt „start“ vor der Antwort auf `/api/generate`, würde „wartet“ den neueren Stand überschreiben. `generate()` setzt „wartet“ deshalb nur, wenn die Bühne noch nicht bei dieser prompt_id ist (im Durchlauf geprüft).
- „fertig“ ohne Bilder (nicht vorgegeben): ein altes Bild bleibt stehen, sonst wird die Bühne wieder leer.
- Statuszeile: ein einziger Absatz für alle Phasen; bei „fertig“ ist er nur für Vorlesehilfen da (`dd-sr-only`), damit „Fertig“ angesagt wird, ohne das Bild zu stören.
- Bündel-Prüfung: die Stärke-Formatierung („0,80“) stand schon in `summary()`; sie liegt jetzt in `strengthText` und wird von Zusammenfassung und Info-Karte gemeinsam genutzt. Info-Karte nutzt die vorhandene Liste `.dd-summary`, Knöpfe das vorhandene `.dd-btn`, die „läuft …“-Kachel den vorhandenen Platzhalter.
- Weniger Bewegung: keine eigene Regel nötig, die vorhandene globale Regel schaltet Streifen-Animation und Breiten-Übergang ab.
- Kein neuer Timer; `live` wird gesetzt, aber noch nirgends angezeigt (die Kopfzeile zeigt weiter den Health-Status).
- `jobs` wächst pro Auftrag um einen kleinen Eintrag und wird in der Sitzung nicht geleert; `batch` und `prompt` sind festgehalten, die Info-Karte zeigt sie noch nicht.
- Bei mehreren Aufträgen hintereinander zeigt die Bühne immer den zuletzt gemeldeten; „noch N vor dir“ rechnet mit der gesamten Warteschlange, nicht mit der Position des eigenen Auftrags.
