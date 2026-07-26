# Agentic-PMPlus
Wie kann ein LLM wissen, was es nicht weiß? Prüfung der Implementierung einer unabhängigen, lokalen Prüfinstanz zur Wahrung der Qualität des LLM-Outputs, zur Wahrung der Data Privacy und zur Optimierung der Tokenkosten.

# Konzeptidee
**Umfeld:** KMU in DE, PPS (typische Ingenieurtätigkeiten)
**Ziel:** Den teuersten Faktor im Prozess – den Menschen – nur dann einsetzen, wenn es wirklich nötig ist.
**Ausgangssituation:** Wenig „gut" strukturierte Daten für ein eigenes LLM oder das Feintuning/Training eines Drittanbieter-LLMs.

Ein lokaler **Preference GP (PGP)** erstellt anhand der vollen Dateneinsicht in das Context Engineering bei Eingang von Aufträgen eine abnehmend priorisierte Reihenfolge der abzuarbeitenden Aufträge. Die gleiche Prognose (Priorisierung) erstellt auch das LLM – mit eingeschränktem Zugriff auf Unternehmensdaten und kleinstmöglichem Kontext.

Die Prognose der Auftragspriorisierung wird anhand der prognostizierten Durchlaufzeit (DZ), aktuellen Maschinenverfügbarkeit, vertraglich festgelegtem Bruttopreis, Materialverfügbarkeit, Abhängigkeiten zu laufenden Aufträgen, Mitarbeiter-Coverage (Urlaubszeiten/Krankmeldungen) und Lieferantenbewertung aufgestellt.

**Volle Einsicht** auf ERP & Context Engineering hat der PGP. **Eingeschränkte Einsicht** hat das LLM; dafür erhält es zusätzlich unstrukturierte Informationen (z. B. Notizen), die dem PGP nicht zugänglich sind.

## Die zentrale Idee: Der PGP liefert zwei Werte, nicht nur einen

Ein Preference GP gibt bei jeder Vorhersage nicht nur eine Rangfolge aus, sondern immer **zwei Größen gleichzeitig** – aus einem einzigen Modell, ohne zusätzlichen Aufwand:

| Wert | Was er bedeutet | Bildlich gesprochen |
|---|---|---|
| **μ (Rang-Prognose)** | Die vom PGP berechnete Auftragsreihenfolge | „Das ist unsere Einschätzung der Priorität." |
| **σ (Selbstunsicherheit)** | Wie sicher sich der PGP bei genau *dieser* Einschätzung ist | „Und so sicher sind wir uns dabei." |

Aus dem Vergleich von **μ (PGP)** gegen die Rang-Prognose des **LLM** ergibt sich die Differenz **τ** (Tau): die Meinungsverschiedenheit zwischen den beiden unabhängigen Einschätzungen. Aus **σ** ergibt sich ein zweites, unabhängiges Signal: Wie tragfähig ist die PGP-Einschätzung selbst – unabhängig davon, ob das LLM zustimmt oder nicht?

**Warum das wichtig ist:** Ein niedriges τ (LLM und PGP stimmen überein) wirkt beruhigend – ist es aber nicht immer. Wenn der PGP bei einem Sonderauftrag mit wenig Historie selbst unsicher ist (hohes σ), kann eine zufällige Übereinstimmung mit dem LLM eine Sicherheit vortäuschen, die nicht existiert. Erst die Kombination beider Werte liefert ein belastbares Bild:

| | PGP ist sich sicher (σ niedrig) | PGP ist sich unsicher (σ hoch) |
|---|---|---|
| **LLM & PGP einig (τ niedrig)** | ✅ Robuste Übereinstimmung – automatisch weiter | ⚠️ Trügerische Ruhe – trotz Einigkeit prüfen |
| **LLM & PGP uneinig (τ hoch)** | 🔎 Klarer Fall für Experten-Review | 🔎 Klarer Fall für Experten-Review |

