"""
step7-active-learning/context_writeback.py

"Zurueck ins Context Engineering" aus Konzept-README.md Ergebnis 3
("jede Experten-Entscheidung ... erweitert das Context Engineering um einen
neuen, validierten Fall") und Active-Learning-Loop-und-Frontend-Konzept.md
Abschnitt 1.3 ("das waere die technische Umsetzung von 'zurueck ins Context
Engineering'"). Dort ausdruecklich als Extrapolation ohne Literaturbeleg
markiert, mit offener Sicherheitsfrage: wie eine einzelne Experten-Entscheidung
gedrosselt werden muss, bevor sie mehrere zukuenftige Planungsentscheidungen
gleichzeitig beeinflusst (Systemgrenzen.md Teil C.1, Analogie zu #17/BAGEL).

--- Drosselung hier: KEIN Schreibzugriff auf den lebenden RAG-Index ---
docker-compose.yml mountet step7s Sicht auf rag_documents/ read-only
(":ro") - das bleibt so. Dieses Modul schreibt ausschliesslich in ein
getrenntes Entwuerfe-Verzeichnis (shared/context/entwuerfe/, siehe
docker-compose.yml Kommentar). Ein Mensch muss einen Entwurf manuell nach
step4-context-engineering/rag_documents/ kopieren und dabei vertrauensstufe
explizit auf "intern-verifiziert" setzen, bevor step4/main.py:build_index()
ihn jemals indexiert (dort werden ausschliesslich als "intern-verifiziert"
markierte Dokumente aufgenommen, alles andere faellt in den
skipped-Zweig - siehe step4-context-engineering/main.py). Kein Code in
step4 muss dafuer geaendert werden.

--- Ausloeser: nicht-leere begruendung, nicht nur wahl=="eigene_reihenfolge" ---
begruendung ist bei wahl=="eigene_reihenfolge" bereits Pflichtfeld (siehe
api.py EntscheidungRequest-Validator), bei folgt_pgp/folgt_llm optional.
Als Ausloeser dient hier "begruendung nicht leer" statt eine Einschraenkung
auf wahl=="eigene_reihenfolge" - deckt damit Konzept-README.md Zeile 48/76
("jede Experten-Entscheidung") woertlicher ab, und begrenzt sich von selbst:
ein Planer erzeugt nur dann entwurfswuerdigen Text, wenn er ohnehin schon
etwas erklaeren wollte (kein zusaetzlicher Aufwand, s. Systemgrenzen.md
Teil B.2 zur begrenzten Feedback-Kapazitaet).

--- Provenienz: zweite, code-seitige Sperre ---
store.py erzwingt entschieden_von an ZWEI Stellen (Pydantic-Schema ohne das
Feld UND fest verdrahtet in save_entscheidung/save_propagierte_entscheidung).
should_generate_draft() spiegelt dieses Muster: auch wenn nur api.py's
post_entscheidung() (niemals der Propagations-Pfad) diese Funktion aufruft,
prueft das Modul selbst nochmal entschieden_von=="mensch" - ein zukuenftiger
Refactor, der versehentlich auch den Propagations-Pfad verdrahtet, schlaegt
damit sicher fehl statt agenten-generierten Text unbemerkt als validiertes
Experten-Wissen einzuschleusen (Systemgrenzen.md Teil D: keine Selbstbestaetigung
an eigenen frueheren Agent-Ausgaben).

--- Fail-safe bei fehlendem Auftragskontext ---
kunde/produkt grenzen im Ziel-RAG-Schema (siehe
step4-context-engineering/rag_documents/_template.md) die kuenftige
Retrieval-Treffermenge ein - genau der eingebaute Begrenzer der
Reichweite eines einzelnen Urteils (s.o.). null/null bedeutet dort
"kundenuebergreifend"/"produktuebergreifend", NICHT "unbekannt". Fehlt der
Auftragskontext (Aufruf mit kunde=None oder produkt=None), wird deshalb GAR
KEIN Entwurf geschrieben statt geraten - sonst wuerde aus einer einzelnen,
engen Entscheidung versehentlich ein Dokument mit unbegrenzter Reichweite
(kein Rateversuch, Muster wie propagation.find_similar_open_orders /
rag_lookup.resolve_matched_docs).
"""

import glob
import os
from datetime import date, datetime, timezone

import yaml

CONTEXT_ENTWUERFE_DIR = os.environ.get("CONTEXT_ENTWUERFE_DIR", "context_entwuerfe")

# Dritter Wert neben "intern-verifiziert"/"extern-ungeprueft" (siehe
# _template.md) - ausschliesslich fuer Entwuerfe aus diesem Modul. step4/main.py
# indexiert ausschliesslich exakt "intern-verifiziert"; jeder andere Wert
# (auch dieser) landet dort ohnehin im skipped-Zweig, s. Modulkopf.
VERTRAUENSSTUFE_ENTWURF = "experten-entscheidung-ungeprueft"


