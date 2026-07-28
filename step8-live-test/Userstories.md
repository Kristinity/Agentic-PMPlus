# User Stories – Agentic-PMPlus (K³)

**Stand:** 2026-07-27 (Ergänzung 2026-07-28, s. Abschnitt "Ergänzung" unten)
**Grundlage:** Pitch-Narrativ (6 Slides, Persona Jens Pirinski/Krasser Spass GmbH),
`Konzept-README.md`, `README.md`, `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`.

> **Hinweis zum Status:** Dies sind ausschließlich User Stories – **kein Backlog**, keine
> Akzeptanzkriterien, keine Priorisierung. Das folgt erst in einem separaten, vom Nutzer
> ausdrücklich freigegebenen Schritt, nachdem diese Stories geprüft wurden.
>
> **Ausnahme:** Die Stories #13–#17 (Abschnitt "Ergänzung") sind bereits Grundlage eines
> freigegebenen Backlogs – siehe `step8-live-test/Produkt-Backlog/README.md`,
> Tickets B10–B14/F08–F12.

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
kleinerer Kunden). **Siehe auch Ergänzung 2026-07-28 (Stories #13–#17):** dort geht es um
ein bisher fehlendes Erfassungsfeld für Sonderaufträge, das diese Story zusätzlich
unterstützen kann – beide Stories bleiben eigenständig (siehe dortige Abgrenzung).

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

## Ergänzung (2026-07-28): Sonderaufträge mit besonderer Vergütung

**Grundlage:** Nutzeranfrage vom 2026-07-28 (Produktionsplaner-Perspektive, K.S. GmbH):
"ich möchte irgendwo Spezialaufträge erfassen können, die besonders teuer vergütet werden,
weil es sonderanfertigungen sind z.b. DV mit 20cm durchmesser - für Bspw. Events".
Verifiziert gegen `step5-pgp/main.py`, `step9-upload-interface/pipeline.py`/`app.py`,
`step3-erp-simulation/company_profile.example.yaml`. Scope-Entscheidungen (Erfassungsfeld
**und** neuer Produkttyp; generisches Flag statt Hardcoding auf den Durchmesser-Fall;
neues Feld statt Wiederverwendung des toten `priority`-Felds) am 2026-07-28 vom Nutzer
bestätigt – Details und Verifikation siehe Backlog-Übergabe
(`step8-live-test/Produkt-Backlog/README.md`).

**Abgrenzung zu Story #4:** #4 ist eine Output-Robustheits-Story (der PGP soll bei
Sonderaufträgen mit wenig Historie trotzdem eine belastbare Einschätzung liefern). Die
folgenden Stories sind Input-Vollständigkeits-Stories (es fehlt ein Datenfeld, das den
wirtschaftlichen Wert/die Sonderstellung überhaupt erfasst) – eigenständig, aber #14
unterstützt #4 direkt, sobald sie umgesetzt ist.

### 13. Sonderaufträge als solche kennzeichnen können
**Als** Produktionsplaner **möchte ich** einen Auftrag beim Erfassen explizit als
"Sonderauftrag/Sonderanfertigung" markieren können, **damit** er im System unabhängig vom
konkreten Produkttyp (nicht nur beim Beispiel "20cm-Drehverschluss") sichtbar von
Standardaufträgen unterschieden wird.
*Bezug:* generisches Flag – vom Nutzer am 2026-07-28 bestätigt statt hart auf den
Durchmesser-Fall zu bauen. Tickets: TICKET-B10, TICKET-F08.

