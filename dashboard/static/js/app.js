// DreamDeck – Oberfläche (klassisches Script, wird vor Alpine geladen).
// Registriert die Komponente "dreamdeck", sobald Alpine startet.

document.addEventListener("alpine:init", () => {
  // Abstand der Statusabfrage in Millisekunden
  const HEALTH_INTERVAL_MS = 30000;

  // Höchstzahl der Bilder im Verlauf, damit die Seite schlank bleibt
  const HISTORY_MAX = 60;

  // Texte zum ComfyUI-Status
  const COMFY_LABELS = {
    unbekannt: "prüfe …",
    ok: "ComfyUI bereit",
    aus: "ComfyUI nicht erreichbar",
  };

  // Grenzen für Breite und Höhe (wie im Backend): Vielfache von 16 zwischen 256 und 2048
  const DIM_STEP = 16;
  const DIM_MIN = 256;
  const DIM_MAX = 2048;
  // Größte Kante der Formvorschau in Pixeln
  const SHAPE_MAX = 28;
  // Höchster erlaubter Seed als Text: 2^64 − 1, Grenze von ComfyUI
  const SEED_MAX = "18446744073709551615";

  // Rundet auf 16 und begrenzt auf 256–2048. Ungültige Eingaben ergeben 256.
  function snap(v) {
    const rounded = Math.round((Number(v) || 0) / DIM_STEP) * DIM_STEP;
    return Math.min(DIM_MAX, Math.max(DIM_MIN, rounded));
  }

  // Höchstzahl gleichzeitiger LoRAs und Stärke einer neu hinzugefügten LoRA
  const LORA_MAX = 6;
  const LORA_STRENGTH_DEFAULT = 0.8;

  Alpine.data("dreamdeck", () => ({
    // Nummer der offenen Box, 0 = alle zu.
    // Später übernimmt ein Klick-Tutorial das Aufklappen.
    open: 0,

    // Die fünf Pipeline-Boxen; alle entstehen aus dieser Liste und einer Vorlage.
    steps: [
      { n: 1, code: "DD//01·MDL", title: "Modelle", hint: "FLUX.1 [dev]", later: "Auswahl folgt später" },
      { n: 2, code: "DD//02·LRA", title: "LoRAs" },
      { n: 3, code: "DD//03·FMT", title: "Format" },
      { n: 4, code: "DD//04·TUN", title: "Feintuning", hint: "25 Schritte · Guidance 3.5", later: "folgt später" },
      { n: 5, code: "DD//05·OUT", title: "Speichern", hint: "Monatsordner · Drive", later: "folgt später" },
    ],

    // Zustand von ComfyUI: "unbekannt" | "ok" | "aus"
    comfy: "unbekannt",

    // Text aus der Prompt-Leiste
    prompt: "",

    // Seitenverhältnisse mit Grundmaß (hochkant, rund 1 MP); "eigen" nutzt custom.
    formats: [
      { key: "9:16", w: 768, h: 1344 },
      { key: "2:3", w: 832, h: 1216 },
      { key: "4:5", w: 896, h: 1120 },
      { key: "1:1", w: 1024, h: 1024 },
      { key: "eigen", label: "Eigenes" },
    ],
    format: "9:16",
    // Quer statt hoch, je Format, z. B. { "9:16": true } – bei 1:1 und "eigen" ohne Wirkung.
    landscape: {},

    // Größenstufen: der Faktor wirkt auf beide Kanten (0,6 / 1 / 1,6-fache Fläche).
    sizes: [
      { key: "s", label: "Klein", factor: Math.sqrt(0.6) },
      { key: "m", label: "Normal", factor: 1 },
      { key: "l", label: "Groß", factor: Math.sqrt(1.6) },
    ],
    size: "m",

    // Eigene Maße für das Format "eigen"
    custom: { w: 1024, h: 1536 },

    // Seed-Modus: "zufaellig" | "fest"; seed ist der Text aus dem Eingabefeld.
    seedMode: "zufaellig",
    seed: "",

    // Anzahl Bilder je Auftrag
    batch: 1,

    // LoRA-Dateien auf dem Pod (Namen wie von ComfyUI geliefert) und Ladezustand:
    // "neu" | "laedt" | "ok" | "fehler"
    loraFiles: [],
    loraState: "neu",
    // Gewählte LoRAs als { id, name, strength, on }; nextLoraId vergibt die ids
    loras: [],
    nextLoraId: 1,
    // Auswahl-Liste unter „+ LoRA“ offen
    pickerOpen: false,

    // Absenden läuft gerade; Meldung unter dem Knopf mit Art "ok" | "err"
    busy: false,
    message: "",
    messageKind: "",

    // Hält die aktuelle SSE-Verbindung zum Backend oder null (nicht reaktiv nötig)
    eventSource: null,

    // Live-Stand: SSE-Verbindung zu ComfyUI (Ereignis „verbindung“) und Länge der Warteschlange
    live: false,
    queueCount: 0,

    // Angaben je prompt_id, beim Absenden festgehalten (für die Info-Karte)
    jobs: {},

    // Bühne; phase: "leer" | "wartet" | "laedt" | "rechnet" | "fertig" | "fehler"
    stage: { phase: "leer", step: 0, steps: 0, error: "", image: null, promptId: null },

    // Bilder vom Pod und aus der Sitzung, neuestes zuerst: { src, datei, ordner, promptId }
    // promptId null = Bild vom Pod ohne Auftragsangaben
    history: [],
    historyLoading: false,

    init() {
      // Sofort prüfen, danach regelmäßig – der einzige Timer der Oberfläche.
      this.checkHealth();
      this.loadHistory();
      setInterval(() => this.checkHealth(), HEALTH_INTERVAL_MS);

      // Live-Ereignisse vom Backend, nur solange der Tab sichtbar ist oder ein
      // eigener Auftrag läuft (siehe syncEvents).
      this.syncEvents();
      document.addEventListener("visibilitychange", () => {
        this.syncEvents();
        if (!document.hidden) {
          this.checkHealth();
          this.loadHistory();
        }
      });
      window.addEventListener("pagehide", () => {
        if (this.eventSource) this.eventSource.close();
        this.eventSource = null;
      });
    },

    // Öffnet oder schließt die SSE-Verbindung passend zum Soll-Zustand.
    // Chrome erlaubt nur 6 Verbindungen je Adresse; Hintergrund-Tabs ohne
    // laufenden Auftrag geben ihre frei. Beim Wiederverbinden schickt der Hub
    // den letzten Stand sofort. EventSource verbindet sich bei Abbruch selbst
    // neu, deshalb braucht es keinen eigenen Timer.
    syncEvents() {
      const wanted = !document.hidden || this.isRunning;
      if (wanted && !this.eventSource) {
        this.eventSource = new EventSource("/api/events");
        this.eventSource.onmessage = (message) => {
          let event;
          try {
            event = JSON.parse(message.data);
          } catch (error) {
            return;
          }
          this.onEvent(event);
        };
      } else if (!wanted && this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
    },

    // Klick auf die offene Box schließt sie wieder.
    // Box 2 lädt beim Öffnen die LoRA-Liste, solange sie noch nicht da ist.
    toggle(n) {
      this.open = this.open === n ? 0 : n;
      if (this.open === 2 && this.loraState !== "ok") this.loadLoras();
    },

    isOpen(n) {
      return this.open === n;
    },

    get comfyLabel() {
      return COMFY_LABELS[this.comfy];
    },

    get isCustom() {
      return this.format === "eigen";
    },

    // Kanten [Breite, Höhe] eines Formats ohne Größenfaktor – Grundlage für
    // Auflösung und Formvorschau. Jedes Format wird nach seinem eigenen Eintrag gedreht.
    baseDims(f) {
      if (f.key === "eigen") return [snap(this.custom.w), snap(this.custom.h)];
      return this.landscape[f.key] ? [f.h, f.w] : [f.w, f.h];
    },

    // Breite und Höhe des Auftrags – die einzige Stelle, an der sie berechnet werden.
    get dims() {
      const active = this.formats.find((f) => f.key === this.format);
      const factor = this.isCustom ? 1 : this.sizes.find((s) => s.key === this.size).factor;
      return this.baseDims(active).map((edge) => snap(edge * factor));
    },

    get width() {
      return this.dims[0];
    },

    get height() {
      return this.dims[1];
    },

    get megapixels() {
      return (this.width * this.height) / 1e6;
    },

    // z. B. "1,0 MP", über 2 MP mit Warnzusatz
    get mpText() {
      const text = this.megapixels.toFixed(1).replace(".", ",") + " MP";
      return this.megapixels > 2 ? text + " · sehr groß" : text;
    },

    // Beschriftung eines Formats; bei Querformat umgedreht (9:16 → 16:9).
    formatLabel(f) {
      if (f.label) return f.label;
      return this.landscape[f.key] ? f.key.split(":").reverse().join(":") : f.key;
    },

    // Kurzhinweis im Box-Kopf; bei Box 3 live aus dem aktiven Format.
    // Box 2 zählt die gewählten und die eingeschalteten LoRAs.
    hintFor(step) {
      if (step.n === 2) {
        return `${this.loras.length} von ${LORA_MAX} · ${this.activeLoras.length} aktiv`;
      }
      if (step.n !== 3) return step.hint;
      const active = this.formats.find((f) => f.key === this.format);
      return `${this.formatLabel(active)} · ${this.width} × ${this.height}`;
    },

    // Maße der kleinen Formvorschau im Seitenverhältnis des Formats
    shapeStyle(f) {
      const [w, h] = this.baseDims(f);
      const scale = SHAPE_MAX / Math.max(w, h);
      return `width: ${Math.round(w * scale)}px; height: ${Math.round(h * scale)}px`;
    },

    // Wählt das Format aus und dreht es: bei "eigen" die Maße tauschen, bei 1:1 nichts.
    rotate(f) {
      this.format = f.key;
      if (f.key === "eigen") {
        this.custom = { w: this.custom.h, h: this.custom.w };
      } else if (f.key !== "1:1") {
        this.landscape[f.key] = !this.landscape[f.key];
      }
    },

    // Übernimmt die Anzahl beim Verlassen des Feldes: ganze Zahl 1–4, sonst 1.
    setBatch(input) {
      const n = Math.trunc(Number(input.value));
      this.batch = n >= 1 ? Math.min(n, 4) : 1;
      input.value = this.batch;
    },

    // Übernimmt ein eigenes Maß beim Verlassen des Feldes; side ist "w" oder "h".
    setCustom(side, input) {
      this.custom[side] = snap(input.value);
      // Feld zeigt den gerundeten Wert, auch wenn er sich im Zustand nicht geändert hat.
      input.value = this.custom[side];
    },

    // Holt die LoRA-Dateien vom Backend – die einzige Stelle, die die Liste lädt.
    async loadLoras() {
      if (this.loraState === "laedt") return;
      this.loraState = "laedt";
      try {
        const response = await this.apiFetch("/api/loras", { cache: "no-store" });
        const data = await response.json();
        if (!response.ok || !Array.isArray(data.loras)) throw new Error("keine Liste");
        this.loraFiles = data.loras;
        this.loraState = "ok";
      } catch (error) {
        this.loraState = "fehler";
      }
    },

    // Anzeigename einer LoRA: ohne Ordnerpfad und ohne „.safetensors“.
    loraLabel(name) {
      return name.split(/[\\/]/).pop().replace(/\.safetensors$/i, "");
    },

    // Stärke einer LoRA als Text mit Komma („0,80“).
    // Number(): während des Tippens kann das Zahlenfeld kurz leer sein
    strengthText(lora) {
      return (Number(lora.strength) || 0).toFixed(2).replace(".", ",");
    },

    // Dateien, die noch nicht gewählt sind – nur sie bietet die Auswahl an,
    // deshalb kann keine Datei doppelt in loras landen.
    get freeLoraFiles() {
      const used = this.loras.map((lora) => lora.name);
      return this.loraFiles.filter((name) => !used.includes(name));
    },

    // „+ LoRA“ ist nur bedienbar, solange Platz ist und freie Dateien da sind.
    get canAddLora() {
      return this.loras.length < LORA_MAX && this.freeLoraFiles.length > 0;
    },

    // Eingeschaltete LoRAs; nur sie gehen in Auftrag und Zusammenfassung.
    get activeLoras() {
      return this.loras.filter((lora) => lora.on);
    },

    addLora(name) {
      if (this.loras.length >= LORA_MAX || !this.freeLoraFiles.includes(name)) return;
      this.loras.push({ id: this.nextLoraId++, name, strength: LORA_STRENGTH_DEFAULT, on: true });
      this.pickerOpen = false;
    },

    removeLora(id) {
      this.loras = this.loras.filter((lora) => lora.id !== id);
    },

    toggleLora(id) {
      const lora = this.loras.find((entry) => entry.id === id);
      if (lora) lora.on = !lora.on;
    },

    // Übernimmt die Stärke beim Verlassen des Zahlenfeldes: −2 bis 2,
    // auf 0.05 gerundet, ungültig → 0.8.
    setStrength(lora, input) {
      const value = parseFloat(input.value);
      lora.strength = Number.isFinite(value)
        ? Math.round(Math.min(2, Math.max(-2, value)) * 20) / 20
        : LORA_STRENGTH_DEFAULT;
      input.value = lora.strength;
    },

    // Zusammenfassung einer Box als Liste { k, v } für die geschlossene Ansicht.
    // Die festen Werte von 1, 4 und 5 entsprechen den heutigen Backend-Standards
    // und werden in späteren Schritten live.
    summary(n) {
      switch (n) {
        case 1:
          return [{ k: "Modell", v: "FLUX.1 [dev]" }];
        case 2:
          if (!this.activeLoras.length) return [{ k: "LoRAs", v: "keine" }];
          return this.activeLoras.map((lora) => ({
            k: this.loraLabel(lora.name),
            v: this.strengthText(lora),
          }));
        case 3:
          return [
            { k: "Format", v: this.formatLabel(this.formats.find((f) => f.key === this.format)) },
            { k: "Auflösung", v: `${this.width} × ${this.height}` },
            { k: "Megapixel", v: this.mpText },
            { k: "Seed", v: this.seedMode === "fest" && this.seed.trim() ? this.seed.trim() : "zufällig" },
            { k: "Anzahl", v: String(this.batch) },
          ];
        case 4:
          return [{ k: "Schritte", v: "25" }, { k: "Guidance", v: "3.5" }];
        case 5:
          return [{ k: "Ablage", v: "Monatsordner" }, { k: "Ziel", v: "Google Drive" }];
        default:
          return [];
      }
    },

    // Setzt die Meldung unter dem Generieren-Knopf; kind ist "ok" oder "err".
    say(text, kind) {
      this.message = text;
      this.messageKind = kind;
    },

    // Schickt Prompt und Format als Auftrag ans Backend.
    async generate() {
      if (this.busy || !this.prompt.trim()) return;

      let seed = null;
      if (this.seedMode === "fest") {
        const text = this.seed.trim();
        if (!/^\d+$/.test(text) || BigInt(text) > BigInt(SEED_MAX)) {
          this.say("Seed: nur Ziffern, höchstens " + SEED_MAX, "err");
          return;
        }
        // Als Text schicken, damit nichts über 2^53 ungenau wird
        seed = text;
      }

      // Angaben für die Info-Karte als Kopie festhalten, damit spätere
      // Änderungen an den Reglern sie nicht verfälschen.
      const job = {
        width: this.width,
        height: this.height,
        format: this.formatLabel(this.formats.find((f) => f.key === this.format)),
        loras: this.activeLoras.map((lora) => this.loraLabel(lora.name) + " · " + this.strengthText(lora)),
        batch: this.batch,
        prompt: this.prompt,
      };

      this.busy = true;
      try {
        const response = await this.apiFetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: this.prompt,
            seed,
            width: this.width,
            height: this.height,
            batch_size: this.batch,
            loras: this.activeLoras.map((lora) => ({ name: lora.name, strength: lora.strength })),
          }),
        });
        // Antwort ohne JSON (z. B. Serverfehler) wie eine leere Antwort behandeln
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
          this.seed = String(data.seed);
          this.say("Auftrag angenommen · Seed " + this.seed, "ok");
          this.jobs[data.prompt_id] = { ...job, seed: this.seed };
          // Kam schon ein Ereignis zu diesem Auftrag (SSE war schneller als
          // die Antwort), bleibt dessen Stand stehen. Ein Bild bleibt sichtbar.
          if (this.stage.promptId !== data.prompt_id) {
            this.stage = {
              ...this.stage,
              phase: "wartet",
              step: 0,
              steps: 0,
              error: "",
              promptId: data.prompt_id,
            };
          }
          this.syncEvents();
        } else if (data.fehler) {
          this.say(data.fehler, "err");
        } else if (data.detail) {
          this.say("Eingaben ungültig", "err");
        } else {
          this.say("Fehler " + response.status, "err");
        }
      } catch (error) {
        this.say("Dashboard nicht erreichbar", "err");
      } finally {
        this.busy = false;
      }
    },

    // Verarbeitet alle Live-Ereignisse vom Backend. Ereignisse zu unbekannten
    // prompt_ids (z. B. aus einem anderen Tab) werden genauso angezeigt, nur
    // fehlen dann die Angaben in der Info-Karte.
    onEvent(event) {
      const stage = this.stage;
      switch (event.typ) {
        case "verbindung":
          this.live = event.ok === true;
          break;
        case "warteschlange":
          this.queueCount = event.anzahl ?? 0;
          break;
        case "start":
          stage.phase = "laedt";
          stage.promptId = event.prompt_id;
          stage.step = 0;
          stage.steps = 0;
          stage.error = "";
          break;
        case "fortschritt":
          stage.phase = "rechnet";
          stage.promptId = event.prompt_id;
          stage.step = event.schritt ?? 0;
          stage.steps = event.von ?? 0;
          break;
        case "fertig": {
          const entries = (event.bilder || [])
            .filter((bild) => bild && bild.datei)
            .map((bild) => ({
              src: this.imageUrl(bild),
              datei: bild.datei,
              ordner: bild.ordner || "",
              promptId: event.prompt_id,
            }));
          // Neueste zuerst; ältere fallen hinten raus
          this.mergeHistory([...entries, ...this.history]);
          stage.promptId = event.prompt_id;
          if (entries.length) {
            this.showImage(entries[0]);
          } else {
            // Auftrag ohne Bild: ein altes Bild bleibt stehen, sonst leere Bühne
            stage.phase = stage.image ? "fertig" : "leer";
          }
          // Im Hintergrund-Tab jetzt die Verbindung freigeben
          this.syncEvents();
          break;
        }
        case "fehler":
          stage.phase = "fehler";
          stage.promptId = event.prompt_id;
          stage.error = event.meldung || "Unbekannter Fehler";
          this.syncEvents();
          break;
      }
    },

    // Adresse eines fertigen Bildes – die einzige Stelle, die sie baut.
    imageUrl(bild) {
      return (
        "/api/bild?ordner=" + encodeURIComponent(bild.ordner || "") +
        "&datei=" + encodeURIComponent(bild.datei)
      );
    },

    // Setzt den Verlauf – die einzige Stelle, die `history` schreibt:
    // entdoppelt nach src (erster Eintrag gewinnt), kürzt auf HISTORY_MAX.
    mergeHistory(entries) {
      const seen = new Set();
      this.history = entries
        .filter((entry) => !seen.has(entry.src) && seen.add(entry.src))
        .slice(0, HISTORY_MAX);
    },

    // Holt den Verlauf vom Pod und führt ihn mit dem bekannten zusammen.
    // Bei Fehlern bleibt der bisherige Verlauf still stehen.
    async loadHistory() {
      if (this.historyLoading) return;
      this.historyLoading = true;
      try {
        const response = await this.apiFetch("/api/verlauf", { cache: "no-store" });
        if (!response.ok) return;
        const data = await response.json();
        if (!data || !Array.isArray(data.bilder)) return;
        const podEntries = data.bilder
          .filter((bild) => bild && bild.datei)
          .map((bild) => ({
            src: this.imageUrl(bild),
            datei: bild.datei,
            ordner: bild.ordner || "",
            promptId: null,
          }));
        const podSrcs = new Set(podEntries.map((entry) => entry.src));
        const known = new Map(this.history.map((entry) => [entry.src, entry]));
        // Was nur die Sitzung kennt, ist neuer und kommt nach vorn
        const newer = this.history.filter((entry) => !podSrcs.has(entry.src));
        const fromPod = podEntries.map((entry) => known.get(entry.src) || entry);
        this.mergeHistory([...newer, ...fromPod]);
        if (!this.stage.image && !this.isRunning && this.history.length) {
          this.showImage(this.history[0]);
        }
      } catch (err) {
        // Netzfehler o. Ä.: Verlauf unverändert lassen, keine Meldung
      } finally {
        this.historyLoading = false;
      }
    },

    // Holt ein Bild aus dem Verlauf auf die Bühne.
    showImage(entry) {
      this.stage.image = entry;
      this.stage.phase = "fertig";
      this.stage.error = "";
    },

    // Läuft gerade ein Auftrag (wartend, ladend oder rechnend)?
    get isRunning() {
      return ["wartet", "laedt", "rechnet"].includes(this.stage.phase);
    },

    // Anteil des Fortschritts von 0 bis 1; null = unbestimmt (wartet, lädt).
    get progress() {
      const { phase, step, steps } = this.stage;
      if (phase !== "rechnet" || !(steps > 0)) return null;
      return Math.min(1, Math.max(0, step / steps));
    },

    // Zeilen { k, v } der Info-Karte zum Bild auf der Bühne.
    // Fehlen Angaben zum Auftrag (fremder Tab), steht dort nur die Datei.
    get stageInfo() {
      const image = this.stage.image;
      if (!image) return [];
      const job = this.jobs[image.promptId];
      const rows = job
        ? [
            { k: "Seed", v: job.seed },
            { k: "Auflösung", v: `${job.width} × ${job.height}` },
            { k: "Format", v: job.format },
            // Mehrere LoRAs untereinander (Zeilenumbruch, im CSS pre-line)
            { k: "LoRAs", v: job.loras.length ? job.loras.join("\n") : "keine" },
          ]
        : [];
      rows.push({ k: "Datei", v: image.datei });
      return rows;
    },

    // Statuszeile der Bühne.
    get stageText() {
      switch (this.stage.phase) {
        case "wartet":
          return this.queueCount > 1
            ? `In der Warteschlange · noch ${this.queueCount - 1} vor dir`
            : "In der Warteschlange";
        case "laedt":
          return "Modell wird geladen …";
        case "rechnet":
          return `Schritt ${this.stage.step} / ${this.stage.steps}`;
        case "fertig":
          return "Fertig";
        case "fehler":
          return this.stage.error;
        default:
          return "";
      }
    },

    // Einziger Weg für alle fetch-Aufrufe der Oberfläche: ohne gültige
    // Anmeldung (401) geht es zur Login-Seite.
    async apiFetch(url, options) {
      const response = await fetch(url, options);
      if (response.status === 401) {
        location.href = "/login.html";
        throw new Error("nicht angemeldet");
      }
      return response;
    },

    // Fragt das Backend, ob ComfyUI erreichbar ist.
    async checkHealth() {
      try {
        const response = await this.apiFetch("/api/health", { cache: "no-store" });
        const data = await response.json();
        this.comfy = response.ok && data.comfyui === true ? "ok" : "aus";
      } catch (error) {
        this.comfy = "aus";
      }
    },
  }));
});
