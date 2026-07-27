/*
 * js/views/orderDetail.js - Agentic-PMPlus Frontend
 * TICKET-F02 (Eskalations-Review) + TICKET-F03 (Entscheidungserfassung).
 *
 * Bewusst als EIN Bildschirm mit zwei klar getrennten, stufenweise freigeschalteten
 * Phasen gebaut statt zwei getrennter Routen:
 *   Phase 1 "Review"     - PGP- und LLM-Einschätzung NEBENEINANDER, nie vermischt.
 *   Phase 2 "Entscheidung" - erst sichtbar/aktivierbar, nachdem Phase 1 bestätigt wurde.
 * Begruendung siehe README.md dieses Ordners ("Warum ein Bildschirm statt zwei Routen").
 * Das erfuellt die AC aus TICKET-F02 ("erst beide Einschaetzungen sehen, dann erst
 * Wechsel zur Entscheidungserfassung moeglich") robuster als ein Routen-Wechsel, der
 * sich per direktem Link umgehen liesse.
 *
 * Propagations-Vorschau (TICKET-F03 AC): POST /entscheidung ist die EINZIGE Quelle fuer
 * propagierte_faelle - es gibt (Stand jetzt) keinen side-effect-freien Vorschau-Endpunkt
 * im Backend. Deshalb: zweistufiger Bestaetigungs-Dialog VOR dem echten Absenden, der
 * transparent macht, dass Propagation passieren KANN, plus unmittelbar nach dem
 * tatsaechlichen Absenden die ECHTE Liste (aus der Server-Antwort) - bevor der Planer den
 * Bildschirm verlaesst, nicht erst spaeter im Audit-Trail nachschlagen muss. Siehe
 * frontend/README.md fuer die vollstaendige Begruendung dieser bewussten Abweichung.
 */
import { getEskalationen, postEntscheidung, ApiError } from "../api.js";
import { ampelInfo, vertrauensstufeInfo, formatNumber, WAHL_LABELS } from "../format.js";
import { escapeHtml } from "./queue.js";

export async function renderOrderDetail({ orderId }) {
  const app = document.getElementById("app");
  app.innerHTML = `<section class="view"><p class="loading">Lade Auftragsdaten…</p></section>`;

  let alle;
  try {
    alle = await getEskalationen();
  } catch (err) {
    renderDetailError(app, err);
    return;
  }

  const eskalation = alle.find((e) => e.order_id === orderId);
  if (!eskalation) {
    app.innerHTML = `
      <section class="view">
        <p class="error-banner">Auftrag "${escapeHtml(orderId)}" wurde in /eskalationen nicht gefunden
          (evtl. bereits entschieden oder ID falsch). <a href="#/">Zurück zur Warteschlange</a></p>
      </section>`;
    return;
  }

  const alleOrderIds = alle.map((e) => e.order_id);
  renderPhases(app, eskalation, alleOrderIds);
}

