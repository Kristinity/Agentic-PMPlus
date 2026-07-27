/*
 * js/views/calibration.js - Agentic-PMPlus Frontend
 * TICKET-F06 (Kalibrierungs-Gesundheit, optional/Post-MVP).
 *
 * Bewusst NICHT in der Hauptnavigation (siehe index.html: nur ein unauffaelliger
 * Footer-Link), da diese Ansicht fuer die Person gedacht ist, die Step 6/7 betreut -
 * nicht fuer den taeglichen Produktionsplaner (Frontend-Konzept 2.3.5: Zielgruppe nicht
 * ueberladen).
 *
 * Snapshot- vs. Trend-Einschraenkung (siehe GET /kalibrierung-Docstring in api.py):
 * "Eskalationsrate ueber Zeit" ist vom Backend NICHT als Zeitreihe verfuegbar (jeder
 * Kalibrierungslauf ueberschreibt denselben Stand). Diese Ansicht zeigt deshalb bewusst
 * NUR den aktuellen Snapshot-Wert, klar als solchen beschriftet, statt einen Trend zu
 * erfinden (AC-Abweichung, siehe frontend/README.md und Task-Vorgabe).
 */
import { getKalibrierung, ApiError } from "../api.js";
import { formatNumber, formatZeitstempel } from "../format.js";
import { escapeHtml } from "./queue.js";

export async function renderCalibration() {
  const app = document.getElementById("app");
  app.innerHTML = `
    <section class="view view--admin">
      <p class="admin-flag">⚙ Techniker-Ansicht — nicht Teil des Hauptbildschirms für Produktionsplaner:innen.</p>
      <h1>Kalibrierungs-Gesundheit</h1>
      <div id="calibration-content"><p class="loading">Lade Kalibrierungsdaten…</p></div>
    </section>
  `;

  const content = document.getElementById("calibration-content");
  let daten;
  try {
    daten = await getKalibrierung();
  } catch (err) {
    const detail = err instanceof ApiError ? err.message : String(err);
    const notFound = err instanceof ApiError && err.status === 404;
    content.innerHTML = `
      <div class="error-banner" role="alert">
        <strong>${notFound ? "Noch keine Kalibrierung gelaufen." : "Kalibrierungsdaten konnten nicht geladen werden."}</strong>
        <p>${escapeHtml(detail)}</p>
        ${notFound ? `<p>Solange Step 6 (<code>kalibrierung.py</code>) nicht gelaufen ist, bleibt der
             Ampel-Status in der Warteschlange auf "unbekannt" — das ist der erwartete
             Fail-safe-Zustand, kein Fehler dieser Ansicht.</p>` : ""}
      </div>`;
    return;
  }

  content.innerHTML = `
    <div class="calibration-grid">
      <div class="calibration-card">
        <h3>τ₀ (Schwellenwert Meinungsverschiedenheit)</h3>
        <p class="calibration-value">${formatNumber(daten.tau0, 4)}</p>
        <p class="hint">Ziel-Eskalationsquote je Dimension: ${formatNumber(daten.escalation_rate_target * 100, 0)} %</p>
      </div>
      <div class="calibration-card">
        <h3>σ₀ (Schwellenwert Selbstunsicherheit)</h3>
        <p class="calibration-value">${formatNumber(daten.sigma0, 4)}</p>
        <p class="hint">Getrennt von τ₀ berechnet, nicht addiert/gleich gewichtet (Konzept-README.md).</p>
      </div>
      <div class="calibration-card">
        <h3>Eskalationsrate (Momentaufnahme)</h3>
        <p class="calibration-value">${daten.eskalationsrate === null ? "–" : formatNumber(daten.eskalationsrate * 100, 1) + " %"}</p>
        <p class="hint hint--warning">
          ⚠ Momentaufnahme des aktuellen Datenstands, KEINE Zeitreihe — das Backend
          historisiert Kalibrierungsläufe (Stand jetzt) nicht. Ein "über Zeit"-Verlauf
          würde hier erfundene Daten zeigen und wird deshalb bewusst nicht dargestellt.
        </p>
      </div>
      <div class="calibration-card">
        <h3>Anteil "Trügerische Ruhe" (🟡)</h3>
        <p class="calibration-value">${daten.truegerische_ruhe_anteil === null ? "–" : formatNumber(daten.truegerische_ruhe_anteil * 100, 1) + " %"}</p>
        <p class="hint">Anteil der Aufträge mit τ niedrig, aber σ hoch — Einigkeit, die
           laut PGP-Selbsteinschätzung nicht tragfähig ist.</p>
      </div>
    </div>

    <div class="calibration-meta">
      <p><strong>Bootstrap-Hinweis:</strong> ${escapeHtml(daten.bootstrap_hinweis)}</p>
      <p><strong>Systemgrenzen-Referenz:</strong> ${escapeHtml(daten.systemgrenzen_referenz)}</p>
      <p><strong>Bootstrap-Stichprobengröße:</strong> ${daten.n_bootstrap_orders} Aufträge</p>
      <p><strong>Berechnet am:</strong> ${escapeHtml(formatZeitstempel(daten.berechnet_am))}</p>
    </div>

    ${renderRiskCoverage(daten.risk_coverage)}
  `;
}

function renderRiskCoverage(rows) {
  if (!rows || rows.length === 0) return "";
  const byDimension = { tau: [], sigma: [] };
  rows.forEach((r) => {
    if (byDimension[r.dimension]) byDimension[r.dimension].push(r);
  });
  return `
    <h2>Risk-Coverage-Kurven (diagnostisch)</h2>
    <p class="hint">
      risk_proxy ist der kumulative Mittelwert der abgedeckten Werte — KEINE Fehlerrate
      gegen Grundwahrheit, siehe Docstring von <code>step6-calibration/kalibrierung.py</code>.
    </p>
    <div class="risk-coverage-columns">
      ${Object.entries(byDimension)
        .map(
          ([dim, values]) => `
        <div>
          <h3>Dimension: ${dim}</h3>
          <table class="risk-coverage-table">
            <thead><tr><th>Threshold</th><th>Coverage</th><th>Risk-Proxy</th></tr></thead>
            <tbody>
              ${values
                .map(
                  (v) => `<tr><td>${formatNumber(v.threshold, 3)}</td><td>${formatNumber(v.coverage * 100, 1)} %</td><td>${formatNumber(v.risk_proxy, 3)}</td></tr>`,
                )
                .join("")}
            </tbody>
          </table>
        </div>`,
        )
        .join("")}
    </div>
  `;
}
