/*
 * js/views/history.js - Agentic-PMPlus Frontend
 * TICKET-F05 (Audit-Trail) + TICKET-F07 (Kosten-Transparenz-Hinweis, hier abgelegt).
 *
 * AC (TICKET-F05-Audit-Trail.md):
 * - Chronologische Liste aus GET /verlauf.
 * - Mensch-/Agent-Provenienz optisch klar unterscheidbar (nicht nur Textfeld).
 */
import { getVerlauf, ApiError } from "../api.js";
import { formatZeitstempel, WAHL_LABELS } from "../format.js";
import { escapeHtml } from "./queue.js";

export async function renderHistory() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <section class="view">
      <h1>Audit-Trail</h1>
      <p class="view-intro">
        Chronologischer Verlauf aller erfassten Entscheidungen — sowohl direkt von einer
        Person getroffene als auch automatisch propagierte ("agent"). Die Unterscheidung
        ist absichtlich nicht nur ein Textfeld, sondern optisch (Farbe + Icon) hervorgehoben,
        da sie in <code>step2-limits/Systemgrenzen.md</code> Teil D als Governance-Anforderung
        benannt ist: ein automatisch propagierter Eintrag ist KEIN eigenständiges
        menschliches Urteil.
      </p>
      <div class="cost-note cost-note--standalone">
        ℹ Kosten-Transparenz: Ein LLM-Ranking wird pro Planungslauf einmalig für alle
        aktuell offenen Aufträge gemeinsam angefragt (<code>step6-calibration/main.py</code>),
        nicht für jeden einzelnen Auftrag separat und nicht erneut pro Eskalationsfall.
        Automatisch propagierte Entscheidungen (unten als "Agent" markiert) lösen
        <strong>keinen</strong> zusätzlichen LLM-Call aus — sie übernehmen ausschließlich
        eine bereits getroffene menschliche Entscheidung per Ähnlichkeitsheuristik
        (<code>propagation.py</code>), ohne erneuten Modellaufruf.
      </div>
      <div id="history-content"><p class="loading">Lade Verlauf…</p></div>
    </section>
  `;

  const content = document.getElementById("history-content");
  let eintraege;
  try {
    eintraege = await getVerlauf();
  } catch (err) {
    const detail = err instanceof ApiError ? err.message : String(err);
    content.innerHTML = `
      <div class="error-banner" role="alert">
        <strong>Verlauf konnte nicht geladen werden.</strong>
        <p>${escapeHtml(detail)}</p>
      </div>`;
    return;
  }

  if (!Array.isArray(eintraege) || eintraege.length === 0) {
    content.innerHTML = `<p class="empty-state">Noch keine Entscheidungen erfasst.</p>`;
    return;
  }

  content.innerHTML = `
    <table class="history-table">
      <thead>
        <tr>
          <th>Zeitstempel</th>
          <th>Auftrag</th>
          <th>Wahl</th>
          <th>Begründung</th>
          <th>Wer/Was hat entschieden</th>
        </tr>
      </thead>
      <tbody>
        ${eintraege.map(renderHistoryRow).join("")}
      </tbody>
    </table>
  `;
}

function renderHistoryRow(entry) {
  const isMensch = entry.entschieden_von === "mensch";
  const provenienzClass = isMensch ? "provenienz-mensch" : "provenienz-agent";
  const provenienzIcon = isMensch ? "🧑" : "🤖";
  const provenienzLabel = isMensch ? "Mensch" : "Agent (automatisch propagiert)";
  return `
    <tr class="${provenienzClass}">
      <td>${escapeHtml(formatZeitstempel(entry.zeitstempel))}</td>
      <td class="order-id">${escapeHtml(entry.order_id)}</td>
      <td>${escapeHtml(WAHL_LABELS[entry.wahl] || entry.wahl)}
        ${entry.eigene_reihenfolge ? `<div class="hint">Reihenfolge: ${escapeHtml(entry.eigene_reihenfolge)}</div>` : ""}
      </td>
      <td>${entry.begruendung ? escapeHtml(entry.begruendung) : "<em>–</em>"}</td>
      <td>
        <span class="provenienz-badge ${provenienzClass}">
          <span class="provenienz-badge__icon">${provenienzIcon}</span>
          <span>${escapeHtml(provenienzLabel)}</span>
        </span>
      </td>
    </tr>
  `;
}
