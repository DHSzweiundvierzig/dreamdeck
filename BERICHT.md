# BERICHT – Schritt 1f: ComfyUI im Hintergrund starten

## Geändert
- `pod/start.sh`: Konstanten `OUTPUT_DIR=/workspace/output` und `COMFY_PORT=8188`. Neue Funktion `step_start_comfyui` (nach `step_check_gpu`): startet ComfyUI per `nohup` ohne `cd`, mit `--listen 127.0.0.1`, `--port` und `--output-directory`, Ausgabe in `comfyui.log`. Wartet per python3/urllib alle 5 s, höchstens 180 s, auf `/system_stats`; bricht ab, wenn der Prozess endet oder die Zeit abläuft. Im Ablauf nach „LoRAs laden“ als `run_step "ComfyUI starten"` eingehängt, Kommentar auf 1g angepasst.
- `ARCHITEKTUR.md`: Zeile „Pod-Startskript“ angepasst; „ComfyUI headless“ auf „Start umgesetzt“ mit Port, Bildablage und Protokoll.
- `NOTIZEN.md`: Drive-Eintrag auf `_NNNNN_.png` geändert, Unterpunkt zu `filename_prefix` ergänzt; neuer Eintrag zur Bildablage außerhalb von ComfyUI.
- `MERKLISTE.md`: 1f abgehakt, neu 1g (rclone), bisherige 1g zu 1h mit Zusatz zur Erreichbarkeit der Oberfläche.

## Offene Punkte
- Nicht getestet (kein Pod/keine GPU hier); Abnahme im Testlauf (1h).
- Klären vor 1h: Wie ist die ComfyUI-Oberfläche trotz „nur intern“ erreichbar?
- `bash -n pod/start.sh` wurde nicht ausgeführt.
