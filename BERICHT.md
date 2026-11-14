# BERICHT – Schritt 1d: Modelle laden (Modell-Sets, Download-Baustein in Python)

## Angelegt
- `pod/models.toml`: Kopfkommentar (Zweck, Regeln), Sets `basis` (loader none, Upscaler), `fp16` (loader split: unet, t5, clip_l, vae) und `fp8` (loader checkpoint). Dateien je Set als `[[sets.<name>.files]]` mit role, url, dest, size, sha256. Werte wie vorgegeben; sha256 von t5, clip_l und vae leer. Reserve-Kommentar zum T5 fp8 steht vor dem t5-Eintrag.
- `pod/models.py`: Download-Baustein, nur Standardbibliothek, kein Code auf Modulebene außer Konstanten und main-Guard.
  - `load_catalog`, `validate_sets` (unbekannter Name, fehlende Felder, „Nur ein FLUX-Set pro Start“), `check_url` (nur https, Host genau huggingface.co oder civitai.com).
  - `check_space`: Summe der fehlenden Dateien × 1,05 gegen freien Platz; Meldung „<Sets> brauchen X GB, frei sind Y GB“.
  - `download_file(url, dest, sha256, headers=None)`: Verhalten wie vorgegeben (vorhandene Datei prüfen/überspringen, falsche Datei bleibt liegen, Pickle nur mit sha256, `.part`, 8-MB-Blöcke, Fortschritt alle 10 %, End-URL https, 3 Versuche, gemessene Prüfsumme mit „bitte in pod/models.toml eintragen“, dann `os.replace`).
  - `download_sets` als gemeinsamer Ablauf (auch fürs Dashboard), CLI `download --sets … --models-dir …`, Ausgaben mit „[models]“, Exit 1 bei jedem Fehler (auch bei falschem Aufruf), sonst 0.

## Geändert
- `pod/versions.env`: `DEFAULT_MODEL_SETS="basis fp16"` mit Kommentar.
- `pod/start.sh`:
  - `source … versions.env` aus den Konstanten entfernt; neue erste Schritt-Funktion `step_load_versions` (source, dann Prüfung auf leere `COMFYUI_VERSION`/`DEFAULT_MODEL_SETS`), Aufruf per `run_step` direkt nach „Repo absichern“.
  - Beschreibungstext von `run_step`: `${COMFYUI_VERSION:-?}` (einzige Stelle).
  - `step_install_comfyui`: PyTorch-Version vor und nach pip, bei Unterschied „WARNUNG: pip hat PyTorch verändert (… → …)“, kein Fehler.
  - Neue Funktion `step_download_models`, Aufruf `run_step "Modelle laden"` nach „GPU prüfen“; Platzhalter-Kommentar auf 1e–1g.
- `ANLEITUNG.md`: Variable `MODEL_SETS`, Container Disk 50 GB, Hinweis zu gemessenen Prüfsummen im Protokoll.
- `NOTIZEN.md`: drei Einträge 14.11.2026 (Modell-Sets mit Ladeart und Reserve T5 fp8; Sicherheitsregeln; Download-Baustein in Python).
- `ARCHITEKTUR.md`: „Pod-Startskript“ nennt `pod/models.toml` und `pod/models.py`; Verweis auf 1e–1g korrigiert.
- `MERKLISTE.md`: 1d abgehakt; 1g, Etappe 2 und Etappe 6 wie vorgegeben ergänzt.

## Prüfung
- `bash -n pod/start.sh`: Exit 0, keine Ausgabe.
- `bash -n pod/versions.env`: Exit 0 (zusätzlich geprüft).
- **models.py ungetestet**: Python ist in der devbox nicht vorhanden, die Datei wurde weder ausgeführt noch auf Syntax geprüft. `models.toml` wurde ebenfalls nicht maschinell gelesen. Erster echter Lauf ist 1g.

## Auffälligkeiten
- Über die Vorgabe hinaus (bitte kurz ansehen):
  - Weiterleitungen: Header (später der Civitai-Token) gehen nur an den ursprünglichen Host, nicht an die Speicher-Server hinter der Weiterleitung. urllib würde sie sonst mitschicken. Weiterleitungen auf http werden schon beim Folgen abgelehnt.
  - Ziele (`dest`) mit absolutem Pfad oder `..` werden abgelehnt.
  - Stimmt die empfangene Größe nicht mit Content-Length überein, zählt das als Netzfehler und wird wiederholt.
  - HTTP-Fehler 4xx (außer 429) werden nicht wiederholt, sondern sofort gemeldet.
  - Zwischen den Versuchen liegt eine Pause von 5 Sekunden.
  - Alle Quellen und die Pickle-Regel werden vor dem ersten Download geprüft, damit ein absehbarer Fehler nicht erst nach 30 GB auffällt.
- Kein Fortsetzen abgebrochener Downloads: Jeder Versuch beginnt bei null (so vorgegeben: `.part` wird vorher gelöscht). Bei der 23,8-GB-Datei kann das Zeit kosten.
- Vorhandene Dateien mit bekannter Prüfsumme werden bei jedem Start neu gehasht. Bei fp16 sind das rund 24 GB (später 34 GB, wenn alle Prüfsummen eingetragen sind) – geschätzt ein bis zwei Minuten, nicht gemessen.
- Platzbedarf fp16 + basis: rund 34,2 GB, mit Zuschlag 36,0 GB. Dazu kommen ComfyUI und pip-Pakete; ob 50 GB Container Disk reichen, zeigt `df -h` in 1g.
- GB werden als 10^9 Bytes gerechnet und mit deutschem Komma ausgegeben.
- Der User-Agent ist der Standard von urllib. Ob civitai.com den annimmt, ist ungeprüft (Thema für 1e).
- Die Größen und Prüfsummen in `models.toml` sind aus der Vorgabe übernommen, nicht gegen die Quellen geprüft.
- Nicht committet.
