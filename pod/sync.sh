#!/usr/bin/env bash
# DreamDeck – Sync der Bilder ins Google Drive.
#
# Kopiert (copy, nicht move) neue Bilder aus OUTPUT_DIR nach
# RCLONE_REMOTE:DRIVE_FOLDER. Pfade stehen nur in pod/paths.env.
#
# Aufrufarten:
#   bash pod/sync.sh        Manueller letzter Sync vor dem Löschen des Pods
#                           (wartet auf laufende Syncs, ohne Mindestalter).
#   bash pod/sync.sh loop   Schleife alle 30 s (startet pod/start.sh im
#                           Hintergrund); Dateien müssen mindestens 15 s alt sein.
#
# Protokoll: /workspace/logs/sync.log (rclone und Schleife gemeinsam).

set -u
set -o pipefail

if ! source "$(dirname "${BASH_SOURCE[0]}")/paths.env"; then
    echo "DreamDeck: pod/paths.env fehlt"
    exit 1
fi

LOCK_FILE=/tmp/dreamdeck-sync.lock

# Einziger Ort mit dem rclone-Befehl. Zusätzliche rclone-Argumente werden
# durchgereicht (z. B. --min-age 15s).
sync_once() {
    rclone --config "$RCLONE_CONF" copy "$OUTPUT_DIR" "$RCLONE_REMOTE:$DRIVE_FOLDER" \
        --log-file "$LOG_DIR/sync.log" --log-level INFO "$@"
}

# Manueller letzter Sync: blockiert, bis kein anderer Sync mehr läuft.
sync_final() {
    local rc
    mkdir -p "$LOG_DIR"
    exec 9>"$LOCK_FILE"
    flock 9
    sync_once
    rc=$?
    flock -u 9
    if [ "$rc" -eq 0 ]; then
        echo "Sync fertig"
    else
        echo "Sync mit Fehler – siehe /workspace/logs/sync.log"
    fi
    return "$rc"
}

# Schleife: läuft gerade ein Sync, wird die Runde übersprungen.
sync_loop() {
    mkdir -p "$LOG_DIR"
    exec 9>"$LOCK_FILE"
    while true; do
        if flock -n 9; then
            if ! sync_once --min-age 15s; then
                printf '%s Sync-Runde mit Fehler\n' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_DIR/sync.log"
            fi
            flock -u 9
        fi
        sleep 30
    done
}

case "${1:-}" in
    "")   sync_final; exit $? ;;
    loop) sync_loop ;;
    *)
        echo "Aufruf: bash pod/sync.sh        (letzter Sync)"
        echo "        bash pod/sync.sh loop   (Schleife alle 30 s)"
        exit 1
        ;;
esac
