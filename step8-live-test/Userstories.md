# User Stories – Agentic-PMPlus (K³)

**Stand:** 2026-07-27
**Grundlage:** Pitch-Narrativ (6 Slides, Persona Jens Pirinski/Krasser Spass GmbH),
`Konzept-README.md`, `README.md`, `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`.

> **Hinweis zum Status:** Dies sind ausschließlich User Stories – **kein Backlog**, keine
> Akzeptanzkriterien, keine Priorisierung. Das folgt erst in einem separaten, vom Nutzer
> ausdrücklich freigegebenen Schritt, nachdem diese Stories geprüft wurden.

---

## Aus Sicht von Jens Pirinski (Produktionsplaner)

### 1. Verlässliche Priorisierung statt Bauchgefühl
**Als** Produktionsplaner **möchte ich** für neu eingehende Aufträge eine datengestützte
Prioritäts-Reihenfolge vorgeschlagen bekommen, **damit** ich nicht mehr nur "nach bestem
Wissen und Gewissen" entscheiden muss (Slide 2).
*Bezug:* PGP-Kernfunktion (`Konzept-README.md`), Warteschlangen-Bildschirm
(Frontend-Konzept 2.3.1).

### 2. Erkennen, wann das System sich selbst unsicher ist
**Als** Produktionsplaner **möchte ich** sehen, wenn eine Priorisierung mit hoher
Unsicherheit behaftet ist, **damit** ich weiß, wann ich genauer hinschauen muss statt der
Empfehlung blind zu vertrauen – genau das Versprechen aus Slide 4 ("verhält sich, als
wüsste es, was es nicht weiß").
*Bezug:* σ (`Konzept-README.md`, "zentrale Idee"), 2×2-Ampel-Status
(Frontend-Konzept 2.3.1).

### 3. Nachvollziehbare Begründung statt Blackbox
**Als** Produktionsplaner **möchte ich** sehen, warum eine bestimmte Reihenfolge
vorgeschlagen wird (Liefertermin, Kunde, Materialverfügbarkeit etc.), **damit** ich die
Empfehlung fachlich einordnen und im Zweifel korrigieren kann.
*Bezug:* Eskalations-Review-Bildschirm (Frontend-Konzept 2.3.2), Vertrauensstufe sichtbar
machen (Frontend-Konzept 2.4 / Systemgrenzen Teil C.1).

### 4. Verlässliche Einschätzung auch bei Sonderaufträgen und saisonalen Kunden
**Als** Produktionsplaner **möchte ich** auch bei saisonalen kleinen Kunden, lokalen
Brauereien und Sonderaufträgen – nicht nur beim Hauptkunden – eine belastbare
Priorisierung erhalten, **damit** ich gerade bei den schwierigen Abwägungen unterstützt
werde, die laut Slide 2 den eigentlichen Stress verursachen.
*Bezug:* Slide 2 (Kernproblem), Kundenstruktur K.S. GmbH (Hauptkunde vs. Sammelposten
kleinerer Kunden).

### 5. Zwei unabhängige Einschätzungen statt einer verschmolzenen Zahl
**Als** Produktionsplaner **möchte ich** erkennen, wenn PGP und LLM unterschiedlicher
Meinung sind, **damit** ich weiß, wann eine Entscheidung besonders sorgfältig geprüft
werden sollte, statt einem einzelnen Blackbox-Wert zu vertrauen.
*Bezug:* τ / Unabhängigkeitsprinzip (`Konzept-README.md`, "zentrale Idee"), Leitplanke
"PGP/LLM nie verschmelzen" (Frontend-Konzept 2.4).

### 6. Weniger Zeit vor dem Rechner
**Als** Produktionsplaner **möchte ich**, dass der Großteil der Aufträge (niedriges τ,
niedriges σ) ohne meine manuelle Prüfung durchläuft, **damit** ich Zeit für andere Aufgaben
– und mein Privatleben (Slide 6) – gewinne.
*Bezug:* "Ergebnis 1" (`Konzept-README.md`, "Ergebnisse"), Happy-End-Kriterium (Slide 6).

### 7. Vertrauen durch nachvollziehbare Historie
**Als** Produktionsplaner **möchte ich** einsehen können, wie oft und wie zuverlässig das
System in der Vergangenheit richtig lag, **damit** ich dem System begründet statt blind
vertrauen kann.
*Bezug:* Audit-Trail-Bildschirm (Frontend-Konzept 2.3.4).

---

## Aus Sicht der Shopfloor-Mitarbeiter

### 8. Robustere, seltener kurzfristig geänderte Pläne
**Als** Mitarbeiter auf dem Shopfloor **möchte ich**, dass Produktionspläne seltener
kurzfristig verworfen werden, **damit** ich meine Arbeit vorausschauend planen kann statt
ständig umzudisponieren.
*Bezug:* Slide 2 (Shopfloor-Frust ist dort explizit als Problem benannt).

### 9. Nachvollziehbarkeit, wenn sich ein Plan doch ändert
**Als** Mitarbeiter auf dem Shopfloor **möchte ich**, wenn sich ein Plan kurzfristig
ändert, den Grund dafür sehen können, **damit** die Änderung nicht willkürlich wirkt.
*Bezug:* Audit-Trail (Frontend-Konzept 2.3.4) – **Annahme:** nicht explizit in den Slides
benannt, sondern aus dem in Slide 2 beschriebenen Vertrauensverlust der Shopfloor-Seite
abgeleitet.

---

## Aus Sicht der Unternehmensleitung / Data Privacy

### 10. Keine sensiblen Daten bei Drittanbietern
**Als** Verantwortlicher bei Krasser Spass GmbH **möchte ich**, dass keine sensiblen
Unternehmensdaten an externe Drittanbieter-LLMs (z. B. ChatGPT) übertragen werden,
**damit** die Data Privacy des Unternehmens gewahrt bleibt.
*Bezug:* Slide 3 (explizit benanntes Risiko), `README.md` ("Wahrung der Data Privacy").

### 11. Nutzbarkeit trotz unstrukturierter historischer Daten
**Als** Verantwortlicher **möchte ich**, dass das System auch mit dem historisch
gewachsenen, unstrukturierten Datenbestand von Krasser Spass GmbH sinnvoll umgehen kann,
**damit** nicht erst monatelang Daten bereinigt werden müssen, bevor das System nützlich
wird.
*Bezug:* Slide 3 ("historischer Wust" macht generische LLMs zum "Magic 8 Ball"),
`Konzept-README.md` ("wenig gut strukturierte Daten" als Ausgangssituation).

### 12. Kontrollierte Token-/API-Kosten
**Als** Verantwortlicher **möchte ich**, dass LLM-Anfragen gezielt (nur bei Eskalation)
statt pauschal für jede Entscheidung erfolgen, **damit** der Einsatz wirtschaftlich
sinnvoll bleibt.
*Bezug:* `README.md` ("Optimierung der Tokenkosten") – **Annahme:** nicht explizit in den
Slides, aber direkte Konsequenz aus der τ/σ-Eskalationslogik (nur Eskalationsfälle
brauchen einen vollen LLM-Call).

---

## Offen / nicht in Stories übersetzt

- **Slide 5** ("Produktionsplanung vorher/nachher") liefert eine Illustration, aber keine
  neue, eigenständige Anforderung – ihr Inhalt steckt bereits in Stories 1, 6 und 8.
- Die genaue Rollenbezeichnung der Persona schwankt im Ausgangstext ("Jens Priorinski" vs.
  "Jens Pirinski") – hier einheitlich als **Jens Pirinski** verwendet; bitte bei der Prüfung
  bestätigen, welche Schreibweise korrekt ist.
