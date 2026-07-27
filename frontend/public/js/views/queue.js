/*
 * js/views/queue.js - Agentic-PMPlus Frontend
 * TICKET-F01: Auftrags-Warteschlange mit Ampel-Status.
 *
 * AC (TICKET-F01-Warteschlange.md):
 * - Liste aus GET /eskalationen, sortiert nach PGP-Rang.
 * - Ampel-Sprache exakt aus Konzept-README.md (siehe js/format.js).
 * - "unbekannt" als eigener, sichtbarer Zustand - nie als 🟢 dargestellt.
 */
import { getEskalationen, ApiError } from "../api.js";
import { ampelInfo } from "../format.js";

export async function renderQueue() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <section class="view">
      <h1>Auftrags-Warteschlange</h1>
      <p class="view-intro">
        Alle offenen Aufträge, sortiert nach PGP-Rang. Der Ampel-Status zeigt, ob PGP und
        LLM übereinstimmen und wie sicher sich der PGP dabei selbst ist
        (siehe <a href="#/kalibrierung" data-route="/kalibrierung">Kalibrierungs-Gesundheit</a>
        für Hintergrund).
      </p>
      <div id="queue-content"><p class="loading">Lade Warteschlange…</p></div>
    </section>
  `;

  const content = document.getElementById("queue-content");
  let eskalationen;
  try {
    eskalationen = await getEskalationen();
  } catch (err) {
    renderQueueError(content, err);
    return;
  }

  if (!Array.isArray(eskalationen) || eskalationen.length === 0) {
    content.innerHTML = `<p class="empty-state">Keine offenen Aufträge gefunden.</p>`;
    return;
  }

  const sorted = [...eskalationen].sort((a, b) => a.pgp.rank - b.pgp.rank);

  const unbekanntCount = sorted.filter((e) => e.ampel_status === "unbekannt").length;
  const banner = unbekanntCount > 0
    ? `<p class="warning-banner">
         ⚠ Für ${unbekanntCount} von ${sorted.length} Aufträgen ist noch keine Kalibrierung
         (τ₀/σ₀) verfügbar. Diese Aufträge sind als <strong>"Kalibrierung noch nicht
         verfügbar"</strong> markiert und werden NICHT automatisch als unbedenklich
         behandelt - bitte wie einen offenen Prüffall betrachten.
       </p>`
    : "";

  content.innerHTML = `
    ${banner}
    <table class="queue-table">
      <thead>
        <tr>
          <th>PGP-Rang</th>
          <th>Auftrag</th>
          <th>Ampel-Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        ${sorted.map(renderRow).join("")}
      </tbody>
    </table>
  `;
}

function renderRow(eskalation) {
  const info = ampelInfo(eskalation.ampel_status);
  const rawAmpel = eskalation.ampel_status === "unbekannt" ? "unbekannt" : eskalation.ampel_status;
  return `
    <tr class="queue-row ${info.cssClass}">
      <td class="queue-row__rank">#${eskalation.pgp.rank}</td>
      <td class="queue-row__order">
        <span class="order-id">${escapeHtml(eskalation.order_id)}</span>
      </td>
      <td class="queue-row__ampel">
        <span class="ampel-badge ${info.cssClass}" title="${escapeHtml(info.beschreibung)}">
          <span class="ampel-badge__emoji">${rawAmpel === "unbekannt" ? "❔" : rawAmpel}</span>
          <span class="ampel-badge__label">${escapeHtml(info.label)}</span>
        </span>
      </td>
      <td class="queue-row__action">
        <a class="button button--secondary" href="#/order/${encodeURIComponent(eskalation.order_id)}" data-route="/order">
          Review öffnen
        </a>
      </td>
    </tr>
  `;
}

function renderQueueError(content, err) {
  // Fail-safe statt fail-open: kein leerer/alter Zustand, sondern ein sichtbarer,
  // blockierender Fehlerhinweis (frontend-dev.md, Leitplanke 5).
  const detail = err instanceof ApiError ? err.message : String(err);
  content.innerHTML = `
    <div class="error-banner" role="alert">
      <strong>Warteschlange konnte nicht geladen werden.</strong>
      <p>${escapeHtml(detail)}</p>
      <p>Es werden absichtlich keine alten/leeren Daten angezeigt, solange der Server
         nicht erreichbar ist.</p>
      <button id="queue-retry">Erneut versuchen</button>
    </div>
  `;
  document.getElementById("queue-retry").addEventListener("click", renderQueue);
}

export function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
