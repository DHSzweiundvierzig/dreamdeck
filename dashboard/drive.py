"""Zugriff auf das Google Drive – alle rclone-Aufrufe des Dashboards an einer Stelle.

Aufrufe laufen immer mit Argumentliste (nie über eine Shell). Höchstens vier
rclone-Prozesse gleichzeitig. Die Bildliste wird 60 Sekunden zwischengespeichert.
"""
import asyncio
import json
import re
import time

from .config import DRIVE_FOLDER, IMAGE_SUFFIXES, RCLONE_CONF, RCLONE_REMOTE

# Zeitlimits in Sekunden
LIST_TIMEOUT = 60
HEAD_TIMEOUT = 20
IMAGE_TIMEOUT = 60
# So lange gilt die zwischengespeicherte Bildliste
LIST_CACHE_SECONDS = 60
# Höchstens so viele rclone-Aufrufe gleichzeitig
MAX_PARALLEL = 4
# Höchstlänge für Ordner- und Dateiname
MAX_NAME_LENGTH = 200
# Unterordner für Vorschaubilder (Etappe 3c); gehört nicht in die Bildliste
PREVIEW_FOLDER = "_vorschau"
# rclone-Exit-Codes „Verzeichnis nicht gefunden“ und „Datei nicht gefunden“
_NOT_FOUND_CODES = (3, 4)
# Erlaubt: Buchstaben, Ziffern, Unterstrich, Punkt, Minus und Leerzeichen
_NAME_PATTERN = re.compile(r"[\w. -]+")

_semaphore = asyncio.Semaphore(MAX_PARALLEL)
_list_lock = asyncio.Lock()
_list_cache: tuple[float, list[dict]] | None = None


class DriveFehler(Exception):
    """rclone war nicht erreichbar, zu langsam oder hat einen Fehler gemeldet."""

    def __init__(self, message: str, nicht_gefunden: bool = False):
        super().__init__(message)
        # True, wenn die Datei im Drive schlicht nicht existiert
        self.nicht_gefunden = nicht_gefunden


async def _rclone(*args: str, timeout: float) -> bytes:
    """Führt rclone mit den Argumenten aus und liefert stdout als Bytes."""
    async with _semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                "rclone", "--config", RCLONE_CONF, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            raise DriveFehler(f"rclone nicht startbar: {exc}") from exc
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise DriveFehler(f"Zeitüberschreitung nach {timeout:.0f} s") from None
        except asyncio.CancelledError:
            proc.kill()  # Browser hat abgebrochen: Prozess nicht weiterlaufen lassen
            await proc.wait()
            raise
    if proc.returncode != 0:
        lines = err.decode("utf-8", "replace").strip().splitlines()
        message = lines[-1] if lines else f"Exit-Code {proc.returncode}"
        raise DriveFehler(message, nicht_gefunden=proc.returncode in _NOT_FOUND_CODES)
    return out


def pruefe_name(ordner: str, datei: str) -> str | None:
    """Prüft Ordner und Dateiname und liefert den rclone-Pfad „REMOTE:FOLDER/ordner/datei“.

    Ungültig (fremde Zeichen, „..“, führender „/“, falsche Endung, zu lang) → None.
    """
    if len(ordner) > MAX_NAME_LENGTH or len(datei) > MAX_NAME_LENGTH:
        return None
    if ".." in ordner or ".." in datei:
        return None
    if not _NAME_PATTERN.fullmatch(datei) or not datei.lower().endswith(IMAGE_SUFFIXES):
        return None
    parts = []
    if ordner:
        parts = ordner.split("/")
        if not all(_NAME_PATTERN.fullmatch(part) for part in parts):
            return None  # leere Segmente (führender „/“, „//“) fallen hier heraus
    return "/".join([f"{RCLONE_REMOTE}:{DRIVE_FOLDER}", *parts, datei])


async def liste() -> list[dict]:
    """Alle Bilder im Drive als {datei, ordner, zeit}; 60 Sekunden zwischengespeichert."""
    global _list_cache
    async with _list_lock:  # gleichzeitige Aufrufer warten auf dasselbe Neuladen
        if _list_cache is not None and time.monotonic() - _list_cache[0] < LIST_CACHE_SECONDS:
            return _list_cache[1]
        out = await _rclone(
            "lsjson", "-R", "--files-only", "--fast-list", f"{RCLONE_REMOTE}:{DRIVE_FOLDER}",
            timeout=LIST_TIMEOUT,
        )
        try:
            entries = json.loads(out)
        except ValueError as exc:
            raise DriveFehler("Antwort von rclone nicht lesbar") from exc
        images = []
        for entry in entries:
            parts = str(entry.get("Path", "")).split("/")
            if parts[0] == PREVIEW_FOLDER or not parts[-1].lower().endswith(IMAGE_SUFFIXES):
                continue
            images.append({
                "datei": parts[-1],
                "ordner": "/".join(parts[:-1]),
                "zeit": entry.get("ModTime", ""),
            })
        _list_cache = (time.monotonic(), images)
        return images


async def kopf(ordner: str, datei: str, anzahl: int) -> bytes:
    """Die ersten `anzahl` Bytes einer Datei aus dem Drive (für die PNG-Metadaten)."""
    pfad = pruefe_name(ordner, datei)
    if pfad is None:
        raise DriveFehler("Ungültiger Name", nicht_gefunden=True)
    return await _rclone("cat", "--count", str(anzahl), pfad, timeout=HEAD_TIMEOUT)


async def bild(ordner: str, datei: str) -> bytes:
    """Das ganze Bild aus dem Drive."""
    pfad = pruefe_name(ordner, datei)
    if pfad is None:
        raise DriveFehler("Ungültiger Name", nicht_gefunden=True)
    return await _rclone("cat", pfad, timeout=IMAGE_TIMEOUT)
