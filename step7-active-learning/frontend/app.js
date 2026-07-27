/**
 * step7-active-learning/frontend/app.js
 *
 * TICKET-F01 (step8-live-test/Produkt-Backlog/TICKET-F01-Warteschlange.md):
 * Auftrags-Warteschlange - Startbildschirm fuer Jens Pirinski (Produktionsplaner,
 * Krasser Spass GmbH, KEIN Data Scientist). Liest GET /eskalationen und zeigt die
 * Liste sortiert nach pgp.rank mit Ampel-Status.
 *
 * TICKET-F02 (step8-live-test/Produkt-Backlog/TICKET-F02-Eskalations-Review.md):
 * erweitert dieselbe Auftragskarte um den "Eskalations-Review"-Inhalt, statt einen
 * separaten Bildschirm/eine Navigation zu bauen. Begruendung: Der bereits von F01
 * gebaute "Details"-Toggle zeigt pro Karte bereits pgp+llm nebeneinander - genau
 * das ist inhaltlich der Kern von Screen 2 aus Active-Learning-Loop-und-Frontend-
 * Konzept.md Abschnitt 2.3.2. F02 ergaenzt darin (a) matched_rag_docs inkl.
 * Vertrauensstufe als dritten, klar abgegrenzten Abschnitt und (b) einen
 * "Entscheidung erfassen"-Button, der erst nach dem Oeffnen der Details aktiv
 * wird. Eine eigene Seite/Route ist bei einem einzigen HTML-Modul ohne Router
 * unverhaeltnismaessig; passt zur in README.md dokumentierten Stack-Entscheidung
 * ("falls die Bildschirme staerker verzahnt werden muessen, spaeter neu
 * bewerten" - genau das ist hier eingetreten und wird hier dokumentiert, nicht
 * stillschweigend entschieden).
 *
 * Design-Leitplanken aus .claude/agents/role/frontend-dev.md (nicht verhandelbar,
 * hier konkret umgesetzt):
 *   1. PGP und LLM werden IMMER als zwei getrennte Objekte/UI-Bloecke gerendert
 *      (renderAssessmentBox aufgerufen fuer "pgp" und "llm" separat) - nirgends
 *      wird ein gemeinsamer/gemittelter Score gebildet. Der neue RAG-Abschnitt
 *      (renderRagDocs) ist bewusst ein DRITTER, eigener Block - er haengt sich
 *      an keine der beiden Boxen an und verwischt ihre Trennung nicht.
 *   2. Der neue "Entscheidung erfassen"-Button loest KEINE echte Aktion aus
 *      (Platzhalter: Konsolen-Log + kurzer "kommt in Kuerze"-Hinweis im UI) -
 *      die echte Funktionalitaet ist F03s Aufgabe. Hier geht es nur um die vom
 *      Ticket geforderte Sichtbarkeits-/Reihenfolge-Regel: der Button bleibt
 *      deaktiviert, bis die Details (pgp+llm+RAG) tatsaechlich geoeffnet wurden.
 *   3. Provenienz-Erzwingung (Pflicht-Begruendung bei Abweichung) betrifft F03,
 *      nicht diese reine Leseansicht - hier nicht anwendbar.
 *   4. matched_rag_docs/Vertrauensstufe wird JETZT angezeigt (renderRagDocs) -
 *      TICKET-F02s Kernauftrag. Eine fehlende/unbekannte Vertrauensstufe
 *      (vertrauensstufe: null, z. B. bei unbekannter Doc-ID, siehe rag_lookup.py)
 *      wird sichtbar als "Vertrauensstufe unbekannt" mit Warnsymbol markiert,
 *      NIE stillschweigend leer gelassen (Systemgrenzen.md Teil C.1/C.2).
 *   5. Fail-safe statt fail-open: jeder Fehlerfall (Netzwerk, HTTP-Fehler,
 *      unerwartete Response-Form, Backend-Hinweis "Step 6 noch nicht gelaufen")
 *      blockiert sichtbar mit einer Fehler-/Hinweisbox statt eine leere oder
 *      alte Liste stillschweigend als aktuell auszugeben (siehe renderError/
 *      renderHinweis, nie renderQueue mit unvollstaendigen Daten). Gilt auch
 *      fuer matched_rag_docs: eine leere Liste wird explizit als "keine
 *      RAG-Dokumente hinterlegt" ausgeschrieben statt den Abschnitt kommentarlos
 *      wegzulassen.
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

  // --- RAG-Treffer / Vertrauensstufe (TICKET-F02) ---------------------------

  // Fail-safe: null, undefined UND "" gelten als "keine Vertrauensstufe
  // vorhanden" - rag_lookup.py liefert explizit None fuer unbekannte Doc-IDs
  // (siehe rag_lookup.resolve_matched_docs), aber ein Frontend sollte sich
  // nicht darauf verlassen, dass ein Backend niemals einen leeren String statt
  // null schickt, wenn dieselbe Bedeutung gemeint ist.
  function istVertrauensstufeUnbekannt(vertrauensstufe) {
    return vertrauensstufe == null || vertrauensstufe === "";
  }

  function renderRagDocs(matchedRagDocs) {
    if (!Array.isArray(matchedRagDocs) || matchedRagDocs.length === 0) {
      // Bewusst NICHT einfach weglassen: eine leere Liste ist ein legitimer,
      // aber vom Planer selbst zu bewertender Zustand ("kein RAG-Kontext
      // gestuetzt diese Einschaetzung") - Leitplanke 5 (Fail-safe).
      return `
        <div class="rag-box">
          <h3>Genutzte RAG-Dokumente</h3>
          <p class="rag-empty">Keine RAG-Dokumente für diesen Auftrag hinterlegt.</p>
        </div>
      `;
    }

    const items = matchedRagDocs
      .map((doc) => {
        const vertrauensstufe = doc ? doc.vertrauensstufe : null;
        const unbekannt = istVertrauensstufeUnbekannt(vertrauensstufe);
        const docId = doc && doc.doc_id != null && doc.doc_id !== "" ? doc.doc_id : "(unbekannte Dokument-ID)";
        const title = doc && doc.title != null && doc.title !== "" ? doc.title : "(kein Titel hinterlegt)";
        return `
          <li class="rag-doc${unbekannt ? " rag-doc-unbekannt" : ""}">
            <span class="rag-doc-title">${escapeHtml(title)}</span>
            <span class="rag-doc-id">${escapeHtml(docId)}</span>
            <span class="rag-vertrauen${unbekannt ? " rag-vertrauen-unbekannt" : ""}">
              ${unbekannt ? "⚠️ " : ""}${escapeHtml(unbekannt ? "Vertrauensstufe unbekannt" : vertrauensstufe)}
            </span>
          </li>
        `;
      })
      .join("");

    return `
      <div class="rag-box">
        <h3>Genutzte RAG-Dokumente</h3>
        <ul class="rag-doc-list">${items}</ul>
      </div>
    `;
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

  // TICKET-F02: Auftrags-IDs, deren Details-Panel (pgp+llm+RAG) mindestens
  // einmal geoeffnet wurde - Voraussetzung dafuer, dass "Entscheidung
  // erfassen" fuer diesen Auftrag ueberhaupt aktivierbar ist (siehe
  // markDetailsViewed/renderDecisionRow). Bewusst NICHT bei jedem load()
  // zurueckgesetzt: "hat der Planer diesen Fall schon einmal angesehen" ist
  // eine Aussage ueber den Menschen in dieser Sitzung, nicht ueber die Aktualitaet
  // der geladenen Daten - ein "Neu laden" soll ein bereits geoeffnetes Detail
  // nicht wieder sperren. Setzt sich bei echtem Seiten-Reload zurueck (Modul-
  // Scope), was fuer einen Prototyp ohne Login/Session als akzeptable,
  // dokumentierte Vereinfachung gilt.
  const detailsViewedOrderIds = new Set();

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

    // TICKET-F02, Akzeptanzkriterium 3: matched_rag_docs inkl. Vertrauensstufe
    // als eigener, dritter Abschnitt - haengt bewusst weder an pgpBox noch an
    // llmBox, damit die PGP/LLM-Trennung (Leitplanke 1) nicht verwaschen wird.
    const ragBox = renderRagDocs(order.matched_rag_docs);

    const alreadyViewed = detailsViewedOrderIds.has(order.order_id);
    const decisionRow = renderDecisionRow(order.order_id, alreadyViewed);

    return `
      <li class="order-card" data-ampel="${escapeHtml(order.ampel_status)}" data-order-id="${escapeHtml(order.order_id)}">
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
          ${ragBox}
        </div>
        ${decisionRow}
      </li>
    `;
  }

  // TICKET-F02, Akzeptanzkriterium 2 ("erst beide Einschätzungen betrachten,
  // dann erst Wechsel zur Entscheidungserfassung möglich"): der Button lebt
  // AUSSERHALB des zusammenklappbaren order-details-Blocks (also immer im DOM
  // sichtbar, nicht versteckt), ist aber bis zum ersten Oeffnen der Details
  // disabled - inkl. Begruendungstext, warum. F03 (Entscheidungserfassung)
  // existiert noch nicht; der Klick fuehrt daher bewusst nur auf eine
  // Platzhalter-Aktion (siehe handleDecisionPlaceholder), NICHT auf eine echte
  // Navigation/Aktion (Leitplanke 2).
  function renderDecisionRow(orderId, viewed) {
    const disabledAttr = viewed ? "" : "disabled";
    const title = viewed
      ? "Entscheidung erfassen (Platzhalter – die eigentliche Entscheidungserfassung folgt in TICKET-F03)"
      : "Erst „Details“ öffnen und PGP-, LLM- sowie RAG-Einschätzung ansehen, bevor Sie entscheiden können.";
    return `
      <div class="decision-row">
        <button
          class="decision-btn"
          type="button"
          data-order-id="${escapeHtml(orderId)}"
          ${disabledAttr}
          aria-disabled="${viewed ? "false" : "true"}"
          title="${escapeHtml(title)}"
        >
          Entscheidung erfassen
        </button>
        ${
          viewed
            ? '<span class="decision-status" aria-live="polite"></span>'
            : '<span class="decision-hint">Erst Details öffnen, um PGP- und LLM-Einschätzung (inkl. RAG-Treffer) zu prüfen.</span><span class="decision-status" aria-live="polite"></span>'
        }
      </div>
    `;
  }

  // Wird beim ersten Oeffnen der Details fuer diesen Auftrag aufgerufen -
  // schaltet den "Entscheidung erfassen"-Button live frei, ohne die ganze
  // Karte neu zu rendern (das wuerde den gerade geoeffneten Zustand wieder
  // einklappen).
  function markDetailsViewed(orderId, cardEl) {
    if (detailsViewedOrderIds.has(orderId)) return;
    detailsViewedOrderIds.add(orderId);
    if (!cardEl) return;
    const btn = cardEl.querySelector(".decision-btn");
    if (btn) {
      btn.disabled = false;
      btn.setAttribute("aria-disabled", "false");
      btn.title = "Entscheidung erfassen (Platzhalter – die eigentliche Entscheidungserfassung folgt in TICKET-F03)";
    }
    const hint = cardEl.querySelector(".decision-hint");
    if (hint) hint.remove();
  }

  // Platzhalter-Aktion (TICKET-F02, Akzeptanzkriterium 2): loest bewusst
  // NICHTS Echtes aus - weder eine Navigation noch eine Produktionsaktion
  // (Leitplanke 2). F03 ersetzt dies durch die echte Entscheidungserfassung.
  function handleDecisionPlaceholder(orderId, cardEl) {
    console.log(
      `[Platzhalter] "Entscheidung erfassen" für Auftrag ${orderId} geklickt – ` +
        "Funktionalität folgt in TICKET-F03 (Entscheidungserfassung)."
    );
    const status = cardEl && cardEl.querySelector(".decision-status");
    if (status) {
      status.textContent = "Entscheidungserfassung kommt in Kürze (TICKET-F03).";
    }
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
        const willExpand = !expanded;
        btn.setAttribute("aria-expanded", String(willExpand));
        target.hidden = expanded;
        btn.textContent = expanded ? "Details" : "Details ausblenden";
        // TICKET-F02: das erste OEFFNEN (nicht das Schliessen) zaehlt als
        // "Details betrachtet" und schaltet den Entscheidung-Button dieser
        // Karte frei - siehe markDetailsViewed.
        if (willExpand) {
          const cardEl = btn.closest(".order-card");
          const orderId = cardEl ? cardEl.getAttribute("data-order-id") : null;
          if (orderId) markDetailsViewed(orderId, cardEl);
        }
      });
    });

    list.querySelectorAll(".decision-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        // Verteidigung in der Tiefe: selbst falls das disabled-Attribut je
        // umgangen wuerde (z. B. durch DevTools), wird die Platzhalter-Aktion
        // nur fuer tatsaechlich betrachtete Auftraege ausgefuehrt.
        const orderId = btn.getAttribute("data-order-id");
        if (btn.disabled || !detailsViewedOrderIds.has(orderId)) return;
        handleDecisionPlaceholder(orderId, btn.closest(".order-card"));
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
    module.exports = {
      ampelMeta,
      sortByPgpRank,
      filterAttention,
      AMPEL,
      ATTENTION_STATES,
      // TICKET-F02
      istVertrauensstufeUnbekannt,
      renderRagDocs,
      renderOrderCard,
      renderDecisionRow,
      detailsViewedOrderIds,
    };
  }
})();
