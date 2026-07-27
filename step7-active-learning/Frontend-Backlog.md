# Frontend-Backlog – Agentic-PMPlus (Step 7)

**Stand:** 2026-07-27
**Grundlage:** `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`,
`step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md`,
`step8-live-test/Userstories.md`, `.claude/agents/role/frontend-dev.md`.
**Abhängigkeit:** Alle Items hier setzen die entsprechenden Backend-Endpunkte aus
`Backend-Backlog.md` voraus (insb. `GET /eskalationen`, `POST /entscheidung`,
`GET /verlauf`) – ohne Backend keine sinnvolle UI-Implementierung, nur Mock-Daten möglich.

---

## 1. Bildschirm: Auftrags-Warteschlange

**Titel:** Priorisierte Auftragsliste mit Ampel-Status
**User Story:** #1 (verlässliche Priorisierung), #4 (auch bei Sonderaufträgen/kleinen
Kunden verlässlich), #6 (weniger Zeit vor dem Rechner – nur relevante Fälle zeigen).
**Akzeptanzkriterien:**
- Liste aus `GET /eskalationen`, sortiert nach PGP-Rang.
- Ampel-Status (🟢/🟡/🔴) nach der 2×2-Matrix aus `Konzept-README.md` – **exakt deren
  Sprache verwenden** ("Robuste Übereinstimmung", "Trügerische Ruhe", "Klarer Fall für
  Experten-Review"), nicht neu formulieren.
- Solange Backend-Item "τ₀/σ₀-Kalibrierung" (Backend-Backlog Punkt 2) nicht fertig ist:
  `ampel_status: "unbekannt"` sichtbar als eigener Zustand darstellen, **nicht** als 🟢
  interpretieren (Fail-safe-Prinzip, Frontend-Konzept 2.4).
**Rolle(n):** frontend-dev.
**Priorität:** Hoch.

## 2. Bildschirm: Eskalations-Review

**Titel:** PGP- und LLM-Einschätzung nebeneinander
**User Story:** #3 (nachvollziehbare Begründung), #5 (zwei unabhängige Einschätzungen).
**Akzeptanzkriterien:**
- `pgp.begruendung` und `llm.begruendung` **immer in getrennten UI-Elementen**, nie zu
  einem Text/Score zusammengeführt (Leitplanke 1 aus `frontend-dev.md` – nicht
  verhandelbar).
- Reihenfolge in der UI erzwingt: erst beide Einschätzungen betrachten, dann erst zur
  Entscheidungserfassung (Bildschirm 3) wechseln.
- `matched_rag_docs` inkl. Vertrauensstufe anzeigen (`intern-verifiziert` vs.
  `extern-ungeprueft`, sobald das Backend das liefert – Backend-Backlog Punkt 3), nicht
  nur den Text ohne Einordnung.
**Rolle(n):** frontend-dev.
**Priorität:** Hoch.

## 3. Bildschirm: Entscheidungserfassung

**Titel:** Entscheidung mit erzwungener Provenienz
**User Story:** #1, #5; Systemgrenzen Teil D (Provenienz Mensch vs. Agent).
**Akzeptanzkriterien:**
- Drei Wahlmöglichkeiten: PGP folgen / LLM folgen / eigene Reihenfolge.
- Bei Abweichung von PGP und LLM: Begründungsfeld ist **im UI als Pflichtfeld markiert**
  und blockiert das Absenden, wenn leer (nicht nur serverseitig validiert – doppelte
  Absicherung, siehe Backend-Backlog "POST /entscheidung").
- Vor dem finalen Bestätigen: falls `propagierte_faelle` in der Vorschau nicht-leer ist,
  **explizit anzeigen, wie viele/welche anderen Fälle mitbetroffen sind**, bevor der
  Planer bestätigt (Architektur-Doc Abschnitt 2.5, Frontend-Konzept 2.4 Punkt 1 – kein
  versteckter Nebeneffekt).
- Kein Button, der wie eine reale, irreversible Produktionsaktion aussieht, ohne
  zusätzlichen expliziten Bestätigungsschritt (Frontend-Konzept 2.4).
**Rolle(n):** frontend-dev.
**Priorität:** Hoch.

## 4. Bildschirm: Audit-Trail

**Titel:** Nachvollziehbarer Entscheidungsverlauf
**User Story:** #7 (Vertrauen durch Historie), #9 (Nachvollziehbarkeit von Planänderungen
für Shopfloor-Mitarbeiter, als Annahme in Userstories.md gekennzeichnet).
**Akzeptanzkriterien:**
- Chronologische Liste aus `GET /verlauf`: μ/σ/τ, Entscheidung, wer/was entschieden hat,
  Zeitstempel.
- Mensch- vs. Agent-Provenienz optisch klar unterscheidbar (nicht nur Textfeld irgendwo).
**Rolle(n):** frontend-dev.
**Priorität:** Mittel.

## 5. Bildschirm: Kalibrierungs-Gesundheit (optional, MVP-Nachlauf)

**Titel:** Technischer Überblick für Step-6-Betreuer
**Akzeptanzkriterien:** Aktuelle τ₀/σ₀, Eskalationsrate über Zeit, Anteil
"trügerische Ruhe"-Fälle. Separate Ansicht/Rolle, nicht im Hauptbildschirm für
Jens/Tagesplaner (Frontend-Konzept 2.3.5 – Zielgruppe nicht überladen).
**Rolle(n):** frontend-dev, in Absprache mit backend-dev (neuer Endpunkt ggf. nötig, siehe
Architektur-Doc Abschnitt 3, Tabellenzeile 5).
**Priorität:** Niedrig – explizit nicht MVP-Scope.

## 6. Übergreifend: Kosten-/Wirtschaftlichkeits-Transparenz

**Titel:** Sichtbarkeit, wann ein LLM-Call ausgelöst wurde
**User Story:** #12 (kontrollierte Token-/API-Kosten, als Annahme in Userstories.md
gekennzeichnet).
**Akzeptanzkriterien:** Im Audit-Trail oder Review-Bildschirm erkennbar, dass ein
LLM-Ranking nur für Eskalationsfälle angefordert wurde, nicht pauschal für jeden Auftrag.
**Rolle(n):** frontend-dev.
**Priorität:** Niedrig.

---

## Nicht verhandelbare Leitplanken (gelten für alle Items, nicht wiederholt pro Item)

Aus `frontend-dev.md` / `Active-Learning-Loop-und-Frontend-Konzept.md` 2.4:
PGP/LLM nie verschmelzen · Vorschlag ≠ Ausführung · Provenienz erzwingen ·
Vertrauensstufe sichtbar · Fail-safe statt Fail-open.
