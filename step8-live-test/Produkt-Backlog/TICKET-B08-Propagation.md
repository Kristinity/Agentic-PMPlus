# TICKET-B08 – Propagation mit harter Obergrenze N

**Rolle:** backend-dev
**Priorität:** Hoch (sicherheitsrelevant)
**Abhängigkeiten:** [B05](TICKET-B05-POST-Entscheidung.md)
**MVP:** nein (Post-MVP)

## Beschreibung
Validierte Entscheidung wirkt auf ähnliche, noch offene Fälle – aber gedrosselt (siehe
`step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt 1.3 für die
Design-Idee).

## Akzeptanzkriterien
- Feste, konfigurierbare Obergrenze N (Startwert 5).
- Fälle über N: erneute Eskalation statt automatischer Übernahme.
- `propagierte_faelle` in der `POST /entscheidung`-Response korrekt befüllt (löst den
  Platzhalter aus B05 ab).

## Bezug zu Leitplanken
`step2-limits/Systemgrenzen.md` Teil D.1 – keine der 17 Quellen validiert sichere
Propagation bei realen Konsequenzen. Die Obergrenze ist die im Architektur-Dokument
geforderte Sicherheitsgrenze, **nicht optional**.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Testfall mit mehr als N ähnlichen offenen Aufträgen zeigt nachweislich, dass nur N
  automatisch mit-angepasst werden, der Rest eskaliert bleibt.

## Folgetickets
[F03](TICKET-F03-Entscheidungserfassung.md) (Propagations-Vorschau)
