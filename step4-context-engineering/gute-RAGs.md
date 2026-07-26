# Was ein gutes RAG für Agentic-PMPlus ausmacht

**Grundlage:** `step1-feasibility/Benchmark-Analyse.md` (Quelle #5: hybrides
KG-Vector-RAG für Smart Manufacturing) und `step2-limits/Systemgrenzen.md`
(Teil C: Sicherheitsbezogene Systemgrenzen, insb. C.1 zu Prompt-Injection
über RAG-Kontext).

Dieses Dokument fasst zusammen, was gute RAG-Dokumente für Step 4 inhaltlich
und strukturell ausmacht, und begründet das Template in `rag_documents/`.

## 1. Kein Abbild der ERP-Tabellen

`orders.csv`, `bom.csv`, `work_centers.csv` etc. aus Step 3 sind strukturierte
Daten - sie gehören direkt abgefragt (SQL/Pandas), nicht als Text-Chunks in
den Vektorindex eingebettet. RAG-Dokumente liefern das **unstrukturierte
Zusatzwissen**, das der LLM-Agent braucht, um diese Rohdaten überhaupt
sinnvoll zu interpretieren.

## 2. Relevante Inhaltskategorien (`doc_type`)

- **`sla`** - Kunden-/Vertragswissen: Liefertreue-Zusagen, Eskalationsregeln,
  Priorisierung nach Kundenwichtigkeit (Beispiel: `sla-becksbrauerei.md`)
- **`prozessanweisung`** - welche Produkte auf welcher Maschine laufen
  (dürfen), Rüstreihenfolgen, Wartungsfenster (Beispiel:
  `prozess-pressenzuordnung.md`)
- **`produktspezifikation`** - Maßtoleranzen/Materialvorgaben je Produkt-
  /Kundenvariante
- **`entscheidungsprotokoll`** - vergangene Planungsentscheidungen mit
  Begründung; spätere Kandidaten für Preference-Trainingsdaten (Step 5)
- **`stoerungsbericht`** - frühere Störungen und das erprobte Vorgehen dazu
  (Beispiel: `stoerung-weissblech-engpass-2025.md`)
- **`richtlinie`** - übergreifende Priorisierungs-/Compliance-Regeln

## 3. Strukturelle Anforderungen an jedes Dokument

- **In sich abgeschlossene Chunks.** Jeder Abschnitt muss eine Frage
  eigenständig beantworten können - keine Verweise wie "siehe oben", die nur
  im Volltext, nicht aber isoliert im Retrieval-Chunk Sinn ergeben.
- **Explizite Handlungsableitung.** Reine Fakten ohne "Konsequenz für die
  Planung" sind für eine PPS-Entscheidung oft zu abstrakt - jedes Dokument
  im Template hat deshalb einen eigenen Abschnitt dafür.
- **Strukturierte Metadaten (Frontmatter) = KG-Seite des hybriden RAG.**
  `kunde`, `produkt`, `work_center` erlauben gefiltertes Retrieval
  ("nur Dokumente zu Becks bzw. zu WC-Presse-KK-02"), analog zur
  KG-Vector-Kombination aus Quelle #5.
- **Konsistente Terminologie mit den Step-3-CSV-Feldnamen** (Kunden-,
  Produkt-, Work-Center-IDs), damit sich Retrieval-Treffer und ERP-Daten
  eindeutig verknüpfen lassen.

## 4. Aktualität und Herkunft

- **`gueltig_ab`/`gueltig_bis`:** eine veraltete Richtlinie ist gefährlicher
  als eine fehlende - abgelaufene Dokumente sollten beim Retrieval
  ausgeschlossen oder explizit als veraltet markiert werden.
- **`autor`/`vertrauensstufe`:** Voraussetzung für **kuratierte statt frei
  erweiterbare Wissensquellen**. Das ist keine Nebensächlichkeit, sondern
  direkt die in `Systemgrenzen.md` (Teil C.1) benannte Systemgrenze:
  ungeprüfte RAG-Dokumente sind der plausibelste Prompt-Injection-Vektor
  im Gesamtkonzept. Nur Dokumente mit `vertrauensstufe: intern-verifiziert`
  sollten ungefiltert in den Kontext des LLM-Agenten gelangen;
  `extern-ungeprueft` markierte Inhalte gehören separat behandelt (z. B.
  klar als Zitat/Fremdquelle gekennzeichnet, nie als Anweisung interpretiert).

## 5. Der Haupt-Trade-off

Mehr/detailliertere Dokumente verbessern die Kontextqualität (weniger
Halluzination, bessere Begründungen), erhöhen aber gleichzeitig
Retrieval-Rauschen und die Angriffsfläche für Prompt-Injection. Die
Metadaten- und Vertrauensstufen-Felder im Template sind der Versuch, diesen
Trade-off nicht durch "weniger Dokumente", sondern durch "besser gefilterte
und gekennzeichnete Dokumente" zu entschärfen.
