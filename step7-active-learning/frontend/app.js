/**
 * step7-active-learning/frontend/app.js
 *
 * TICKET-F01 (step8-live-test/Produkt-Backlog/TICKET-F01-Warteschlange.md):
 * Auftrags-Warteschlange - Startbildschirm fuer Jens Pirinski (Produktionsplaner,
 * Krasser Spass GmbH, KEIN Data Scientist). Liest GET /eskalationen und zeigt die
 * Liste sortiert nach pgp.rank mit Ampel-Status.
 *
 * Design-Leitplanken aus .claude/agents/role/frontend-dev.md (nicht verhandelbar,
 * hier konkret umgesetzt):
 *   1. PGP und LLM werden IMMER als zwei getrennte Objekte/UI-Bloecke gerendert
 *      (renderAssessmentBox aufgerufen fuer "pgp" und "llm" separat) - nirgends
 *      wird ein gemeinsamer/gemittelter Score gebildet.
 *   2. Diese Seite hat KEINEN Button, der eine echte Aktion ausloest (kein
 *      "Entscheiden"/"Bestaetigen") - das ist bewusst F03s Aufgabe. Vorschlag/
 *      Ausfuehrung-Trennung ist hier trivial erfuellt: es gibt nichts auszufuehren.
 *   3. Provenienz-Erzwingung betrifft F03 (Entscheidungserfassung), nicht diese
 *      reine Leseansicht - hier nicht anwendbar.
 *   4. matched_rag_docs/Vertrauensstufe wird auf DIESEM Screen bewusst NICHT
 *      angezeigt (siehe README.md in diesem Ordner, Abschnitt "Scope-Entscheidung")
 *      - gehoert inhaltlich zu F02 (Eskalations-Review), wo die volle
 *      LLM-Begruendung im Kontext der RAG-Treffer geprueft wird.
 *   5. Fail-safe statt fail-open: jeder Fehlerfall (Netzwerk, HTTP-Fehler,
 *      unerwartete Response-Form, Backend-Hinweis "Step 6 noch nicht gelaufen")
 *      blockiert sichtbar mit einer Fehler-/Hinweisbox statt eine leere oder
 *      alte Liste stillschweigend als aktuell auszugeben (siehe renderError/
 *      renderHinweis, nie renderQueue mit unvollstaendigen Daten).
 *
 * Kein Build-Schritt, kein Framework - siehe README.md fuer die Stack-Begruendung.
 */

