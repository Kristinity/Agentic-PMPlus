"""
step6-calibration/kalibrierung.py - Agentic-PMPlus

Teil 3 des Step-6-Scopes (siehe Docstring von main.py): die eigentliche
tau0/sigma0-Kalibrierung, die im urspruenglichen Scope bewusst ausgeklammert
war (TICKET-B07-Kalibrierung.md, step7-active-learning/Backend-Backlog.md
Abschnitt 2). Liest die von main.py erzeugte tau_vergleich.csv, leitet daraus
getrennte Schwellenwerte tau0 und sigma0 ab und berechnet pro Auftrag den
ampel_status nach der 2x2-Matrix aus Konzept-README.md ("zentrale Idee"):

    tau hoch                    -> Rot: klarer Eskalationsfall (Experten-Review)
    tau niedrig, sigma hoch     -> Gelb: "truegerische Ruhe" (trotz Einigkeit pruefen)
    tau niedrig, sigma niedrig  -> Gruen: robuste Uebereinstimmung, automatisch weiter

Eskalationsregel (Konzept-README.md Step 6): tau > tau0 ODER sigma > sigma0
-> Flag an Experten. tau und sigma werden bewusst NICHT addiert oder gleich
gewichtet (unterschiedliche, nicht direkt vergleichbare Skalen) - die
Schwellenwerte werden komplett getrennt je Dimension berechnet.

Bootstrap-Hinweis (analog step5-pgp/main.py, compute_heuristic_utility):
Es liegen noch keine echten, von Menschen validierten Praeferenzurteile vor
(die sammelt erst der Active Learning Loop, Step 7). Als Kalibrierungs-
datensatz dient deshalb schlicht die aktuelle tau_vergleich.csv selbst - ein
bewusster Uebergangszustand fuer den Prototyp. tau0/sigma0 sind Quantile der
beobachteten tau-/sigma-Verteilung (ESCALATION_RATE_TARGET = Ziel-
Eskalationsquote je Dimension), KEINE gegen echte Fehlerraten/Grundwahrheit
kalibrierten Risk-Coverage-Schwellenwerte im eigentlichen Sinn von Conformal
Risk Control.

Systemgrenzen.md Teil A.3: Die Uebertragung des Risk-Coverage-Prinzips von
LLM-Unsicherheit (#11/#12) auf ein nachgelagertes GP-Unsicherheitsmass (sigma
des PGP aus Step 5) ist eine Designannahme dieses Projekts, keine aus der
Literatur belegte Methode. Sobald Step 7 echte Experten-Entscheidungen
sammelt (z. B. "hat der Planer PGP oder LLM gefolgt"), sollte diese
Quantil-Heuristik durch eine Kalibrierung gegen tatsaechliche Korrektheit
ersetzt werden.
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

TAU_VERGLEICH_PATH = os.environ.get(
    "TAU_VERGLEICH_PATH", os.path.join("shared_data", "tau_vergleich.csv")
)
SCHWELLENWERTE_OUTPUT_PATH = os.environ.get(
    "SCHWELLENWERTE_OUTPUT_PATH",
    os.path.join("shared_data", "kalibrierung_schwellenwerte.json"),
)
RISK_COVERAGE_OUTPUT_PATH = os.environ.get(
    "RISK_COVERAGE_OUTPUT_PATH",
    os.path.join("shared_data", "kalibrierung_risk_coverage.csv"),
)
# Ziel-Eskalationsquote je Dimension (tau, sigma getrennt) - z. B. 0.2 heisst:
# hoechstens ~20 % der Auftraege sollen ueber JEDE einzelne Dimension eskaliert
# werden. Kein Risikomass gegen echte Fehlerraten (siehe Modulkopf), sondern
# ein Quantil der Bootstrap-Verteilung.
ESCALATION_RATE_TARGET = float(os.environ.get("ESCALATION_RATE_TARGET", "0.2"))

SYSTEMGRENZEN_REF = (
    "step2-limits/Systemgrenzen.md Teil A.3: Uebertragung von "
    "Risk-Coverage-Prinzipien von LLM-Unsicherheit auf GP-Unsicherheit ist "
    "unbelegt, keine aus der Literatur ableitbare Methode."
)
BOOTSTRAP_HINWEIS = (
    "Kalibrierungsdatensatz ist die aktuelle tau_vergleich.csv selbst, NICHT "
    "echte, von Menschen validierte Praeferenzurteile (die sammelt erst "
    "Step 7 / Active Learning Loop). tau0/sigma0 sind Quantile der "
    "beobachteten Verteilung, keine gegen Grundwahrheit kalibrierten "
    "Risk-Coverage-Schwellenwerte."
)

AMPEL_GRUEN = "\U0001F7E2"
AMPEL_GELB = "\U0001F7E1"
AMPEL_ROT = "\U0001F534"


def load_bootstrap_dataset(path):
    df = pd.read_csv(path)
    for col in ("tau", "sigma"):
        if col not in df.columns:
            raise ValueError(f"{path} hat keine Spalte '{col}' - main.py zuerst laufen lassen.")
    return df


def risk_coverage_curve(values, n_points=20):
    """Diagnostische Kurve fuer den optionalen 'Kalibrierungs-Gesundheit'-
    Bildschirm (step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md,
    Abschnitt 2.3 Punkt 5). risk_proxy ist der kumulative Mittelwert der
    abgedeckten (<=threshold) Werte - ein Mass dafuer, wie stark die
    automatisch durchgelassenen Faelle im Schnitt abweichen, KEINE Fehlerrate
    gegen Grundwahrheit (siehe Modulkopf)."""
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n == 0:
        return pd.DataFrame(columns=["threshold", "coverage", "risk_proxy"])

    step = max(1, n // n_points)
    rows = []
    running_sum = 0.0
    for i, v in enumerate(sorted_values, start=1):
        running_sum += v
        if i % step == 0 or i == n:
            rows.append({
                "threshold": v,
                "coverage": i / n,
                "risk_proxy": running_sum / i,
            })
    return pd.DataFrame(rows)


def select_threshold(values, escalation_rate_target):
    """Schwellenwert = (1 - escalation_rate_target)-Quantil der Bootstrap-
    Verteilung (siehe Modulkopf: Quantil-Heuristik statt echter
    Risk-Coverage-Kalibrierung gegen Grundwahrheit)."""
    return float(pd.Series(values).quantile(1 - escalation_rate_target))


def apply_escalation_rule(df, tau0, sigma0):
    """2x2-Matrix aus Konzept-README.md ('zentrale Idee'):
    tau hoch (>tau0) -> immer Rot, unabhaengig von sigma.
    tau niedrig + sigma hoch (>sigma0) -> Gelb ('truegerische Ruhe').
    tau niedrig + sigma niedrig -> Gruen.
    Eskalationsregel (Konzept-README.md Step 6): tau > tau0 ODER sigma > sigma0."""
    result = df.copy()
    result["tau0"] = tau0
    result["sigma0"] = sigma0

    def status(row):
        if row["tau"] > tau0:
            return AMPEL_ROT
        if row["sigma"] > sigma0:
            return AMPEL_GELB
        return AMPEL_GRUEN

    result["ampel_status"] = result.apply(status, axis=1)
    result["eskaliert"] = result["ampel_status"].isin([AMPEL_ROT, AMPEL_GELB])
    return result


def main():
    print("=== step6-calibration / kalibrierung.py ===")
    print(BOOTSTRAP_HINWEIS)
    print(SYSTEMGRENZEN_REF)

    df = load_bootstrap_dataset(TAU_VERGLEICH_PATH)
    print(f"\n{len(df)} Auftraege aus {TAU_VERGLEICH_PATH} als Bootstrap-Kalibrierungsdatensatz geladen.")

    tau0 = select_threshold(df["tau"], ESCALATION_RATE_TARGET)
    sigma0 = select_threshold(df["sigma"], ESCALATION_RATE_TARGET)
    print(f"tau0   = {tau0:.4f}  (Ziel-Eskalationsquote={ESCALATION_RATE_TARGET:.0%})")
    print(f"sigma0 = {sigma0:.4f}  (Ziel-Eskalationsquote={ESCALATION_RATE_TARGET:.0%})")

    result = apply_escalation_rule(df, tau0, sigma0)
    result.to_csv(TAU_VERGLEICH_PATH, index=False)
    print(f"-> ampel_status ergaenzt in {TAU_VERGLEICH_PATH}")

    counts = result["ampel_status"].value_counts()
    print("\nAmpel-Verteilung:")
    for status in (AMPEL_GRUEN, AMPEL_GELB, AMPEL_ROT):
        print(f"  {status}: {counts.get(status, 0)}")

    risk_coverage = pd.concat([
        risk_coverage_curve(df["tau"]).assign(dimension="tau"),
        risk_coverage_curve(df["sigma"]).assign(dimension="sigma"),
    ], ignore_index=True)
    os.makedirs(os.path.dirname(RISK_COVERAGE_OUTPUT_PATH) or ".", exist_ok=True)
    risk_coverage.to_csv(RISK_COVERAGE_OUTPUT_PATH, index=False)
    print(f"-> Risk-Coverage-Kurven (Diagnose) -> {RISK_COVERAGE_OUTPUT_PATH}")

    schwellenwerte = {
        "tau0": tau0,
        "sigma0": sigma0,
        "escalation_rate_target": ESCALATION_RATE_TARGET,
        "n_bootstrap_orders": len(df),
        "berechnet_am": datetime.now(timezone.utc).isoformat(),
        "bootstrap_hinweis": BOOTSTRAP_HINWEIS,
        "systemgrenzen_referenz": SYSTEMGRENZEN_REF,
    }
    os.makedirs(os.path.dirname(SCHWELLENWERTE_OUTPUT_PATH) or ".", exist_ok=True)
    with open(SCHWELLENWERTE_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(schwellenwerte, f, ensure_ascii=False, indent=2)
    print(f"-> Schwellenwerte + Kalibrierungs-Metadaten -> {SCHWELLENWERTE_OUTPUT_PATH}\n")


if __name__ == "__main__":
    main()
