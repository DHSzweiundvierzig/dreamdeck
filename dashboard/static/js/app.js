// DreamDeck – Oberfläche (klassisches Script, wird vor Alpine geladen).
// Registriert die Komponente "dreamdeck", sobald Alpine startet.

document.addEventListener("alpine:init", () => {
  // Abstand der Statusabfrage in Millisekunden
  const HEALTH_INTERVAL_MS = 30000;

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
  // Höchster erlaubter Seed (2^32 − 1)
  const SEED_MAX = 4294967295;

  // Rundet auf 16 und begrenzt auf 256–2048. Ungültige Eingaben ergeben 256.
  function snap(v) {
    const rounded = Math.round((Number(v) || 0) / DIM_STEP) * DIM_STEP;
    return Math.min(DIM_MAX, Math.max(DIM_MIN, rounded));
  }

  Alpine.data("dreamdeck", () => ({
    // Nummer der offenen Box, 0 = alle zu.
    // Später übernimmt ein Klick-Tutorial das Aufklappen.
    open: 0,

    // Die fünf Pipeline-Boxen; alle entstehen aus dieser Liste und einer Vorlage.
    steps: [
      { n: 1, code: "DD//01·MDL", title: "Modelle", hint: "FLUX.1 [dev]", later: "Auswahl folgt später" },
      { n: 2, code: "DD//02·LRA", title: "LoRAs", hint: "bis zu 6 gleichzeitig", later: "folgt in 2h" },
      { n: 3, code: "DD//03·FMT", title: "Format", hint: "9:16 · 768 × 1344" },
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
    // Quer statt hoch – gilt für das aktive Format, bei 1:1 ohne Wirkung.
    landscape: false,

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

    // Absenden läuft gerade; Meldung unter dem Knopf mit Art "ok" | "err"
    busy: false,
    message: "",
    messageKind: "",

    init() {
      // Sofort prüfen, danach regelmäßig – der einzige Timer der Oberfläche.
      this.checkHealth();
      setInterval(() => this.checkHealth(), HEALTH_INTERVAL_MS);
    },

    // Klick auf die offene Box schließt sie wieder.
    toggle(n) {
      this.open = this.open === n ? 0 : n;
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
    // Auflösung und Formvorschau. Gedreht wird nur das aktive Format.
    baseDims(f) {
      if (f.key === "eigen") return [snap(this.custom.w), snap(this.custom.h)];
      return this.landscape && f.key === this.format ? [f.h, f.w] : [f.w, f.h];
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

    // Beschriftung eines Formats; das aktive wird bei Querformat umgedreht (9:16 → 16:9).
    formatLabel(f) {
      if (f.label) return f.label;
      const parts = f.key.split(":");
      return this.landscape && f.key === this.format ? parts.reverse().join(":") : f.key;
    },

    // Maße der kleinen Formvorschau im Seitenverhältnis des Formats
    shapeStyle(f) {
      const [w, h] = this.baseDims(f);
      const scale = SHAPE_MAX / Math.max(w, h);
      return `width: ${Math.round(w * scale)}px; height: ${Math.round(h * scale)}px`;
    },

    // Hoch/Quer wechseln: bei "eigen" die Maße tauschen, sonst Querformat umschalten.
    rotate() {
      if (this.isCustom) {
        this.custom = { w: this.custom.h, h: this.custom.w };
      } else {
        this.landscape = !this.landscape;
      }
    },

    // Übernimmt ein eigenes Maß beim Verlassen des Feldes; side ist "w" oder "h".
    setCustom(side, input) {
      this.custom[side] = snap(input.value);
      // Feld zeigt den gerundeten Wert, auch wenn er sich im Zustand nicht geändert hat.
      input.value = this.custom[side];
    },

    // Zusammenfassung einer Box als Liste { k, v } für die geschlossene Ansicht.
    // Die festen Werte von 1, 2, 4 und 5 entsprechen den heutigen Backend-Standards
    // und werden in späteren Schritten live.
    summary(n) {
      switch (n) {
        case 1:
          return [{ k: "Modell", v: "FLUX.1 [dev]" }];
        case 2:
          return [{ k: "LoRAs", v: "keine" }];
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
        seed = /^\d+$/.test(text) ? Number(text) : NaN;
        if (!(seed <= SEED_MAX)) {
          this.say("Seed muss eine ganze Zahl sein", "err");
          return;
        }
      }

      this.busy = true;
      try {
        const response = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: this.prompt,
            seed,
            width: this.width,
            height: this.height,
            batch_size: this.batch,
          }),
        });
        // Antwort ohne JSON (z. B. Serverfehler) wie eine leere Antwort behandeln
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
          this.seed = String(data.seed);
          this.say("Auftrag angenommen · Seed " + this.seed, "ok");
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

    // Fragt das Backend, ob ComfyUI erreichbar ist.
    async checkHealth() {
      try {
        const response = await fetch("/api/health", { cache: "no-store" });
        const data = await response.json();
        this.comfy = response.ok && data.comfyui === true ? "ok" : "aus";
      } catch (error) {
        this.comfy = "aus";
      }
    },
  }));
});
