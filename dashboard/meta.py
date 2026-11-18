"""Liest Einstellungen aus den Textchunks eines PNG-Bildes.

Arbeitet nur mit Bytes (kein Dateizugriff, kein Pillow), damit es später auch
für Bilder aus Google Drive taugt. Abgeschnittene Daten sind erlaubt.
"""
import json
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# Höchstzahl der Schritte beim Verfolgen von Verbindungen (Schutz gegen Schleifen)
MAX_LINK_STEPS = 50


def _decode_zlib(data: bytes) -> bytes:
    return zlib.decompress(data)


def _parse_text_chunk(kind: bytes, data: bytes) -> tuple[str, str] | None:
    """Zerlegt einen tEXt-, zTXt- oder iTXt-Chunk in (Schlüssel, Text)."""
    if kind == b"tEXt":
        key, _, value = data.partition(b"\x00")
        return key.decode("latin-1"), value.decode("latin-1")
    if kind == b"zTXt":
        key, _, rest = data.partition(b"\x00")
        # rest: 1 Byte Kompressionsverfahren, dann zlib-Daten
        return key.decode("latin-1"), _decode_zlib(rest[1:]).decode("latin-1")
    if kind == b"iTXt":
        key, _, rest = data.partition(b"\x00")
        compressed = rest[0] == 1
        # Kompressionsverfahren (1 Byte) überspringen, dann Sprache und
        # übersetzten Schlüssel (je nullterminiert), dann der Text
        rest = rest[2:]
        _, _, rest = rest.partition(b"\x00")
        _, _, text = rest.partition(b"\x00")
        if compressed:
            text = _decode_zlib(text)
        return key.decode("utf-8"), text.decode("utf-8")
    return None


def lese_png_texte(daten: bytes) -> dict[str, str]:
    """Liest alle Textchunks (tEXt, zTXt, iTXt) eines PNG als {Schlüssel: Text}.

    Kein PNG oder kaputte Daten: leeres dict bzw. das bisher Gefundene.
    Wirft nie eine Ausnahme nach außen.
    """
    texte: dict[str, str] = {}
    try:
        if daten[:8] != PNG_SIGNATURE:
            return texte
        pos = 8
        while pos + 8 <= len(daten):
            length, kind = struct.unpack(">I4s", daten[pos : pos + 8])
            if kind in (b"IDAT", b"IEND"):
                break
            start = pos + 8
            end = start + length
            if end + 4 > len(daten):
                break  # Chunk abgeschnitten (Daten oder CRC fehlen)
            if kind in (b"tEXt", b"zTXt", b"iTXt"):
                try:
                    item = _parse_text_chunk(kind, daten[start:end])
                except (ValueError, zlib.error, IndexError):
                    item = None  # defekter Textchunk: überspringen
                if item:
                    texte[item[0]] = item[1]
            pos = end + 4  # CRC wird nicht geprüft
    except Exception:
        pass
    return texte


def _follow(graph: dict, link, wanted: set[str], visit) -> dict | None:
    """Folgt einer Verbindung [knoten_id, index] rückwärts.

    Ruft für jeden besuchten Knoten visit(knoten) auf. Hält an, wenn der
    Knoten eine class_type aus wanted hat, und gibt ihn zurück (sonst None).
    Weiter geht es über den Eingang "model", "conditioning" oder "positive",
    je nachdem, was der Knoten hat. Höchstens MAX_LINK_STEPS Schritte.
    """
    for _ in range(MAX_LINK_STEPS):
        if not (isinstance(link, list) and link):
            return None
        node = graph.get(str(link[0]))
        if not isinstance(node, dict):
            return None
        visit(node)
        if node.get("class_type") in wanted:
            return node
        inputs = node.get("inputs") or {}
        link = next(
            (inputs[name] for name in ("model", "conditioning", "positive") if isinstance(inputs.get(name), list)),
            None,
        )
    return None


def _value(inputs: dict, name: str):
    """Wert eines Eingangs; per Link gesetzt (Liste) oder fehlend → None."""
    value = inputs.get(name)
    return None if isinstance(value, list) else value


def lese_einstellungen(texte: dict) -> dict | None:
    """Baut die Einstellungen aus dem ComfyUI-Workflow (texte["prompt"]) nach.

    Erkennung über class_type, nicht über Titel. Kein Sampler oder kein
    gültiges JSON: None.
    """
    try:
        graph = json.loads(texte["prompt"])
        if not isinstance(graph, dict):
            return None
        nodes = [n for n in graph.values() if isinstance(n, dict)]
        sampler = next((n for n in nodes if n.get("class_type") == "KSampler"), None)
        if sampler is None:
            sampler = next(
                (n for n in nodes if n.get("class_type") == "KSamplerAdvanced"), None
            )
        if sampler is None:
            return None
        inputs = sampler.get("inputs") or {}
        seed = _value(inputs, "seed")
        if seed is None:
            seed = _value(inputs, "noise_seed")

        # positive rückwärts: guidance aus FluxGuidance, am Ende der Prompt-Text
        found: dict = {}

        def visit_positive(node):
            node_inputs = node.get("inputs") or {}
            if node.get("class_type") == "FluxGuidance" and "guidance" not in found:
                found["guidance"] = _value(node_inputs, "guidance")

        text_node = _follow(graph, inputs.get("positive"), {"CLIPTextEncode"}, visit_positive)
        prompt = _value(text_node.get("inputs") or {}, "text") if text_node else None

        # latent_image: Breite und Höhe
        latent = _follow(
            graph, inputs.get("latent_image"), {"EmptyLatentImage", "EmptySD3LatentImage"}, lambda n: None
        )
        latent_inputs = (latent.get("inputs") or {}) if latent else {}

        # model rückwärts: LoRAs (Sampler → Modell), danach umdrehen
        loras: list[dict] = []

        def visit_model(node):
            node_inputs = node.get("inputs") or {}
            if node.get("class_type") in ("LoraLoaderModelOnly", "LoraLoader"):
                loras.append(
                    {
                        "name": _value(node_inputs, "lora_name"),
                        "staerke": _value(node_inputs, "strength_model"),
                    }
                )

        model_node = _follow(
            graph,
            inputs.get("model"),
            {"UNETLoader", "CheckpointLoaderSimple", "CheckpointLoader"},
            visit_model,
        )
        model_inputs = (model_node.get("inputs") or {}) if model_node else {}
        model = _value(model_inputs, "unet_name")
        if model is None:
            model = _value(model_inputs, "ckpt_name")

        return {
            "prompt": prompt,
            "seed": seed,
            "steps": _value(inputs, "steps"),
            "guidance": found.get("guidance"),
            "breite": _value(latent_inputs, "width"),
            "hoehe": _value(latent_inputs, "height"),
            "modell": model,
            "loras": loras[::-1],
        }
    except Exception:
        return None
