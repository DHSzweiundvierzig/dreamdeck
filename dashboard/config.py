"""Einstellungen des Dashboards.

Einzige Stelle, die pod/paths.env liest. Secrets werden hier nicht gelesen.
"""
from pathlib import Path

PATHS_ENV = Path(__file__).resolve().parent.parent / "pod" / "paths.env"


def _read_env(path: Path) -> dict[str, str]:
    """Liest einfache Zeilen NAME=Wert; Leerzeilen und #-Zeilen werden übersprungen."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Einstellungsdatei nicht gefunden: {path}. "
            "Sie gehört ins Repo (pod/paths.env) und muss vorhanden sein."
        )
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


_env = _read_env(PATHS_ENV)

REPO_DIR = _env["REPO_DIR"]
OUTPUT_DIR = _env["OUTPUT_DIR"]
COMFY_PORT = int(_env["COMFY_PORT"])
DASHBOARD_PORT = int(_env["DASHBOARD_PORT"])
COMFY_URL = f"http://127.0.0.1:{COMFY_PORT}"
