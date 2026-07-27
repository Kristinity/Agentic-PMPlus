"""
step9-upload-interface/pipeline.py - Agentic-PMPlus

Reine Orchestrierungs-Logik (kein Streamlit-Import), damit sie unabhaengig von
der UI getestet werden kann. Fuehrt step5-pgp/main.py und
step6-calibration/main.py als Subprozesse gegen ein Lauf-Verzeichnis aus -
bewusst KEINE Neuimplementierung der PGP-/Kalibrierungs-Logik, sondern
Wiederverwendung derselben main.py-Skripte, die schon einzeln Docker-getestet
sind (dieselbe Env-Var-Schnittstelle wie in docker-compose.yml fuer
step5-pgp/step6-calibration).

Nutzer-Vorgabe: die ERP-Stammdaten (Auftragshistorie, Maschinen, Lager,
Stoerungen - siehe REQUIRED_ERP_FILES) sind fixer Teil des Context
Engineering (step3-erp-simulation/output_2026/, read-only gemountet) und
werden NICHT hochgeladen. Hochgeladen werden ausschliesslich NEUE Auftraege
nach ORDER_TEMPLATE_COLUMNS - die werden der bestehenden orders.csv
hinzugefuegt (nicht ersetzt), damit die PGP-Priorisierung sie im Kontext der
gesamten Auftragslage bewertet.
"""

import io
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field

import pandas as pd

REQUIRED_ERP_FILES = ["orders.csv", "bom.csv", "routings.csv", "work_centers.csv",
                       "calendar.csv", "inventory.csv", "disruptions.csv"]

# Schema von orders.csv (siehe step3-erp-simulation/main.py generate_orders) -
# order_id wird beim Upload immer neu vergeben (siehe prepare_new_orders),
# daher hier nicht als Pflichtfeld gelistet.
NEW_ORDER_REQUIRED_COLUMNS = ["customer", "product_id", "order_date", "due_date", "quantity"]
NEW_ORDER_OPTIONAL_DEFAULTS = {"variant": None, "is_rush": False, "priority": "normal"}
ORDER_TEMPLATE_COLUMNS = ["order_id", "customer", "product_id", "variant",
                           "order_date", "due_date", "is_rush", "priority", "quantity"]

# Nur diese beiden Produkte existieren im simulierten Sortiment von K.S.
# (siehe company_profile.example.yaml) - Freitext bei product_id wuerde die
# PGP-Feature-Berechnung (BOM/Routing-Lookup) stillschweigend scheitern lassen.
VALID_PRODUCT_IDS = ["P-KK", "P-DV"]


def order_template_csv_bytes():
    """Downloadbare Vorlage fuer den 'Neue Auftraege hochladen'-Uploader -
    eine Beispielzeile, order_id absichtlich leer (wird beim Verarbeiten immer
    automatisch vergeben, damit keine Kollision mit bestehenden IDs entsteht)."""
    example = pd.DataFrame([{
        "order_id": "",
        "customer": "Becksbrauerei",
        "product_id": "P-KK",
        "variant": "",
        "order_date": "2026-07-27",
        "due_date": "2026-08-10",
        "is_rush": "False",
        "priority": "normal",
        "quantity": 12,
    }], columns=ORDER_TEMPLATE_COLUMNS)
    buf = io.StringIO()
    example.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def empty_new_orders_editor_df():
    """Startzustand fuer die In-App-Tabelle (st.data_editor) - 0 Zeilen, aber
    mit den richtigen Spalten, damit column_config greift. Ersetzt den
    Download-Bearbeiten-Hochladen-Umweg ueber eine externe CSV-Datei."""
    cols = [c for c in ORDER_TEMPLATE_COLUMNS if c != "order_id"]
    return pd.DataFrame(columns=cols)


def drop_empty_rows(df):
    """Entfernt Zeilen, die in allen Pflichtspalten leer sind - passiert z. B.
    wenn im data_editor eine Zeile per '+' angelegt, aber nicht ausgefuellt
    wurde."""
    present_required = [c for c in NEW_ORDER_REQUIRED_COLUMNS if c in df.columns]
    if not present_required:
        return df
    return df[~df[present_required].isna().all(axis=1)].reset_index(drop=True)


