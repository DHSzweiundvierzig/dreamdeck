"""Live-Fortschritt: ComfyUI-Websocket lesen, übersetzen und an alle Browser verteilen."""
import asyncio
import contextlib
import json
import logging
from dataclasses import dataclass, field

from websockets.asyncio.client import connect
from websockets.exceptions import WebSocketException

from .config import COMFY_WS_URL

log = logging.getLogger(__name__)

QUEUE_SIZE = 100
# Obergrenze je Websocket-Nachricht (Vorschaubilder können groß sein).
MAX_MESSAGE_BYTES = 16 * 1024 * 1024
RECONNECT_SECONDS = 3.0


class EventHub:
    """Verteilt Ereignisse an alle angemeldeten Browser (eine Queue je Browser)."""

    def __init__(self) -> None:
        self._queues: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        """Legt eine neue Queue an, merkt sie und gibt sie zurück."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=QUEUE_SIZE)
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Entfernt die Queue wieder (unbekannte Queues werden ignoriert)."""
        self._queues.discard(queue)

    def publish(self, event: dict) -> None:
        """Stellt das Ereignis in alle Queues. Blockiert nie und wirft nie.

        Ist eine Queue voll (langsamer Browser), fliegt ihr ältestes Ereignis raus.
        """
        for queue in list(self._queues):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                with contextlib.suppress(asyncio.QueueEmpty):
                    queue.get_nowait()
                with contextlib.suppress(asyncio.QueueFull):
                    queue.put_nowait(event)


@dataclass
class ComfyState:
    """Merkt sich laufende Aufträge und deren bisher gemeldete Bilder."""

    laufend: set = field(default_factory=set)
    bilder: dict = field(default_factory=dict)


def _dict(value) -> dict:
    """Gibt value zurück, wenn es ein dict ist, sonst ein leeres dict."""
    return value if isinstance(value, dict) else {}


def _forget(state: ComfyState, prompt_id) -> None:
    """Räumt einen Auftrag aus laufend und bilder."""
    state.laufend.discard(prompt_id)
    state.bilder.pop(prompt_id, None)


def translate(message: dict, state: ComfyState) -> list[dict]:
    """Übersetzt eine ComfyUI-Meldung in null oder mehr DreamDeck-Ereignisse.

    Unbekannte Meldungen und fehlende Felder führen nie zu einem Fehler.
    """
    message = _dict(message)
    kind = message.get("type")
    data = _dict(message.get("data"))
    prompt_id = data.get("prompt_id")

    if kind == "status":
        exec_info = _dict(_dict(data.get("status")).get("exec_info"))
        return [{"typ": "warteschlange", "anzahl": exec_info.get("queue_remaining")}]

    if kind == "execution_start":
        state.laufend.add(prompt_id)
        return [{"typ": "start", "prompt_id": prompt_id}]

    if kind == "progress":
        return [
            {
                "typ": "fortschritt",
                "prompt_id": prompt_id,
                "schritt": data.get("value"),
                "von": data.get("max"),
            }
        ]

    if kind == "executed":
        images = _dict(data.get("output")).get("images")
        if isinstance(images, list) and images:
            collected = state.bilder.setdefault(prompt_id, [])
            for image in images:
                image = _dict(image)
                collected.append(
                    {"datei": image.get("filename"), "ordner": image.get("subfolder")}
                )
        return []

    # ComfyUI meldet das Ende je nach Version auf zwei Arten; "fertig" kommt genau einmal.
    if kind == "execution_success" or (kind == "executing" and data.get("node") is None):
        if prompt_id not in state.laufend:
            return []
        state.laufend.discard(prompt_id)
        return [
            {"typ": "fertig", "prompt_id": prompt_id, "bilder": state.bilder.pop(prompt_id, [])}
        ]

    if kind == "execution_error":
        _forget(state, prompt_id)
        return [
            {
                "typ": "fehler",
                "prompt_id": prompt_id,
                "meldung": data.get("exception_message"),
                "knoten": data.get("node_type"),
            }
        ]

    if kind == "execution_interrupted":
        _forget(state, prompt_id)
        return [{"typ": "fehler", "prompt_id": prompt_id, "meldung": "abgebrochen"}]

    return []


async def listen_comfyui(hub: EventHub, client_id: str) -> None:
    """Hält die Websocket-Verbindung zu ComfyUI und veröffentlicht die Ereignisse.

    Läuft endlos und verbindet sich nach einem Abbruch neu. Beendet wird die
    Schleife nur durch Abbrechen des Tasks (asyncio.CancelledError).
    """
    state = ComfyState()  # lebt über Neuverbindungen hinweg
    url = f"{COMFY_WS_URL}?clientId={client_id}"
    while True:
        try:
            async with connect(url, max_size=MAX_MESSAGE_BYTES) as websocket:
                hub.publish({"typ": "verbindung", "ok": True})
                log.info("Mit ComfyUI-Websocket verbunden.")
                async for raw in websocket:
                    if not isinstance(raw, str):
                        continue  # Binärnachricht (Vorschaubild), vorerst übersprungen
                    try:
                        message = json.loads(raw)
                    except ValueError:
                        continue
                    try:
                        for event in translate(message, state):
                            hub.publish(event)
                    except Exception:
                        log.exception("Fehler beim Verarbeiten einer ComfyUI-Meldung")
        except (OSError, WebSocketException) as error:
            log.warning("ComfyUI-Websocket nicht verbunden: %s", error)
        except Exception:
            log.exception("Unerwarteter Fehler in der ComfyUI-Websocket-Schleife")
        hub.publish({"typ": "verbindung", "ok": False})
        await asyncio.sleep(RECONNECT_SECONDS)
