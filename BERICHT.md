# Bericht – Etappe 3 · 3b: Galerie-Backend liest live aus Google Drive

## Änderungen
- `dashboard/config.py:33-37` – `RCLONE_CONF`, `RCLONE_REMOTE`, `DRIVE_FOLDER` aus `_env`; `IMAGE_SUFFIXES` hierher verschoben.
- `dashboard/drive.py` (neu) – alle rclone-Aufrufe: `_rclone` (Zeile 44), `pruefe_name` (72), `liste` (91), `kopf` (119), `bild` (127), `DriveFehler` (35).
- `dashboard/app.py:23-25` Importe (`drive`, `IMAGE_SUFFIXES` aus config, `DriveFehler`); `:277` `/api/bild` mit Drive-Rückfall; `:301` `_drive_fehler`; `:319` `/api/bild/info` jetzt `async` mit `_info_cache` (`:315`); `:346` `_lokale_bilder`; `:375` `/api/verlauf` nutzt sie; `:399` neue Route `/api/galerie` (Sortierschlüssel `_sort_time` `:389`).
- `MERKLISTE.md` – 3c-Zusatz, neue Zeile 3g, Verweis „entschieden: live per rclone → 3b“, Ideen-Parkplatz „Einstellungs-Oberfläche“. 3b **nicht** abgehakt.
- `ARCHITEKTUR.md`, `NOTIZEN.md` – wie beauftragt ergänzt.

## ⚠️-Punkte
- Zeitlimits: `liste` 60 s, `kopf` 20 s, `bild` 60 s (Konstanten in `drive.py`); bei Ablauf wird der Prozess beendet (`kill` + `wait`) und `DriveFehler` ausgelöst. Auch bei Abbruch durch den Browser wird der Prozess beendet.
- Passwortschutz: `/api/galerie` liegt unter `/api/`, die `AuthMiddleware` greift wie bei den übrigen Routen.
- `_vorschau/` wird in `drive.liste` und `_lokale_bilder` übersprungen.
- Einstellungs-Oberfläche im Ideen-Parkplatz war noch nicht vorhanden → ergänzt.

## Bündel-Befund
- `IMAGE_SUFFIXES` → `config.py`, kein Zirkel-Import.
- `_lokale_bilder()` – gemeinsam für `/api/verlauf` und `/api/galerie`.
- `_drive_fehler()` – gemeinsame Fehlerantwort für `/api/bild` und `/api/bild/info`.
- Weitere Doppelungen: keine gefunden.

## Entscheidungen, die von der Vorgabe abweichen oder sie auslegen
- `zeit` lokaler Bilder ist ein UTC-Text (`JJJJ-MM-TTThh:mm:ss.ffffff`) statt einer Zahl, damit lokale und Drive-Zeiten (ModTime-Text) vergleichbar sind. `/api/verlauf` sortiert danach (Mikrosekunden, Reihenfolge wie bisher).
- `pruefe_name`: „Buchstaben“ umfasst auch Umlaute (`\w`).
- `DriveFehler.nicht_gefunden` (rclone-Exit-Code 3 oder 4) unterscheidet 404 von 502.
- Bei doppelten Bildern gewinnt der Drive-Eintrag.

## Offene Punkte
- Nichts ausgeführt (kein Python hier). Test auf dem Pod: `/api/galerie`, `/api/bild` und `/api/bild/info` mit einem Bild, das nur im Drive liegt; Verhalten von `rclone cat --count` und der Exit-Codes bei fehlender Datei prüfen; Ausfall des Drives (Token ungültig) → `"drive": "fehler"`.
- Die Oberfläche nutzt `/api/galerie` noch nicht (3c).
