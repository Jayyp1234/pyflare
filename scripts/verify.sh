#!/usr/bin/env bash
# scripts/verify.sh — pyflare execution gate checker
#
# Usage:
#   bash scripts/verify.sh             # run all gates G1..G14
#   bash scripts/verify.sh G1 G2 G3    # run specific gates
#
# Exit codes:
#   0 = no failures (pending OK)
#   1 = one or more gates failed
#   2 = unknown gate name passed in
#
# This script is idempotent and never modifies the repo.

set -u

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$REPO_ROOT"

# colors (disabled if NO_COLOR set or stdout not a tty)
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  G='\033[0;32m'; R='\033[0;31m'; Y='\033[0;33m'; D='\033[0;90m'; B='\033[1m'; N='\033[0m'
else
  G=''; R=''; Y=''; D=''; B=''; N=''
fi

PASSED=0; FAILED=0; PENDING=0
FAILED_GATES=()

pass()    { printf "  ${G}PASS${N}  %s\n" "$1"; PASSED=$((PASSED+1)); }
fail()    { printf "  ${R}FAIL${N}  %s\n" "$1"; FAILED=$((FAILED+1)); FAILED_GATES+=("$2"); }
pend()    { printf "  ${Y}PEND${N}  %s\n" "$1"; PENDING=$((PENDING+1)); }
info()    { printf "  ${D}info${N}  %s\n" "$1"; }
header()  { printf "\n${B}=== %s ===${N}\n" "$1"; }

# ---------- gate definitions ----------

gate_G1() {
  header "G1: Repo public + CI green"
  [ -d .git ] && pass "Local git repo present" || fail "No .git directory" "G1"
  [ -f .github/workflows/ci.yml ] && pass "CI workflow file exists" || fail "Missing .github/workflows/ci.yml" "G1"
  if git remote get-url origin > /dev/null 2>&1; then
    pass "Remote 'origin' configured: $(git remote get-url origin)"
  else
    pend "No remote 'origin' yet (push to GitHub pending)"
    return 0
  fi
  if command -v gh > /dev/null 2>&1 && gh auth status > /dev/null 2>&1; then
    LATEST=$(gh run list --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || true)
    case "$LATEST" in
      success) pass "Latest CI run on remote: success" ;;
      "")      pend "No CI runs found on remote yet" ;;
      *)       fail "Latest CI run conclusion: $LATEST" "G1" ;;
    esac
  else
    pend "Cannot check remote CI (gh not configured)"
  fi
}

gate_G2() {
  header "G2: Headline number (CO2-eq) reproducible"
  if grep -q "def volume_to_co2eq" src/pyflare/analysis.py 2>/dev/null; then
    pass "volume_to_co2eq function defined"
    if python -c "from pyflare.analysis import volume_to_co2eq; v=volume_to_co2eq(7.4, 0.02); assert v > 0" > /dev/null 2>&1; then
      pass "Function importable and returns positive value for sample input"
    else
      fail "Function not importable or fails on sample input" "G2"
    fi
    if grep -q "test_volume_to_co2eq\|test_co2eq" tests/test_analysis.py 2>/dev/null; then
      pass "Unit test exists for volume_to_co2eq"
    else
      fail "No unit test for volume_to_co2eq" "G2"
    fi
  else
    pend "volume_to_co2eq not yet implemented (Day 2 task)"
  fi
}

gate_G3() {
  header "G3: Niger Delta notebook end-to-end"
  if [ -f notebooks/01_niger_delta.ipynb ]; then
    pass "Notebook file exists"
  else
    pend "Notebook not yet created (Day 3 task)"
  fi
}

gate_G4() {
  header "G4: All 4 country notebooks render"
  for nb in 01_niger_delta 02_angola 03_algeria 04_libya; do
    if [ -f "notebooks/${nb}.ipynb" ]; then
      pass "notebooks/${nb}.ipynb exists"
    else
      pend "notebooks/${nb}.ipynb not yet created"
    fi
  done
}

gate_G5() {
  header "G5: Iconic Africa map @ 600 dpi"
  if [ -f assets/africa_overview_600dpi.png ]; then
    pass "Iconic map file exists"
    if command -v python > /dev/null 2>&1; then
      DIMS=$(python -c "from PIL import Image; im=Image.open('assets/africa_overview_600dpi.png'); print(f'{im.size[0]}x{im.size[1]}')" 2>/dev/null || echo "")
      if [ -n "$DIMS" ]; then
        info "Dimensions: $DIMS"
      fi
    fi
  else
    pend "Iconic map not yet generated (Day 5 task)"
  fi
}