def validate_new_orders(df):
    """Prueft Pflichtspalten und product_id-Werte. Gibt eine Liste
    verstaendlicher Fehlermeldungen zurueck (leer = valide)."""
    errors = []
    missing_cols = [c for c in NEW_ORDER_REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Pflichtspalten fehlen: {', '.join(missing_cols)}. "
                       f"Bitte die Vorlage verwenden.")
        return errors  # weitere Checks brauchen die Spalten
    if df[NEW_ORDER_REQUIRED_COLUMNS].isna().any().any():
        errors.append("Mindestens eine Pflichtspalte hat leere Zellen "
                       f"({', '.join(NEW_ORDER_REQUIRED_COLUMNS)}).")
    bad_products = sorted(set(df["product_id"].dropna()) - set(VALID_PRODUCT_IDS))
    if bad_products:
        errors.append(f"Unbekannte product_id-Werte: {', '.join(bad_products)}. "
                       f"Erlaubt: {', '.join(VALID_PRODUCT_IDS)}.")
    return errors


def prepare_new_orders(df, existing_order_ids):
    """Vergibt kollisionsfreie order_ids (NEU-0001, ...), fuellt optionale
    Spalten mit Default-Werten und bringt die Spaltenreihenfolge auf das
    orders.csv-Schema. Erwartet bereits validierte Pflichtspalten."""
    df = df.copy()
    n = len(df)
    i = 1
    new_ids = []
    while len(new_ids) < n:
        candidate = f"NEU-{i:04d}"
        if candidate not in existing_order_ids:
            new_ids.append(candidate)
        i += 1
    df["order_id"] = new_ids

    for col, default in NEW_ORDER_OPTIONAL_DEFAULTS.items():
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default)
    df["variant"] = df.apply(
        lambda r: r["variant"] if pd.notna(r["variant"]) and str(r["variant"]).strip()
        else f"{r['product_id']}-V1", axis=1)

    # order_date/due_date kommen aus dem data_editor als datetime.date-Objekte,
    # aus einem CSV-Upload dagegen als Strings - beide auf dasselbe
    # JJJJ-MM-TT-Format normalisieren, damit die kombinierte orders.csv
    # konsistent bleibt (sonst uebernimmt to_csv() im Zweifel str()).
    for col in ["order_date", "due_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    df["quantity"] = df["quantity"].astype(int)

    return df[ORDER_TEMPLATE_COLUMNS], new_ids


@dataclass
class RunResult:
    ok: bool
    run_dir: str
    step5_stdout: str = ""
    step5_stderr: str = ""
    step6_stdout: str = ""
    step6_stderr: str = ""
    error: str = ""
    result_df: pd.DataFrame = field(default=None)
    new_order_ids: list = field(default_factory=list)


def missing_baseline_files(baseline_dir):
    """Fixe Kontext-Dateien (siehe Modulkopf) - fehlt eine, ist die
    Baseline-Konfiguration kaputt, das ist kein Nutzerfehler."""
    return [name for name in REQUIRED_ERP_FILES
            if not os.path.isfile(os.path.join(baseline_dir, name))]


def build_run_dir(runs_root, baseline_dir, new_orders_df=None):
    """Kopiert die fixen Kontext-Dateien 1:1; new_orders_df (falls gegeben)
    wird an die bestehende orders.csv angehaengt, nicht ersetzt. Gibt
    (run_dir, neue order_ids) zurueck."""
    os.makedirs(runs_root, exist_ok=True)
    run_dir = tempfile.mkdtemp(dir=runs_root)
    for name in REQUIRED_ERP_FILES:
        shutil.copyfile(os.path.join(baseline_dir, name), os.path.join(run_dir, name))

    new_ids = []
    if new_orders_df is not None and len(new_orders_df) > 0:
        orders_path = os.path.join(run_dir, "orders.csv")
        existing = pd.read_csv(orders_path)
        prepared, new_ids = prepare_new_orders(new_orders_df, set(existing["order_id"]))
        combined = pd.concat([existing, prepared], ignore_index=True)
        combined.to_csv(orders_path, index=False)

    return run_dir, new_ids


def run_pipeline(run_dir, as_of_date_iso, mock_llm, step5_dir, step6_dir,
                  rag_documents_dir, target_escalation_rate=None,
                  max_new_orders=None, new_order_ids=None):
    """Fuehrt step5-pgp und step6-calibration gegen run_dir aus. Gibt ein
    RunResult zurueck - result_df ist None bei einem Fehlschlag, sonst der
    Inhalt von tau_vergleich.csv.

    max_new_orders erhoeht step5s MAX_NEW_ORDERS (Default 20) grosszuegig,
    damit hochgeladene neue Auftraege nicht durch das "20 am naechsten
    faellige offene Auftraege"-Limit aus den bestehenden offenen Auftraegen
    der Baseline verdraengt werden und im Ergebnis fehlen."""
    env = os.environ.copy()
    env["ERP_DATA_DIR"] = run_dir
    env["RAG_DOCUMENTS_DIR"] = rag_documents_dir
    env["AS_OF_DATE"] = as_of_date_iso
    if max_new_orders is not None:
        env["MAX_NEW_ORDERS"] = str(max_new_orders)

    step5 = subprocess.run(
        ["python", "main.py"], cwd=step5_dir, env=env,
        capture_output=True, text=True,
    )
    if step5.returncode != 0:
        return RunResult(ok=False, run_dir=run_dir, step5_stdout=step5.stdout,
                          step5_stderr=step5.stderr,
                          error="step5-pgp ist fehlgeschlagen (siehe Rohausgabe unten).")

    pgp_ranking_path = os.path.join(run_dir, "pgp_priorisierung.csv")
    if not os.path.isfile(pgp_ranking_path):
        return RunResult(ok=False, run_dir=run_dir, step5_stdout=step5.stdout,
                          step5_stderr=step5.stderr,
                          error="step5-pgp hat keine pgp_priorisierung.csv erzeugt.")

    env6 = os.environ.copy()
    env6["PGP_RANKING_PATH"] = pgp_ranking_path
    env6["ORDERS_PATH"] = os.path.join(run_dir, "orders.csv")
    env6["LLM_CONTEXT_DIR"] = os.path.join(step6_dir, "llm_context")
    env6["OUTPUT_PATH"] = os.path.join(run_dir, "tau_vergleich.csv")
    env6["MOCK_LLM_RESPONSE"] = "1" if mock_llm else "0"
    if target_escalation_rate is not None:
        env6["TARGET_ESCALATION_RATE"] = str(target_escalation_rate)

    step6 = subprocess.run(
        ["python", "main.py"], cwd=step6_dir, env=env6,
        capture_output=True, text=True,
    )
    if step6.returncode != 0:
        return RunResult(ok=False, run_dir=run_dir, step5_stdout=step5.stdout,
                          step5_stderr=step5.stderr, step6_stdout=step6.stdout,
                          step6_stderr=step6.stderr,
                          error="step6-calibration ist fehlgeschlagen (siehe Rohausgabe unten).")

    tau_path = os.path.join(run_dir, "tau_vergleich.csv")
    if not os.path.isfile(tau_path):
        return RunResult(ok=False, run_dir=run_dir, step5_stdout=step5.stdout,
                          step5_stderr=step5.stderr, step6_stdout=step6.stdout,
                          step6_stderr=step6.stderr,
                          error="step6-calibration hat keine tau_vergleich.csv erzeugt.")

    df = pd.read_csv(tau_path)
    return RunResult(ok=True, run_dir=run_dir, step5_stdout=step5.stdout,
                      step5_stderr=step5.stderr, step6_stdout=step6.stdout,
                      step6_stderr=step6.stderr, result_df=df,
                      new_order_ids=new_order_ids or [])