(function () {
  "use strict";

  // Default passt zum docker-compose-Port-Mapping "8007:8000" (siehe
  // docker-compose.yml). Ueberschreibbar ohne Code-Aenderung, z. B. beim
  // Aufruf der Seite als index.html?api=http://andere-adresse:8007 - nuetzlich,
  // weil dieses Frontend (statisches HTML) nicht zwingend vom selben Origin wie
  // die API ausgeliefert wird.
  const DEFAULT_API_BASE = "http://localhost:8007";

  function resolveApiBase() {
    const params = new URLSearchParams(window.location.search);
    return params.get("api") || window.PMPLUS_API_BASE || DEFAULT_API_BASE;
  }

  const API_BASE = resolveApiBase();

  // --- Ampel-Sprache -------------------------------------------------------
  // Wortlaut EXAKT aus Konzept-README.md (2x2-Matrix, "zentrale Idee") und
  // step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md 2.3.1
  // uebernommen - nicht neu formuliert (TICKET-F01-Akzeptanzkriterium).
  // "unbekannt" ist KEIN Teil der urspruenglichen Matrix, sondern der in
  // api.py dokumentierte Fail-safe-Fallback (fehlende Kalibrierung) - eigener,
  // klar erkennbarer vierter Zustand, NIE als gruen/robust interpretiert.
  const AMPEL = {
    robuste_uebereinstimmung: {
      icon: "\u{1F7E2}", // 🟢
      symbol: "✓", // ✓ - zusaetzlich zur Farbe, fuer Farbfehlsichtigkeit
      label: "Robuste Übereinstimmung",
      explain:
        "PGP und LLM sind sich einig, und der PGP ist sich seiner Einschätzung " +
        "selbst sicher – läuft automatisch weiter, nur informativ sichtbar.",
    },
    truegerische_ruhe: {
      icon: "\u{1F7E1}", // 🟡
      symbol: "!",
      label: "Trügerische Ruhe",
      explain:
        "PGP und LLM sind sich zwar einig – aber der PGP ist sich bei genau " +
        "diesem Auftrag selbst nicht sicher. Die Einigkeit kann eine Sicherheit " +
        "vortäuschen, die nicht existiert. Trotz Einigkeit prüfen.",
    },
    klarer_fall_fuer_review: {
      icon: "\u{1F534}", // 🔴
      symbol: "\u{1F50E}", // 🔎
      label: "Klarer Fall für Experten-Review",
      explain:
        "PGP und LLM widersprechen sich in der Priorisierung – unabhängig " +
        "davon, wie sicher sich der PGP ist. Braucht eine Entscheidung.",
    },
    unbekannt: {
      icon: "⚪", // ⚪
      symbol: "?",
      label: "Status unbekannt",
      explain:
        "Die τ/σ-Kalibrierung für diesen Fall liegt (noch) nicht vor. " +
        "Das ist KEIN grünes Licht – solange kein belastbarer Ampel-Status " +
        "berechnet werden konnte, gilt dieser Auftrag als ungeprüft.",
    },
  };

  // Fail-safe: jeder ampel_status-Wert, der nicht einer der vier bekannten
  // Strings ist (z. B. weil eine zukuenftige Backend-Version neue Werte
  // einfuehrt, oder ein Tippfehler in den Daten), wird WIE "unbekannt"
  // behandelt statt das Rendering brechen zu lassen oder - schlimmer -
  // versehentlich auf robuste_uebereinstimmung zurueckzufallen.
  function ampelMeta(status) {
    return AMPEL[status] || AMPEL.unbekannt;
  }

  // --- Datenzugriff ----------------------------------------------------------

  async function fetchEskalationen() {
    let response;
    try {
      response = await fetch(`${API_BASE}/eskalationen`);
    } catch (networkError) {
      throw new FetchFailure(
        "Die Warteschlange konnte nicht geladen werden (Netzwerkfehler). " +
          "Es wird bewusst KEINE alte oder leere Liste angezeigt.",
        networkError
      );
    }
    if (!response.ok) {
      throw new FetchFailure(
        `Backend antwortete mit Status ${response.status}. ` +
          "Es wird bewusst KEINE alte oder leere Liste angezeigt.",
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
    if (!data || !Array.isArray(data.eskalationen)) {
      throw new FetchFailure(
        "Antwort des Backends hatte nicht die erwartete Form " +
          '(Feld "eskalationen" fehlt oder ist keine Liste).',
        null
      );
    }
    // GET /eskalationen liefert {eskalationen: [], hinweis: "..."}, wenn
    // tau_vergleich.csv (noch) nicht existiert (siehe api.py) - das ist kein
    // "0 offene Auftraege, alles erledigt", sondern "Backend-Daten nicht
    // bereit". Muss getrennt von einer echten leeren Warteschlange behandelt
        // werden, sonst taeuscht die UI Ruhe vor, die nicht existiert.
    if (data.eskalationen.length === 0 && data.hinweis) {
      throw new BackendNotReady(data.hinweis);
    }
    return data.eskalationen;
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

  // --- Sortierung/Filter -------------------------------------------------
  // AC: "Liste aus GET /eskalationen, sortiert nach PGP-Rang." Die API
  // sortiert bereits serverseitig (api.py: eskalationen.sort(...)) - hier
  // trotzdem defensiv erneut sortiert, damit die UI nicht blind auf eine
  // Server-Eigenschaft vertraut, die sich unbemerkt aendern koennte.
  function sortByPgpRank(eskalationen) {
    return [...eskalationen].sort((a, b) => a.pgp.rank - b.pgp.rank);
  }

  const ATTENTION_STATES = new Set([
    "truegerische_ruhe",
    "klarer_fall_fuer_review",
    "unbekannt",
  ]);

  function filterAttention(eskalationen, onlyAttention) {
    if (!onlyAttention) return eskalationen;
    return eskalationen.filter((e) => ATTENTION_STATES.has(e.ampel_status));
  }

  // --- Rendering -----------------------------------------------------------

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value == null ? "" : String(value);
    return div.innerHTML;
  }

  function formatNumber(value, digits) {
    if (value == null || Number.isNaN(value)) return "–";
    return value.toFixed(digits);
  }

  function renderAssessmentBox({ kind, title, rankLabel, rank, rawLabel, rawValue, rawDigits, rawExplain, begruendung }) {
    return `
      <div class="assessment-box ${kind}">
        <h3>${escapeHtml(title)}</h3>
        <p class="assessment-value">
          ${escapeHtml(rankLabel)}: <span class="raw">#${escapeHtml(rank)}</span>
        </p>
        <p class="assessment-value">
          <span class="raw">${escapeHtml(rawLabel)} = ${escapeHtml(formatNumber(rawValue, rawDigits))}</span>
          <span class="explain"> – ${escapeHtml(rawExplain)}</span>
        </p>
        <div class="assessment-begruendung">
          <span class="label">Begründung</span>
          ${escapeHtml(begruendung || "(keine Begründung übermittelt)")}
        </div>
      </div>
    `;
  }

  function renderOrderCard(order, index) {
    const meta = ampelMeta(order.ampel_status);
    const cardId = `order-details-${index}`;

    // Leitplanke 1 (nicht verhandelbar): pgp und llm werden hier als zwei
    // separate Aufrufe von renderAssessmentBox mit eigenem DOM-Block gerendert
    // - es gibt an keiner Stelle eine gemeinsame/gemittelte Zahl.
    const pgpBox = renderAssessmentBox({
      kind: "pgp",
      title: "Preference GP – volle Datenlage",
      rankLabel: "PGP-Rang",
      rank: order.pgp.rank,
      rawLabel: "μ",
      rawValue: order.pgp.mu,
      rawDigits: 3,
      rawExplain: "unsere Prioritätseinschätzung",
      begruendung: order.pgp.begruendung,
    });

    const llmBox = renderAssessmentBox({
      kind: "llm",
      title: "LLM – eingeschränkter Kontext",
      rankLabel: "LLM-Rang",
      rank: order.llm.rank,
      rawLabel: "τ",
      rawValue: order.llm.tau,
      rawDigits: 2,
      rawExplain: "Meinungsverschiedenheit zum PGP-Rang",
      begruendung: order.llm.begruendung,
    });

    return `
      <li class="order-card" data-ampel="${escapeHtml(order.ampel_status)}">
        <div class="order-row">
          <span class="order-rank">#${escapeHtml(order.pgp.rank)}</span>
          <div class="order-main">
            <div class="order-id">${escapeHtml(order.order_id)} – ${escapeHtml(order.customer)}</div>
            <div class="order-meta">
              ${escapeHtml(order.product_id)} &middot; fällig ${escapeHtml(order.due_date)}
            </div>
          </div>
          <span class="ampel-badge" data-ampel="${escapeHtml(order.ampel_status)}">
            <span class="ampel-icon" aria-hidden="true">${meta.icon}</span>
            <span aria-hidden="true">${meta.symbol}</span>
            ${escapeHtml(meta.label)}
          </span>
          <button class="details-toggle" type="button" aria-expanded="false" aria-controls="${cardId}">
            Details
          </button>
        </div>
        <div class="order-details" id="${cardId}" hidden>
          <p class="ampel-explain">${escapeHtml(meta.explain)}</p>
          ${pgpBox}
          ${llmBox}
        </div>
      </li>
    `;
  }

  function renderQueue(eskalationen) {
    const list = document.getElementById("queue-list");
    if (eskalationen.length === 0) {
      list.hidden = true;
      showStatus(
        '<p class="empty-state">Keine offenen Aufträge in der Warteschlange.</p>'
      );
      return;
    }
    list.innerHTML = eskalationen.map(renderOrderCard).join("");
    list.hidden = false;
    clearStatus();

    list.querySelectorAll(".details-toggle").forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = document.getElementById(btn.getAttribute("aria-controls"));
        const expanded = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", String(!expanded));
        target.hidden = expanded;
        btn.textContent = expanded ? "Details" : "Details ausblenden";
      });
    });
  }

  function showStatus(html) {
    document.getElementById("status-region").innerHTML = html;
  }

  function clearStatus() {
    document.getElementById("status-region").innerHTML = "";
  }

  function renderLoading() {
    document.getElementById("queue-list").hidden = true;
    showStatus('<p class="loading">Warteschlange wird geladen …</p>');
  }

  function renderError(err) {
    document.getElementById("queue-list").hidden = true;
    showStatus(`
      <div class="error-box" role="alert">
        <h2>Warteschlange konnte nicht angezeigt werden</h2>
        <p>${escapeHtml(err.message)}</p>
        <button id="retry-btn" type="button">Erneut versuchen</button>
      </div>
    `);
    document.getElementById("retry-btn").addEventListener("click", load);
  }

  function renderHinweis(hinweis) {
    document.getElementById("queue-list").hidden = true;
    showStatus(`
      <div class="hinweis-box" role="status">
        <h2>Warteschlange noch nicht verfügbar</h2>
        <p>${escapeHtml(hinweis)}</p>
        <p>Das ist keine leere Warteschlange – die Priorisierung wurde für
        diesen Datenstand noch nicht berechnet.</p>
        <button id="retry-btn" type="button">Erneut versuchen</button>
      </div>
    `);
    document.getElementById("retry-btn").addEventListener("click", load);
  }

  // --- Orchestrierung --------------------------------------------------------

  let lastEskalationen = null;

  async function load() {
    renderLoading();
    try {
      const eskalationen = await fetchEskalationen();
      lastEskalationen = eskalationen;
      applyFilterAndRender();
    } catch (err) {
      lastEskalationen = null;
      if (err instanceof BackendNotReady) {
        renderHinweis(err.message);
      } else {
        renderError(err);
      }
    }
  }

  function applyFilterAndRender() {
    if (!lastEskalationen) return;
    const onlyAttention = document.getElementById("filter-attention").checked;
    const sorted = sortByPgpRank(lastEskalationen);
    const filtered = filterAttention(sorted, onlyAttention);
    renderQueue(filtered);
  }

  function init() {
    document.getElementById("reload-btn").addEventListener("click", load);
    document
      .getElementById("filter-attention")
      .addEventListener("change", applyFilterAndRender);
    load();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Fuer eine Logik-Verifikation ohne Browser (siehe frontend/README.md,
  // Abschnitt "Was getestet wurde") exportiert - im Browser ungenutzt.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { ampelMeta, sortByPgpRank, filterAttention, AMPEL, ATTENTION_STATES };
  }
})();
