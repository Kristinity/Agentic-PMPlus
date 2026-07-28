/**
 * step7-active-learning/frontend/kalibrierung.js
 *
 * TICKET-F06 (step8-live-test/Produkt-Backlog/TICKET-F06-Kalibrierungs-Gesundheit.md):
 * eigene, separate Seite fuer die Person, die Step 6/7 (tau/sigma-Kalibrierung,
 * Active Learning Loop) betreut - NICHT fuer Jens Pirinski (Produktionsplaner). Zeigt
 * GET /kalibrierung: aktuelle tau0/sigma0-Schwellenwerte, Eskalationsrate ueber Zeit
 * und Anteil "truegerische Ruhe"-Faelle - alles aus tatsaechlich gelaufenen
 * Kalibrierungslaeufen (step6-calibration/main.py:append_kalibrierung_verlauf), keine
 * synthetische Zeitreihe.
 *
 * Design-Entscheidung (AC "Separate Ansicht/Rolle, nicht im Hauptbildschirm fuer
 * Jens", Active-Learning-Loop-und-Frontend-Konzept.md 2.3.5): index.html/verlauf.html
 * verlinken NICHT hierher - nur umgekehrt (diese Seite verlinkt zurueck zur
 * Warteschlange). Erreichbar ueber die direkte URL, dokumentiert in README.md.
 *
 * Struktur/Stil bewusst analog zu verlauf.js (TICKET-F05) uebernommen, siehe dort
 * fuer die ausfuehrlichere Begruendung der Konventionen (Datenzugriff/Rendering-
 * Trennung, escapeHtml ueberall, Fail-safe-Fehlerbehandlung, API_BASE per
 * URL-Parameter ueberschreibbar).
 *
 * Design-Leitplanken aus .claude/agents/role/frontend-dev.md (nicht verhandelbar):
 *   1. PGP/LLM-Verschmelzung: nicht anwendbar - diese Seite zeigt Kalibrierungs-
 *      Metadaten (tau0/sigma0/Eskalationsrate), keine Einzelfall-Einschaetzungen.
 *   2. Vorschlag != Ausfuehrung: nicht anwendbar - reine Leseansicht ohne jeden
 *      Aktions-Button.
 *   5. Fail-safe statt fail-open: jeder Fehlerfall (Netzwerk, HTTP-Fehler,
 *      unerwartete Response-Form, Backend-Hinweis "Step 6 noch nicht gelaufen")
 *      blockiert sichtbar mit einer Fehler-/Hinweisbox statt eine leere oder alte
 *      Historie stillschweigend als aktuell auszugeben (renderError/renderHinweis,
 *      nie renderKalibrierung mit unvollstaendigen Daten).
 *
 * Kein Build-Schritt, kein Framework - siehe README.md.
 */