function renderPhases(app, eskalation, alleOrderIds) {
  const info = ampelInfo(eskalation.ampel_status);
  const rawAmpel = eskalation.ampel_status === "unbekannt" ? "❔" : eskalation.ampel_status;

  app.innerHTML = `
    <section class="view">
      <p class="breadcrumb"><a href="#/">← Zurück zur Warteschlange</a></p>
      <h1>Eskalations-Review: ${escapeHtml(eskalation.order_id)}</h1>

      <div class="ampel-banner ${info.cssClass}">
        <span class="ampel-banner__emoji">${rawAmpel}</span>
        <div>
          <strong>${escapeHtml(info.label)}</strong>
          <p>${escapeHtml(info.beschreibung)}</p>
        </div>
      </div>

      <div class="review-columns">
        <article class="review-card review-card--pgp">
          <h2>PGP-Einschätzung <span class="badge badge--pgp">unabhängige Einschätzung 1</span></h2>
          <p class="review-card__rank">Rang <strong>#${eskalation.pgp.rank}</strong></p>
          <dl class="metric-list">
            <dt>μ (Rang-Prognose)</dt>
            <dd>${formatNumber(eskalation.pgp.mu, 3)}
              <span class="metric-caption">„Das ist unsere Einschätzung der Priorität.“</span>
            </dd>
            <dt>σ (Selbstunsicherheit)</dt>
            <dd>${formatNumber(eskalation.pgp.sigma, 3)}
              <span class="metric-caption">„Und so sicher sind wir uns dabei.“ — Einordnung: siehe Ampel-Status oben (${escapeHtml(info.label)}).</span>
            </dd>
          </dl>
          <h3>Begründung des PGP</h3>
          <p class="begruendung begruendung--pgp">${escapeHtml(eskalation.pgp.begruendung) || "<em>Keine Begründung vom PGP übermittelt.</em>"}</p>
        </article>

        <article class="review-card review-card--llm">
          <h2>LLM-Einschätzung <span class="badge badge--llm">unabhängige Einschätzung 2</span></h2>
          <p class="review-card__rank">Rang <strong>#${eskalation.llm.rank}</strong></p>
          <dl class="metric-list">
            <dt>τ (Meinungsverschiedenheit zu PGP)</dt>
            <dd>${formatNumber(eskalation.llm.tau, 3)}
              <span class="metric-caption">Einordnung: siehe Ampel-Status oben (${escapeHtml(info.label)}).</span>
            </dd>
          </dl>
          <h3>Begründung des LLM</h3>
          <p class="begruendung begruendung--llm">${escapeHtml(eskalation.llm.begruendung) || "<em>Keine Begründung vom LLM übermittelt.</em>"}</p>
          ${renderRagDocs(eskalation.llm.matched_rag_docs)}
          <p class="cost-note">
            ℹ Kosten-Hinweis: Diese LLM-Einschätzung stammt aus dem gemeinsamen
            Planungslauf für alle aktuell offenen Aufträge (ein Batch-API-Call für den
            gesamten Lauf, siehe <code>step6-calibration/main.py</code>) — es wird nicht
            pro Auftrag oder pro Eskalation ein zusätzlicher LLM-Call ausgelöst.
          </p>
        </article>
      </div>

      <div id="phase-gate" class="phase-gate">
        <p>Bevor eine Entscheidung erfasst werden kann, müssen beide unabhängigen
           Einschätzungen (PGP und LLM) betrachtet worden sein.</p>
        <button id="btn-reviewed" class="button button--primary">
          Beide Einschätzungen geprüft → weiter zur Entscheidung
        </button>
      </div>

      <div id="decision-phase" class="decision-phase" hidden></div>
    </section>
  `;

  document.getElementById("btn-reviewed").addEventListener("click", () => {
    document.getElementById("phase-gate").hidden = true;
    const decisionPhase = document.getElementById("decision-phase");
    decisionPhase.hidden = false;
    renderDecisionForm(decisionPhase, eskalation, alleOrderIds);
    decisionPhase.scrollIntoView({ behavior: "smooth" });
  });
}

function renderRagDocs(docs) {
  if (!docs || docs.length === 0) {
    return `<p class="rag-docs rag-docs--empty">Kein RAG-Dokument für diese Begründung herangezogen.</p>`;
  }
  return `
    <div class="rag-docs">
      <h4>Herangezogene RAG-Dokumente</h4>
      <ul>
        ${docs.map(renderRagDoc).join("")}
      </ul>
    </div>
  `;
}

function renderRagDoc(doc) {
  const trust = vertrauensstufeInfo(doc.vertrauensstufe);
  const title = doc.title || `(Titel unbekannt, doc_id="${doc.doc_id}" nicht auflösbar)`;
  return `
    <li class="rag-doc">
      <span class="rag-doc__title">${escapeHtml(title)}</span>
      <span class="trust-badge ${trust.cssClass}" title="Vertrauensstufe">
        ${trust.icon} ${escapeHtml(trust.label)}
      </span>
    </li>
  `;
}

