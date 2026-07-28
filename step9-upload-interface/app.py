"""
step9-upload-interface/app.py - Agentic-PMPlus

Nutzer-Vorgabe: die ERP-Stammdaten (Auftragshistorie, Maschinen, Lager,
Stoerungen) sollen fixer Teil des Context Engineering sein - nicht bei jedem
Lauf erneut hochgeladen werden. Hochgeladen werden ausschliesslich NEUE
Auftraege nach einem festen Auftragstemplate (siehe pipeline.py
ORDER_TEMPLATE_COLUMNS); die PGP-Priorisierung bewertet sie im Kontext der
gesamten bestehenden Auftragslage (step3-erp-simulation/output_2026/, siehe
BASELINE_DATA_DIR unten), nicht isoliert.

Mobile-freundliches Layout: st.data_editor/st.dataframe reflowen NICHT auf
schmalen Bildschirmen - eine Tabelle mit vielen Spalten erzwingt horizontales
Scrollen innerhalb des Widgets, selbst wenn die Seite drumherum (Viewport-
Meta-Tag) responsiv ist. Primaere Eingabe ist deshalb ein einspaltiges
Formular (ein Auftrag pro Absenden), das wie jeder andere Block reflowt. Die
breite Tabelle/CSV-Upload bleibt als "Erweitert"-Bereich fuer Bulk-Eingabe auf
groesseren Bildschirmen erhalten. Das Ergebnis wird als gestapelte
Karten-Liste (ein Expander pro Auftrag) statt einer breiten Tabelle gezeigt.

Kein neuer fachlicher Code - reine Oberflaeche um pipeline.py, das wiederum
dieselben main.py-Skripte aus step5-pgp/step6-calibration aufruft.
"""

import os
import shutil
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

