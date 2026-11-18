# Bericht – Etappe 3 · 3a Korrektur: Info-Karte lesbarer

## Änderungen
- `dashboard/static/js/app.js:284-287` – `loraLabel` entfernt jetzt neben dem Ordnerpfad die Endungen `.safetensors`, `.ckpt`, `.pt`, `.pth` (Groß-/Kleinschreibung egal). Kommentar angepasst.
- `dashboard/static/js/app.js:~611` – `add(k, v, breit = false)` in `stageInfo` setzt `breit` im Zeilen-Objekt; „Prompt“ wird mit `true` hinzugefügt.
- `dashboard/static/js/app.js:623` – Modellname wird über `loraLabel` ohne Endung angezeigt.
- `dashboard/static/js/app.js:626-631` – LoRA-Namen in der Info-Karte werden über `loraLabel` gekürzt.
- `dashboard/static/index.html:290` – Klassen-Bindung `:class="{ 'dd-summary__row--breit': row.breit }"` auf der Zeile.
- `dashboard/static/css/dreamdeck.css:~770-775` – Regel `.dd-info .dd-summary__row--breit` (Block über volle Breite, Wert linksbündig). Keine neue Datei.
- `MERKLISTE.md:71` – 3a mit `[x]` abgehakt.

## ⚠️-Punkte
- Markierung: Eigenschaft `breit: true` im Zeilen-Objekt, wie vorgeschlagen.
- Endungen: `.safetensors`, `.ckpt`, `.pt`, `.pth`, Groß-/Kleinschreibung egal. Nur die Anzeige ändert sich, `infoCache` bleibt vollständig.

## Bündel-Prüfung
- Es gab schon `loraLabel(name)` (Ordnerpfad + `.safetensors` entfernen). Diese wurde wiederverwendet und um die weiteren Endungen erweitert, keine neue Hilfsfunktion.
- Folge: Die bestehenden Aufrufe (LoRA-Auswahl in index.html:187–227, app.js:348 und :395) kürzen jetzt auch `.ckpt/.pt/.pth`. Das ist gewollt und harmlos.
- Stellen, die dasselbe auf eigene Art tun: keine gefunden.
- Hinweis: Der Name `loraLabel` ist jetzt auch für Modelle zuständig; ein Umbenennen (z. B. `displayName`) wäre optional.

## Prüfung
- `node --check dashboard/static/js/app.js`: OK. Im Browser nicht geprüft.