function renderDecisionForm(container, eskalation, alleOrderIds) {
  container.innerHTML = `
    <h2>Entscheidung erfassen</h2>
    <form id="decision-form" novalidate>
      <fieldset>
        <legend>Wahlmöglichkeit</legend>
        <label class="radio-option">
          <input type="radio" name="wahl" value="folgt_pgp" checked />
          ${WAHL_LABELS.folgt_pgp} (Rang #${eskalation.pgp.rank})
        </label>
        <label class="radio-option">
          <input type="radio" name="wahl" value="folgt_llm" />
          ${WAHL_LABELS.folgt_llm} (Rang #${eskalation.llm.rank})
        </label>
        <label class="radio-option">
          <input type="radio" name="wahl" value="eigene_reihenfolge" />
          ${WAHL_LABELS.eigene_reihenfolge}
        </label>
      </fieldset>

      <div id="eigene-reihenfolge-block" hidden>
        <p class="hint">Optional: eigene Reihenfolge der offenen Aufträge (per Pfeiltasten anpassen).
           Wird leer gelassen, meldet die Entscheidung nur die Abweichung selbst, ohne konkrete
           alternative Reihenfolge.</p>
        <ol id="reorder-list" class="reorder-list"></ol>
      </div>

      <label class="form-field">
        <span id="begruendung-label">Kurzbegründung (optional)</span>
        <textarea id="begruendung" name="begruendung" rows="3"
          placeholder="Warum folgen Sie weder PGP noch LLM? (Pflichtfeld bei „eigene Reihenfolge“)"></textarea>
        <span id="begruendung-error" class="field-error" hidden>
          Pflichtfeld: Bei „eigene Reihenfolge“ weichen Sie von BEIDEN unabhängigen
          Einschätzungen ab – dafür ist laut Governance-Vorgabe (Systemgrenzen Teil D)
          eine nachvollziehbare Kurzbegründung erforderlich, kein reiner Klick.
        </span>
      </label>

      <div class="disclosure-note">
        <strong>Hinweis zu Folgeeffekten:</strong> Diese Entscheidung kann automatisch auf
        ähnliche, noch nicht entschiedene Aufträge übertragen werden (Propagation, mit
        harter Obergrenze N je Entscheidung). Eine exakte Vorschau der betroffenen Aufträge
        ist technisch erst nach dem tatsächlichen Absenden möglich (das Backend hat aktuell
        keinen separaten Vorschau-Endpunkt) – die vollständige Liste wird Ihnen unmittelbar
        nach dem Absenden auf dieser Seite angezeigt, bevor Sie weitergehen.
      </div>

      <button type="submit" class="button button--secondary">
        Weiter zur Bestätigung
      </button>
    </form>
    <div id="confirm-block" hidden></div>
    <div id="result-block" hidden></div>
  `;

  const radios = container.querySelectorAll('input[name="wahl"]');
  const eigeneBlock = container.querySelector("#eigene-reihenfolge-block");
  const reorderList = container.querySelector("#reorder-list");
  const begruendungLabel = container.querySelector("#begruendung-label");

  let currentOrder = [...alleOrderIds];
  renderReorderList(reorderList, currentOrder, (newOrder) => {
    currentOrder = newOrder;
  });

  function syncWahlUi() {
    const wahl = container.querySelector('input[name="wahl"]:checked').value;
    eigeneBlock.hidden = wahl !== "eigene_reihenfolge";
    begruendungLabel.textContent =
      wahl === "eigene_reihenfolge" ? "Kurzbegründung (Pflichtfeld)" : "Kurzbegründung (optional)";
  }
  radios.forEach((r) => r.addEventListener("change", syncWahlUi));
  syncWahlUi();

  container.querySelector("#decision-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const wahl = container.querySelector('input[name="wahl"]:checked').value;
    const begruendung = container.querySelector("#begruendung").value.trim();
    const begruendungError = container.querySelector("#begruendung-error");

    // Client-seitige Pflichtfeld-Sperre (zusaetzlich zur Server-400-Validierung,
    // frontend-dev.md Leitplanke 3 - "erzwingen, nicht nur anzeigen").
    if (wahl === "eigene_reihenfolge" && begruendung === "") {
      begruendungError.hidden = false;
      container.querySelector("#begruendung").focus();
      return;
    }
    begruendungError.hidden = true;

    renderConfirmStep(container, eskalation, {
      wahl,
      begruendung: begruendung || null,
      eigene_reihenfolge: wahl === "eigene_reihenfolge" ? currentOrder : null,
    });
  });
}

function renderReorderList(listEl, order, onChange) {
  function draw() {
    listEl.innerHTML = order
      .map(
        (id, i) => `
        <li>
          <span>${escapeHtml(id)}</span>
          <span class="reorder-controls">
            <button type="button" data-action="up" data-index="${i}" ${i === 0 ? "disabled" : ""}>↑</button>
            <button type="button" data-action="down" data-index="${i}" ${i === order.length - 1 ? "disabled" : ""}>↓</button>
          </span>
        </li>`,
      )
      .join("");
  }
  listEl.addEventListener("click", (event) => {
    const btn = event.target.closest("button[data-action]");
    if (!btn) return;
    const i = Number(btn.dataset.index);
    const j = btn.dataset.action === "up" ? i - 1 : i + 1;
    if (j < 0 || j >= order.length) return;
    [order[i], order[j]] = [order[j], order[i]];
    onChange(order);
    draw();
  });
  draw();
}

