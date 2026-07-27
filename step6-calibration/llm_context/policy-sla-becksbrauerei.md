# Liefertreue-Vereinbarung Becksbrauerei

> Policy-Auszug für den LLM-Ranking-Agenten (Step 6). Enthält nur die vertragliche Regel
> selbst, keine live abgefragten ERP-Kennzahlen (kein aktueller Lagerbestand, keine aktuelle
> Maschinenverfügbarkeit o. ä. - das sieht ausschließlich der PGP). Quelle:
> `step4-context-engineering/rag_documents/sla-becksbrauerei.md`.

Becksbrauerei ist der wichtigste Kunde von K.S. GmbH und verlangt vertraglich eine
On-Time-Delivery-Quote von 98 %.

## Regel

Bei drohender Terminüberschreitung eines Becks-Auftrags muss die Planung diesen Auftrag
automatisch als "hoch"-Priorität einstufen, sobald weniger als 3 Arbeitstage Puffer bis
zum Liefertermin verbleiben. Unterschreitet die gleitende 4-Wochen-Liefertreue für Becks
98 %, ist der Vertrieb unverzüglich zu informieren.

## Konsequenz für die Priorisierung

Ein Planungsvorschlag, der einen Becks-Auftrag zugunsten eines Nicht-Becks-Auftrags
verspätet, braucht eine explizite Begründung und sollte im Zweifel an einen Menschen
eskaliert statt automatisch entschieden werden.
