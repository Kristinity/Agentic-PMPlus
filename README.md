# Agentic-PMPlus
Wie kann ein LLM Wissen, was es nicht weiß? Prüfung der Implementierung einer unabhängigen lokalen Prüfinstanz, zur Wahrung der Degradation des LLM Outputs, Wahrung der Data Privacy, Und zur Optimierung der Tokenkosten 

# Konzeptidee
Umfeld: KMU in DE, PPS (typische Ingenieurtätigkeiten)
Ziel: (das teuerste in Prozess nur dann einsetzen wenn nötig - den Menschen)
Ausgangssituation: Wenig "gut" strukturierte Daten für eigenes LLM oder dem Feintuning/Training eines Drittanbieter LLMS.
Ein lokaler Preference GP (Gaussian Process) soll anhand der vollen Dateneinsicht in das Context Engineering bei Eingang von Aufträgen eine Reihenfolge der abzuarbeitenden Aufträgen erstellen, dabei ist der die Priorisierung abnehmend. 
Die gleiche Prognose (Priorisierung über das  soll das LLM auch erstellen, mit eingeschränkten Zugriff auf Unternehmensdaten und kleinstmöglichen Kontext)
Die Differenz zwischen LLM Output und PGP ist ab einem bestimmten Wert 𝝉 zu groß, sodass ein Flag gesetzt wird und ein Supervision vom Experten (Produktionsplaner) eingeholt wird.
Die Prognose der Auftragspriorisierung wird anhand der prognostizierten DZ, aktuellen Maschinenverfügbarkeit, vertraglich festgelegtem Bruttopreis, Materialverfügbarkeit, Abhängigkeiten zu laufenden Aufträgen, Mitarbeiter Coverage (Urlaubszeiten - Krankmeldungen) und Lieferantenbewertung aufgestellt.
Volle Einsicht auf das ERP & Context Engineering hat das PGP. Eingeschränkte das LLM, das LLM erhält zusätzlich unstrukturierte Informationen (Notizen bspw.)
Ergebnis 1: 𝝉 ist klein -> LLM liegt richtig - Produktionsplan und Arbeitsplan schreiben und zu Freigabe an Experten/Verantwortlichen schicken
Ergebnis 2.1.: 𝝉 ist groß -> LLM liegt falsch - Flag & Trigger an Experten zur neuvalidierung /Anpassung der Auftragspriorisierung
Ergebnis 2.2.: Active Learning Loop, Erweiterung des Context Engineering um neuen Fall

# Step 1 - Recherche der Feasability der Konzepidee
Agenten aufsetzen, der nach solchen Ansätzen, Realisierungen und Bestpractices sucht. Diese sollen dokumentiert werden.

# Step 2 - Grenzen (Technisch & Ökonomisch)
Was kann abgedeckt werden, und was nicht? Wann wird der PGP zu aufwändig (O³) 

# Step 3 - ERP DATA simulieren
CSVs erstellen lassen (als Beispiel Datenbasis)

# PRÄMISSE: Step 4 - Context Engieneering aufbauen
RAGs aufsetzen

# PRÄMISSE: Step 5 - PGP bauen 
- Agent soll einen PGP aufbauen

# KONZEPT: Step 6 - Active Learning Loop bauen 
- Treshhold - Risk Coverage - prüfen

# Step 7 - LIVE TEST
