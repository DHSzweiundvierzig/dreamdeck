"""Download-Baustein für Modelldateien (Modelle, später LoRAs und Nachladen im Dashboard).

Liest die Modell-Sets aus pod/models.toml und lädt fehlende Dateien sicher herunter:
nur erlaubte Quellen, Platzprüfung vorab, Prüfsumme, Download über eine .part-Datei.

Aufruf:
    python3 pod/models.py download --sets "basis fp16" --models-dir /pfad

Nur Python-Standardbibliothek, Python 3.12.
"""

import argparse
import hashlib
import http.client
import os
import shutil
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED_HOSTS = ("huggingface.co", "civitai.com")
PICKLE_SUFFIXES = (".pth", ".pt", ".ckpt", ".bin")
FILE_FIELDS = ("role", "url", "dest", "size", "sha256")
CHUNK_SIZE = 8 * 1024 * 1024
MAX_ATTEMPTS = 3
RETRY_PAUSE_SECONDS = 5
TIMEOUT_SECONDS = 60
SPACE_FACTOR = 1.05
DEFAULT_CATALOG = Path(__file__).with_name("models.toml")


class ModelError(Exception):
    """Fehler mit einer Meldung, die so ins Protokoll darf (nie mit Headern)."""


def say(message):
    """Zeile mit Präfix ausgeben, sofort sichtbar im Protokoll."""
    print(f"[models] {message}", flush=True)


def format_gb(size):
    """Bytes als GB mit einer Nachkommastelle (deutsches Komma)."""
    return f"{size / 1e9:.1f}".replace(".", ",")


