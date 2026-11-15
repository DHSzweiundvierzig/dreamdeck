"""Baut ComfyUI-Workflows aus den Vorlagen in ``workflows/``."""
import copy
import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

WORKFLOW_DIR = Path(__file__).resolve().parent / "workflows"

# Erste ID der LoRA-Knoten; liegt weit über den IDs der Vorlagen.
LORA_ID_START = 101


@lru_cache
def _read_template(name: str) -> dict:
    """Liest eine Vorlage einmal von der Platte (danach aus dem Zwischenspeicher)."""
    with open(WORKFLOW_DIR / f"{name}.json", encoding="utf-8") as file:
        return json.load(file)


def load_template(name: str) -> dict:
    """Gibt eine frische Kopie der Vorlage ``workflows/<name>.json`` zurück."""
    return copy.deepcopy(_read_template(name))


def find_node(workflow: dict, title: str) -> str:
    """Gibt die ID des einzigen Knotens mit diesem Titel (``_meta.title``) zurück.

    Wirft ValueError, wenn kein oder mehr als ein Knoten so heißt.
    """
    hits = [
        node_id
        for node_id, node in workflow.items()
        if node.get("_meta", {}).get("title") == title
    ]
    if not hits:
        raise ValueError(f"Kein Knoten mit dem Titel „{title}“ im Workflow gefunden.")
    if len(hits) > 1:
        raise ValueError(
            f"Titel „{title}“ ist nicht eindeutig: {len(hits)} Knoten gefunden "
            f"(IDs {', '.join(hits)})."
        )
    return hits[0]


def make_filename_prefix() -> str:
    """Dateinamen-Präfix mit Monatsordner und Zeitstempel (Europe/Berlin).

    Format nach der Ablage-Regel in NOTIZEN.md (14.11.2026): Ordner
    JJJJ-MM, Dateiname JJJJ-MM-TT_hhmmss; ComfyUI hängt _NNNNN_ an.
    Beispiel: ``2026-11/2026-11-15_170616`` ergibt
    ``2026-11/2026-11-15_170616_00001_.png``. Monat und Zeitstempel
    stammen aus demselben Zeitpunkt. ComfyUI legt den Unterordner im
    Output-Ordner selbst an, der Sync übernimmt ihn ins Drive.
    """
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    return now.strftime("%Y-%m/%Y-%m-%d_%H%M%S")


def build_flux_workflow(
    prompt: str,
    seed: int,
    width: int,
    height: int,
    steps: int,
    guidance: float,
    batch_size: int,
    loras: list[tuple[str, float]],
) -> tuple[dict, str]:
    """Baut den FLUX-Workflow (Vorlage ``flux_split``) für einen Bildauftrag.

    ``loras`` ist eine Liste von (name, strength). Die LoRAs werden als Kette
    zwischen „Modell“ und „Sampler“ eingehängt; ohne LoRAs bleibt die
    Verdrahtung der Vorlage unverändert.

    Rückgabe: (workflow, filename_prefix).
    """
    workflow = load_template("flux_split")
    filename_prefix = make_filename_prefix()

    def inputs(title: str) -> dict:
        return workflow[find_node(workflow, title)]["inputs"]

    inputs("Prompt")["text"] = prompt
    inputs("Guidance")["guidance"] = guidance
    inputs("Format").update(width=width, height=height, batch_size=batch_size)
    sampler = inputs("Sampler")
    sampler.update(seed=seed, steps=steps)
    inputs("Speichern")["filename_prefix"] = filename_prefix

    # LoRA-Kette: Modell → LoRA 1 → LoRA 2 → … → Sampler.
    previous_id = find_node(workflow, "Modell")
    for number, (name, strength) in enumerate(loras, start=1):
        node_id = str(LORA_ID_START + number - 1)
        workflow[node_id] = {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": [previous_id, 0],
                "lora_name": name,
                "strength_model": strength,
            },
            "_meta": {"title": f"LoRA {number}"},
        }
        previous_id = node_id
    if loras:
        sampler["model"] = [previous_id, 0]

    return workflow, filename_prefix
