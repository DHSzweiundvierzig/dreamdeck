#!/usr/bin/env bash
# DreamDeck – Startskript für den RunPod-Pod (Gerüst).
#
# Zweck: richtet einen frischen Pod ein. Aufgerufen wird es vom
# „Container Start Command“ der RunPod-Vorlage, der das Repo klont und
# dieses Skript startet (siehe ANLEITUNG.md, Abschnitt „Pod starten“).
#
# Aufbau: Alle Schritte laufen über run_step (Protokoll, Zeitmessung,
# Fehlerbehandlung an einer Stelle). Bewusst KEIN „set -e“: Fehler
# behandelt run_step, damit der Pod im Fehlerfall erreichbar bleibt.

set -u
set -o pipefail

# --- Konstanten ---------------------------------------------------------
# Gemeinsame Pfade (REPO_DIR, LOG_DIR, COMFY_DIR, OUTPUT_DIR, COMFY_PORT,
# DASHBOARD_PORT, DASHBOARD_VENV, RCLONE_CONF, RCLONE_REMOTE, DRIVE_FOLDER) stehen nur in pod/paths.env.
if ! source "$(dirname "${BASH_SOURCE[0]}")/paths.env"; then
    echo "DreamDeck: pod/paths.env fehlt"
    [ -f /start.sh ] && /start.sh &
    sleep infinity
fi
LOG_FILE=$LOG_DIR/start.log
REPO_URL=https://github.com/DHSzweiundvierzig/dreamdeck.git
COMFY_REPO=https://github.com/Comfy-Org/ComfyUI.git

# --- Protokoll ----------------------------------------------------------
mkdir -p "$LOG_DIR"
# Ab hier geht alles zusätzlich ins Protokoll.
exec > >(tee -a "$LOG_FILE") 2>&1

