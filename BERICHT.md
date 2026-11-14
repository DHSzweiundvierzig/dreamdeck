# BERICHT – Schritt 1c: Basis-Image festlegen, ComfyUI in fester Version installieren

## Angelegt
- `pod/versions.env`: Kopfkommentar, `COMFYUI_VERSION=v0.45.2`, Kommentarzeile mit Basis-Image (nur Info).

## Geändert
- `pod/start.sh`:
  - Konstanten: `COMFY_DIR=/workspace/ComfyUI`, `COMFY_REPO=https://github.com/Comfy-Org/ComfyUI.git`; direkt danach `source "$REPO_DIR/pod/versions.env"`.
  - `step_secure_repo`: `unset GITHUB_TOKEN` ist jetzt die erste Zeile, vor `git remote set-url`.
  - Neue Funktion `step_install_comfyui`: überspringt das Klonen bei passender Version (`git describe --tags`), löscht den Ordner bei anderer Version, klont sonst mit `--depth 1 --branch`, installiert `requirements.txt` mit `--break-system-packages`. Jeder Befehl endet mit `|| return 1`.
  - Neue Funktion `step_check_gpu`: `python3 -c` gibt PyTorch-Version, CUDA-Version und GPU-Namen aus; bei `torch.cuda.is_available()` False Exit 1 plus Hinweis-Log.
  - Ablauf: nach „Secrets prüfen“ die Aufrufe `run_step "ComfyUI $COMFYUI_VERSION installieren"` und `run_step "GPU prüfen"`; Platzhalter-Kommentar auf 1d–1f aktualisiert.
- `ANLEITUNG.md`: Container Image eingetragen, Hinweis zum CUDA-Filter 13.0 und Treiber ab 580.
- `NOTIZEN.md`: Eintrag „Basis-Image“ (14.11.2026) um Image, ComfyUI-Version und fehlendes venv ergänzt.
- `ARCHITEKTUR.md`: „Pod-Startskript“ nennt `pod/versions.env`, `/workspace/ComfyUI` und die GPU-Probe; Verweis auf 1d–1f.
- `CLAUDE.md`: Ausnahme für BERICHT.md unter „Dateien ändern“ ergänzt.
- `MERKLISTE.md`: 1c mit `[x]` abgehakt.

## Prüfung
- `bash -n pod/start.sh`: Exit 0, keine Ausgabe.
- `bash -n pod/versions.env`: Exit 0 (zusätzlich geprüft).
- Nichts ausgeführt: kein Klonen, kein pip, kein GPU-Test. Der Ablauf ist auf dem Pod nicht getestet.

## Auffälligkeiten
- Bei Versionswechsel wird der Ordner `/workspace/ComfyUI` ohne Rückfrage per `rm -rf` gelöscht. Das ist so vorgegeben; ein Ordner ohne Git-Stand gilt ebenfalls als „andere Version“ und wird gelöscht.
- `requirements.txt` von ComfyUI kann Pakete mitbringen, die das PyTorch des Images ändern. Ob das bei v0.45.2 passiert, habe ich nicht geprüft (kein Netzzugriff in dieser Sitzung). Das ist der wichtigste Punkt für den Test in 1g.
- `step_check_gpu` meldet auch dann den Treiber-Hinweis, wenn `import torch` selbst fehlschlägt. Die Python-Fehlermeldung steht dann im Protokoll darüber.
- `--break-system-packages` wirkt nur auf dem System-Python des Images; ein venv wird nicht angelegt, wie in NOTIZEN.md festgehalten.
- Nicht committet.
