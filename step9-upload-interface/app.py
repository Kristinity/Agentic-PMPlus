"""
step9-upload-interface/app.py - Agentic-PMPlus

Neue Userstory: Jens laedt seine eigenen, generierten Auftragsdaten hoch und
bekommt die PGP-Priorisierung + unabhaengige LLM-Einschaetzung (Step 5+6) als
Ergebnis zurueck, ohne die Kommandozeile/Docker direkt bedienen zu muessen.
Kein neuer fachlicher Code - reine Oberflaeche um pipeline.py, das wiederum
dieselben main.py-Skripte aus step5-pgp/step6-calibration aufruft, die schon
einzeln getestet sind (siehe RUNBOOK.md fuer den bisherigen, rein
Docker-basierten Weg).

Framework-Entscheidung (Streamlit) und zwei Alternativen (Gradio, FastAPI+React)
mit dem Nutzer abgestimmt - Ruby als Option verworfen, weil die komplette
bestehende Logik (PGP/GPyTorch, Anthropic-Call) bereits in Python steht und ein
zweiter Sprach-Stack hier keinen Mehrwert haette.
"""

import os
from datetime import date

import pandas as pd
import streamlit as st

from pipeline import (REQUIRED_ERP_FILES, build_run_dir, missing_required_files,
                       run_pipeline)

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

st.title("📦 Auftrags-Priorisierung hochladen")
st.caption(
    "Lade deine generierten Auftragsdaten hoch und erhalte die PGP-Priorisierung "
    "sowie die unabhängige LLM-Einschätzung (τ/Ampel) als Ergebnis zurück. "
    "Für die Detailprüfung und das Erfassen von Entscheidungen pro Auftrag "
    "weiterhin das Review-Interface unter Port 8080 verwenden – dieser Screen "
    "erzeugt nur die Priorisierung, ändert die laufende Warteschlange dort nicht."
)

with st.expander("Welche Dateien werden gebraucht?", expanded=False):
    st.markdown(
        "Pflicht ist **orders.csv** (deine generierten Aufträge). Die übrigen "
        "sechs Stammdaten-Dateien (`work_centers.csv`, `inventory.csv`, "
        "`disruptions.csv`, `bom.csv`, `routings.csv`, `calendar.csv`) kannst du "
        "optional mit hochladen – für alles, was du nicht hochlädst, wird das "
        "zuletzt in der Pipeline erzeugte Datenset als Fallback verwendet. "
        "Format wie in `step3-erp-simulation/output_2025/`."
    )

uploaded = {}
orders_file = st.file_uploader("orders.csv (Pflicht)", type="csv", key="orders")
if orders_file is not None:
    uploaded["orders.csv"] = orders_file

with st.expander("Weitere Stammdaten hochladen (optional)"):
    for name in ["work_centers.csv", "inventory.csv", "disruptions.csv",
                 "bom.csv", "routings.csv", "calendar.csv"]:
        f = st.file_uploader(name, type="csv", key=name)
        if f is not None:
            uploaded[name] = f

col1, col2 = st.columns(2)
with col1:
    as_of = st.date_input(
        "Stichtag für die Priorisierung", value=date(2026, 1, 1),
        help="Bezugsdatum für Puffer-/Dringlichkeitsberechnung (AS_OF_DATE).",
    )
with col2:
    api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    use_real_llm = st.checkbox(
        "Echte, unabhängige LLM-Einschätzung verwenden (statt Mock)",
        value=api_key_present,
        disabled=not api_key_present,
        help=("Benötigt ein gültiges ANTHROPIC_API_KEY-Guthaben in .env." if api_key_present
              else "Kein ANTHROPIC_API_KEY gefunden – läuft im Mock-Modus."),
    )
    if not api_key_present:
        st.caption("⚠️ Kein ANTHROPIC_API_KEY gefunden – Ergebnis läuft im Mock-Modus "
                   "(τ nicht aussagekräftig, siehe RUNBOOK.md).")

run_clicked = st.button("Priorisierung berechnen", type="primary",
                         disabled=(orders_file is None))
if orders_file is None:
    st.info("Bitte zuerst orders.csv hochladen.")

if run_clicked:
    missing = missing_required_files(
        {k: "x" for k in uploaded}, BASELINE_DATA_DIR)
    if missing:
        st.error(
            "Diese Pflicht-Dateien fehlen sowohl im Upload als auch als "
            f"Fallback-Datenset: {', '.join(missing)}. Bitte hochladen."
        )
    else:
        saved_paths = {}
        run_dir = None
        try:
            for name, f in uploaded.items():
                tmp_path = os.path.join("/tmp", f"upload_{name}")
                with open(tmp_path, "wb") as out:
                    out.write(f.getbuffer())
                saved_paths[name] = tmp_path

            run_dir = build_run_dir(RUNS_DIR, saved_paths, BASELINE_DATA_DIR)

            with st.spinner("Priorisierung läuft (PGP-Training + unabhängige LLM-Einschätzung, "
                             "kann 10–30s dauern)…"):
                result = run_pipeline(
                    run_dir=run_dir,
                    as_of_date_iso=as_of.isoformat(),
                    mock_llm=not use_real_llm,
                    step5_dir=STEP5_DIR,
                    step6_dir=STEP6_DIR,
                    rag_documents_dir=RAG_DOCUMENTS_DIR,
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
                st.success(f"{len(df)} offene Aufträge priorisiert.")

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
                show_cols = ["rank", "order_id", "customer", "product_id", "due_date",
                             "Ampel", "tau", "sigma", "pgp_begruendung", "llm_begruendung"]
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
