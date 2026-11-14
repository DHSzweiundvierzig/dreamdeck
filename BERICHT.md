# BERICHT – Schritt 1e: LoRAs von Civitai laden (nur Versionsnummer pflegen)

## Angelegt
- `pod/loras.toml`: Kopfkommentar (Zweck, Pflege, Regeln) und ein Eintrag `[[loras]]` mit `version_id = 1051416` (PsyDreamer).

## Geändert
- `pod/models.py`:
  - Neue Konstanten `DEFAULT_LORA_CATALOG`, `USER_AGENT` („DreamDeck/1.0“), `CIVITAI_API`, `ALLOWED_LORA_BASE`; `import json`; Modulkommentar um den Befehl `loras` ergänzt.
  - `open_url(url, headers=None, timeout=TIMEOUT_SECONDS)`: einzige Stelle für Quellenprüfung, User-Agent, Weiterleitungsschutz (vorhandener `SafeRedirectHandler`), Timeout und https-Prüfung der End-Adresse. `fetch_to_part` nutzt sie statt eigenem Request/Opener.
  - `civitai_lora(version_id, token)`: Abfrage der Civitai-API, Prüfungen wie vorgegeben (Typ LORA, Basismodell Flux.1 D, Datei primary bzw. erste vom Typ Model, SafeTensor, SHA256 vorhanden, Dateiname ohne Pfadteile mit Endung .safetensors, Download-Adresse besteht `check_url`). Rückgabe url, dest, size, sha256, label.
  - `download_loras(catalog_path, models_dir, token)`: erst alle Einträge auflösen (Label ausgeben), dann `check_space`, dann `download_file` je Datei. Kein zweiter Download-Weg.
  - CLI: Befehl `loras` mit `--models-dir` (Pflicht) und `--catalog`; Token nur aus `CIVITAI_TOKEN`. Fehlerbehandlung gemeinsam mit `download`.
- `pod/start.sh`: neue Funktion `step_download_loras`, Aufruf `run_step "LoRAs laden"` nach „Modelle laden“; Platzhalter-Kommentar auf 1f–1g.
- `ANLEITUNG.md`: bei `MODEL_SETS` „ohne Anführungszeichen eintragen“; neuer Abschnitt „LoRAs beim Start“.
- `NOTIZEN.md`: Einträge 14.11.2026 (Grundhaltung „DreamDeck gibt nichts vor“; LoRA-Liste nur mit Versionsnummer, Regeln, Token nur aus der Umgebung, User-Agent).
- `ARCHITEKTUR.md`: „Pod-Startskript“ nennt `pod/loras.toml` und den Befehl `loras`; Verweis auf 1f–1g.
- `MERKLISTE.md`: 1e abgehakt; Etappe 2, 3 und 6 wie vorgegeben ergänzt.

## Prüfung
- `bash -n pod/start.sh`: Exit 0, keine Ausgabe.
- **models.py ungetestet**: kein Python in der devbox, die Datei wurde weder ausgeführt noch auf Syntax geprüft. `loras.toml` wurde nicht maschinell gelesen. Erster echter Lauf ist 1g.
- Die Civitai-API wurde nicht abgefragt. Die Feldnamen (`model.type`, `baseModel`, `files[].primary`, `metadata.format`, `hashes.SHA256`, `sizeKB`, `downloadUrl`) stammen aus der Vorgabe; ob Version 1051416 alle Regeln besteht (vor allem der genaue Text „Flux.1 D“), zeigt erst 1g.

## Auffälligkeiten
- Kleine Verhaltensänderung in `fetch_to_part`: Die Meldung „End-Adresse nach Weiterleitung ist nicht https“ kommt jetzt aus `open_url` und nennt den Dateinamen nicht mehr.
- Über die Vorgabe hinaus (bitte kurz ansehen):
  - Der Token wird vor der ersten Anfrage geprüft (Leerraum am Rand entfernt; nur druckbare ASCII-Zeichen ohne Leerzeichen, sonst „CIVITAI_TOKEN enthält ungültige Zeichen“). Grund: Python nennt bei einem ungültigen Header-Wert den Wert in der Fehlermeldung – der Token stünde sonst im Protokoll.
  - Netz- und JSON-Fehler bei der API-Abfrage werden als „Civitai-Version <id>: Abfrage fehlgeschlagen (<Fehlertyp>)“ gemeldet, ohne Details.
  - Fehlende Modelldatei, fehlende Download-Adresse oder fehlende Größenangabe in der Antwort geben eine eigene Fehlermeldung.
- Die API-Abfrage wird nicht wiederholt (anders als der Datei-Download mit 3 Versuchen). Ein kurzer Aussetzer bei Civitai bricht den Schritt „LoRAs laden“ ab.
- Bei der Platzprüfung heißt es in der Meldung „LoRAs brauchen X GB, frei sind Y GB“ (`check_space` unverändert wiederverwendet).
- Zwei LoRA-Versionen mit gleichem Dateinamen würden auf dasselbe Ziel zeigen; die zweite scheitert dann an der Prüfsumme der vorhandenen Datei. Bei einem Eintrag ohne Belang.
- „Secrets prüfen“ verlangt `CIVITAI_TOKEN` schon vorher; die Meldung „CIVITAI_TOKEN fehlt“ aus `models.py` greift nur beim direkten Aufruf.
- Nicht committet.
