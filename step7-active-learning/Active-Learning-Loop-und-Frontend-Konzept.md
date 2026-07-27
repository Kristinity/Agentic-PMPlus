# Step 7 – Vorarbeit: Active Learning Loop & Frontend-Konzept

**Stand:** 2026-07-27
**Grundlage:** `step1-feasibility/Benchmark-Analyse.md` (17 Quellen), `step2-limits/Systemgrenzen.md`
(Teil A.4, D.1), `Konzept-README.md`, `README.md`. Recherche-Zuarbeit über Search-Buddy
(reine Aufarbeitung vorhandener Projektquellen, keine neue Web-Recherche).

Dieses Dokument ist bewusst **vor** jeder Implementierung entstanden (auch vor dem Anlegen
neuer Agentenrollen) – Zweck ist, die Faktenbasis und die Design-Leitplanken einmal
schriftlich festzuhalten, bevor Code oder neue Agenten-Definitionen entstehen.

---

## Teil 1: Active Learning Loop – Stand aus der Literaturbasis

### 1.1 Relevante Quellen und was sich übertragen lässt

| # | Quelle | Kernmethode | Übertragbar auf Step 7 | Nicht übertragbar |
|---|---|---|---|---|
| #3 | Bemporad & Piga (2020) | Iterativ: Vergleichspaar vorschlagen → Nutzer bewertet → RBF-Surrogat per LP/QP anpassen; Akquisition = Distanzgewichtung (Exploration) + Präferenzwahrscheinlichkeit (Exploitation) | Grundmuster "ein Paar pro Iteration → Modell-Update" passt strukturell zum README-Ablauf; Exploration/Exploitation-Trennung als Akquisitions-Vorbild | RBF statt GP (Konzept sieht PGP vor); kein PPS-Bezug; keine Aussage zu realen Konsequenzen |
| #4 | Ozaki et al. (2023) | Akquisitionsfunktion bezieht **zwei** Unsicherheitsquellen ein: Ziel-GP-Unsicherheit UND Präferenz-Unsicherheit; minimiert Interaktionszahl bis zur bevorzugten Lösung | Methodisch am nächsten an PPS-Mehrzielsituation (Kapazität/Termin/Kosten); Interaktionskosten explizit als Designziel in der Akquisition – direkt auf "Eskalationszahl minimieren" übertragbar | Laut Systemgrenzen A.4 ungetestet an Produktionsplanungsszenarien |
| #9 | Kholodna et al. (2024) | LLM übernimmt Annotation statt Mensch im AL-Loop eines Klassifikators | Belegt grundsätzlich: LLM kann im Loop menschliches Feedback kosteneffizient ersetzen/vorfiltern (Größenordnung 42,45× günstiger) | Nur Klassifikation, keine Preference-Paare, kein GP-Bezug (A.4) |
| #10 | Huang, Yang & Fu (2024) | Wählt nicht nur den Datenpunkt, sondern die **Query-Strategie selbst** adaptiv | Idee einer adaptiven, mehrstufigen Strategie-Wahl (statt fest verdrahteter Akquisitionsfunktion) konzeptionell interessant | Kein Preference-/GP-/PPS-Bezug |
| #16 | Bıyık et al. (2024) | Reward-Funktion **mit GP** modelliert, aktiv nur über Trajektorien-Präferenzvergleiche angepasst; Variante "volle Landschaft lernen" vs. "nur beste Option finden" | Am nächsten an Step 5+7 kombiniert; die Unterscheidung "volle PGP-Landschaft" vs. "nur pro Fall die beste Option" ist eine direkt relevante Design-Weiche für Step 7 (Dateneffizienz) | Domäne Robotik/Trajektorien, keine PPS, keine Aussage zu irreversiblen Konsequenzen |
| #17 | Kim et al., BAGEL (2026) | GP propagiert **sparse LLM-Relevanzsignale** über den gesamten Embedding-Raum – ein einzelnes teures Urteil wirkt auf viele ähnliche Fälle | Kombiniert methodisch alle drei Kernbausteine (GP+Loop+LLM) am direktesten; Propagationsprinzip entspricht strukturell genau "validierter Fall → zurück ins Context Engineering" aus dem README | Domäne Passage Retrieval, keine τ/σ-Kalibrierungsschicht; **Sicherheitsrelevant** (siehe 1.3) |
| #7 | Cercola et al. (2025) | Trade-off-Rahmen RLHF-Skalierbarkeit vs. Query-Effizienz | Liefert keinen Kostenwert, aber den Rahmen für die Frage "wie viele Eskalationen/Zeiteinheit sind leistbar" | Kein konkretes Kostenmodell (A.7) |