def load_catalog(path):
    """Katalog (models.toml) einlesen und als dict zurückgeben."""
    try:
        with open(path, "rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ModelError(f"Katalog {path} nicht lesbar: {error}") from error


def validate_sets(catalog, names):
    """Prüft die gewählten Sets: Namen bekannt, Felder vollständig, nur ein FLUX-Set."""
    sets = catalog.get("sets", {})
    if not names:
        raise ModelError("Keine Modell-Sets angegeben")
    flux_sets = []
    for name in names:
        if name not in sets:
            known = ", ".join(sorted(sets)) or "keine"
            raise ModelError(f"Unbekanntes Modell-Set „{name}“ (bekannt: {known})")
        entry = sets[name]
        if "loader" not in entry:
            raise ModelError(f"Set „{name}“: Feld loader fehlt")
        if entry["loader"] != "none":
            flux_sets.append(name)
        for item in entry.get("files", []):
            for field in FILE_FIELDS:
                if field not in item:
                    raise ModelError(f"Set „{name}“: Feld {field} fehlt bei einer Datei")
    if len(flux_sets) > 1:
        raise ModelError(f"Nur ein FLUX-Set pro Start (gewählt: {', '.join(flux_sets)})")


def check_url(url):
    """Erlaubt nur https und genau die Hosts aus ALLOWED_HOSTS."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise ModelError(f"Quelle abgelehnt (nur https erlaubt): {parts.scheme}://{parts.hostname}")
    if parts.hostname not in ALLOWED_HOSTS or parts.port is not None or parts.username is not None:
        raise ModelError(f"Quelle abgelehnt (Host nicht erlaubt): {parts.hostname}")


def resolve_dest(models_dir, dest):
    """Zielpfad unter models_dir bilden; Pfade, die den Ordner verlassen, ablehnen."""
    relative = Path(dest)
    if relative.is_absolute() or ".." in relative.parts:
        raise ModelError(f"Ziel abgelehnt (muss im Modellordner liegen): {dest}")
    return Path(models_dir) / relative


def selected_files(catalog, names, models_dir):
    """Alle Dateien der gewählten Sets als Liste (Eintrag, Zielpfad)."""
    result = []
    for name in names:
        for item in catalog["sets"][name].get("files", []):
            result.append((item, resolve_dest(models_dir, item["dest"])))
    return result


def check_space(files, names, models_dir):
    """Platzprüfung: Summe der noch fehlenden Dateien × 1,05 gegen den freien Platz."""
    needed = sum(item["size"] for item, dest in files if not dest.exists()) * SPACE_FACTOR
    free = shutil.disk_usage(models_dir).free
    if needed > free:
        raise ModelError(
            f"{', '.join(names)} brauchen {format_gb(needed)} GB, frei sind {format_gb(free)} GB"
        )


def hash_file(path):
    """sha256 einer vorhandenen Datei berechnen."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Folgt Weiterleitungen nur nach https.

    Die eigenen Header (z. B. ein Token) gehen nur an den ursprünglichen Host,
    nie an fremde Hosts wie die Speicher-Server hinter der Weiterleitung.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        if target.scheme != "https":
            raise ModelError("Weiterleitung abgelehnt (Ziel ist nicht https)")
        new_request = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_request is not None and target.hostname == urllib.parse.urlsplit(req.full_url).hostname:
            for key, value in req.unredirected_hdrs.items():
                new_request.add_unredirected_header(key, value)
        return new_request


def fetch_to_part(url, part, headers, name):
    """Ein Download-Versuch nach part; gibt die gemessene sha256 zurück."""
    part.unlink(missing_ok=True)
    request = urllib.request.Request(url)
    for key, value in (headers or {}).items():
        # Nicht weiterleitbar: fremde Hosts bekommen die Header nie zu sehen.
        request.add_unredirected_header(key, value)
    opener = urllib.request.build_opener(SafeRedirectHandler())
    digest = hashlib.sha256()
    received = 0
    next_mark = 10
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        if urllib.parse.urlsplit(response.geturl()).scheme != "https":
            raise ModelError(f"{name}: End-Adresse nach Weiterleitung ist nicht https")
        total = int(response.headers.get("Content-Length") or 0)
        say(f"{name}: Download startet ({format_gb(total)} GB)" if total else f"{name}: Download startet")
        with open(part, "wb") as handle:
            while chunk := response.read(CHUNK_SIZE):
                handle.write(chunk)
                digest.update(chunk)
                received += len(chunk)
                # Fortschritt nur alle 10 % ausgeben.
                while total and next_mark <= 100 and received * 100 >= total * next_mark:
                    say(f"{name}: {next_mark} %")
                    next_mark += 10
    if total and received != total:
        raise ConnectionError(f"Übertragung unvollständig ({received} von {total} Bytes)")
    return digest.hexdigest()


def fetch_with_retries(url, part, headers, name):
    """Bis zu MAX_ATTEMPTS Versuche bei Netzfehlern; gibt die gemessene sha256 zurück."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fetch_to_part(url, part, headers, name)
        except urllib.error.HTTPError as error:
            # Fehler wie 401/403/404 werden durch Wiederholen nicht besser.
            if error.code < 500 and error.code != 429:
                part.unlink(missing_ok=True)
                raise ModelError(f"{name}: Server antwortet mit HTTP {error.code}") from None
            reason = f"HTTP {error.code}"
        except (OSError, http.client.HTTPException) as error:
            reason = f"{type(error).__name__}: {error}"
        say(f"{name}: Versuch {attempt} von {MAX_ATTEMPTS} fehlgeschlagen ({reason})")
        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_PAUSE_SECONDS)
    part.unlink(missing_ok=True)
    raise ModelError(f"{name}: Download nach {MAX_ATTEMPTS} Versuchen fehlgeschlagen")


def download_file(url, dest, sha256, headers=None):
    """Lädt eine Datei sicher nach dest. headers (z. B. Token) werden nie ausgegeben.

    Rückgabe: True, wenn geladen wurde; False, wenn die Datei schon da war.
    """
    check_url(url)
    dest = Path(dest)
    name = dest.name
    expected = (sha256 or "").strip().lower()

    if dest.exists():
        if not expected:
            say(f"{name}: vorhanden, Prüfsumme unbekannt – übersprungen (ungeprüft)")
            return False
        actual = hash_file(dest)
        if actual != expected:
            # Datei bewusst NICHT löschen: erst ansehen, dann entscheiden.
            raise ModelError(
                f"{name}: vorhandene Datei hat eine falsche Prüfsumme "
                f"(erwartet {expected}, gemessen {actual}) – Datei bleibt liegen"
            )
        say(f"{name}: vorhanden, Prüfsumme stimmt – übersprungen")
        return False

    if dest.suffix.lower() in PICKLE_SUFFIXES and not expected:
        raise ModelError(f"{name}: Pickle-Datei ({dest.suffix}) ohne sha256 wird nicht geladen")

    dest.parent.mkdir(parents=True, exist_ok=True)
    part = Path(str(dest) + ".part")
    actual = fetch_with_retries(url, part, headers, name)

    if expected and actual != expected:
        part.unlink(missing_ok=True)
        raise ModelError(
            f"{name}: Prüfsumme falsch (erwartet {expected}, gemessen {actual}) – Download verworfen"
        )
    if not expected:
        say(f"{name}: gemessene Prüfsumme sha256 = {actual} – bitte in pod/models.toml eintragen")
    os.replace(part, dest)
    say(f"{name}: fertig")
    return True


def download_sets(catalog, names, models_dir):
    """Lädt alle fehlenden Dateien der gewählten Sets nach models_dir."""
    names = list(dict.fromkeys(names))  # Doppelte Namen entfernen, Reihenfolge behalten
    validate_sets(catalog, names)
    files = selected_files(catalog, names, models_dir)
    # Erst alles prüfen, dann laden – kein langer Download vor einem absehbaren Fehler.
    for item, dest in files:
        check_url(item["url"])
        if not dest.exists() and dest.suffix.lower() in PICKLE_SUFFIXES and not item["sha256"]:
            raise ModelError(f"{dest.name}: Pickle-Datei ({dest.suffix}) ohne sha256 wird nicht geladen")
    os.makedirs(models_dir, exist_ok=True)
    check_space(files, names, models_dir)
    for item, dest in files:
        download_file(item["url"], dest, item["sha256"])
    say(f"Alle Dateien vorhanden ({', '.join(names)})")


class Parser(argparse.ArgumentParser):
    """Wie ArgumentParser, aber mit Exit 1 statt 2 bei falschem Aufruf."""

    def error(self, message):
        say(f"FEHLER: {message}")
        sys.exit(1)


def main(argv=None):
    """Kommandozeile; Rückgabe ist der Exit-Code."""
    parser = Parser(description="Modelldateien für DreamDeck laden")
    commands = parser.add_subparsers(dest="command", required=True)
    download = commands.add_parser("download", help="Fehlende Dateien der Sets laden")
    download.add_argument("--sets", required=True, help='Set-Namen mit Leerzeichen, z. B. "basis fp16"')
    download.add_argument("--models-dir", required=True, help="Modellordner von ComfyUI")
    download.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Pfad zu models.toml")
    args = parser.parse_args(argv)

    try:
        catalog = load_catalog(args.catalog)
        download_sets(catalog, args.sets.split(), args.models_dir)
    except ModelError as error:
        say(f"FEHLER: {error}")
        return 1
    except Exception as error:  # Unerwartetes: Meldung ohne Details aus der Anfrage
        say(f"FEHLER: {type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
