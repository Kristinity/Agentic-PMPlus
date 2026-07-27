"""
step9-upload-interface/pipeline.py - Agentic-PMPlus

Reine Orchestrierungs-Logik (kein Streamlit-Import), damit sie unabhaengig von
der UI getestet werden kann. Fuehrt step5-pgp/main.py und
step6-calibration/main.py als Subprozesse gegen ein Lauf-Verzeichnis aus -
bewusst KEINE Neuimplementierung der PGP-/Kalibrierungs-Logik, sondern
Wiederverwendung derselben main.py-Skripte, die schon einzeln Docker-getestet
sind (dieselbe Env-Var-Schnittstelle wie in docker-compose.yml fuer
step5-pgp/step6-calibration).

Ablauf pro Lauf: hochgeladene Dateien + Baseline-Fallback fuer fehlende
Stammdaten in ein frisches Verzeichnis kopieren -> step5 -> step6 -> Ergebnis
(tau_vergleich.csv) zurueckgeben.
"""

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field

import pandas as pd

REQUIRED_ERP_FILES = ["orders.csv", "bom.csv", "routings.csv", "work_centers.csv",
                       "calendar.csv", "inventory.csv", "disruptions.csv"]


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


def missing_required_files(provided_paths, baseline_dir):
    """provided_paths: {filename: path}. Liefert Dateinamen, die weder
    hochgeladen noch als Baseline vorhanden sind."""
    missing = []
    for name in REQUIRED_ERP_FILES:
        if name in provided_paths:
            continue
        if not (baseline_dir and os.path.isfile(os.path.join(baseline_dir, name))):
            missing.append(name)
    return missing


def build_run_dir(runs_root, provided_paths, baseline_dir):
    """Legt ein frisches Verzeichnis mit allen 7 ERP-Dateien an: hochgeladene
    Datei wenn vorhanden, sonst Kopie aus baseline_dir."""
    os.makedirs(runs_root, exist_ok=True)
    run_dir = tempfile.mkdtemp(dir=runs_root)
    for name in REQUIRED_ERP_FILES:
        dest = os.path.join(run_dir, name)
        if name in provided_paths:
            shutil.copyfile(provided_paths[name], dest)
        else:
            shutil.copyfile(os.path.join(baseline_dir, name), dest)
    return run_dir


def run_pipeline(run_dir, as_of_date_iso, mock_llm, step5_dir, step6_dir,
                  rag_documents_dir, target_escalation_rate=None):
    """Fuehrt step5-pgp und step6-calibration gegen run_dir aus. Gibt ein
    RunResult zurueck - result_df ist None bei einem Fehlschlag, sonst der
    Inhalt von tau_vergleich.csv."""
    env = os.environ.copy()
    env["ERP_DATA_DIR"] = run_dir
    env["RAG_DOCUMENTS_DIR"] = rag_documents_dir
    env["AS_OF_DATE"] = as_of_date_iso

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
                      step6_stderr=step6.stderr, result_df=df)
