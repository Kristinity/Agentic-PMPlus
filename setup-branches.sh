#!/usr/bin/env bash
# Prestep: "Branches aufbauen"
# Legt fuer jeden Step im Agentic-PMPlus-Konzept einen eigenen Git-Branch an.
# Ausfuehren im Wurzelverzeichnis des Git-Repos (nicht im Container - Branches
# sind ein Git-Konzept und wirken auf das Host-Repo).

set -e

BRANCHES=(
  "prestep"
  "step1-feasibility"
  "step2-limits"
  "step3-erp-simulation"
  "step4-context-engineering"
  "step5-pgp"
  "step6-calibration"
  "step7-active-learning"
  "step8-live-test"
)

BASE_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "main")
echo "Basis-Branch: $BASE_BRANCH"

for b in "${BRANCHES[@]}"; do
  if git show-ref --verify --quiet "refs/heads/$b"; then
    echo "Branch '$b' existiert bereits - ueberspringe."
  else
    git branch "$b" "$BASE_BRANCH"
    echo "Branch '$b' angelegt."
  fi
done

echo ""
echo "Fertig. Uebersicht:"
git branch
