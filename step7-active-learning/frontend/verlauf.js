/**
 * step7-active-learning/frontend/verlauf.js
 *
 * TICKET-F05 (step8-live-test/Produkt-Backlog/TICKET-F05-Audit-Trail.md):
 * Audit-Trail - chronologischer Entscheidungsverlauf fuer Jens Pirinski
 * (Produktionsplaner, Krasser Spass GmbH, KEIN Data Scientist). Liest
 * GET /verlauf und zeigt jede Entscheidung mit klar unterscheidbarer
 * Mensch-/Agent-Provenienz.
 *
 * EIGENE, neue Seite (verlauf.html/verlauf.js), NICHT app.js/index.html
 * veraendert - siehe Aufgabenstellung: ein Sibling-Agent baut parallel
 * TICKET-F02 auf app.js/index.html, eine eigene Seite haelt Merge-Konflikte
 * klein.
 *
 * Struktur/Stil bewusst analog zu app.js (TICKET-F01) uebernommen, siehe dort
 * fuer die ausfuehrlichere Begruendung der Konventionen (Datenzugriff/
 * Rendering-Trennung, escapeHtml ueberall, Fail-safe-Fehlerbehandlung,
 * API_BASE per URL-Parameter ueberschreibbar).
 *
 * Design-Leitplanken aus .claude/agents/role/frontend-dev.md (nicht
 * verhandelbar), hier konkret umgesetzt:
 *   1. PGP/LLM-Verschmelzung: nicht anwendbar - GET /verlauf liefert (Stand
 *      B06) pro Eintrag keine mu/sigma/tau-Rohwerte, siehe Hinweis unten und
 *      im README.md dieses Ordners ("Abweichung von Frontend-Backlog.md
 *      Abschnitt 2.3 Punkt 4"). Es gibt hier nichts zu verschmelzen, weil es
 *      nichts Getrenntes zum Anzeigen gibt - keine stillschweigende Annahme,
 *      sondern eine dokumentierte Backend-Datenluecke.
 *   2. Vorschlag != Ausfuehrung: diese Seite ist reine Leseansicht ohne jeden
 *      Aktions-Button - nicht anwendbar.
 *   3. Provenienz erzwingen: betrifft F03 (Entscheidungserfassung). Hier
 *      (F05) geht es um die LESE-Seite derselben Anforderung aus
 *      Systemgrenzen.md Teil D: jede bereits gespeicherte Entscheidung MUSS
 *      klar als "mensch" oder "agent" erkennbar sein, nicht nur als
 *      Textfeld irgendwo - umgesetzt ueber ein eigenes, farbig UND per
 *      Icon/Text unterscheidbares Provenienz-Badge (siehe
 *      renderProvenienzBadge) plus Erklaertext, was "agent" hier bedeutet
 *      (automatisch propagiert, TICKET-B08), damit es fuer Jens nicht wie
 *      eine geheimnisvolle Blackbox-Entscheidung wirkt.
 *   4. Vertrauensstufe von RAG-Kontext: nicht anwendbar - GET /verlauf
 *      liefert keine RAG-Treffer, das ist F02s Bereich.
 *   5. Fail-safe statt fail-open: jeder Fehlerfall (Netzwerk, HTTP-Fehler,
 *      unerwartete Response-Form) blockiert sichtbar mit einer Fehlerbox
 *      statt eine leere oder alte Liste stillschweigend als aktuell
 *      auszugeben (siehe renderError, nie renderVerlauf mit unvollstaendigen
 *      Daten). Eine WIRKLICH leere Liste (0 Entscheidungen bisher) ist ein
 *      legitimer, sichtbar anders dargestellter Zustand (renderEmpty) - kein
 *      Fehler, aber auch keine stillschweigend generierte "Liste".
 *
 * TICKET-F07 (step8-live-test/Produkt-Backlog/TICKET-F07-Kosten-Transparenz.md):
 * ergaenzt einen Kosten-Transparenz-Kasten (renderKostenBox), der GET /kalibrierung
 * (TICKET-F06, ../api.py) laedt und anzeigt, wie oft/wofuer das LLM ueberhaupt
 * aufgerufen wird. WICHTIGE, EHRLICHE ABWEICHUNG von der urspruenglichen
 * Ticket-Formulierung ("Erkennbar, dass ein LLM-Ranking nur fuer Eskalationsfaelle
 * angefragt wurde") und von Frontend-Backlog.md Abschnitt 6: das stimmt in der
 * AKTUELLEN Architektur so NICHT - step6-calibration/main.py ruft das LLM genau
 * EINMAL pro Kalibrierungslauf fuer ALLE offenen Auftraege gemeinsam auf (ein
 * einziger Anthropic-Tool-Use-Call, keine Eskalations-Vorfilterung). Das ist kein
 * Bug, sondern strukturell zwingend: der Eskalationsstatus (ampel_status) wird erst
 * AUS diesem LLM-Ranking abgeleitet (tau = Rangdifferenz PGP vs. LLM) - eine
 * Vorfilterung auf "nur Eskalationsfaelle" ist ein Henne-Ei-Problem, bevor das
 * Ranking existiert, ist unbekannt, welche Faelle eskalieren wuerden. Statt eine
 * falsche Behauptung anzuzeigen ("nur bei Eskalation angefragt"), zeigt
 * renderKostenBox die tatsaechlich zutreffende, wirtschaftlich ebenso relevante
 * Eigenschaft (User Story #12, Kernanliegen "nicht pauschal fuer jede
 * Entscheidung"): KEINE Planer-Entscheidung (POST /entscheidung, s. ../api.py)
 * loest jemals einen LLM-Call aus - die gesamte LLM-Nutzung ist der EINE
 * gebuendelte Kalibrierungslauf, sichtbar mit Zeitstempel und Auftragsanzahl.
 * Diese Abweichung wird hier UND im UI-Text selbst dokumentiert, nicht
 * stillschweigend "passend gemacht".
 *
 * Kein Build-Schritt, kein Framework - siehe frontend/README.md.
 */

