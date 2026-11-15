# Bericht – Etappe 2 · Schritt 2f (Oberflächen-Gerüst nach Variante B)

## Neue Dateien
- `dashboard/static/vendor/alpine-3.17.5.min.js`: Alpine.js 3.17.5 fest im Repo (55 935 Bytes, per curl von jsDelivr geladen).
- `dashboard/static/css/dreamdeck.css`: Tokens auf `:root`, Layout für Kopfzeile, Pipeline-Boxen, Prompt-Leiste, Bühne und Verlauf; ein `@keyframes dd-flicker`, Zustände nur über die Klassen `is-open` und `dd-status--…`.
- `dashboard/static/js/app.js`: klassisches Script, registriert bei `alpine:init` die Komponente `dreamdeck` (`open`, `toggle`, `isOpen`, `steps`, `comfy`) und fragt `/api/health` sofort und danach alle 30 s ab – mit dem einzigen `setInterval` der Oberfläche.

## Geänderte Dateien
- `dashboard/static/index.html`: Platzhalterseite komplett ersetzt durch das Gerüst (header, nav, drei sections, aside); die fünf Boxen entstehen per `x-for` aus `steps` und einer Vorlage.
- `ARCHITEKTUR.md`: Punkt „Oberfläche“ auf „(Gerüst umgesetzt)“ gestellt und um Ablageort und Alpine-Version ergänzt.
- `NOTIZEN.md`: Unterpunkt zu den Box-Codes und zum späteren Klick-Tutorial beim Eintrag „Oberfläche nach Entwurf Variante B“ ergänzt.
- `MERKLISTE.md`: drei neue Punkte unter „Etappe 2 – Ausbau“ angehängt; 2f bleibt offen bis zur Browser-Kontrolle.
- `BERICHT.md`: dieser Bericht.

## Prüfsumme
- sha256 von `alpine-3.17.5.min.js`: `b4036e9e9ac22fa6f6ae1ba292e015e1f3e9c85d0d79e73e4c8eb9bb139b522e` – stimmt mit dem erwarteten Wert überein.

## Geprüft
- `node --check dashboard/static/js/app.js`: Syntax in Ordnung.
- Genau ein `setInterval` in `app.js`, genau ein `@keyframes` in der CSS, feste Farbwerte nur im `:root`-Block.
- `vendor/` wird von `.gitignore` nicht erfasst.
- **Nicht geprüft:** die Seite im Browser. Auf der devbox gibt es kein Python, das Dashboard ließ sich hier nicht starten. Optik, Auf-/Zuklappen, Flackern und Statuspunkt sind also noch ungesehen.

## Auffälligkeiten
- **Zwei Zusatz-Tokens:** `--dd-on-cyan` (#04161A, Schrift auf dem Generieren-Knopf) und `--dd-cyan-glow` (rgba(34,228,240,.35), Leuchten). Beide Werte standen im Auftrag als feste Farben; als Tokens bleibt die Regel „Farben nur über Tokens“ gewahrt.
- **„Weiß“ beim aktiven Menüpunkt** ist `--dd-text` (#ECECF2), kein reines Weiß – aus demselben Grund.
- **Widerspruch in der Doku:** ARCHITEKTUR.md und NOTIZEN.md nennen weiterhin „ES-Module statt globaler Variablen“, `app.js` ist laut Auftrag aber ein klassisches Script. Nicht geändert, weil nicht beauftragt – sollte in einem der nächsten Schritte angeglichen werden.
- **Geschlossene Boxen neben einer offenen** strecken sich auf deren Höhe (mind. 320px), damit die Reihe einheitlich bleibt; sind alle zu, ist die Reihe niedrig. Sollen geschlossene Boxen auch dann niedrig bleiben, genügt `align-items: flex-start` an `.dd-pipeline`.
- **`x-cloak` am body:** Lädt Alpine nicht, bleibt die Seite leer (so beauftragt).
- **Ausgegraute Links** (Navigation, „Zur Galerie“) sind `<a>` ohne `href` mit `aria-disabled="true"` – nicht anklickbar und nicht per Tab erreichbar.
- Nichts committet.