Es wird **nur ein PGP** benötigt – nicht zwei. Wichtig ist lediglich, dass PGP und LLM ihre Einschätzung unabhängig voneinander, ohne gegenseitige Beeinflussung, abgeben. Nur so bleibt die Meinungsverschiedenheit (τ) aussagekräftig; würde man dem LLM die PGP-Einschätzung vorab zeigen, correlated man künstlich beide Fehler und die Kontrolllogik verliert ihren Sinn.

## Ablauf pro Auftrag

1. Auftrag kommt ins System.
2. PGP berechnet Rang-Prognose **μ** und Selbstunsicherheit **σ** in einem Schritt.
3. LLM berechnet, unabhängig und mit eingeschränktem Kontext, seine eigene Rang-Prognose.
4. Differenz **τ** zwischen beiden Rang-Prognosen wird berechnet.
5. Eskalationsregel: **τ zu groß ODER σ zu groß → Flag an den Experten (Produktionsplaner)**.

## Ergebnisse

- **Ergebnis 1** – τ klein UND σ niedrig: LLM liegt vermutlich richtig, PGP ist sich sicher → Produktionsplan und Arbeitsplan werden geschrieben und zur Freigabe an den Verantwortlichen geschickt.
- **Ergebnis 2.1** – τ groß (unabhängig von σ): LLM und PGP widersprechen sich → Flag & Trigger an den Experten zur Neuvalidierung/Anpassung der Auftragspriorisierung.
- **Ergebnis 2.2** – τ klein, aber σ hoch: trügerische Übereinstimmung → ebenfalls Flag an den Experten, da die PGP-Einschätzung selbst noch nicht tragfähig ist.
- **Ergebnis 3** – Active Learning Loop: jede Experten-Entscheidung (aus 2.1 oder 2.2) erweitert das Context Engineering um einen neuen, validierten Fall und verbessert damit sowohl PGP als auch LLM-Kontext für zukünftige Aufträge.

# Prestep
- Branches aufbauen
- Dockercontainer aufbauen

# Step 1 - Recherche der Feasibility der Konzeptidee
Agenten aufsetzen, der nach solchen Ansätzen, Realisierungen und Best Practices sucht. Diese sollen dokumentiert werden.

# Step 2 - Grenzen (Technisch & Ökonomisch)
Was kann abgedeckt werden, und was nicht? Wann wird der PGP zu aufwändig (O³)?

# Step 3 - ERP-Daten simulieren
CSVs erstellen lassen (als Beispiel-Datenbasis).

# PRÄMISSE: Step 4 - Context Engineering aufbauen
RAGs aufsetzen.

# PRÄMISSE: Step 5 - PGP bauen
- Agent soll einen PGP aufbauen, der bei jeder Vorhersage **beide Werte** liefert: Rang-Prognose (μ) und Selbstunsicherheit (σ).
- Sicherstellen, dass PGP und LLM unabhängig voneinander urteilen (keine gegenseitige Einsicht in die jeweils andere Prognose vor der τ-Berechnung).

# Step 6 - τ- und σ-Kalibrierung
- Skalen von τ (Rangdifferenz) und σ (Varianz) sind nicht direkt vergleichbar und dürfen nicht einfach addiert oder gleich gewichtet werden.
- Für beide Größen getrennt Schwellenwerte (τ₀, σ₀) über Risk-Coverage-Kurven festlegen (z. B. mittels Conformal Risk Control), statt sie ad hoc zu schätzen.
- Eskalationsregel als ODER-Verknüpfung festlegen: τ > τ₀ ODER σ > σ₀ → Flag an Experten.

# KONZEPT: Step 7 - Active Learning Loop bauen
- Jede Experten-Entscheidung aus dem Eskalationsschritt als neuen, validierten Trainingsfall in das Context Engineering zurückführen.
- Threshold-/Risk-Coverage-Kalibrierung (aus Step 6) regelmäßig mit neuen Fällen überprüfen und nachschärfen.

# Step 8 - LIVE TEST