(function () {
  "use strict";

  // Gleicher Default wie app.js (TICKET-F01) - passt zum
  // docker-compose-Port-Mapping "8007:8000". Ueberschreibbar ohne
  // Code-Aenderung, z. B. verlauf.html?api=http://andere-adresse:8007.
  const DEFAULT_API_BASE = "http://localhost:8007";

  function resolveApiBase() {
    const params = new URLSearchParams(window.location.search);
    return params.get("api") || window.PMPLUS_API_BASE || DEFAULT_API_BASE;
  }

  const API_BASE = resolveApiBase();

  // --- Provenienz-Sprache ---------------------------------------------------
  // Systemgrenzen.md Teil D / Leitplanke 3 (frontend-dev.md): "mensch" und
  // "agent" muessen optisch klar unterscheidbar sein, nicht nur ein
  // Textfeld. "agent" bedeutet hier konkret TICKET-B08-Propagation - EIN
  // Mensch hat fuer einen AEHNLICHEN Auftrag entschieden, das System hat die
  // Entscheidung automatisch fuer diesen Auftrag uebernommen. Wortlaut
  // bewusst erklaerend, damit es fuer Jens nicht wie eine geheimnisvolle
  // Blackbox-Entscheidung wirkt (Aufgabenstellung).
  const PROVENIENZ = {
    mensch: {
      icon: "\u{1F464}", // 👤
      symbol: "M",
      label: "Mensch entschieden",
      explain:
        "Ein Mensch hat diese Entscheidung direkt fuer diesen Auftrag getroffen.",
    },
    agent: {
      icon: "\u{1F916}", // 🤖
      symbol: "A",
      label: "Automatisch übernommen",
      explain:
        "Kein Mensch hat diesen Auftrag einzeln geprüft. Ein Mensch hat für einen " +
        "ähnlichen Auftrag (gleiches Produkt, nahes Fälligkeitsdatum) entschieden " +
        "– das System hat diese Entscheidung automatisch für diesen Auftrag " +
        "übernommen (Propagation, begrenzt auf wenige Fälle je Ursprungsentscheidung).",
    },
    // Fail-safe: ein unbekannter/fehlender entschieden_von-Wert (z. B. durch
    // eine zukuenftige Backend-Aenderung) wird NIE stillschweigend als
    // "mensch" interpretiert - das waere die gefaehrlichere Fehlrichtung
    // (eine Automatik-Entscheidung koennte sich als menschliches Urteil
    // ausgeben). Stattdessen ein eigener, klar als unklar erkennbarer
    // Zustand.
    unbekannt: {
      icon: "❓", // ❓
      symbol: "?",
      label: "Herkunft unbekannt",
      explain:
        "Für diesen Eintrag konnte nicht bestimmt werden, ob ein Mensch oder das " +
        "System entschieden hat. Das wird NICHT als menschliche Entscheidung " +
        "gewertet - im Zweifel gilt der Eintrag als ungeklärt.",
    },
  };

  function provenienzMeta(entschieden_von) {
    if (entschieden_von === "mensch" || entschieden_von === "agent") {
      return PROVENIENZ[entschieden_von];
    }
    return PROVENIENZ.unbekannt;
  }

  // --- wahl in verstaendliche Sprache ---------------------------------------
  // Rohwerte aus store.py/api.py (CHECK-Constraint: 'folgt_pgp', 'folgt_llm',
  // 'eigene_reihenfolge') - Wortlaut angelehnt an die Ampel-/PGP-Sprache aus
  // Konzept-README.md ("PGP" = Preference GP, volle Datenlage; "LLM" =
  // eingeschraenkter Kontext, siehe app.js).
  const WAHL = {
    folgt_pgp: "folgt PGP-Empfehlung",
    folgt_llm: "folgt LLM-Empfehlung",
    eigene_reihenfolge: "eigene Reihenfolge des Planers",
  };

  function wahlLabel(wahl) {
    return WAHL[wahl] || `Unbekannter Wert ("${wahl}")`;
  }

  // --- Datenzugriff ----------------------------------------------------------

  async function fetchVerlauf() {
    let response;
    try {
      response = await fetch(`${API_BASE}/verlauf`);
    } catch (networkError) {
      throw new FetchFailure(
        "Der Entscheidungsverlauf konnte nicht geladen werden (Netzwerkfehler). " +
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
    if (!data || !Array.isArray(data.verlauf)) {
      throw new FetchFailure(
        "Antwort des Backends hatte nicht die erwartete Form " +
          '(Feld "verlauf" fehlt oder ist keine Liste).',
        null
      );
    }
    return data.verlauf;
  }

  class FetchFailure extends Error {
    constructor(message, cause) {
      super(message);
      this.name = "FetchFailure";
      this.cause = cause;
    }
  }

  // TICKET-F07: laedt GET /kalibrierung (TICKET-F06, bereits vorhanden - kein
  // neuer Backend-Endpunkt fuer diesen Kosten-Transparenz-Hinweis noetig).
  // Bewusst eine EIGENE, von fetchVerlauf() unabhaengige Funktion: schlaegt sie
  // fehl, soll das den eigentlichen Audit-Trail (die Kernfunktion dieser Seite)
  // NICHT blockieren (s. renderKostenBox/load).
  async function fetchKalibrierung() {
    let response;
    try {
      response = await fetch(`${API_BASE}/kalibrierung`);
    } catch (networkError) {
      throw new FetchFailure(
        "Kosten-Transparenz-Daten konnten nicht geladen werden (Netzwerkfehler).",
        networkError
      );
    }
    if (!response.ok) {
      throw new FetchFailure(
        `Backend antwortete mit Status ${response.status}.`,
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
    return data;
  }

  // --- Sortierung ------------------------------------------------------------
  // AC: "Chronologische Liste". Die API liefert bereits ASC nach zeitstempel
  // sortiert (api.py/store.py: "ORDER BY zeitstempel ASC") - hier trotzdem
  // defensiv erneut sortiert, damit die UI nicht blind auf eine
  // Server-Eigenschaft vertraut, die sich unbemerkt aendern koennte (gleiches
  // Muster wie sortByPgpRank in app.js). Neueste zuerst ist fuer einen
  // Audit-Trail die ueblichere Lesereihenfolge (Jens will i. d. R. zuerst
  // sehen, was zuletzt passiert ist) - deshalb hier absteigend, das Backend
  // selbst bleibt aufsteigend (unveraendert, ausserhalb des Scopes).
  function sortByZeitstempelDesc(verlauf) {
    return [...verlauf].sort((a, b) =>
      String(b.zeitstempel).localeCompare(String(a.zeitstempel))
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
      // Fail-safe: kaputtes/unerwartetes Datumsformat wird nicht verschluckt,
      // sondern der Rohwert sichtbar gezeigt, damit nichts stillschweigend
      // fehlt.
      return `${iso} (Format nicht erkannt)`;
    }
    return date.toLocaleString("de-DE", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  }

  function renderProvenienzBadge(entschieden_von) {
    const meta = provenienzMeta(entschieden_von);
    return `
      <span class="provenienz-badge" data-provenienz="${escapeHtml(entschieden_von)}">
        <span class="provenienz-icon" aria-hidden="true">${meta.icon}</span>
        <span aria-hidden="true">${meta.symbol}</span>
        ${escapeHtml(meta.label)}
      </span>
    `;
  }

  function renderVerlaufEntry(entry) {
    const meta = provenienzMeta(entry.entschieden_von);
    const begruendungText =
      entry.begruendung && String(entry.begruendung).trim()
        ? entry.begruendung
        : null;
    const eigeneReihenfolgeBlock =
      entry.wahl === "eigene_reihenfolge" && entry.eigene_reihenfolge
        ? `<p class="verlauf-eigene-reihenfolge">
             <span class="label">Eigene Reihenfolge</span>
             ${escapeHtml(entry.eigene_reihenfolge)}
           </p>`
        : "";

    return `
      <li class="verlauf-entry" data-provenienz="${escapeHtml(entry.entschieden_von)}">
        <div class="verlauf-row">
          <div class="verlauf-main">
            <div class="verlauf-order-id">${escapeHtml(entry.order_id)}</div>
            <div class="verlauf-wahl">${escapeHtml(wahlLabel(entry.wahl))}</div>
          </div>
          ${renderProvenienzBadge(entry.entschieden_von)}
          <div class="verlauf-zeitstempel">${escapeHtml(formatZeitstempel(entry.zeitstempel))}</div>
        </div>
        <p class="provenienz-explain">${escapeHtml(meta.explain)}</p>
        ${eigeneReihenfolgeBlock}
        <div class="verlauf-begruendung">
          <span class="label">Begründung</span>
          ${begruendungText ? escapeHtml(begruendungText) : "(keine Begründung übermittelt)"}
        </div>
      </li>
    `;
  }

  function renderVerlauf(verlauf) {
    const list = document.getElementById("verlauf-list");
    list.innerHTML = verlauf.map(renderVerlaufEntry).join("");
    list.hidden = false;
    clearStatus();
  }

  function renderEmpty() {
    document.getElementById("verlauf-list").hidden = true;
    showStatus(
      '<p class="empty-state">Es liegen noch keine Entscheidungen im Verlauf vor.</p>'
    );
  }

  function formatZeitpunktKurz(iso) {
    if (!iso) return "unbekannter Zeitpunkt";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return String(iso);
    return date.toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" });
  }

  // TICKET-F07: zeigt die tatsaechlich zutreffende Kosten-Eigenschaft (s.
  // Modulkopf fuer die ausfuehrliche Begruendung der Abweichung von der
  // urspruenglichen Ticket-Formulierung) statt einer falschen Behauptung.
  // aktuell === null (Feld existiert, aber kein Lauf bisher) wird explizit
  // als eigener Zustand gezeigt, nicht mit dem Fehlerfall verwechselt.
  function renderKostenBox(aktuell) {
    const section = document.getElementById("kosten-section");
    if (!aktuell) {
      section.innerHTML = `
        <p class="kosten-hinweis">
          💶 <strong>Kosten-Transparenz:</strong> Noch kein protokollierter
          Kalibrierungslauf (Step 6) gefunden - keine LLM-Nutzungsdaten verfügbar.
        </p>
      `;
      return;
    }
    section.innerHTML = `
      <p class="kosten-hinweis">
        💶 <strong>Kosten-Transparenz:</strong> Keine Planer-Entscheidung auf
        dieser Seite löst einen LLM-Aufruf aus. Die gesamte LLM-Nutzung ist ein
        <strong>einziger, gebündelter API-Call</strong> pro Kalibrierungslauf
        (Step 6) für <strong>alle</strong> offenen Aufträge gemeinsam - zuletzt
        am ${escapeHtml(formatZeitpunktKurz(aktuell.zeitstempel))} für
        ${escapeHtml(aktuell.n_auftraege)} Aufträge (kein Call pro Auftrag,
        kein Call pro Entscheidung).
      </p>
      <p class="kosten-hinweis-einschraenkung">
        Hinweis zur Genauigkeit: dieser eine Call deckt aktuell ALLE offenen
        Aufträge ab, nicht nur die später als Eskalation markierten Fälle - der
        Eskalationsstatus wird ja erst aus diesem Ranking abgeleitet
        (<a href="kalibrierung.html">Details unter Kalibrierungs-Gesundheit</a>).
      </p>
    `;
  }

  function renderKostenBoxError(err) {
    const section = document.getElementById("kosten-section");
    section.innerHTML = `
      <p class="kosten-hinweis kosten-hinweis-fehler" role="alert">
        💶 <strong>Kosten-Transparenz derzeit nicht verfügbar:</strong>
        ${escapeHtml(err.message)}
      </p>
    `;
  }

  function showStatus(html) {
    document.getElementById("status-region").innerHTML = html;
  }

  function clearStatus() {
    document.getElementById("status-region").innerHTML = "";
  }

  function renderLoading() {
    document.getElementById("verlauf-list").hidden = true;
    showStatus('<p class="loading">Verlauf wird geladen …</p>');
  }

  function renderError(err) {
    document.getElementById("verlauf-list").hidden = true;
    showStatus(`
      <div class="error-box" role="alert">
        <h2>Verlauf konnte nicht angezeigt werden</h2>
        <p>${escapeHtml(err.message)}</p>
        <button id="retry-btn" type="button">Erneut versuchen</button>
      </div>
    `);
    document.getElementById("retry-btn").addEventListener("click", load);
  }

  // --- Orchestrierung --------------------------------------------------------

  // TICKET-F07: unabhaengig vom eigentlichen Verlauf geladen - ein Fehler hier
  // (z. B. Step 6 noch nie gelaufen) darf den Audit-Trail selbst nicht
  // blockieren, deshalb eigener try/catch statt Teil von load().
  async function loadKosten() {
    try {
      const data = await fetchKalibrierung();
      renderKostenBox(data.aktuell);
    } catch (err) {
      renderKostenBoxError(err);
    }
  }

  async function load() {
    renderLoading();
    try {
      const verlauf = await fetchVerlauf();
      if (verlauf.length === 0) {
        renderEmpty();
        return;
      }
      renderVerlauf(sortByZeitstempelDesc(verlauf));
    } catch (err) {
      renderError(err);
    }
  }

  function init() {
    document.getElementById("reload-btn").addEventListener("click", load);
    load();
    loadKosten();
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
      provenienzMeta,
      wahlLabel,
      sortByZeitstempelDesc,
      formatZeitstempel,
      PROVENIENZ,
      WAHL,
      // TICKET-F07
      formatZeitpunktKurz,
      renderKostenBox,
      renderKostenBoxError,
      fetchKalibrierung,
      FetchFailure,
    };
  }
})();
