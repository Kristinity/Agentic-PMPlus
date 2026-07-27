"""
step9-upload-interface/app.py - Agentic-PMPlus

Nutzer-Vorgabe: die ERP-Stammdaten (Auftragshistorie, Maschinen, Lager,
Stoerungen) sollen fixer Teil des Context Engineering sein - nicht bei jedem
Lauf erneut hochgeladen werden. Hochgeladen werden ausschliesslich NEUE
Auftraege nach einem festen Auftragstemplate (siehe pipeline.py
ORDER_TEMPLATE_COLUMNS); die PGP-Priorisierung bewertet sie im Kontext der
gesamten bestehenden Auftragslage (step3-erp-simulation/output_2026/, siehe
BASELINE_DATA_DIR unten), nicht isoliert.

Kein neuer fachlicher Code - reine Oberflaeche um pipeline.py, das wiederum
dieselben main.py-Skripte aus step5-pgp/step6-calibration aufruft.
"""

import os
from datetime import date

import pandas as pd
import streamlit as st

from pipeline import (missing_baseline_files, build_run_dir, run_pipeline,
                       validate_new_orders, order_template_csv_bytes,
                       empty_new_orders_editor_df, drop_empty_rows, VALID_PRODUCT_IDS)

STEP5_DIR = os.environ.get("STEP5_DIR", "/app/step5-pgp")
STEP6_DIR = os.environ.get("STEP6_DIR", "/app/step6-calibration")
RAG_DOCUMENTS_DIR = os.environ.get("RAG_DOCUMENTS_DIR", "/app/rag_documents")
BASELINE_DATA_DIR = os.environ.get("BASELINE_DATA_DIR", "/app/baseline_data")
RUNS_DIR = os.environ.get("RUNS_DIR", "/app/runs")

AMPEL_LABEL = {
    "robuste_uebereinstimmung": "🟢 Robuste Übereinstimmung",
    "truegerische_ruhe": "🟡 Trügerische Ruhe",
    "klarer_fall_fuer_review": "🔴 Klarer Fall für Review",
}

st.set_page_config(page_title="Agentic-PMPlus – Auftrags-Priorisierung", page_icon="📦",
                    layout="wide")

st.title("📦 Neue Aufträge priorisieren")
st.caption(
    "Die Auftragshistorie, Maschinen-, Lager- und Störungsdaten sind fixer Teil "
    "des Context Engineering und müssen nicht hochgeladen werden. Hier werden "
    "ausschließlich neue Aufträge hochgeladen – sie werden zusammen mit der "
    "bestehenden, offenen Auftragslage priorisiert (nicht isoliert betrachtet). "
    "Für Review/Entscheidung pro Auftrag weiterhin das Interface unter Port 8080 "
    "verwenden – dieser Screen ändert die dortige Warteschlange nicht."
)

missing_baseline = missing_baseline_files(BASELINE_DATA_DIR)
if missing_baseline:
    st.error(
        "Konfigurationsfehler: dem System fehlen Kontext-Dateien "
        f"({', '.join(missing_baseline)}). Das ist kein Nutzerfehler – bitte "
        "an die Projektverantwortlichen melden."
    )
    st.stop()

st.subheader("Neue Aufträge")
st.caption(
    "Zeilen unten über das **+** hinzufügen, über das 🗑️-Symbol am Zeilenende "
    "entfernen – beliebig viele Aufträge auf einmal, keine Datei nötig. "
    "**order_id** wird automatisch vergeben."
)

if "new_orders_editor" not in st.session_state:
    st.session_state.new_orders_editor = empty_new_orders_editor_df()

edited_orders = st.data_editor(
    st.session_state.new_orders_editor,
    num_rows="dynamic",
    use_container_width=True,
    key="new_orders_data_editor",
    column_config={
        "customer": st.column_config.TextColumn("customer", required=True,
                                                  help="z. B. Becksbrauerei"),
        "product_id": st.column_config.SelectboxColumn(
            "product_id", options=VALID_PRODUCT_IDS, required=True),
        "variant": st.column_config.TextColumn("variant", help="optional"),
        "order_date": st.column_config.DateColumn("order_date", required=True,
                                                    format="YYYY-MM-DD"),
        "due_date": st.column_config.DateColumn("due_date", required=True,
                                                  format="YYYY-MM-DD"),
        "is_rush": st.column_config.CheckboxColumn("is_rush", default=False),
        "priority": st.column_config.SelectboxColumn(
            "priority", options=["normal", "hoch"], default="normal"),
        "quantity": st.column_config.NumberColumn("quantity", required=True,
                                                    min_value=1, step=1),
    },
)

with st.expander("Alternativ: CSV-Datei hochladen (z. B. viele Aufträge auf einmal)"):
    st.download_button(
        "📄 Auftragstemplate herunterladen",
        data=order_template_csv_bytes(),
        file_name="auftragstemplate.csv",
        mime="text/csv",
    )
    uploaded_orders = st.file_uploader("CSV nach Vorlage hochladen", type="csv")
    st.caption(
        "Wenn hier eine Datei hochgeladen wird, wird sie verwendet – die Tabelle "
        "oben wird in diesem Fall ignoriert."
    )

