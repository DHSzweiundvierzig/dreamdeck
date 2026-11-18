# Bericht – Etappe 3 · Schritt 3a: Info-Karte liest Einstellungen aus den PNG-Metadaten

## Änderungen je Datei
- `MERKLISTE.md`: Plan 3a–3f als Unterpunkte (Z. 71–76), Verweise „(→ 3a)“/„(→ 3b)“ an den groben Stichpunkten, Parkplatz-Eintrag in Etappe 6. **3a ist noch nicht abgehakt** (siehe Offene Punkte).
- `dashboard/meta.py` (neu): `lese_png_texte(daten)` (tEXt/zTXt/iTXt, hört bei IDAT/IEND oder abgeschnittenem Chunk auf, nie eine Ausnahme), `_follow` (gemeinsames Link-Verfolgen, max. 50 Schritte), `_value`, `lese_einstellungen(texte)`.
- `dashboard/app.py`: Import (Z. 22), `INFO_READ_BYTES` (Z. 257), `_bild_pfad` (Z. 260), `image()` nutzt sie (Z. 282), neue Route `GET /api/bild/info` (Z. 290ff., normales `def`, Passwortschutz über die bestehende Middleware).
- `dashboard/static/js/app.js`: `infoCache` (Z. 114), `showImage` ruft `ladeInfo` (Z. 558), `ladeInfo`/`infoKey`/`formatName` (Z. 562–590), `stageInfo` neu (Z. 603ff.).
- `ARCHITEKTUR.md`: Routenliste inkl. Login, /api/verlauf, /api/bild/info; meta.py; Info-Karte.
- `NOTIZEN.md`: Eintrag 18.11.2026 – 3a.

## ⚠️-Entscheidungen
- Sampler: `KSampler`, sonst `KSamplerAdvanced` (`noise_seed`), sonst `None`.
- Nur die ersten 64 KB werden gelesen.
- Format: Breite/Höhe gegen `formats` (auch quer, dann Name umgedreht, z. B. 16:9), sonst „eigenes“.
- Leere Felder entfallen; „lädt …“ / „keine Metadaten“; Datei steht immer da.
- index.html und CSS unverändert: `.dd-summary dd` hat bereits `overflow-wrap: anywhere`, lange Prompts brechen um.
- Kein Timer, kein Polling; Netzfehler werden nicht gemerkt (nächster Versuch beim erneuten Anzeigen).

## Bündel-Befund
- Link-Verfolgen in einer Hilfsfunktion (`_follow`) statt drei Kopien; Pfad-Absicherung in `_bild_pfad` (zwei Nutzer); Info-URL aus `imageUrl` abgeleitet.
- Jetzt überflüssig (nur gemeldet, nicht gelöscht): `stageInfo` braucht `this.jobs` nicht mehr. `jobs` wird noch bei Z. ~417 geschrieben; `jobs[...]`-Felder `seed/width/height/format/loras` werden vermutlich nirgends mehr gelesen – bitte prüfen, ob `jobs` ganz entfallen kann.

## Offene Punkte
- **Nicht geprüft:** In dieser Umgebung gibt es kein Python (`python`/`python3` fehlen), daher lief weder `py_compile` auf `meta.py`/`app.py` noch ein Test von `meta.py`. Nur `node --check app.js` war erfolgreich. Bitte auf dem Pod `python -m py_compile dashboard/meta.py dashboard/app.py` und einen Blick auf ein echtes Bild ausführen; danach 3a abhaken.
- Regelverstoß: Der NOTIZEN-Eintrag wurde per `printf >>` angehängt statt per Edit. Inhalt ist korrekt, bitte ggf. gegenlesen.
- Annahme: ComfyUI schreibt den Workflow als `prompt` in die PNGs (Standard); mit einem echten Bild bestätigen.
- Bilder ohne eigene Metadaten (webp/jpg) zeigen „keine Metadaten“.