def should_generate_draft(decision):
    """entschieden_von=="mensch" UND begruendung nicht leer - s. Modulkopf
    fuer die Begruendung beider Bedingungen."""
    if decision.get("entschieden_von") != "mensch":
        return False
    begruendung = decision.get("begruendung")
    return bool(begruendung and begruendung.strip())


def build_document_text(decision, kunde, produkt):
    """Baut ein RAG-Dokument im Schema von rag_documents/_template.md
    (Frontmatter + Markdown-Body). Frontmatter via yaml.safe_dump statt
    String-Interpolation, um YAML-Escaping-Fehler bei Sonderzeichen (z. B.
    Anfuehrungszeichen in Kundennamen/Begruendungen) zu vermeiden."""
    begruendung = decision["begruendung"].strip()
    order_id = decision["order_id"]
    wahl = decision["wahl"]
    doc_id = f"ENTSCHEID-{decision['id']}"

    if wahl == "folgt_pgp":
        wahl_text = "der PGP-Priorisierung gefolgt"
    elif wahl == "folgt_llm":
        wahl_text = "der LLM-Priorisierung gefolgt"
    else:
        eigene = (decision.get("eigene_reihenfolge") or "").strip()
        wahl_text = f"einer eigenen Reihenfolge gefolgt ({eigene})" if eigene else "einer eigenen Reihenfolge gefolgt"

    frontmatter = {
        "doc_id": doc_id,
        "doc_type": "entscheidungsprotokoll",
        "title": f"Experten-Entscheidung {order_id}",
        "kunde": kunde,
        "produkt": produkt,
        "work_center": None,
        "gueltig_ab": date.today().isoformat(),
        "gueltig_bis": None,
        "autor": f"Experte (Entscheidung #{decision['id']})",
        "vertrauensstufe": VERTRAUENSSTUFE_ENTWURF,
        "tags": ["auto-generiert", "context-writeback", wahl],
        # Zusaetzliche, ueber das Template hinausgehende Felder - rein
        # informativ fuer einen Kurator, werden von step4/main.py:build_index()
        # nicht gelesen und aendern dessen Filterverhalten nicht.
        "quelle_entscheidung_id": decision["id"],
        "quelle_order_id": order_id,
        "erzeugt_am": datetime.now(timezone.utc).isoformat(),
    }
    frontmatter_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()

    body = f"""# Experten-Entscheidung {order_id}

Bei Auftrag {order_id} ist der Planer bei der Eskalationspruefung {wahl_text}
und hat dies begruendet. Automatisch erzeugter Entwurf aus Entscheidung
#{decision['id']} (Context-Writeback) - **noch nicht kuratiert**, siehe
vertrauensstufe. Nicht Teil des lebenden RAG-Index, bis ein Mensch dieses
Dokument geprueft, ggf. angepasst und mit vertrauensstufe:
"intern-verifiziert" nach step4-context-engineering/rag_documents/ verschoben
hat.

## Kernaussage

{begruendung}

## Konsequenz fuer die Planung

Bei aehnlich gelagerten Auftraegen (gleicher Kunde/gleiches Produkt) ist diese
Begruendung als moeglicher Praezedenzfall zu pruefen - keine automatische
Regel, sondern ein dokumentierter Einzelfall, dessen Verallgemeinerung ein
Mensch bei der Kuratierung explizit entscheiden muss.
"""
    return f"---\n{frontmatter_yaml}\n---\n\n{body}"


def write_draft(decision, kunde=None, produkt=None, directory=CONTEXT_ENTWUERFE_DIR):
    """Orchestriert should_generate_draft -> kunde/produkt vorhanden? (sonst
    fail-safe: kein Entwurf, s. Modulkopf) -> build_document_text -> Schreiben.
    Gibt den relativen Dateipfad zurueck, oder None wenn bewusst nichts
    generiert wurde (kein Fehlerfall)."""
    if not should_generate_draft(decision):
        return None
    if not kunde or not produkt:
        return None

    text = build_document_text(decision, kunde, produkt)
    filename = f"ENTSCHEID-{decision['id']}.md"
    path = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def list_drafts(directory=CONTEXT_ENTWUERFE_DIR):
    """Listet alle Entwuerfe im Entwuerfe-Verzeichnis - gleiches
    Frontmatter-Parsing wie rag_lookup.load_rag_metadata()."""
    drafts = []
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        meta = yaml.safe_load(parts[1]) or {}
        drafts.append({
            "doc_id": meta.get("doc_id"),
            "title": meta.get("title"),
            "kunde": meta.get("kunde"),
            "produkt": meta.get("produkt"),
            "gueltig_ab": meta.get("gueltig_ab"),
            "autor": meta.get("autor"),
            "vertrauensstufe": meta.get("vertrauensstufe"),
            "pfad": path,
        })
    return drafts