gate_G6() {
  header "G6: communities_near_sites function"
  if grep -q "def communities_near_sites" src/pyflare/analysis.py 2>/dev/null; then
    pass "Function defined"
  else
    pend "Function not yet implemented (Day 6 task)"
  fi
}

gate_G7() {
  header "G7: Time-lapse GIF"
  if [ -f assets/africa_timelapse.gif ]; then
    pass "Time-lapse GIF exists"
  else
    pend "Time-lapse not yet generated (Day 7 task)"
  fi
}

gate_G8() {
  header "G8: Streamlit dashboard MVP"
  if [ -f src/pyflare/dashboard.py ]; then
    pass "Dashboard module exists"
  else
    pend "Dashboard not yet built (Day 8 task)"
  fi
}

gate_G9() {
  header "G9: Sphinx docs"
  if [ -f docs/conf.py ]; then
    pass "Sphinx config exists"
  else
    pend "Sphinx not yet configured (Day 9 task)"
  fi
}

gate_G10() {
  header "G10: pip install pyflare works"
  if git tag | grep -q "^v0.1.0$"; then
    pass "v0.1.0 tag exists locally"
  else
    pend "v0.1.0 not yet tagged (Day 10 task)"
  fi
}

gate_G11() {
  header "G11: Poster artifact"
  if [ -f poster/pyflare_poster.pdf ] || [ -f poster/poster.pdf ]; then
    pass "Poster PDF exists"
  else
    pend "Poster not yet designed (Day 11-12 task)"
  fi
}

gate_G12() {
  header "G12: All systems green (Day 12)"
  pend "Composite gate — checked Day 12"
}

gate_G13() {
  header "G13: Reviewer-ready (abstract reads as human voice)"
  pend "Manual confirm — Day 13 internal review by 2+ humans"
}

gate_G14() {
  header "G14: SUBMITTED"
  pend "Manual confirm — submission email received"
}

# ---------- always-on baseline checks ----------

gate_baseline() {
  header "Baseline (always run)"
  if command -v python > /dev/null 2>&1; then
    pass "python available: $(python --version 2>&1)"
  else
    fail "python not on PATH" "baseline"
  fi
  if [ -f pyproject.toml ]; then
    pass "pyproject.toml present"
  else
    fail "pyproject.toml missing" "baseline"
  fi
  if python -c "import pyflare" > /dev/null 2>&1; then
    PFV=$(python -c "import pyflare; print(pyflare.__version__)" 2>/dev/null)
    pass "pyflare importable, version=$PFV"
  else
    pend "pyflare not installed in this env (run: pip install -e .)"
  fi
  if python -m pytest --collect-only -q > /dev/null 2>&1; then
    pass "pytest collects tests"
  else
    pend "pytest cannot collect (env not set up?)"
  fi
}

# ---------- main ----------

ALL_GATES="G1 G2 G3 G4 G5 G6 G7 G8 G9 G10 G11 G12 G13 G14"
if [ $# -eq 0 ]; then
  GATES="$ALL_GATES"
  RUN_BASELINE=1
else
  GATES="$@"
  RUN_BASELINE=0
fi

printf "${B}pyflare verify.sh${N}  ${D}(today: $(date +%Y-%m-%d))${N}\n"

if [ "$RUN_BASELINE" = "1" ]; then
  gate_baseline
fi

for g in $GATES; do
  if declare -F "gate_$g" > /dev/null; then
    "gate_$g"
  else
    printf "\n${R}Unknown gate: %s${N}\n" "$g"
    exit 2
  fi
done

# summary
printf "\n${D}═════════════════════════════════${N}\n"
printf "  ${B}Summary${N}\n"
printf "  ${G}Passed:${N}  %d\n" "$PASSED"
printf "  ${R}Failed:${N}  %d\n" "$FAILED"
printf "  ${Y}Pending:${N} %d\n" "$PENDING"
printf "${D}═════════════════════════════════${N}\n"

if [ "$FAILED" -gt 0 ]; then
  printf "\n${R}Failed gates:${N} %s\n" "${FAILED_GATES[*]}"
  exit 1
fi
exit 0
