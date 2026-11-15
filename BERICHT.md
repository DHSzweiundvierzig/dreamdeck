# Bericht – Etappe 2 · Schritt 2e (Live-Fortschritt per Server-Sent Events)

## Neue Dateien
- `dashboard/events.py`: `EventHub` (eine Queue je Browser, `subscribe`/`unsubscribe`/`publish`), `ComfyState` (`laufend`, `bilder`), `translate` (ComfyUI-Meldung → Ereignisse) und `listen_comfyui` (dauerhafte Websocket-Verbindung mit Neuverbindung nach 3 s).

## Geänderte Dateien
- `dashboard/config.py`: `COMFY_WS_URL = "ws://127.0.0.1:<COMFY_PORT>/ws"` ergänzt.
- `dashboard/app.py`: Im lifespan `app.state.events = EventHub()` und der Hintergrund-Task `listen_comfyui` (wird beim Beenden vor dem Schließen des httpx-Clients abgebrochen); neuer Endpunkt `GET /api/events` vor dem Static-Mount.
- `ARCHITEKTUR.md`: Backend-Punkt um den Satz zum Fortschritt ergänzt.
- `MERKLISTE.md`: 2d abgehakt (Pod-Test vom 15.11.2026 bestanden, Bild identisch mit dem ComfyUI-Testbild); 2e bleibt offen.
- `dashboard/requirements.txt`: unverändert, `websockets==17.4` war schon gepinnt.

## Ereignisse (je eine Zeile `data: <json>` im Strom)
| Typ | Beispiel | Auslöser in ComfyUI |
|---|---|---|
| verbindung | `{"typ": "verbindung", "ok": true}` | Websocket verbunden (`ok: false` bei Abbruch oder Verbindungsfehler) |
| warteschlange | `{"typ": "warteschlange", "anzahl": 1}` | `status` |
| start | `{"typ": "start", "prompt_id": "abc-123"}` | `execution_start` |
| fortschritt | `{"typ": "fortschritt", "prompt_id": "abc-123", "schritt": 7, "von": 25}` | `progress` |
| fertig | `{"typ": "fertig", "prompt_id": "abc-123", "bilder": [{"datei": "dreamdeck_20261115-143000_00001_.png", "ordner": "2026-11"}]}` | `execution_success` oder `executing` mit `node: null` (genau einmal) |
| fehler | `{"typ": "fehler", "prompt_id": "abc-123", "meldung": "CUDA out of memory", "knoten": "KSampler"}` | `execution_error` |
| fehler | `{"typ": "fehler", "prompt_id": "abc-123", "meldung": "abgebrochen"}` | `execution_interrupted` (ohne `knoten`) |

Dazu Kommentarzeilen ohne Daten: `: verbunden` direkt nach dem Verbinden, `: ping` nach 15 s Stille.

## Test auf dem Pod
- Im SSH-Tunnel: `curl -N http://127.0.0.1:<DASHBOARD_PORT>/api/events` – zeigt sofort `: verbunden`, danach die Ereignisse.
- In einem zweiten Fenster einen Auftrag über `/docs` (POST /api/generate) schicken: erwartet `warteschlange`, `start`, mehrere `fortschritt`, einmal `fertig` mit Bildliste.
- ComfyUI stoppen: alle 3 s `verbindung ok=false`; nach dem Neustart `verbindung ok=true`.

## Prüfung
- Nichts ausgeführt: In dieser Umgebung gibt es kein Python. Code nur durchgesehen; der erste echte Lauf ist der Pod-Test.

## Auffälligkeiten
- Kein Anfangszustand: Ein Browser, der sich später verbindet, erfährt den Verbindungsstatus und die Warteschlange erst beim nächsten Ereignis. `verbindung ok=true` wird nur einmal beim Verbinden veröffentlicht. Für die Oberfläche wäre es sinnvoll, den letzten Stand beim Abonnieren mitzuschicken (nicht umgesetzt, stand nicht im Auftrag).
- Ist ComfyUI nicht erreichbar, kommt alle 3 s ein `verbindung ok=false` (und eine Warnzeile im Protokoll), nicht nur einmal beim Abbruch.
- „fertig“ kommt nur für Aufträge, deren `execution_start` gesehen wurde. Fällt die Websocket-Verbindung genau beim Start eines Auftrags aus, gibt es für ihn kein „fertig“; seine Bilder bleiben dann in `state.bilder` liegen (klein, bis zum Neustart).
- Bricht die Verbindung mitten in einem Auftrag ab und ComfyUI startet neu, bleibt die `prompt_id` in `state.laufend`, ohne dass je „fertig“ oder „fehler“ folgt.
- Beenden: uvicorn wartet beim Herunterfahren auf offene Verbindungen. Ein offener `/api/events`-Strom endet nie von selbst, das Dashboard beendet sich also erst, wenn die Browser getrennt sind (oder per kill). In `pod/start.sh` ist kein `--timeout-graceful-shutdown` gesetzt; bei „neuer Code = neuer Pod“ vermutlich egal.
- `execution_start` usw. schickt ComfyUI nur an den Client, der den Auftrag gestellt hat. Aufträge aus der ComfyUI-Oberfläche erscheinen daher nur in `warteschlange`, nicht als `start`/`fortschritt`/`fertig`.
- `progress` kommt bei ComfyUI ohne Bezug zum Knoten in die Übersetzung: Meldet später ein anderer Knoten als der Sampler Fortschritt, erscheint er genauso als `fortschritt`.
- `executed` sammelt alle Bilder, auch solche von Vorschau-Knoten (`type: "temp"`). Die aktuelle Vorlage hat nur einen Speicher-Knoten, daher ohne Wirkung.
- Fehlende Felder werden zu `null` im Ereignis (z. B. `anzahl: null`), nie zu einem Fehler. Nachrichten, die kein JSON-Objekt sind, werden ignoriert.
- Bei voller Queue (100 Ereignisse) geht das älteste verloren; das kann im ungünstigen Fall auch ein „fertig“ sein. Bei 15-s-Ping und normalem Browser praktisch nicht zu erwarten.
- Verbindungsfehler (`OSError`, `WebSocketException`) werden als Warnung geloggt, alles Unerwartete mit Traceback; in beiden Fällen läuft die Schleife nach 3 s weiter. `asyncio.CancelledError` wird nicht abgefangen.