### 1.2 Dokumentierte Lücken (bereits in Systemgrenzen.md erfasst)

- **A.4 (Aufgaben-Mismatch):** #9/#10 belegen LLM-gestützte Active-Learning-Loops nur für
  Klassifikation/Annotation, nicht für Preference-Paare in der PPS. #3/#4 liefern die
  methodische Blaupause, wurden aber nie an Produktionsplanungsszenarien getestet – die
  Übertragung der Akquisitionsfunktion auf PPS-Zielkonflikte (Kapazität/Termin/Kosten)
  ist ungetestet.
- **D.1 (Exploration in folgenlosen vs. konsequenzbehafteten Kontexten):** Alle vier
  Kern-Loop-Quellen (#3, #4, #16, #17) werten ihre Strategie dort aus, wo ein "Fehlversuch"
  nichts Reales kostet. Für Step 7 in der PPS bedeutet dieselbe Logik im Zweifel eine
  tatsächlich durchgeführte, teils irreversible Produktionsentscheidung. **Keine der 17
  Quellen validiert eine sichere Übertragung** – eigenständige Systemgrenze.
- Ergänzend: kein belegter Fail-safe-Default bei Kalibrierungsversagen (Schnittstelle
  Step 6→7); keine Provenienz-Unterscheidung Mensch- vs. Agent-Feedback im Audit-Trail –
  ohne die riskiert Step 7, sich an eigenen früheren Agent-Ausgaben zu "bestätigen" statt
  an echtem Experten-Feedback zu lernen.

### 1.3 Abgeleitete Design-Idee (Extrapolation, nicht direkt belegt)

Aus der Kombination von #4 (Interaktionskosten in der Akquisition), #16 (volle Landschaft
vs. nur beste Option) und #17 (Propagation eines Urteils auf ähnliche Fälle) ergibt sich
eine mögliche Grundstruktur für den Loop:

1. Akquisition wählt Eskalationsfälle nicht nur nach Unsicherheit (klassisches Sampling wie
   #9/#10), sondern gewichtet die **erwartete Reduktion künftiger Eskalationen** gegen die
   Kosten einer Planeranfrage (analog #4).
2. Prüfen, ob Step 7 wirklich die volle PGP-Landschaft über alle Planungsszenarien lernen
   muss, oder ob – analog zu #16s "Reward-Optimierung"-Variante – pro Eskalationsfall nur
   die jeweils bevorzugte Option gelernt werden muss (deutlich dateneffizienter, entschärft
   die in A.7 benannte Kapazitätsgrenze).
3. Eine validierte Experten-Entscheidung wird über das PGP-σ auf **ähnliche, noch nicht
   entschiedene Fälle** propagiert (analog #17), nicht nur auf den einen Fall angewendet –
   das wäre die technische Umsetzung von "zurück ins Context Engineering" aus dem README.

**Explizit offen, nicht aus der Literatur ableitbar:** Wie diese Propagation in einem Kontext
mit realen Konsequenzen sicher gedrosselt/begrenzt werden muss, bevor ein einzelnes (ggf.
fehlerhaftes) Experten-Urteil mehrere reale Produktionsentscheidungen gleichzeitig
beeinflusst. Reine Projektentscheidung, kein Befund aus den 17 Quellen.

---

## Teil 2: Frontend-Konzept

### 2.1 Ausgangslage

Weder `README.md` noch `Konzept-README.md` beschreiben bisher ein Frontend – beide sind
Docker/CLI-orientiert (`docker compose up`, `main.py`-Skripte, CSV-Output nach
`shared/data`). Es gibt aktuell keine visuelle Oberfläche für Produktionsplaner:innen; das
ist eine Lücke, kein Widerspruch zu etwas bereits Entschiedenem.

### 2.2 Zielgruppe und Kernfrage

Laut Konzeptidee: KMU-Produktionsplanung, Zielgruppe **Produktionsplaner:innen** als
Freigabe-/Eskalationsinstanz (nicht Data Scientists). Die zentrale Frage, die das Frontend
für diese Zielgruppe beantworten muss, ist nicht "wie funktioniert der PGP", sondern:
**"Welche Aufträge brauchen jetzt meine Entscheidung, und warum?"**

### 2.3 Vorgeschlagene Kernbildschirme

1. **Auftrags-Warteschlange (Startbildschirm).** Liste aller offenen Aufträge, sortiert
   nach PGP-Rang (μ), mit Ampel-Status pro Auftrag nach der 2×2-Matrix aus
   `Konzept-README.md`:
   - 🟢 τ niedrig + σ niedrig → automatisch weiter, nur informativ sichtbar
   - 🟡 τ niedrig + σ hoch → "trügerische Ruhe", zur Prüfung markiert
   - 🔴 τ hoch → klarer Eskalationsfall
   Genau diese Sprache ("Bildlich gesprochen") nutzt das Konzept-Dokument selbst – das
   Frontend sollte sie direkt übernehmen statt rohe Zahlen (τ=0.34, σ=0.02) ungefiltert
   zu zeigen.

2. **Eskalations-Review (Kernbildschirm).** Für 🟡/🔴-Aufträge: PGP-Rang + Begründung
   (aus welchen Faktoren wie in `step5-pgp/main.py` berechnet: Puffer, Maschinen-,
   Materialverfügbarkeit, Kontention) **nebeneinander** mit LLM-Rang + Begründung (aus
   `step6-calibration/main.py`, inkl. der vom LLM gemeldeten Kontext-Warnungen – siehe
   `parse_llm_response`/`warnungen`-Feld). Erst nach Betrachtung beider unabhängiger
   Einschätzungen soll der Planer entscheiden – die UI sollte diese Reihenfolge erzwingen,
   nicht beide Werte vermischt als eine Zahl präsentieren, sonst geht der ganze Sinn der
   Unabhängigkeit (siehe Konzept-README, Abschnitt "zentrale Idee") verloren.

3. **Entscheidungserfassung mit Provenienz.** Planer wählt: PGP folgen / LLM folgen /
   eigene Reihenfolge. Diese Entscheidung muss **explizit als "Mensch"** markiert im
   Audit-Trail landen (Systemgrenzen.md Teil D: Provenienz-Unterscheidung Mensch- vs.
   Agent-Feedback) – UI-seitig z. B. durch verpflichtende Kurzbegründung bei Abweichung
   von PGP oder LLM, nicht nur einen Klick.

4. **Audit-Trail / Verlauf.** Chronologische Liste aller automatisch durchgelaufenen UND
   eskalierten Entscheidungen, je Eintrag: μ/σ/τ, Entscheidung, wer/was entschieden hat,
   Zeitstempel. Erfüllt die in Systemgrenzen.md Teil B.6 benannte Governance-Anforderung
   ("Verantwortlichkeit bei automatisierten Entscheidungen muss vorab geklärt werden").

5. **Kalibrierungs-Gesundheit (optionaler, technischerer Bildschirm).** Aktuelle τ₀/σ₀-
   Schwellenwerte, Eskalationsrate über Zeit, Anteil "trügerische Ruhe"-Fälle – für die
   Person, die Step 6 betreut, nicht zwingend für den Tagesplaner. Sinnvoll als separate
   Rolle/Ansicht statt im Hauptbildschirm, um die Kernzielgruppe nicht zu überladen.

### 2.4 Leitplanken aus den Systemgrenzen (nicht verhandelbar für das Frontend-Design)

- **Vorschlag vs. Ausführung klar trennen** (Systemgrenzen Teil D.1/D.2): Kein Button, der
  wie eine reale, irreversible Aktion aussieht (z. B. "Auftrag stornieren"), ohne
  expliziten Bestätigungsschritt – besonders relevant, sobald Step 8 (Live-Test) reale
  Aktionen auslösen kann.
  - **Bezug zum Active-Learning-Loop (Teil 1):** genau hier trifft die in 1.2/1.3
    beschriebene Propagations-Lücke auf die UI – wenn eine einzelne Experten-Entscheidung
    laut Design-Idee (1.3) auf mehrere ähnliche Fälle propagiert wird, muss das Frontend
    sichtbar machen, *wie viele* Fälle von einer einzelnen Freigabe betroffen sind, bevor
    der Planer bestätigt. Sonst entsteht genau das in Systemgrenzen Teil C.1 beschriebene
    Risiko (ein Urteil wirkt unbemerkt auf viele Entscheidungen).
- **Kuratierte statt frei erweiterbare Wissensquellen sichtbar machen** (Teil C.1/C.2):
  Wenn das Frontend RAG-Kontext anzeigt (z. B. welches Dokument die LLM-Begründung
  gestützt hat), sollte die Vertrauensstufe (`intern-verifiziert` vs. `extern-ungeprueft`,
  siehe `step4-context-engineering/gute-RAGs.md`) sichtbar mitlaufen, nicht nur der Text.
- **Fail-safe, nicht fail-open per Default** (Teil B.6/D.2): Bei technischen Fehlern
  (z. B. LLM-Call schlägt fehl, wie im aktuellen `step6-calibration/main.py` bei fehlendem
  API-Guthaben) muss die UI eskalieren/blockieren, nicht stillschweigend automatisch
  weiterlaufen.

### 2.5 Offene technische Fragen (nicht Teil dieses Dokuments, für Backend-/Frontend-Rollen)

- Wie werden die aktuell dateibasierten Zwischenergebnisse (`pgp_priorisierung.csv`,
  `tau_vergleich.csv` in `shared_data/`) für ein Frontend nutzbar gemacht – direkter
  Dateizugriff, oder ein dünner Backend-Service (API), der die Step-CSVs aggregiert?
  Gehört zur Backend-Dev-Rolle.
- Framework-/Stack-Wahl für das Frontend selbst ist hier bewusst noch offen – das ist
  Aufgabe der neuen Frontend-Dev-Rolle, nicht Vorwegnahme in diesem Dokument.

---

## Zusammenfassung für die nächsten Schritte

1. Active Learning Loop (Step 7 Code) hat eine literaturgestützte Design-Richtung
   (Abschnitt 1.3), aber zwei ungelöste, projekteigene Fragen: PPS-Übertragbarkeit der
   Akquisitionsfunktion (A.4) und sichere Drosselung der Propagation in einem
   konsequenzbehafteten Kontext (D.1) – beides sollte in der Implementierung explizit
   adressiert, nicht stillschweigend übergangen werden.
2. Ein Frontend ist bisher nirgends im Konzept beschrieben; Abschnitt 2 markiert eine
   sinnvolle erste Bildschirmstruktur (Warteschlange → Eskalations-Review →
   Entscheidungserfassung → Audit-Trail), abgeleitet direkt aus der im
   `Konzept-README.md` beschriebenen Logik, nicht frei erfunden.
3. Auf Basis davon: zwei neue Agentenrollen (Backend-Dev, Frontend-Dev) anlegen –
   noch nicht geschehen, folgt nach Rücksprache.