function renderConfirmStep(container, eskalation, decision) {
  container.querySelector("#decision-form").hidden = true;
  const confirmBlock = container.querySelector("#confirm-block");
  confirmBlock.hidden = false;
  confirmBlock.innerHTML = `
    <div class="confirm-card">
      <h3>Bestätigung erforderlich</h3>
      <p>Dies ist <strong>noch keine</strong> ausgeführte Aktion. Bitte prüfen Sie die
         Angaben – erst der Button unten löst die tatsächliche, im Audit-Trail als
         "Mensch"-Entscheidung erfasste Aktion aus.</p>
      <table class="confirm-summary">
        <tr><th>Auftrag</th><td>${escapeHtml(eskalation.order_id)}</td></tr>
        <tr><th>Wahl</th><td>${escapeHtml(WAHL_LABELS[decision.wahl])}</td></tr>
        <tr><th>Eigene Reihenfolge</th><td>${decision.eigene_reihenfolge ? escapeHtml(decision.eigene_reihenfolge.join(" → ")) : "– (nicht angegeben)"}</td></tr>
        <tr><th>Begründung</th><td>${decision.begruendung ? escapeHtml(decision.begruendung) : "– (keine angegeben)"}</td></tr>
      </table>
      <label class="checkbox-confirm">
        <input type="checkbox" id="confirm-checkbox" />
        Ich bestätige, dass ich diese Entscheidung als verantwortliche Person treffe
        (wird als "Mensch"-Entscheidung im Audit-Trail gespeichert).
      </label>
      <div class="confirm-actions">
        <button id="btn-cancel-confirm" class="button button--secondary">Zurück / Ändern</button>
        <button id="btn-final-confirm" class="button button--danger" disabled>
          Jetzt verbindlich entscheiden
        </button>
      </div>
      <div id="confirm-error"></div>
    </div>
  `;

  const checkbox = confirmBlock.querySelector("#confirm-checkbox");
  const finalBtn = confirmBlock.querySelector("#btn-final-confirm");
  checkbox.addEventListener("change", () => {
    finalBtn.disabled = !checkbox.checked;
  });
  confirmBlock.querySelector("#btn-cancel-confirm").addEventListener("click", () => {
    confirmBlock.hidden = true;
    container.querySelector("#decision-form").hidden = false;
  });
  finalBtn.addEventListener("click", async () => {
    finalBtn.disabled = true;
    finalBtn.textContent = "Wird gesendet…";
    try {
      const result = await postEntscheidung({
        order_id: eskalation.order_id,
        wahl: decision.wahl,
        eigene_reihenfolge: decision.eigene_reihenfolge,
        begruendung: decision.begruendung,
      });
      renderResult(container, eskalation, result);
    } catch (err) {
      const detail = err instanceof ApiError ? err.message : String(err);
      confirmBlock.querySelector("#confirm-error").innerHTML = `
        <p class="error-banner">Entscheidung konnte NICHT gespeichert werden: ${escapeHtml(detail)}
        Bitte erneut versuchen — es wurde nichts stillschweigend übernommen.</p>`;
      finalBtn.disabled = false;
      finalBtn.textContent = "Jetzt verbindlich entscheiden";
    }
  });
}

function renderResult(container, eskalation, result) {
  container.querySelector("#confirm-block").hidden = true;
  const resultBlock = container.querySelector("#result-block");
  resultBlock.hidden = false;

  const propagationHtml =
    result.propagierte_faelle && result.propagierte_faelle.length > 0
      ? `<p class="propagation-list">
           <strong>${result.propagierte_faelle.length} weitere(r) Auftrag/Aufträge</strong>
           wurde(n) automatisch mit derselben Entscheidung übernommen (Propagation,
           gedrosselt auf eine harte Obergrenze N):
         </p>
         <ul>${result.propagierte_faelle.map((id) => `<li>${escapeHtml(id)}</li>`).join("")}</ul>
         <p class="hint">Alle davon sind mit "entschieden_von: agent" im Audit-Trail sichtbar,
            nicht als eigenständiges menschliches Urteil.</p>`
      : `<p class="propagation-list">Keine weiteren Aufträge waren betroffen.</p>`;

  resultBlock.innerHTML = `
    <div class="result-card">
      <h3>✓ Entscheidung erfasst</h3>
      <p>Decision-ID <code>${result.decision_id}</code>, Zeitstempel ${escapeHtml(result.zeitstempel)}.</p>
      ${propagationHtml}
      <div class="result-actions">
        <a class="button button--secondary" href="#/verlauf" data-route="/verlauf">Zum Audit-Trail</a>
        <a class="button button--primary" href="#/" data-route="/">Zurück zur Warteschlange</a>
      </div>
    </div>
  `;
}

function renderDetailError(app, err) {
  const detail = err instanceof ApiError ? err.message : String(err);
  app.innerHTML = `
    <section class="view">
      <div class="error-banner" role="alert">
        <strong>Auftragsdaten konnten nicht geladen werden.</strong>
        <p>${escapeHtml(detail)}</p>
        <p><a href="#/">Zurück zur Warteschlange</a></p>
      </div>
    </section>
  `;
}