# Zeile mit Zeitstempel ausgeben.
log() {
    printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

# --- Schritt-Baustein ---------------------------------------------------
SETUP_FAILED=0

# run_step "Beschreibung" funktionsname
# Führt die Funktion ohne Subshell aus (Änderungen an der Umgebung bleiben
# erhalten). Nach dem ersten Fehler werden alle weiteren Schritte übersprungen.
run_step() {
    local description=$1
    local func=$2
    local start_time

    if [ "$SETUP_FAILED" -eq 1 ]; then
        log "ÜBERSPRUNGEN: $description"
        return 0
    fi

    log "START: $description"
    start_time=$(date +%s)
    if "$func"; then
        log "OK: $description ($(( $(date +%s) - start_time )) s)"
    else
        log "FEHLER: $description ($(( $(date +%s) - start_time )) s)"
        SETUP_FAILED=1
    fi
    return 0
}

# --- Schritte -----------------------------------------------------------

# Feste Versionen und Standardwerte aus pod/versions.env laden.
# Läuft ohne Subshell, damit die Werte in der Hauptshell bleiben.
step_load_versions() {
    source "$REPO_DIR/pod/versions.env" || return 1
    if [ -z "${COMFYUI_VERSION:-}" ] || [ -z "${DEFAULT_MODEL_SETS:-}" ] \
        || [ -z "${RCLONE_VERSION:-}" ] || [ -z "${RCLONE_SHA256:-}" ]; then
        log "pod/versions.env unvollständig: COMFYUI_VERSION, DEFAULT_MODEL_SETS, RCLONE_VERSION oder RCLONE_SHA256 ist leer"
        return 1
    fi
}

# Token aus der Git-Adresse entfernen und aus der Umgebung löschen.
# Läuft ohne Subshell, damit unset in der Hauptshell wirkt.
step_secure_repo() {
    unset GITHUB_TOKEN
    git -C "$REPO_DIR" remote set-url origin "$REPO_URL" || return 1
}

# Prüft nur, ob die Secrets gesetzt sind – der Wert wird nie ausgegeben.
step_check_secrets() {
    local name
    local missing=0
    for name in CIVITAI_TOKEN DREAMDECK_DRIVE_TOKEN DREAMDECK_DRIVE_CLIENT_ID DREAMDECK_DRIVE_CLIENT_SECRET; do
        if [ -n "${!name:-}" ]; then
            log "Secret $name: gesetzt"
        else
            log "Secret $name: fehlt"
            missing=1
        fi
    done
    return "$missing"
}

# ComfyUI in der festen Version aus pod/versions.env installieren.
# Passt der vorhandene Ordner nicht zur Version, wird er gelöscht und neu geklont.
step_install_comfyui() {
    local current torch_before torch_after
    current=$(git -C "$COMFY_DIR" describe --tags 2>/dev/null || true)
    if [ -d "$COMFY_DIR" ] && [ "$current" = "$COMFYUI_VERSION" ]; then
        log "ComfyUI $COMFYUI_VERSION ist schon vorhanden – Klonen übersprungen"
    else
        if [ -d "$COMFY_DIR" ]; then
            log "ComfyUI in anderer Version (${current:-unbekannt}) – Ordner wird gelöscht"
            rm -rf "$COMFY_DIR" || return 1
        fi
        git clone --depth 1 --branch "$COMFYUI_VERSION" "$COMFY_REPO" "$COMFY_DIR" || return 1
    fi
    # Kein venv: das PyTorch des Basis-Images wird genutzt.
    # Version vor und nach pip merken – pip darf PyTorch nicht unbemerkt tauschen.
    torch_before=$(python3 -c 'import torch; print(torch.__version__)' 2>/dev/null || true)
    python3 -m pip install --no-cache-dir --break-system-packages -r "$COMFY_DIR/requirements.txt" || return 1
    torch_after=$(python3 -c 'import torch; print(torch.__version__)' 2>/dev/null || true)
    if [ "$torch_before" != "$torch_after" ]; then
        log "WARNUNG: pip hat PyTorch verändert (${torch_before:-unbekannt} → ${torch_after:-unbekannt})"
    fi
}

# Modell-Sets laden (Standard aus pod/versions.env, überschreibbar per MODEL_SETS).
# Die ganze Download-Logik steckt in pod/models.py.
step_download_models() {
    MODEL_SETS="${MODEL_SETS:-$DEFAULT_MODEL_SETS}"
    log "Modell-Sets: $MODEL_SETS"
    python3 "$REPO_DIR/pod/models.py" download --sets "$MODEL_SETS" --models-dir "$COMFY_DIR/models" || return 1
}

# LoRAs aus pod/loras.toml laden. Der Token kommt aus der Umgebung (CIVITAI_TOKEN),
# nie als Argument.
step_download_loras() {
    python3 "$REPO_DIR/pod/models.py" loras --models-dir "$COMFY_DIR/models" || return 1
}

# Prüft, ob PyTorch die GPU sieht. Ohne GPU schlägt der Schritt fehl.
step_check_gpu() {
    if ! python3 -c '
import sys
import torch
print("PyTorch:", torch.__version__)
print("CUDA (PyTorch):", torch.version.cuda)
if not torch.cuda.is_available():
    sys.exit(1)
print("GPU:", torch.cuda.get_device_name(0))
'; then
        log "GPU nicht verfügbar – Treiber des Hosts zu alt? Beim Pod-Start CUDA 13.0 oder neuer wählen."
        return 1
    fi
}

# rclone in der festen Version aus pod/versions.env installieren (Prüfsumme
# Pflicht). Entpackt wird mit python3 (zipfile), weil unzip im Image fehlen kann.
step_install_rclone() {
    local url zip_file extract_dir
    if rclone version 2>/dev/null | head -n 1 | grep -qF "rclone $RCLONE_VERSION"; then
        log "rclone $RCLONE_VERSION ist schon vorhanden – Installation übersprungen"
        return 0
    fi
    url="https://github.com/rclone/rclone/releases/download/$RCLONE_VERSION/rclone-$RCLONE_VERSION-linux-amd64.zip"
    zip_file=/tmp/rclone.zip
    extract_dir=/tmp/rclone-extract
    curl -fsSL --retry 3 -o "$zip_file" "$url" || { rm -f "$zip_file"; return 1; }
    if ! echo "$RCLONE_SHA256  $zip_file" | sha256sum -c --quiet -; then
        rm -f "$zip_file"
        log "rclone: Prüfsumme stimmt nicht – Datei gelöscht"
        return 1
    fi
    rm -rf "$extract_dir"
    mkdir -p "$extract_dir" || return 1
    python3 -I -c '
import sys, zipfile
zipfile.ZipFile(sys.argv[1]).extract(sys.argv[2], sys.argv[3])
' "$zip_file" "rclone-$RCLONE_VERSION-linux-amd64/rclone" "$extract_dir" \
        || { rm -rf "$zip_file" "$extract_dir"; return 1; }
    install -m 755 "$extract_dir/rclone-$RCLONE_VERSION-linux-amd64/rclone" /usr/local/bin/rclone \
        || { rm -rf "$zip_file" "$extract_dir"; return 1; }
    rm -rf "$zip_file" "$extract_dir"
}

# rclone-Konfiguration aus DREAMDECK_DRIVE_TOKEN (base64 ohne Padding, darin JSON
# mit Feld „token“), DREAMDECK_DRIVE_CLIENT_ID und DREAMDECK_DRIVE_CLIENT_SECRET
# schreiben, Secrets aus der Umgebung löschen, Verbindung testen und Ordner
# DreamDeck anlegen. Token, Client-ID und Client-Secret werden nie ausgegeben.
# Läuft ohne Subshell, damit unset in der Hauptshell wirkt.
step_configure_rclone() {
    if ! python3 -I -c '
import base64, json, os, sys
conf_path, remote = sys.argv[1], sys.argv[2]
try:
    raw = os.environ["DREAMDECK_DRIVE_TOKEN"].strip()
    raw += "=" * (-len(raw) % 4)
    token = json.loads(base64.b64decode(raw))["token"]
    json.loads(token)
    client_id = os.environ["DREAMDECK_DRIVE_CLIENT_ID"].strip()
    client_secret = os.environ["DREAMDECK_DRIVE_CLIENT_SECRET"].strip()
except Exception:
    print("DREAMDECK_DRIVE_TOKEN ist unbrauchbar (Dekodieren fehlgeschlagen oder Feld token fehlt)")
    sys.exit(1)
if not client_id or not client_secret or not client_id.endswith(".apps.googleusercontent.com"):
    print("Client-ID oder Client-Secret unbrauchbar (leer oder vertauscht?)")
    sys.exit(1)
token = json.dumps(json.loads(token))
os.makedirs(os.path.dirname(conf_path), exist_ok=True)
fd = os.open(conf_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    f.write("[%s]\ntype = drive\nclient_id = %s\nclient_secret = %s\nscope = drive.file\ntoken = %s\n" % (remote, client_id, client_secret, token))
' "$RCLONE_CONF" "$RCLONE_REMOTE"; then
        unset DREAMDECK_DRIVE_TOKEN DREAMDECK_DRIVE_CLIENT_ID DREAMDECK_DRIVE_CLIENT_SECRET
        return 1
    fi
    unset DREAMDECK_DRIVE_TOKEN DREAMDECK_DRIVE_CLIENT_ID DREAMDECK_DRIVE_CLIENT_SECRET
    if ! rclone --config "$RCLONE_CONF" mkdir "$RCLONE_REMOTE:$DRIVE_FOLDER"; then
        log "rclone-Verbindung fehlgeschlagen – Token abgelaufen? Siehe ANLEITUNG, Zugänge erneuern"
        return 1
    fi
}

# Wartet, bis eine Adresse antwortet. Prüft alle 5 s, ob der Prozess (PID) noch
# lebt und ob die URL antwortet; gibt nach MAX_SEKUNDEN auf.
# Aufruf: wait_for_http NAME PID URL MAX_SEKUNDEN LOGDATEI
wait_for_http() {
    local name=$1 pid=$2 url=$3 max=$4 logfile=$5 waited=0
    while [ "$waited" -lt "$max" ]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            log "$name wurde vorzeitig beendet – siehe $logfile"
            return 1
        fi
        if python3 -c '
import sys, urllib.request
try:
    urllib.request.urlopen(sys.argv[1], timeout=3)
except Exception:
    sys.exit(1)
' "$url"; then
            log "$name läuft"
            return 0
        fi
        sleep 5
        waited=$((waited + 5))
    done
    log "$name antwortet nach $max s nicht – siehe $logfile"
    return 1
}

# ComfyUI im Hintergrund starten, nur auf 127.0.0.1 erreichbar (--listen wird
# bewusst ausdrücklich gesetzt), ohne CIVITAI_TOKEN (wird nicht geerbt). Bilder
# liegen außerhalb des ComfyUI-Ordners, weil ein Versionswechsel diesen Ordner
# löscht. Wartet höchstens 180 s, bis /system_stats antwortet.
step_start_comfyui() {
    local pid
    mkdir -p "$OUTPUT_DIR" || return 1
    env -u CIVITAI_TOKEN nohup python3 "$COMFY_DIR/main.py" --listen 127.0.0.1 --port "$COMFY_PORT" \
        --output-directory "$OUTPUT_DIR" > "$LOG_DIR/comfyui.log" 2>&1 &
    pid=$!
    log "ComfyUI gestartet (PID $pid), Protokoll: $LOG_DIR/comfyui.log"

    wait_for_http "ComfyUI auf 127.0.0.1:$COMFY_PORT" "$pid" "http://127.0.0.1:$COMFY_PORT/system_stats" 180 "$LOG_DIR/comfyui.log"
}

# Sync-Schleife (pod/sync.sh loop) im Hintergrund starten, ohne CIVITAI_TOKEN.
# Protokoll: sync.log (gemeinsam mit rclone).
step_start_sync() {
    env -u CIVITAI_TOKEN nohup bash "$REPO_DIR/pod/sync.sh" loop >> "$LOG_DIR/sync.log" 2>&1 &
    log "Sync-Schleife gestartet (PID $!), Protokoll: $LOG_DIR/sync.log"
}

# Eigene venv für das Dashboard anlegen (falls noch nicht vorhanden) und die
# gepinnten Abhängigkeiten installieren.
step_install_dashboard() {
    if [ ! -x "$DASHBOARD_VENV/bin/python" ]; then
        if ! python3 -m venv "$DASHBOARD_VENV"; then
            log "venv konnte nicht angelegt werden – fehlt python3-venv im Image?"
            return 1
        fi
    fi
    "$DASHBOARD_VENV/bin/pip" install --no-cache-dir -r "$REPO_DIR/dashboard/requirements.txt" || return 1
}

# Dashboard im Hintergrund starten, nur auf 127.0.0.1, ohne CIVITAI_TOKEN.
# --app-dir statt Verzeichniswechsel. Wartet höchstens 30 s auf /api/health.
step_start_dashboard() {
    local pid
    env -u CIVITAI_TOKEN nohup "$DASHBOARD_VENV/bin/uvicorn" dashboard.app:app --app-dir "$REPO_DIR" \
        --host 127.0.0.1 --port "$DASHBOARD_PORT" > "$LOG_DIR/dashboard.log" 2>&1 &
    pid=$!
    log "Dashboard gestartet (PID $pid), Protokoll: $LOG_DIR/dashboard.log"

    wait_for_http "Dashboard auf 127.0.0.1:$DASHBOARD_PORT" "$pid" "http://127.0.0.1:$DASHBOARD_PORT/api/health" 30 "$LOG_DIR/dashboard.log"
}

# --- Ablauf -------------------------------------------------------------
log "DreamDeck-Start beginnt"

run_step "Repo absichern (Token aus Git-Adresse entfernen)" step_secure_repo
run_step "Versionen laden (pod/versions.env)" step_load_versions

# RunPod-Dienste (Web-Terminal, SSH) im Hintergrund starten, damit der Pod
# auch während der Einrichtung erreichbar ist.
# Erst nach dem Absichern starten, damit die Dienste GITHUB_TOKEN nicht erben.
if [ -f /start.sh ]; then
    log "Starte RunPod-Dienste (/start.sh) im Hintergrund (Ausgabe in runpod.log)"
    /start.sh > "$LOG_DIR/runpod.log" 2>&1 &
fi

run_step "Secrets prüfen" step_check_secrets
run_step "ComfyUI ${COMFYUI_VERSION:-?} installieren" step_install_comfyui
run_step "GPU prüfen" step_check_gpu
run_step "Modelle laden" step_download_models
run_step "LoRAs laden" step_download_loras
run_step "rclone ${RCLONE_VERSION:-?} installieren" step_install_rclone
run_step "rclone einrichten" step_configure_rclone
run_step "ComfyUI starten" step_start_comfyui
run_step "Sync-Schleife starten" step_start_sync
run_step "Dashboard einrichten" step_install_dashboard
run_step "Dashboard starten" step_start_dashboard

# --- Abschluss ----------------------------------------------------------
if [ "$SETUP_FAILED" -eq 0 ]; then
    log "Einrichtung fertig"
else
    log "Einrichtung mit Fehler abgebrochen – Details oben"
fi

# Pod am Leben halten, auch im Fehlerfall.
sleep infinity
