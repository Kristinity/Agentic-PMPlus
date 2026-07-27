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
 * TICKET-F03 (step8-live-test/Produkt-Backlog/TICKET-F03-Entscheidungserfassung.md):
 * ersetzt den bisherigen Platzhalter (handleDecisionPlaceholder) durch die echte
 * Entscheidungserfassung: PGP folgen / LLM folgen / eigene Reihenfolge, mit
 * erzwungener Begruendung bei Abweichung, einem echten Vorschau-Schritt VOR dem
 * verbindlichen Speichern und Anzeige des echten Ergebnisses (inkl. tatsaechlich
 * propagierter Faelle) danach.
 *
 * Architektur-Konflikt und Loesung (siehe auch Kommentar in api.py): das Ticket
 * verlangt, VOR dem finalen Bestaetigen sichtbar zu machen, wie viele/welche
 * Faelle mitbetroffen sind (Frontend-Konzept 2.4, Leitplanke 2). POST /entscheidung
 * berechnet die Propagation aber bisher im selben Aufruf, in dem sie auch persistiert
 * wird - ein "vorher sehen, ohne dass es passiert" gab es nicht. Geloest ueber
 * Weg (a): ein NEUER, rein lesender Endpunkt GET /aehnliche-faelle (ruft
 * propagation.propagate() side-effect-frei auf, persistiert nichts). Das Frontend
 * ruft ihn im ersten Schritt ("Weiter: Auswirkung pruefen") auf und zeigt die ECHTE
 * Liste; erst ein zweiter, separater Klick ("Entscheidung jetzt endgueltig
 * speichern") loest POST /entscheidung aus. Bewusst NICHT eine bloss als Schaetzung
 * gekennzeichnete Anzeige ohne echten Server-Call (Weg b) - Weg (a) war technisch
 * genauso einfach umzusetzen (propagation.propagate() existierte bereits
 * side-effect-frei) und erfuellt den Ticket-Wortlaut woertlicher.
 *
 * Design-Leitplanken aus .claude/agents/role/frontend-dev.md (nicht verhandelbar,
 * hier konkret umgesetzt):
 *   1. PGP und LLM werden IMMER als zwei getrennte Objekte/UI-Bloecke gerendert
 *      (renderAssessmentBox aufgerufen fuer "pgp" und "llm" separat) - nirgends
 *      wird ein gemeinsamer/gemittelter Score gebildet. Der neue RAG-Abschnitt
 *      (renderRagDocs) ist bewusst ein DRITTER, eigener Block - er haengt sich
 *      an keine der beiden Boxen an und verwischt ihre Trennung nicht.
 *   2. Vorschlag != Ausfuehrung (TICKET-F03): "Entscheidung erfassen" oeffnet nur
 *      ein Formular; das Absenden des Formulars fuehrt NICHT direkt zu
 *      POST /entscheidung, sondern zunaechst zu einem echten Vorschau-Schritt
 *      (GET /aehnliche-faelle, s. o.). Erst ein zweiter, separat beschrifteter
 *      Bestaetigungs-Klick loest die tatsaechliche, irreversible Aktion aus. Der
 *      Button bleibt ausserdem weiterhin deaktiviert, bis die Details
 *      (pgp+llm+RAG) tatsaechlich geoeffnet wurden (F02-Erbe, unveraendert).
 *   3. Provenienz-Erzwingung (TICKET-F03): bei wahl === "eigene_reihenfolge" ist
 *      die Begruendung ein Pflichtfeld, das clientseitig das Absenden blockiert
 *      (validateDecisionForm) - zusaetzlich zur serverseitigen 422-Validierung in
 *      api.py (Verteidigung in der Tiefe, nicht als Ersatz dafuer gedacht).
 *      entschieden_von wird NIRGENDS als waehlbares Feld angeboten (Backend
 *      ignoriert/ueberschreibt es ohnehin hart auf "mensch", s. store.py) - ein
 *      UI-Feld dafuer waere Kontrolle vortaeuschen, die serverseitig wirkungslos
 *      waere.
 *   4. matched_rag_docs/Vertrauensstufe wird angezeigt (renderRagDocs) -
 *      TICKET-F02s Kernauftrag, unveraendert. Eine fehlende/unbekannte
 *      Vertrauensstufe (vertrauensstufe: null, z. B. bei unbekannter Doc-ID,
 *      siehe rag_lookup.py) wird sichtbar als "Vertrauensstufe unbekannt" mit
 *      Warnsymbol markiert, NIE stillschweigend leer gelassen (Systemgrenzen.md
 *      Teil C.1/C.2).
 *   5. Fail-safe statt fail-open: jeder Fehlerfall (Netzwerk, HTTP-Fehler,
 *      unerwartete Response-Form, Backend-Hinweis "Step 6 noch nicht gelaufen")
 *      blockiert sichtbar mit einer Fehler-/Hinweisbox statt eine leere oder
 *      alte Liste stillschweigend als aktuell auszugeben (siehe renderError/
 *      renderHinweis, nie renderQueue mit unvollstaendigen Daten). Gilt auch
 *      fuer matched_rag_docs (leere Liste explizit ausgeschrieben) UND fuer
 *      TICKET-F03: schlaegt GET /aehnliche-faelle fehl, wird der Bestaetigen-
 *      Button NICHT freigegeben (keine blinde Bestaetigung ohne echte Vorschau);
 *      schlaegt POST /entscheidung fehl (z. B. 422 trotz Client-Validierung durch
 *      eine Race Condition, oder Netzwerkfehler), wird das sichtbar gemeldet, die
 *      eingegebenen Werte bleiben erhalten, nichts wird still verschluckt.
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

  // --- Wahlmoeglichkeiten (TICKET-F03) ---------------------------------------
  // Werte MUESSEN exakt den drei in api.py:EntscheidungRequest.wahl (Literal)
  // und store.py (CHECK-Constraint) erlaubten Strings entsprechen - hier fest
  // verdrahtet statt vom Backend erfragt, weil es (bewusst, s. Architektur-Doc)
  // keinen eigenen "welche Wahlmoeglichkeiten gibt es"-Endpunkt gibt.
  const WAHL_OPTIONS = [
    { value: "folgt_pgp", label: "PGP folgen" },
    { value: "folgt_llm", label: "LLM folgen" },
    { value: "eigene_reihenfolge", label: "Eigene Reihenfolge festlegen" },
  ];

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

  // TICKET-F03: eigene Fehlerklasse fuer eine vom Backend ABGELEHNTE Entscheidung
  // (z. B. HTTP 422, fehlende Begruendung trotz Client-Validierung) - bewusst
  // getrennt von FetchFailure (Netzwerk-/Transport-Ebene), damit die UI beide
  // Faelle unterschiedlich, aber jeweils sichtbar behandeln kann (Leitplanke 5).
  class DecisionRejected extends Error {
    constructor(message, status, detail) {
      super(message);
      this.name = "DecisionRejected";
      this.status = status;
      this.detail = detail;
    }
  }

  // Extrahiert eine lesbare Fehlermeldung aus einer FastAPI/Pydantic-422-Antwort
  // ({"detail": [{"msg": "...", ...}, ...]} oder {"detail": "..."}) - fail-safe:
  // liefert bei unbekannter Form einen generischen, aber ehrlichen Hinweis statt
  // "undefined" oder eine leere Meldung anzuzeigen.
  function extractErrorDetail(data, status) {
    if (data && Array.isArray(data.detail) && data.detail.length > 0) {
      return data.detail
        .map((d) => (d && d.msg ? String(d.msg) : JSON.stringify(d)))
        .join("; ");
    }
    if (data && typeof data.detail === "string" && data.detail.trim()) {
      return data.detail;
    }
    return `Backend antwortete mit Status ${status}.`;
  }

  // TICKET-F03: rein lesende Vorschau (siehe api.py:get_aehnliche_faelle und der
  // Architektur-Konflikt-Kommentar im Modulkopf dieser Datei) - persistiert
  // NICHTS, wird vor dem finalen Bestaetigen aufgerufen.
  async function fetchAehnlicheFaelle(orderId, wahl) {
    const url = `${API_BASE}/aehnliche-faelle?${new URLSearchParams({ order_id: orderId, wahl })}`;
    let response;
    try {
      response = await fetch(url);
    } catch (networkError) {
      throw new FetchFailure(
        "Die Auswirkung dieser Entscheidung konnte nicht geprüft werden " +
          "(Netzwerkfehler). Ohne diese Prüfung wird die Entscheidung NICHT " +
          "zur Bestätigung freigegeben.",
        networkError
      );
    }
    let data = null;
    try {
      data = await response.json();
    } catch (parseError) {
      data = null;
    }
    if (!response.ok) {
      throw new FetchFailure(
        `Die Auswirkung dieser Entscheidung konnte nicht geprüft werden ` +
          `(${extractErrorDetail(data, response.status)}). Ohne diese Prüfung ` +
          `wird die Entscheidung NICHT zur Bestätigung freigegeben.`,
        null
      );
    }
    if (!data || !Array.isArray(data.propagierte_faelle) || !Array.isArray(data.uebersprungene_faelle)) {
      throw new FetchFailure(
        "Antwort des Backends auf die Auswirkungs-Prüfung hatte nicht die " +
          "erwartete Form.",
        null
      );
    }
    return data;
  }

  // TICKET-F03: die tatsaechliche, irreversible Aktion - erst hier wird etwas in
  // shared_feedback/entscheidungen.db geschrieben (siehe store.py). Wird
  // ausschliesslich vom zweiten, separaten Bestaetigen-Klick ausgeloest, nie vom
  // ersten Formular-Absenden (Leitplanke 2).
  async function postEntscheidung(payload) {
    let response;
    try {
      response = await fetch(`${API_BASE}/entscheidung`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (networkError) {
      throw new FetchFailure(
        "Die Entscheidung konnte nicht gespeichert werden (Netzwerkfehler). " +
          "Es ist NICHT sicher, ob sie angekommen ist - bitte den Verlauf " +
          "prüfen, bevor Sie es erneut versuchen.",
        networkError
      );
    }
    let data = null;
    try {
      data = await response.json();
    } catch (parseError) {
      data = null;
    }
    if (!response.ok) {
      // 422 (fehlende Begruendung trotz Client-Validierung, z. B. durch eine
      // Race Condition oder umgangene Validierung) landet HIER, nicht in
      // FetchFailure - die UI unterscheidet danach, ob sie zur Korrektur
      // zurueckfuehrt (DecisionRejected) oder nur "erneut versuchen" anbietet.
      throw new DecisionRejected(
        extractErrorDetail(data, response.status),
        response.status,
        data && data.detail
      );
    }
    if (!data || typeof data.decision_id === "undefined") {
      throw new FetchFailure(
        "Antwort des Backends nach dem Speichern hatte nicht die erwartete " +
          "Form - die Entscheidung wurde möglicherweise trotzdem gespeichert, " +
          "bitte den Verlauf prüfen.",
        null
      );
    }
    return data;
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

  // TICKET-F03: Auftrags-IDs, fuer die bereits erfolgreich POST /entscheidung
  // aufgerufen wurde (diese Sitzung) - verhindert, dass dieselbe Karte
  // versehentlich ein zweites Mal "entschieden" wird, und zeigt stattdessen das
  // echte, gespeicherte Ergebnis. decidedOrderResults haelt dafuer das
  // vollstaendige Ergebnis (inkl. der echten propagierte_faelle-Liste aus der
  // Response). Gleiches Muster/gleiche bewusste Vereinfachung wie
  // detailsViewedOrderIds oben (Modul-Scope, ueberlebt "Neu laden" nicht aber
  // einen echten Seiten-Reload nicht - fuer einen Prototyp ohne Login/Session
  // akzeptabel).
  const decidedOrderIds = new Set();
  const decidedOrderResults = new Map();

  function formatZeitstempelShort(iso) {
    if (!iso) return "unbekannter Zeitpunkt";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return String(iso);
    return date.toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" });
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

    // TICKET-F02, Akzeptanzkriterium 3: matched_rag_docs inkl. Vertrauensstufe
    // als eigener, dritter Abschnitt - haengt bewusst weder an pgpBox noch an
    // llmBox, damit die PGP/LLM-Trennung (Leitplanke 1) nicht verwaschen wird.
    const ragBox = renderRagDocs(order.matched_rag_docs);

    const alreadyViewed = detailsViewedOrderIds.has(order.order_id);
    const decidedResult = decidedOrderResults.get(order.order_id) || null;
    const decisionRow = renderDecisionRow(order, index, alreadyViewed, decidedResult);

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
  // disabled - inkl. Begruendungstext, warum.
  //
  // TICKET-F03: ist der Auftrag bereits entschieden (decidedResult gesetzt),
  // wird statt Button+Formular nur noch das ECHTE Ergebnis gezeigt (kein
  // erneuter Button) - verhindert, dass dieselbe Karte irrtuemlich ein
  // zweites Mal entschieden wird (Aufgabenstellung Punkt 3). Sonst: Button +
  // (anfangs verstecktes) Formular, das erst nach einem Klick sichtbar wird.
  function renderDecisionRow(order, index, viewed, decidedResult) {
    const orderId = order.order_id;

    if (decidedResult) {
      return `<div class="decision-row decision-row-done">${renderDecisionDone(decidedResult)}</div>`;
    }

    const disabledAttr = viewed ? "" : "disabled";
    const formId = `decision-form-${index}`;
    const title = viewed
      ? "Entscheidung erfassen"
      : "Erst „Details“ öffnen und PGP-, LLM- sowie RAG-Einschätzung ansehen, bevor Sie entscheiden können.";
    return `
      <div class="decision-row">
        <button
          class="decision-btn"
          type="button"
          data-order-id="${escapeHtml(orderId)}"
          ${disabledAttr}
          aria-disabled="${viewed ? "false" : "true"}"
          aria-expanded="false"
          aria-controls="${formId}"
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
      <div class="decision-form-container" id="${formId}" hidden>
        ${renderDecisionFormFields(order, index)}
      </div>
    `;
  }

  // TICKET-F03: das eigentliche Entscheidungsformular - PGP folgen / LLM
  // folgen / eigene Reihenfolge, Begruendung (Pflicht bei eigener
  // Reihenfolge), ein "Weiter"-Schritt (fuehrt zur echten Vorschau, s.
  // fetchAehnlicheFaelle) und erst danach ein separater, eindeutig
  // beschrifteter Bestaetigen-Button (Leitplanke 2 - Vorschlag != Ausfuehrung).
  // entschieden_von wird hier BEWUSST NICHT als Feld angeboten (Leitplanke 3 -
  // s. Modulkopf).
  function renderDecisionFormFields(order, index) {
    const orderId = order.order_id;
    const radioName = `wahl-${index}`;
    const options = WAHL_OPTIONS.map((opt) => {
      let explain = "";
      if (opt.value === "folgt_pgp") {
        explain = ` – übernimmt PGP-Rang #${escapeHtml(order.pgp.rank)}`;
      } else if (opt.value === "folgt_llm") {
        explain = ` – übernimmt LLM-Rang #${escapeHtml(order.llm.rank)}`;
      }
      return `
        <label class="decision-wahl-option">
          <input type="radio" name="${escapeHtml(radioName)}" value="${opt.value}" class="decision-wahl-input" />
          ${escapeHtml(opt.label)}<span class="decision-wahl-explain">${explain}</span>
        </label>
      `;
    }).join("");

    return `
      <form class="decision-wizard" data-order-id="${escapeHtml(orderId)}" data-stage="input" novalidate>
        <fieldset class="decision-wahl-fieldset">
          <legend>Wie möchten Sie entscheiden?</legend>
          ${options}
        </fieldset>

        <div class="decision-field decision-eigene-reihenfolge-field" hidden>
          <label for="eigene-reihenfolge-${index}">Eigene Reihenfolge</label>
          <textarea
            id="eigene-reihenfolge-${index}"
            class="decision-eigene-reihenfolge-input"
            rows="2"
            placeholder="Gewünschte Reihenfolge in eigenen Worten, z. B. „zuerst ${escapeHtml(orderId)}, danach …“"
          ></textarea>
        </div>

        <div class="decision-field">
          <label for="begruendung-${index}">
            Begründung
            <span class="decision-begruendung-pflicht" hidden>(Pflichtfeld bei „eigene Reihenfolge“)</span>
            <span class="decision-begruendung-optional">(optional bei „PGP folgen“/„LLM folgen“)</span>
          </label>
          <textarea
            id="begruendung-${index}"
            class="decision-begruendung-input"
            rows="2"
            placeholder="Warum entscheiden Sie so?"
          ></textarea>
        </div>

        <p class="decision-form-error" role="alert" hidden></p>

        <div class="decision-actions">
          <button type="button" class="decision-preview-btn">Weiter: Auswirkung prüfen</button>
        </div>

        <div class="decision-preview-panel" hidden>
          <p class="decision-preview-loading" hidden>Ähnliche Fälle werden geprüft …</p>
          <p class="decision-preview-error" role="alert" hidden></p>
          <div class="decision-preview-result" hidden></div>
          <p class="decision-preview-explain">
            Dies ist eine echte Abfrage des Backends (keine Schätzung). Solange sich
            zwischen dieser Prüfung und dem Bestätigen kein anderer Fall ändert, entspricht
            sie exakt dem tatsächlichen Ergebnis.
          </p>
          <div class="decision-actions">
            <button type="button" class="decision-back-btn">Zurück</button>
            <button type="button" class="decision-confirm-btn" disabled>
              Entscheidung jetzt endgültig speichern
            </button>
          </div>
        </div>

        <p class="decision-submit-error" role="alert" hidden></p>
      </form>
    `;
  }

  // TICKET-F03: client-seitige Validierung - MUSS inhaltlich exakt der
  // Server-Regel in api.py (EntscheidungRequest.begruendung_pflicht_bei_
  // eigener_reihenfolge) entsprechen, ist aber KEIN Ersatz dafuer (der Server
  // bleibt die verbindliche zweite Instanz, s. postEntscheidung/
  // DecisionRejected). Reine Funktion, ohne DOM-Zugriff - fuer Tests ohne
  // Browser exportiert (s. Dateiende).
  function validateDecisionForm(values) {
    if (!values || !values.wahl) {
      return "Bitte eine der drei Optionen auswählen.";
    }
    if (!WAHL_OPTIONS.some((opt) => opt.value === values.wahl)) {
      return "Unbekannte Auswahl.";
    }
    if (values.wahl === "eigene_reihenfolge") {
      if (!values.eigeneReihenfolge || !values.eigeneReihenfolge.trim()) {
        // Zusaetzliche, rein clientseitige Anforderung UEBER die Server-Pflicht
        // hinaus (der Server verlangt bei eigene_reihenfolge nur begruendung,
        // s. api.py) - eine "eigene Reihenfolge" ohne angegebene Reihenfolge
        // waere fuer Jens ein sinnloser Zustand. Produktentscheidung, nicht
        // Server-Vorgabe - hier bewusst dokumentiert.
        return "Bitte die gewünschte Reihenfolge im Freitextfeld angeben.";
      }
      if (!values.begruendung || !values.begruendung.trim()) {
        return (
          "Begründung ist Pflichtfeld bei „eigene Reihenfolge“ " +
          "(weicht von PGP UND LLM gleichzeitig ab)."
        );
      }
    }
    return null;
  }

  // TICKET-F03: baut exakt den Request-Body, den POST /entscheidung erwartet
  // (api.py:EntscheidungRequest) - bewusst OHNE jedes entschieden_von-Feld
  // (Leitplanke 3/Aufgabenstellung Punkt 5: das Backend ignoriert/ueberschreibt
  // es ohnehin, ein UI-Feld dafuer wuerde nur wirkungslose Kontrolle
  // vortaeuschen).
  function buildEntscheidungPayload(orderId, values) {
    return {
      order_id: orderId,
      wahl: values.wahl,
      eigene_reihenfolge:
        values.wahl === "eigene_reihenfolge" && values.eigeneReihenfolge
          ? values.eigeneReihenfolge.trim()
          : null,
      begruendung:
        values.begruendung && values.begruendung.trim() ? values.begruendung.trim() : null,
    };
  }

  function pluralSuffix(n) {
    return n === 1 ? "" : "e";
  }

  // TICKET-F03: rendert das ECHTE Ergebnis von GET /aehnliche-faelle (nicht
  // geschaetzt) - zeigt sowohl die tatsaechlich automatisch mituebernommenen
  // Faelle (propagierte_faelle) als auch die wegen der Sicherheitsgrenze N
  // weiterhin eskalierten (uebersprungene_faelle), damit "wie viele/welche
  // Faelle mitbetroffen sind" vollstaendig beantwortet ist (Akzeptanzkriterium
  // 3 des Tickets). Reine Funktion - fuer Tests exportiert.
  function renderPreviewResult(preview, wahl) {
    if (wahl === "eigene_reihenfolge") {
      return (
        '<p class="decision-preview-none">Keine weiteren Fälle betroffen. Bei „eigene ' +
        "Reihenfolge“ wird eine Entscheidung NIE automatisch auf andere Aufträge " +
        "übertragen – es wird ausschließlich dieser eine Auftrag entschieden.</p>"
      );
    }
    const propagiert = (preview && preview.propagierte_faelle) || [];
    const uebersprungen = (preview && preview.uebersprungene_faelle) || [];

    if (propagiert.length === 0 && uebersprungen.length === 0) {
      return '<p class="decision-preview-none">Keine weiteren Fälle betroffen von dieser Entscheidung.</p>';
    }

    const propagiertBlock = propagiert.length
      ? `
        <p class="decision-preview-count">
          ${propagiert.length} ähnliche${pluralSuffix(propagiert.length)} offene${pluralSuffix(propagiert.length)}
          Auftrag${propagiert.length === 1 ? "" : "sfälle"} werden automatisch mit derselben
          Entscheidung mitübernommen:
        </p>
        <ul class="decision-preview-list">
          ${propagiert.map((id) => `<li>${escapeHtml(id)}</li>`).join("")}
        </ul>
      `
      : '<p class="decision-preview-none">Keine ähnlichen offenen Aufträge werden automatisch mitübernommen.</p>';

    const uebersprungenBlock = uebersprungen.length
      ? `
        <p class="decision-preview-skipped">
          ⚠️ ${uebersprungen.length} weitere${pluralSuffix(uebersprungen.length)} ähnliche${pluralSuffix(uebersprungen.length)}
          Fall${uebersprungen.length === 1 ? "" : "-Fälle"} bleiben wegen der Sicherheitsgrenze
          weiterhin eskaliert (werden NICHT automatisch übernommen):
        </p>
        <ul class="decision-preview-list decision-preview-skipped-list">
          ${uebersprungen.map((id) => `<li>${escapeHtml(id)}</li>`).join("")}
        </ul>
      `
      : "";

    return propagiertBlock + uebersprungenBlock;
  }

  // TICKET-F03: Anzeige NACH erfolgreichem POST /entscheidung - zeigt das
  // ECHTE Ergebnis (decision_id/zeitstempel/entschieden_von/propagierte_faelle
  // aus der tatsaechlichen Response), nicht die zuvor angezeigte Vorschau
  // erneut. Ersetzt Button+Formular vollstaendig (s. renderDecisionRow), damit
  // fuer Jens eindeutig ist: diese Karte ist erledigt.
  function renderDecisionDone(result) {
    const wahlOption = WAHL_OPTIONS.find((opt) => opt.value === result.wahl);
    const wahlLabelText = wahlOption ? wahlOption.label : String(result.wahl);
    const propagiert = Array.isArray(result.propagierte_faelle) ? result.propagierte_faelle : [];
    const eigeneReihenfolgeBlock =
      result.wahl === "eigene_reihenfolge" && result.eigene_reihenfolge
        ? `<p class="decision-done-eigene-reihenfolge">
             <span class="label">Eigene Reihenfolge</span>${escapeHtml(result.eigene_reihenfolge)}
           </p>`
        : "";
    const begruendungBlock = result.begruendung
      ? `<p class="decision-done-begruendung">
           <span class="label">Begründung</span>${escapeHtml(result.begruendung)}
         </p>`
      : "";
    const propagiertBlock = propagiert.length
      ? `<p class="decision-done-propagiert">
           Automatisch mit derselben Entscheidung übernommen (${propagiert.length}):
           ${propagiert.map((id) => escapeHtml(id)).join(", ")}
         </p>`
      : '<p class="decision-done-propagiert">Keine weiteren Fälle wurden automatisch mitübernommen.</p>';

    return `
      <div class="decision-done" role="status">
        <p class="decision-done-summary">
          ✅ Entscheidung gespeichert: <strong>${escapeHtml(wahlLabelText)}</strong>
          (Entscheidungs-Nr. ${escapeHtml(result.decision_id)},
          ${escapeHtml(formatZeitstempelShort(result.zeitstempel))},
          erfasst als „${escapeHtml(result.entschieden_von || "mensch")}“).
          Diese Karte gilt als entschieden und sollte nicht erneut entschieden werden.
        </p>
        ${eigeneReihenfolgeBlock}
        ${begruendungBlock}
        ${propagiertBlock}
        <p class="decision-done-hinweis">
          Vollständiger Verlauf inkl. automatisch übernommener Fälle:
          <a href="verlauf.html">Entscheidungsverlauf</a>.
        </p>
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
      btn.title = "Entscheidung erfassen";
    }
    const hint = cardEl.querySelector(".decision-hint");
    if (hint) hint.remove();
  }

  // TICKET-F03: verdrahtet EIN Entscheidungsformular (Radios, Freitext-/
  // Begruendungsfelder, "Weiter"-Vorschau, Bestaetigen). Wird pro Karte einmal
  // nach jedem renderQueue()-Aufruf aufgerufen (gleiches Muster wie die
  // details-toggle/decision-btn-Wiring weiter unten).
  function wireDecisionForm(form) {
    const orderId = form.getAttribute("data-order-id");
    const cardEl = form.closest(".order-card");

    const radios = Array.from(form.querySelectorAll(".decision-wahl-input"));
    const eigeneReihenfolgeField = form.querySelector(".decision-eigene-reihenfolge-field");
    const eigeneReihenfolgeInput = form.querySelector(".decision-eigene-reihenfolge-input");
    const begruendungInput = form.querySelector(".decision-begruendung-input");
    const begruendungPflichtHint = form.querySelector(".decision-begruendung-pflicht");
    const begruendungOptionalHint = form.querySelector(".decision-begruendung-optional");
    const formError = form.querySelector(".decision-form-error");
    const previewBtn = form.querySelector(".decision-preview-btn");
    const previewPanel = form.querySelector(".decision-preview-panel");
    const previewLoading = form.querySelector(".decision-preview-loading");
    const previewError = form.querySelector(".decision-preview-error");
    const previewResult = form.querySelector(".decision-preview-result");
    const backBtn = form.querySelector(".decision-back-btn");
    const confirmBtn = form.querySelector(".decision-confirm-btn");
    const submitError = form.querySelector(".decision-submit-error");

    // Der EXAKTE Payload, fuer den die zuletzt erfolgreiche Vorschau berechnet
    // wurde. Der Bestaetigen-Klick sendet garantiert genau diesen - nie einen
    // zwischenzeitlich unbemerkt veraenderten (s. resetPreview: jede
    // Formular-Aenderung nach einer Vorschau macht sie sofort ungueltig).
    let previewedPayload = null;

    function currentValues() {
      const checked = radios.find((r) => r.checked);
      return {
        wahl: checked ? checked.value : null,
        eigeneReihenfolge: eigeneReihenfolgeInput.value,
        begruendung: begruendungInput.value,
      };
    }

    function updateWahlDependentUi() {
      const checked = radios.find((r) => r.checked);
      const isEigene = !!checked && checked.value === "eigene_reihenfolge";
      eigeneReihenfolgeField.hidden = !isEigene;
      begruendungPflichtHint.hidden = !isEigene;
      begruendungOptionalHint.hidden = isEigene;
    }

    function resetPreview() {
      previewedPayload = null;
      previewPanel.hidden = true;
      previewError.hidden = true;
      previewResult.hidden = true;
      previewResult.innerHTML = "";
      previewLoading.hidden = true;
      confirmBtn.disabled = true;
      submitError.hidden = true;
      previewBtn.hidden = false;
      // Formularfelder wieder editierbar (falls durch eine vorige erfolgreiche
      // Vorschau gesperrt, s. previewBtn-Handler unten).
      radios.forEach((r) => (r.disabled = false));
      eigeneReihenfolgeInput.disabled = false;
      begruendungInput.disabled = false;
    }

    radios.forEach((radio) => {
      radio.addEventListener("change", () => {
        updateWahlDependentUi();
        formError.hidden = true;
        resetPreview();
      });
    });
    eigeneReihenfolgeInput.addEventListener("input", resetPreview);
    begruendungInput.addEventListener("input", resetPreview);

    previewBtn.addEventListener("click", async () => {
      const values = currentValues();
      const validationError = validateDecisionForm(values);
      if (validationError) {
        formError.textContent = validationError;
        formError.hidden = false;
        return;
      }
      formError.hidden = true;

      const payload = buildEntscheidungPayload(orderId, values);
      previewPanel.hidden = false;
      previewLoading.hidden = false;
      previewError.hidden = true;
      previewResult.hidden = true;
      confirmBtn.disabled = true;

      try {
        const preview = await fetchAehnlicheFaelle(orderId, payload.wahl);
        previewLoading.hidden = true;
        previewResult.innerHTML = renderPreviewResult(preview, payload.wahl);
        previewResult.hidden = false;
        previewedPayload = payload;
        confirmBtn.disabled = false;
        // Sperrt die Eingabefelder, solange die Vorschau gueltig ist - so kann
        // nie etwas anderes bestaetigt werden als das, was gerade angezeigt
        // wurde (Vorschlag == das, was tatsaechlich ausgefuehrt wird).
        radios.forEach((r) => (r.disabled = true));
        eigeneReihenfolgeInput.disabled = true;
        begruendungInput.disabled = true;
        previewBtn.hidden = true;
      } catch (err) {
        previewLoading.hidden = true;
        previewError.textContent = err.message;
        previewError.hidden = false;
        confirmBtn.disabled = true;
      }
    });

    backBtn.addEventListener("click", () => {
      resetPreview();
    });

    confirmBtn.addEventListener("click", async () => {
      // Verteidigung in der Tiefe: ohne gueltige Vorschau ist der Button
      // disabled, aber selbst falls das je umgangen wuerde, wird ohne
      // previewedPayload nichts gesendet.
      if (!previewedPayload) return;
      confirmBtn.disabled = true;
      backBtn.disabled = true;
      submitError.hidden = true;

      try {
        const result = await postEntscheidung(previewedPayload);
        decidedOrderIds.add(orderId);
        decidedOrderResults.set(orderId, {
          ...result,
          wahl: previewedPayload.wahl,
          eigene_reihenfolge: previewedPayload.eigene_reihenfolge,
          begruendung: previewedPayload.begruendung,
        });
        if (cardEl) {
          const decisionRowEl = cardEl.querySelector(".decision-row");
          const formContainer = cardEl.querySelector(".decision-form-container");
          if (decisionRowEl) {
            decisionRowEl.outerHTML = `<div class="decision-row decision-row-done">${renderDecisionDone(
              decidedOrderResults.get(orderId)
            )}</div>`;
          }
          if (formContainer) formContainer.remove();
        }
      } catch (err) {
        backBtn.disabled = false;
        if (err instanceof DecisionRejected) {
          submitError.textContent =
            `Backend hat die Entscheidung abgelehnt: ${err.message} ` +
            "Bitte prüfen/korrigieren und erneut versuchen.";
          submitError.hidden = false;
          // Zurueck zur editierbaren Ansicht, damit z. B. eine fehlende
          // Begruendung (422 trotz Client-Validierung - z. B. durch eine
          // umgangene Validierung oder eine Race Condition) tatsaechlich
          // korrigiert werden kann, statt in einer Sackgasse zu enden.
          resetPreview();
        } else {
          // Netzwerkfehler/unerwartete Response-Form: previewedPayload bleibt
          // erhalten, ein erneuter Klick auf "Bestätigen" versucht denselben
          // Payload nochmal - postEntscheidung warnt in diesem Fall explizit,
          // dass unklar ist, ob die vorige Anfrage bereits angekommen ist.
          submitError.textContent = err.message;
          submitError.hidden = false;
          confirmBtn.disabled = false;
        }
      }
    });

    updateWahlDependentUi();
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
        // umgangen wuerde (z. B. durch DevTools), oeffnet sich das Formular
        // nur fuer tatsaechlich betrachtete Auftraege.
        const orderId = btn.getAttribute("data-order-id");
        if (btn.disabled || !detailsViewedOrderIds.has(orderId)) return;
        const container = document.getElementById(btn.getAttribute("aria-controls"));
        if (!container) return;
        const expanded = btn.getAttribute("aria-expanded") === "true";
        const willExpand = !expanded;
        btn.setAttribute("aria-expanded", String(willExpand));
        container.hidden = expanded;
        btn.textContent = expanded ? "Entscheidung erfassen" : "Formular ausblenden";
      });
    });

    // TICKET-F03: jedes tatsaechlich gerenderte Entscheidungsformular
    // verdrahten (nur nicht-entschiedene Karten haben eines, s.
    // renderDecisionRow).
    list.querySelectorAll(".decision-wizard").forEach((form) => {
      wireDecisionForm(form);
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
      // TICKET-F03
      WAHL_OPTIONS,
      validateDecisionForm,
      buildEntscheidungPayload,
      renderPreviewResult,
      renderDecisionDone,
      renderDecisionFormFields,
      fetchAehnlicheFaelle,
      postEntscheidung,
      extractErrorDetail,
      DecisionRejected,
      FetchFailure,
      decidedOrderIds,
      decidedOrderResults,
    };
  }
})();