### 14. Wirtschaftlich wichtige Sonderaufträge nicht durch die Mengen-Heuristik untergehen lassen
**Als** Produktionsplaner **möchte ich** für einen Sonderauftrag den vereinbarten
Sondervergütungswert erfassen können, **damit** dieser Wert die PGP-Priorisierung
beeinflusst und ein wirtschaftlich wichtiger, aber mengenmäßig kleiner Sonderauftrag nicht
durch das aktuell mit nur 0.3 (niedrigstes von sieben Gewichten) gewichtete
`quantity_proxy` untergeht.
*Bezug:* `step5-pgp/main.py` Zeilen 17–19/288 (kein Preisfeld im Datenmodell,
`quantity_proxy` niedrigstes Gewicht); `Konzept-README.md` ("vertraglich festgelegter
Bruttopreis" als vorgesehener, aber bisher nicht modellierter Faktor) – hier bewusst nur
für als Sonderauftrag markierte Aufträge, nicht als generisches Preisfeld für alle
Aufträge (kleinerer, vom Nutzer am 2026-07-28 bestätigter Scope). Tickets: TICKET-B11,
TICKET-F09.

### 15. Strukturell neue Sonderanfertigungs-Produkttypen abbilden können
**Als** Produktionsplaner **möchte ich** auch einen strukturell neuen
Sonderanfertigungs-Produkttyp (z. B. Drehverschluss mit 20cm Durchmesser für Events) im
System anlegen können, **damit** die PGP-Priorisierung dessen abweichende
Maschinenkapazität, Werkzeug-/Rüstzeit und Materialbedarf korrekt berücksichtigt, statt
ihn fälschlich wie einen Standard-Drehverschluss zu behandeln.
*Bezug:* `step3-erp-simulation/company_profile.example.yaml` (Durchmesser ist fix an
`product_id` gebunden, nicht an `variant`); vom Nutzer am 2026-07-28 ausdrücklich als Teil
des Scopes bestätigt (großer Scope, s. TICKET-B13). **Offene Annahme, die weiterhin
ungeklärt bleibt:** ob dafür eine neue Maschine/Presse nötig ist oder bestehende Werkzeuge
mit zusätzlicher Rüstzeit reichen, muss K.S. GmbH fachlich beantworten, ist keine
technische Entscheidung. Tickets: TICKET-B13, TICKET-F11.

### 16. Sonderaufträge auch in der Warteschlange erkennen
**Als** Produktionsplaner **möchte ich** Sonderaufträge in der Auftrags-Warteschlange
optisch erkennen können, **damit** ich sie im Blick behalte, auch wenn ihr PGP-Rang sie
nicht automatisch nach oben schiebt.
*Bezug:* Frontend-Konzept 2.3.1 (Warteschlange) – additive Erweiterung der bestehenden
Kartenstruktur (Muster aus TICKET-F01/F02). Tickets: TICKET-B14, TICKET-F12.

### 17. Nachvollziehbarkeit der Sonderauftrags-/Wertangaben
**Als** Produktionsplaner **möchte ich** nachvollziehen können, wer wann welchen
Sondervergütungswert für einen Auftrag eingetragen hat, **damit** im Zweifel
nachvollziehbar bleibt, warum ein Auftrag hochpriorisiert wurde, falls die Angabe falsch
war oder missbräuchlich hoch angesetzt wurde.
*Bezug:* Systemgrenzen Teil D (Provenienz Mensch- vs. Agent-Feedback), hier von
Entscheidungen auf Dateneingaben übertragen – **Annahme:** nicht explizit vom Nutzer
gefordert, sondern vom Produktanalysten aus der bestehenden Provenienz-Leitplanke
abgeleitet (2026-07-28). Tickets: TICKET-B12, TICKET-F10.

---

## Offen / nicht in Stories übersetzt

- **Slide 5** ("Produktionsplanung vorher/nachher") liefert eine Illustration, aber keine
  neue, eigenständige Anforderung – ihr Inhalt steckt bereits in Stories 1, 6 und 8.
- Die genaue Rollenbezeichnung der Persona schwankt im Ausgangstext ("Jens Priorinski" vs.
  "Jens Pirinski") – hier einheitlich als **Jens Pirinski** verwendet; bitte bei der Prüfung
  bestätigen, welche Schreibweise korrekt ist.
