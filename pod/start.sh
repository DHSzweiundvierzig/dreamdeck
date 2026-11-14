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
REPO_DIR=/workspace/dreamdeck
LOG_DIR=/workspace/logs
LOG_FILE=$LOG_DIR/start.log
REPO_URL=https://github.com/DHSzweiundvierzig/dreamdeck.git

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

# Token aus der Git-Adresse entfernen und aus der Umgebung löschen.
# Läuft ohne Subshell, damit unset in der Hauptshell wirkt.
step_secure_repo() {
    git -C "$REPO_DIR" remote set-url origin "$REPO_URL" || return 1
    unset GITHUB_TOKEN
}

# Prüft nur, ob die Secrets gesetzt sind – der Wert wird nie ausgegeben.
step_check_secrets() {
    local name
    local missing=0
    for name in CIVITAI_TOKEN RCLONE_DRIVE_TOKEN; do
        if [ -n "${!name:-}" ]; then
            log "Secret $name: gesetzt"
        else
            log "Secret $name: fehlt"
            missing=1
        fi
    done
    return "$missing"
}

# --- Ablauf -------------------------------------------------------------
log "DreamDeck-Start beginnt"

run_step "Repo absichern (Token aus Git-Adresse entfernen)" step_secure_repo

# RunPod-Dienste (Web-Terminal, SSH) im Hintergrund starten, damit der Pod
# auch während der Einrichtung erreichbar ist.
# Erst nach dem Absichern starten, damit die Dienste GITHUB_TOKEN nicht erben.
if [ -f /start.sh ]; then
    log "Starte RunPod-Dienste (/start.sh) im Hintergrund (Ausgabe in runpod.log)"
    /start.sh > "$LOG_DIR/runpod.log" 2>&1 &
fi

run_step "Secrets prüfen" step_check_secrets

# Hier folgen die Schritte aus 1c–1f
# (ComfyUI installieren, Modelle laden, LoRAs laden, ComfyUI starten, rclone).

# --- Abschluss ----------------------------------------------------------
if [ "$SETUP_FAILED" -eq 0 ]; then
    log "Einrichtung fertig"
else
    log "Einrichtung mit Fehler abgebrochen – Details oben"
fi

# Pod am Leben halten, auch im Fehlerfall.
sleep infinity
