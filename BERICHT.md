# Bericht – Etappe 2 · Schritt 2d (ComfyUI-Anbindung)

## Neue Dateien
- `dashboard/workflows/flux_split.json`: Der am 15.11.2026 auf dem Pod getestete FLUX-Workflow (split) im API-Format, ohne LoRA-Knoten.
- `dashboard/workflow.py`: `load_template`, `find_node`, `make_filename_prefix` und `build_flux_workflow` – setzt die Werte über die Knotentitel und hängt die LoRA-Kette (IDs ab "101") zwischen „Modell“ und „Sampler“.

## Geänderte Dateien
- `dashboard/requirements.txt`: `tzdata==2026.6` nach `typing-inspection` ergänzt.
- `dashboard/app.py`: Anfrage-Modelle `LoraIn` und `GenerateIn`, `app.state.client_id` im lifespan, neuer Endpunkt `POST /api/generate` (vor dem Static-Mount).
- `ARCHITEKTUR.md`: Backend-Punkt um den Satz zu Workflows, `workflow.py` und `POST /api/generate` ergänzt.
- `MERKLISTE.md`: 2c abgehakt (Pod-Test vom 15.11.2026), Text von 2d ersetzt (noch offen bis zum Pod-Test).

## Beispiel für den Test unter /docs (POST /api/generate)
```json
{
  "prompt": "a dreamlike forest at dawn, glowing mushrooms, soft mist",
  "seed": 12345,
  "width": 768,
  "height": 1344,
  "steps": 25,
  "guidance": 3.5,
  "batch_size": 1,
  "loras": [
    {"name": "FLUX_Psy_Dreamer_Style-000007.safetensors", "strength": 0.8}
  ]
}
```
Erwartete Antwort: `{"prompt_id": "…", "seed": 12345, "filename_prefix": "JJJJ-MM/dreamdeck_JJJJMMTT-HHMMSS"}`. Ohne `seed` wählt das Dashboard einen zufälligen und gibt ihn zurück. Kleinster Auftrag: `{"prompt": "test"}`.

Weitere Prüfungen auf dem Pod:
- Falscher LoRA-Name → HTTP 422 mit `fehler` und den `node_errors` von ComfyUI unter `details`.
- `width: 770` → HTTP 422 von FastAPI selbst (nicht durch 16 teilbar).
- ComfyUI gestoppt → HTTP 503 `{"fehler": "ComfyUI nicht erreichbar"}`.

## Prüfung
- Nichts ausgeführt: In dieser Umgebung gibt es kein Python. Code nur durchgesehen; der erste echte Lauf ist der Pod-Test.

## Auffälligkeiten
- `tzdata==2026.6`: Die Version konnte hier nicht gegen PyPI geprüft werden. Gibt es sie nicht, scheitert `pip install` in `step_install_dashboard` und das Dashboard startet nicht – im Protokoll des Pods sichtbar.
- Zwei verschiedene 422-Formen: Eingabefehler kommen von FastAPI im Standardformat (`detail`), Ablehnungen von ComfyUI im eigenen Format (`fehler`, `details`). Für die Oberfläche (später) zu beachten.
- 422 gibt es auch, wenn ComfyUI zwar 200 meldet, aber keine `prompt_id` liefert, oder wenn die Antwort kein JSON ist (dann steht der Rohtext in `details`).
- Der LoRA-Name geht ungeprüft an ComfyUI; liegt die Datei in einem Unterordner von `loras/`, muss der Name den Unterordner enthalten (so wie ComfyUI ihn auflistet).
- `strength` wird als `strength_model` gesetzt (`LoraLoaderModelOnly` wirkt nur auf das Modell, nicht auf die Textencoder).
- `filename_prefix` ist sekundengenau: Zwei Aufträge in derselben Sekunde bekommen dasselbe Präfix; ComfyUI zählt die Bildnummer dann weiter, überschrieben wird nichts.
- `load_template` liest die Vorlage einmal und hält sie im Speicher; Änderungen an der JSON-Datei wirken erst nach einem Neustart des Dashboards (passt zu „neuer Code = neuer Pod“).
- Anfrage-Modelle liegen wie vorgeschlagen in `app.py`. Der Timeout von 10 s gilt nur für `/prompt`; `/api/health` bleibt bei 2 s.

## Nachbesserung Monatsordner

- `dashboard/workflow.py`: `make_filename_prefix` liefert jetzt `JJJJ-MM/dreamdeck_JJJJMMTT-HHMMSS` (Monat und Zeitstempel aus demselben Zeitpunkt in Europe/Berlin), Docstring ergänzt.
- `ARCHITEKTUR.md`: Backend-Punkt nennt bei `POST /api/generate` den Monatsordner `JJJJ-MM/`.
- `MERKLISTE.md`: Unterschritt 2d lautet jetzt „filename_prefix mit Monatsordner und Zeitstempel“.
- `BERICHT.md`: Beispielantwort von `/api/generate` an das neue Präfix-Format angepasst; dieser Abschnitt angehängt.
