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

  Alpine.data("dreamdeck", () => ({
    // Nummer der offenen Box, 0 = alle zu.
    // Später übernimmt ein Klick-Tutorial das Aufklappen.
    open: 0,

    // Die fünf Pipeline-Boxen; alle entstehen aus dieser Liste und einer Vorlage.
    steps: [
      { n: 1, code: "DD//01·MDL", title: "Modelle", hint: "FLUX.1 [dev]", later: "Auswahl folgt später" },
      { n: 2, code: "DD//02·LRA", title: "LoRAs", hint: "bis zu 6 gleichzeitig", later: "folgt in 2h" },
      { n: 3, code: "DD//03·FMT", title: "Format", hint: "9:16 · 768 × 1344", later: "folgt in 2g" },
      { n: 4, code: "DD//04·TUN", title: "Feintuning", hint: "25 Schritte · Guidance 3.5", later: "folgt später" },
      { n: 5, code: "DD//05·OUT", title: "Speichern", hint: "Monatsordner · Drive", later: "folgt später" },
    ],

    // Zustand von ComfyUI: "unbekannt" | "ok" | "aus"
    comfy: "unbekannt",

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
