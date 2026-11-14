# CLAUDE.md – Arbeitsregeln für DreamDeck

## Suchen und Lesen
- Suchen mit dem Grep-Werkzeug; falls nicht verfügbar, `grep` per Bash, nur lesend.
- Token sparen: erst greppen, dann nur die nötigen Zeilen lesen. Große Dateien nie komplett lesen.

## Dateien ändern
- Bestehende Dateien ausschließlich per Edit ändern, nie per Skript (kein sed/awk/Python zum Umschreiben).
- Neue Dateien per Write anlegen.
- Ausnahme: BERICHT.md wird jedes Mal komplett neu per Write geschrieben (einzige Datei mit dieser Ausnahme).

## Code-Hygiene
- Bündel-Prüfung: vor neuen Funktionen prüfen, ob es schon passende gibt. Doppelungen zusammenlegen.
- Keine unnötigen neuen Timer.

## Sprache
- Doku und Kommentare auf Deutsch.
- Bezeichner im Code (Variablen, Funktionen, Dateinamen im Code) auf Englisch – gilt, solange nichts anderes beschlossen wird.

## Merkliste und Bericht
- Erledigtes in `MERKLISTE.md` mit `[x]` abhaken, nie löschen.
- Ergebnis jedes Schritts kurz in `BERICHT.md` festhalten (überschreiben, nicht anhängen).

## Geheimnisse
- Tokens, Passwörter und Keys nie ins Repo.
- Nur über Umgebungsvariablen aus RunPod-Secrets.