(function () {
  "use strict";

  // Gleicher Default wie app.js/verlauf.js - passt zum docker-compose-Port-Mapping
  // "8007:8000". Ueberschreibbar ohne Code-Aenderung, z. B.
  // kalibrierung.html?api=http://andere-adresse:8007.
  const DEFAULT_API_BASE = "http://localhost:8007";

  function resolveApiBase() {
    const params = new URLSearchParams(window.location.search);
    return params.get("api") || window.PMPLUS_API_BASE || DEFAULT_API_BASE;
  }

  const API_BASE = resolveApiBase();

  // --- Datenzugriff ----------------------------------------------------------

  async function fetchKalibrierung() {
    let response;
    try {
      response = await fetch(`${API_BASE}/kalibrierung`);
    } catch (networkError) {
      throw new FetchFailure(
        "Die Kalibrierungsdaten konnten nicht geladen werden (Netzwerkfehler). " +
          "Es wird bewusst KEINE alte oder leere Historie angezeigt.",
        networkError
      );
    }
    if (!response.ok) {
      throw new FetchFailure(
        `Backend antwortete mit Status ${response.status}. ` +
          "Es wird bewusst KEINE alte oder leere Historie angezeigt.",
        null
      );
    }
    let data;
    try {
      data = await response.json();
    } catch (parseError) {
      throw new FetchFailure(
        "Antwort des Backends war kein gueltiges JSON.",
        parseError
      );
    }
    if (!data || !Array.isArray(data.verlauf)) {
      throw new FetchFailure(
        "Antwort des Backends hatte nicht die erwartete Form " +
          '(Feld "verlauf" fehlt oder ist keine Liste).',
        null
      );
    }
    // GET /kalibrierung liefert {verlauf: [], aktuell: null, hinweis: "..."}, wenn
    // die Verlaufs-CSV (noch) nicht existiert (Step 6 noch nie mit dem
    // F06-Patch gelaufen) - kein "0 Laeufe bisher", sondern "Daten nicht bereit".
    if (data.verlauf.length === 0 && data.hinweis) {
      throw new BackendNotReady(data.hinweis);
    }
    return data;
  }

  class FetchFailure extends Error {
    constructor(message, cause) {
      super(message);
      this.name = "FetchFailure";
      this.cause = cause;
    }
  }

  class BackendNotReady extends Error {
    constructor(hinweis) {
      super(hinweis);
      this.name = "BackendNotReady";
    }
  }

  // --- Sortierung --------------------------------------------------------
  // Aelteste zuerst in der Tabelle (chronologischer Verlauf, wie ein Zeitreihen-
  // Chart gelesen wuerde) - die API liefert bereits ASC nach zeitstempel sortiert
  // (api.py: verlauf.sort(...)), hier trotzdem defensiv erneut sortiert (gleiches
  // Muster wie sortByPgpRank in app.js / sortByZeitstempelDesc in verlauf.js).
  function sortByZeitstempelAsc(verlauf) {
    return [...verlauf].sort((a, b) =>
      String(a.zeitstempel).localeCompare(String(b.zeitstempel))
    );
  }

  // --- Rendering -----------------------------------------------------------

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value == null ? "" : String(value);
    return div.innerHTML;
  }

  function formatZeitstempel(iso) {
    if (!iso) return "(kein Zeitstempel)";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) {
      return `${iso} (Format nicht erkannt)`;
    }
    return date.toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" });
  }

  function formatNumber(value, digits) {
    if (value == null || Number.isNaN(value)) return "–";
    return Number(value).toFixed(digits);
  }

  function formatPercent(value) {
    if (value == null || Number.isNaN(value)) return "–";
    return `${(Number(value) * 100).toFixed(1)} %`;
  }

  function renderAktuell(aktuell) {
    const section = document.getElementById("aktuell-section");
    if (!aktuell) {
      section.hidden = true;
      return;
    }
    section.hidden = false;
    section.innerHTML = `
      <h2>Aktueller Stand</h2>
      <p class="kalibrierung-aktuell-zeitpunkt">
        Letzter Kalibrierungslauf: ${escapeHtml(formatZeitstempel(aktuell.zeitstempel))}
        (${escapeHtml(aktuell.n_auftraege)} offene Aufträge)
      </p>
      <div class="kalibrierung-metrics">
        <div class="kalibrierung-metric">
          <span class="kalibrierung-metric-label">τ₀ (Schwellenwert)</span>
          <span class="kalibrierung-metric-value">${escapeHtml(formatNumber(aktuell.tau0, 3))}</span>
        </div>
        <div class="kalibrierung-metric">
          <span class="kalibrierung-metric-label">σ₀ (Schwellenwert)</span>
          <span class="kalibrierung-metric-value">${escapeHtml(formatNumber(aktuell.sigma0, 3))}</span>
        </div>
        <div class="kalibrierung-metric">
          <span class="kalibrierung-metric-label">Eskalationsrate</span>
          <span class="kalibrierung-metric-value">${escapeHtml(formatPercent(aktuell.eskalationsrate))}</span>
          <span class="kalibrierung-metric-explain">
            Ziel laut Konfiguration: ${escapeHtml(formatPercent(aktuell.target_escalation_rate))}
          </span>
        </div>
        <div class="kalibrierung-metric">
          <span class="kalibrierung-metric-label">Anteil „Trügerische Ruhe“</span>
          <span class="kalibrierung-metric-value">${escapeHtml(formatPercent(aktuell.truegerische_ruhe_anteil))}</span>
          <span class="kalibrierung-metric-explain">
            PGP und LLM einig, PGP sich selbst aber unsicher (σ &gt; σ₀).
          </span>
        </div>
      </div>
    `;
  }

  function renderVerlaufRow(eintrag) {
    return `
      <tr>
        <td>${escapeHtml(formatZeitstempel(eintrag.zeitstempel))}</td>
        <td>${escapeHtml(formatNumber(eintrag.tau0, 3))}</td>
        <td>${escapeHtml(formatNumber(eintrag.sigma0, 3))}</td>
        <td>${escapeHtml(eintrag.n_auftraege)}</td>
        <td>${escapeHtml(formatPercent(eintrag.eskalationsrate))}</td>
        <td>${escapeHtml(formatPercent(eintrag.truegerische_ruhe_anteil))}</td>
      </tr>
    `;
  }

  function renderVerlauf(verlauf) {
    const section = document.getElementById("verlauf-section");
    const tbody = document.getElementById("kalibrierung-tbody");
    tbody.innerHTML = sortByZeitstempelAsc(verlauf).map(renderVerlaufRow).join("");
    section.hidden = false;
  }

  function showStatus(html) {
    document.getElementById("status-region").innerHTML = html;
  }

  function clearStatus() {
    document.getElementById("status-region").innerHTML = "";
  }

  function hideContent() {
    document.getElementById("aktuell-section").hidden = true;
    document.getElementById("verlauf-section").hidden = true;
  }

  function renderLoading() {
    hideContent();
    showStatus('<p class="loading">Kalibrierungsdaten werden geladen …</p>');
  }

  function renderError(err) {
    hideContent();
    showStatus(`
      <div class="error-box" role="alert">
        <h2>Kalibrierungsdaten konnten nicht angezeigt werden</h2>
        <p>${escapeHtml(err.message)}</p>
        <button id="retry-btn" type="button">Erneut versuchen</button>
      </div>
    `);
    document.getElementById("retry-btn").addEventListener("click", load);
  }

  function renderHinweis(hinweis) {
    hideContent();
    showStatus(`
      <div class="hinweis-box" role="status">
        <h2>Kalibrierungsdaten noch nicht verfügbar</h2>
        <p>${escapeHtml(hinweis)}</p>
        <p>Das bedeutet nicht, dass keine Kalibrierung stattgefunden hat – nur dass
        noch kein Lauf mit dieser Verlaufs-CSV protokolliert wurde.</p>
        <button id="retry-btn" type="button">Erneut versuchen</button>
      </div>
    `);
    document.getElementById("retry-btn").addEventListener("click", load);
  }

  // --- Orchestrierung --------------------------------------------------------

  async function load() {
    renderLoading();
    try {
      const data = await fetchKalibrierung();
      clearStatus();
      renderAktuell(data.aktuell);
      renderVerlauf(data.verlauf);
    } catch (err) {
      if (err instanceof BackendNotReady) {
        renderHinweis(err.message);
      } else {
        renderError(err);
      }
    }
  }

  function init() {
    document.getElementById("reload-btn").addEventListener("click", load);
    load();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Fuer eine Logik-Verifikation ohne Browser exportiert (siehe frontend/README.md,
  // Abschnitt "Was getestet wurde") - im Browser ungenutzt.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      formatZeitstempel,
      formatNumber,
      formatPercent,
      sortByZeitstempelAsc,
      renderAktuell,
      renderVerlaufRow,
      FetchFailure,
      BackendNotReady,
    };
  }
})();
