/*
 * js/format.js - Agentic-PMPlus Frontend
 *
 * Zentrale Stelle fuer die bildhafte Sprache aus Konzept-README.md ("zentrale Idee",
 * 2x2-Matrix) - WIRD NUR HIER DEFINIERT UND SONST IMPORTIERT, damit die exakte
 * Formulierung nicht an mehreren Stellen leicht abweichend neu erfunden wird
 * (nicht verhandelbare Leitplanke: "diese Begriffe im UI-Text wiederverwenden, nicht
 * neu erfinden").
 *
 * WICHTIG (Scope-Disziplin, frontend-dev.md): dieses Modul erfindet KEINE eigene
 * Schwellenwert-/Kalibrierungslogik. Die qualitative Einordnung kommt ausschliesslich
 * aus dem von der API bereits berechneten `ampel_status` - das Frontend leitet nicht
 * selbststaendig her, ob ein einzelnes tau/sigma "hoch" oder "niedrig" ist (das waere
 * neue fachliche Kalibrierungslogik und nicht Aufgabe von frontend-dev).
 */

// Reihenfolge/Wortlaut 1:1 aus Konzept-README.md, Abschnitt "zentrale Idee", 2x2-Tabelle.
export const AMPEL_INFO = {
  "🟢": {
    // 🟢
    label: "Robuste Übereinstimmung",
    beschreibung:
      "LLM und PGP sind sich einig (τ niedrig), und PGP ist sich seiner Einschätzung sicher (σ niedrig) — läuft automatisch weiter, nur informativ.",
    cssClass: "ampel-gruen",
  },
  "🟡": {
    // 🟡
    label: "Trügerische Ruhe",
    beschreibung:
      "LLM und PGP sind sich einig (τ niedrig) — aber PGP ist sich bei genau diesem Auftrag selbst unsicher (σ hoch). Die Übereinstimmung könnte eine Sicherheit vortäuschen, die nicht existiert. Trotz Einigkeit prüfen.",
    cssClass: "ampel-gelb",
  },
  "🔴": {
    // 🔴
    label: "Klarer Fall für Experten-Review",
    beschreibung:
      "LLM und PGP sind unterschiedlicher Meinung (τ hoch) — unabhängig davon, wie sicher sich der PGP ist. Braucht eine menschliche Entscheidung.",
    cssClass: "ampel-rot",
  },
  unbekannt: {
    label: "Kalibrierung noch nicht verfügbar",
    beschreibung:
      "Die τ₀/σ₀-Kalibrierung (Schritt 6) ist für diesen Datenstand noch nicht gelaufen. Dieser Auftrag kann deshalb NICHT automatisch als unbedenklich eingestuft werden — er wird sicherheitshalber wie ein offener Prüffall behandelt, bis eine Kalibrierung vorliegt (Fail-safe-Prinzip).",
    cssClass: "ampel-unbekannt",
  },
};

export function ampelInfo(status) {
  return AMPEL_INFO[status] || AMPEL_INFO.unbekannt;
}

// Vertrauensstufen aus step4-context-engineering/gute-RAGs.md — Wortlaut/Werte kommen
// 1:1 von der API (matched_rag_docs[].vertrauensstufe). Hier nur Anzeige-Metadaten
// (Label/Icon/CSS-Klasse), keine neue fachliche Einordnung.
export const VERTRAUENSSTUFE_INFO = {
  "intern-verifiziert": {
    label: "Intern verifiziert",
    cssClass: "trust-verifiziert",
    icon: "✓",
  },
  "extern-ungeprueft": {
    label: "Extern, ungeprüft",
    cssClass: "trust-ungeprueft",
    icon: "!",
  },
};

export function vertrauensstufeInfo(stufe) {
  return (
    VERTRAUENSSTUFE_INFO[stufe] || {
      label: stufe ? `Unbekannte Vertrauensstufe (${stufe})` : "Vertrauensstufe unbekannt (Dokument-Metadaten fehlen)",
      cssClass: "trust-unbekannt",
      icon: "?",
    }
  );
}

export function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "–";
  return Number(value).toFixed(digits);
}

export function formatZeitstempel(iso) {
  if (!iso) return "–";
  try {
    const d = new Date(iso);
    return d.toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" });
  } catch (_e) {
    return iso;
  }
}

export const WAHL_LABELS = {
  folgt_pgp: "Folgt PGP-Vorschlag",
  folgt_llm: "Folgt LLM-Vorschlag",
  eigene_reihenfolge: "Eigene Reihenfolge (weicht von beiden ab)",
};