as_of = st.date_input(
    "Auswertungsdatum", value=date.today(),
    help="Bezugsdatum für Puffer-/Dringlichkeitsberechnung (AS_OF_DATE). "
         "Aufträge mit Liefertermin davor gelten als bereits erledigt.",
)
api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
use_real_llm = st.checkbox(
    "Echte, unabhängige LLM-Einschätzung verwenden (statt Mock)",
    value=api_key_present, disabled=not api_key_present,
    help=("Benötigt ein gültiges ANTHROPIC_API_KEY-Guthaben in .env." if api_key_present
          else "Kein ANTHROPIC_API_KEY gefunden – läuft im Mock-Modus."),
)
if not api_key_present:
    st.caption("⚠️ Kein ANTHROPIC_API_KEY gefunden – Ergebnis läuft im Mock-Modus "
               "(τ nicht aussagekräftig, siehe RUNBOOK.md).")

has_table_rows = len(drop_empty_rows(edited_orders)) > 0
run_clicked = st.button("Priorisierung berechnen", type="primary",
                         disabled=not (has_table_rows or uploaded_orders is not None))
if not (has_table_rows or uploaded_orders is not None):
    st.info("Bitte mindestens einen neuen Auftrag in der Tabelle eintragen oder eine "
            "CSV-Datei hochladen.")

if run_clicked:
    if uploaded_orders is not None:
        try:
            new_orders_df = pd.read_csv(uploaded_orders)
        except Exception as exc:  # noqa: BLE001 - CSV-Parsing-Fehler dem Nutzer zeigen statt Crash
            st.error(f"Datei konnte nicht gelesen werden: {exc}")
            st.stop()
    else:
        new_orders_df = drop_empty_rows(edited_orders)

    errors = validate_new_orders(new_orders_df)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    try:
        with st.spinner("Priorisierung läuft (PGP-Training + unabhängige "
                         "LLM-Einschätzung, kann 10–30s dauern)…"):
            run_dir, new_ids = build_run_dir(RUNS_DIR, BASELINE_DATA_DIR, new_orders_df)
            result = run_pipeline(
                run_dir=run_dir,
                as_of_date_iso=as_of.isoformat(),
                mock_llm=not use_real_llm,
                step5_dir=STEP5_DIR,
                step6_dir=STEP6_DIR,
                rag_documents_dir=RAG_DOCUMENTS_DIR,
                new_order_ids=new_ids,
            )

        if not result.ok:
            st.error(result.error)
            with st.expander("Rohausgabe (für Fehlersuche)"):
                st.text("--- step5-pgp stdout ---\n" + result.step5_stdout)
                st.text("--- step5-pgp stderr ---\n" + result.step5_stderr)
                st.text("--- step6-calibration stdout ---\n" + result.step6_stdout)
                st.text("--- step6-calibration stderr ---\n" + result.step6_stderr)
        else:
            df = result.result_df
            new_in_result = df[df["order_id"].isin(result.new_order_ids)]
            st.success(
                f"{len(df)} offene Aufträge priorisiert, davon "
                f"{len(new_in_result)} von {len(result.new_order_ids)} neu "
                "hochgeladenen."
            )
            if len(new_in_result) < len(result.new_order_ids):
                st.warning(
                    "Nicht alle neuen Aufträge erscheinen im Ergebnis – sie hatten "
                    "vermutlich einen späteren Liefertermin als die aktuell "
                    "priorisierten Aufträge und wurden nicht in die engste "
                    "Auswahl übernommen."
                )

            counts = df["ampel_status"].value_counts()
            m1, m2, m3 = st.columns(3)
            m1.metric(AMPEL_LABEL["robuste_uebereinstimmung"],
                      int(counts.get("robuste_uebereinstimmung", 0)))
            m2.metric(AMPEL_LABEL["truegerische_ruhe"],
                      int(counts.get("truegerische_ruhe", 0)))
            m3.metric(AMPEL_LABEL["klarer_fall_fuer_review"],
                      int(counts.get("klarer_fall_fuer_review", 0)))

            display_df = df.copy()
            display_df["Ampel"] = display_df["ampel_status"].map(AMPEL_LABEL)
            display_df["Neu hochgeladen"] = display_df["order_id"].isin(
                result.new_order_ids).map({True: "🆕", False: ""})
            show_cols = ["rank", "order_id", "Neu hochgeladen", "customer", "product_id",
                         "due_date", "Ampel", "tau", "sigma", "pgp_begruendung",
                         "llm_begruendung"]
            show_cols = [c for c in show_cols if c in display_df.columns]
            st.dataframe(display_df[show_cols], use_container_width=True, hide_index=True)

            warn_block = ""
            if "!!! LLM meldet Warnungen zum Kontext:" in result.step6_stdout:
                warn_block = result.step6_stdout.split(
                    "!!! LLM meldet Warnungen zum Kontext:")[1].split("\n\n")[0]
            if warn_block.strip():
                st.warning("Die LLM hat beim Priorisieren Unsicherheiten/Annahmen "
                           "gemeldet:\n" + warn_block)

            st.download_button(
                "Ergebnis als CSV herunterladen",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="tau_vergleich.csv",
                mime="text/csv",
            )
    except Exception as exc:  # noqa: BLE001 - dem Nutzer die Ursache zeigen statt eines Stacktrace-Crashs
        st.error(f"Unerwarteter Fehler: {exc}")
