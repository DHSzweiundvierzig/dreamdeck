# Bericht – Etappe 3 · 3a Korrektur 2: LoRAs und Datei in der Info-Karte breit

## Änderungen
- `dashboard/static/js/app.js:625-633` – Zeile „LoRAs“ in `stageInfo` bekommt als viertes Argument `true` (`breit`), wie „Prompt“.
- `dashboard/static/js/app.js:637` – Zeile „Datei“ bekommt `breit: true` im Zeilen-Objekt.
- Sonst nichts geändert: `index.html` und CSS unverändert.

## Prüfung
- `node --check dashboard/static/js/app.js`: OK. Im Browser nicht geprüft.