st.set_page_config(page_title="Agentic-PMPlus – Auftrags-Priorisierung", page_icon="📋✅",
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

# --- Primaere Eingabe: ein Auftrag pro Formular (mobile-freundlich) ---------

st.subheader("Neuen Auftrag hinzufügen")
st.caption(
    "Ein Formular pro Auftrag – reflowt auf jedem Bildschirm, auch Handy. "
    "Für viele Aufträge auf einmal siehe „Erweitert“ weiter unten. "
    "**order_id** wird automatisch vergeben."
)

if "quick_orders" not in st.session_state:
    st.session_state.quick_orders = []

with st.form("quick_add_form", clear_on_submit=True):
    customer_in = st.text_input("Kunde", placeholder="z. B. Becksbrauerei")
    product_id_in = st.selectbox("Produkt", VALID_PRODUCT_IDS)
    is_sonderauftrag_in = st.checkbox(
        "Sonderauftrag (gesonderte Vergütung)",
        help="Sonderanfertigung mit gesonderter Vergütung, unabhängig von "
             "zeitlicher Dringlichkeit. Nicht zu verwechseln mit „Priorität“ "
             "unten – die beschreibt zeitliche Dringlichkeit, nicht die "
             "Vergütungsart.",
    )
    order_date_in = st.date_input("Bestelldatum", value=date.today())
    due_date_in = st.date_input("Liefertermin", value=date.today())
    quantity_in = st.number_input("Menge", min_value=1, step=1, value=1)
    with st.expander("Weitere Angaben (optional)"):
        variant_in = st.text_input("Variante", value="")
        is_rush_in = st.checkbox("Eilauftrag (is_rush)", value=False)
        priority_in = st.selectbox("Priorität", ["normal", "hoch"])
    quick_submitted = st.form_submit_button("➕ Zur Liste hinzufügen", type="primary")

if quick_submitted:
    if not customer_in.strip():
        st.error("Bitte einen Kundennamen eintragen.")
    else:
        st.session_state.quick_orders.append({
            "customer": customer_in.strip(),
            "product_id": product_id_in,
            "is_sonderauftrag": is_sonderauftrag_in,
            "variant": variant_in,
            "order_date": order_date_in,
            "due_date": due_date_in,
            "is_rush": is_rush_in,
            "priority": priority_in,
            "quantity": int(quantity_in),
        })

if st.session_state.quick_orders:
    st.write(f"**{len(st.session_state.quick_orders)} Auftrag/Aufträge in der Liste:**")
    for i, o in enumerate(st.session_state.quick_orders):
        # 2 Spalten (Text + Loeschen) bleiben auch auf schmalen Bildschirmen
        # lesbar - anders als eine 8-Spalten-Tabelle weiter unten.
        row_col, del_col = st.columns([6, 1])
        marker = " ⭐" if o["is_sonderauftrag"] else ""
        row_col.write(
            f"{o['customer']} – {o['product_id']} × {o['quantity']}, "
            f"fällig {o['due_date']}{marker}"
        )
        if del_col.button("🗑️", key=f"del_quick_{i}", help="Aus der Liste entfernen"):
            st.session_state.quick_orders.pop(i)
            st.rerun()

# --- Erweitert: Tabelle/CSV fuer Bulk-Eingabe (Desktop/Tablet) --------------

with st.expander("Erweitert: mehrere Aufträge auf einmal (Tabelle oder CSV)"):
    st.caption(
        "Für Desktop/Tablet gedacht – die Tabelle scrollt auf schmalen "
        "Bildschirmen seitlich. Für einzelne Aufträge das Formular oben nutzen."
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
            "is_sonderauftrag": st.column_config.CheckboxColumn(
                "is_sonderauftrag", default=False,
                help="Sonderanfertigung mit gesonderter Vergütung, unabhängig von "
                     "zeitlicher Dringlichkeit. Nicht zu verwechseln mit 'priority' "
                     "('normal'/'hoch') – priority beschreibt, wie dringend ein "
                     "Auftrag zeitlich ist, is_sonderauftrag, ob er gesondert "
                     "vergütet wird."),
            "variant": st.column_config.TextColumn("variant", help="optional"),
            "order_date": st.column_config.DateColumn("order_date", required=True,
                                                        format="YYYY-MM-DD"),
            "due_date": st.column_config.DateColumn("due_date", required=True,
                                                      format="YYYY-MM-DD"),
            "is_rush": st.column_config.CheckboxColumn("is_rush", default=False),
            "priority": st.column_config.SelectboxColumn(
                "priority", options=["normal", "hoch"], default="normal",
                help="Zeitliche Dringlichkeit – unabhängig vom 'is_sonderauftrag'-"
                     "Flag (das beschreibt die Vergütungsart, nicht die Dringlichkeit)."),
            "quantity": st.column_config.NumberColumn("quantity", required=True,
                                                        min_value=1, step=1),
        },
    )

    st.download_button(
        "📄 Auftragstemplate herunterladen",
        data=order_template_csv_bytes(),
        file_name="auftragstemplate.csv",
        mime="text/csv",
    )
    uploaded_orders = st.file_uploader("CSV nach Vorlage hochladen", type="csv")
    st.caption(
        "Wenn hier eine Datei hochgeladen wird, wird NUR sie verwendet – weder "
        "die Tabelle oben noch die Schnellerfassungs-Liste."
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

table_rows = drop_empty_rows(edited_orders)
has_manual_rows = len(st.session_state.quick_orders) > 0 or len(table_rows) > 0
run_clicked = st.button("Priorisierung berechnen", type="primary",
                         disabled=not (has_manual_rows or uploaded_orders is not None))
if not (has_manual_rows or uploaded_orders is not None):
    st.info("Bitte mindestens einen neuen Auftrag erfassen (Formular oder "
            "Tabelle) oder eine CSV-Datei hochladen.")

if run_clicked:
    if uploaded_orders is not None:
        try:
            new_orders_df = pd.read_csv(uploaded_orders)
        except Exception as exc:  # noqa: BLE001 - CSV-Parsing-Fehler dem Nutzer zeigen statt Crash
            st.error(f"Datei konnte nicht gelesen werden: {exc}")
            st.stop()
    else:
        # Schnellerfassungs-Liste (mobile-freundliches Formular) und
        # Tabellen-Editor (Erweitert) ergaenzen sich - beide koennen
        # gleichzeitig befuellt sein, z. B. wenn jemand auf dem Handy anfaengt
        # und spaeter am Desktop weitermacht.
        parts = []
        if st.session_state.quick_orders:
            parts.append(pd.DataFrame(st.session_state.quick_orders))
        if len(table_rows) > 0:
            parts.append(table_rows)
        new_orders_df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    errors = validate_new_orders(new_orders_df)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    try:
        with st.spinner("Priorisierung läuft (PGP-Training + unabhängige "
                         "LLM-Einschätzung, kann 10–30s dauern)…"):
            run_dir, new_ids = build_run_dir(RUNS_DIR, BASELINE_DATA_DIR, new_orders_df)
            try:
                result = run_pipeline(
                    run_dir=run_dir,
                    as_of_date_iso=as_of.isoformat(),
                    mock_llm=not use_real_llm,
                    step5_dir=STEP5_DIR,
                    step6_dir=STEP6_DIR,
                    rag_documents_dir=RAG_DOCUMENTS_DIR,
                    new_order_ids=new_ids,
                )
            finally:
                # run_dir wird nur fuer die Subprozess-Laeufe gebraucht - Ergebnis
                # (result.result_df) liegt danach im Speicher. Ohne dieses Aufraeumen
                # sammelt sich pro Klick ein neues tempfile.mkdtemp()-Verzeichnis
                # unter RUNS_DIR an, das nie wieder geloescht wuerde (Streamlit-
                # Container laeuft lange, RUNS_DIR waechst unbegrenzt).
                shutil.rmtree(run_dir, ignore_errors=True)

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

            # is_sonderauftrag wird von step5-pgp/step6-calibration noch nicht
            # durchgereicht (das kommt erst mit TICKET-B11) - die Ergebnisdatei
            # (df/tau_vergleich.csv) hat die Spalte also nicht. Wir kennen den
            # Wert aber pro Zeile bereits aus new_orders_df (dem Eingabe-
            # DataFrame vor prepare_new_orders) und new_ids (in derselben
            # Zeilenreihenfolge von build_run_dir zurueckgegeben) - analog zum
            # "Neu hochgeladen"-Muster unten, nur auf Basis der Eingabedaten
            # statt der Ergebnisdatei.
            def _is_truthy_flag(value):
                if isinstance(value, bool):
                    return value
                if pd.isna(value):
                    return False
                return str(value).strip().lower() in ("true", "1")

            sonderauftrag_order_ids = set()
            if "is_sonderauftrag" in new_orders_df.columns:
                sonderauftrag_order_ids = {
                    order_id for order_id, flag in zip(new_ids, new_orders_df["is_sonderauftrag"])
                    if _is_truthy_flag(flag)
                }

            display_df = df.copy()
            display_df["Ampel"] = display_df["ampel_status"].map(AMPEL_LABEL)
            display_df["Neu hochgeladen"] = display_df["order_id"].isin(
                result.new_order_ids).map({True: "🆕", False: ""})
            display_df["Sonderauftrag"] = display_df["order_id"].isin(
                sonderauftrag_order_ids).map({True: "⭐", False: ""})

            # Mobile-freundlich: gestapelte Karten (ein Expander pro Auftrag)
            # statt einer breiten Tabelle - reflowt wie jeder andere Block,
            # erzwingt kein seitliches Scrollen. Die volle Tabelle bleibt
            # optional (Expander unten) fuer Desktop-Nutzer, die Rohdaten
            # nebeneinander vergleichen wollen.
            st.subheader("Ergebnis")
            for _, row in display_df.sort_values("rank").iterrows():
                marker = f"{row['Neu hochgeladen']}{row['Sonderauftrag']}".strip()
                header = f"#{int(row['rank'])} · {row['order_id']} · {row['customer']}"
                if marker:
                    header += f" {marker}"
                header += f" · {row['Ampel']}"
                with st.expander(header):
                    st.write(f"**Produkt:** {row['product_id']}  ·  **Fällig:** {row['due_date']}")
                    tau_val = row.get("tau")
                    sigma_val = row.get("sigma")
                    tau_str = f"{tau_val:.2f}" if pd.notna(tau_val) else "–"
                    sigma_str = f"{sigma_val:.3f}" if pd.notna(sigma_val) else "–"
                    st.write(f"τ = {tau_str}   σ = {sigma_str}")
                    if row.get("pgp_begruendung"):
                        st.caption(f"PGP: {row['pgp_begruendung']}")
                    if row.get("llm_begruendung"):
                        st.caption(f"LLM: {row['llm_begruendung']}")

            with st.expander("Als Tabelle anzeigen (breiter Bildschirm empfohlen)"):
                show_cols = ["rank", "order_id", "Neu hochgeladen", "Sonderauftrag", "customer",
                             "product_id", "due_date", "Ampel", "tau", "sigma", "pgp_begruendung",
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
