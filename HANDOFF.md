# pyflare — Handoff & Next Steps

This document is the bridge between the v0.1 scaffold (built in a chat
session) and the production-quality library that needs to exist by
**20 May 2026** — the PyCon Africa 2026 poster submission deadline.

It is written to be useful both as a project status note **and** as
context that can be dropped into a Claude Code session to continue work.

---

## 1. Where things stand

### What's built and tested

| File | Purpose | Status |
|---|---|---|
| `pyproject.toml` | Package metadata, deps, ruff/pytest config | ✅ |
| `LICENSE` | MIT | ✅ |
| `README.md` | Iconic project README with placeholder origin story | ✅ |
| `CONTRIBUTING.md` | Contributor guide + Adopt-a-Country programme | ✅ |
| `.gitignore` | Python + pyflare-specific ignores | ✅ |
| `src/pyflare/__init__.py` | Public API surface | ✅ |
| `src/pyflare/data.py` | GFMR + VNF fetchers, spatial filters, schema normalization | ✅ |
| `src/pyflare/analysis.py` | Flare classification, persistence, site clustering, volume + methane proxy | ✅ |
| `src/pyflare/viz.py` | Folium maps, matplotlib charts, project palette | ✅ |
| `tests/test_data.py` | 17 tests | ✅ |
| `tests/test_analysis.py` | 16 tests | ✅ |
| `tests/test_viz.py` | 5 tests, gated on `[viz]` extras | ✅ |

**Total: 38 tests, all passing.** No network calls in the test suite.

### What's missing (these are Claude Code's job)

| File | Why it matters |
|---|---|
| `CODE_OF_CONDUCT.md` | Required for PyCon-aligned community projects. Use Contributor Covenant 2.1 verbatim. |
| `CITATION.cff` | Makes the repo machine-citable on GitHub. Required for JOSS submission. |
| `CHANGELOG.md` | Keep-a-Changelog format. Start with `## [0.1.0] - 2026-05-XX`. |
| `.github/workflows/ci.yml` | Run pytest + ruff on push/PR across Python 3.10, 3.11, 3.12. |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Standard bug template. |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Standard feature template. |
| `.github/ISSUE_TEMPLATE/country_maintainer.md` | Adopt-a-Country onboarding — see CONTRIBUTING.md. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Checklist matching CONTRIBUTING.md style guide. |
| `notebooks/01_niger_delta_quickstart.ipynb` | First demo notebook; should run with synthetic fallback if no EOG creds. |
| `docs/` scaffolding | Sphinx config + index page. ReadTheDocs-ready. |
| `.pre-commit-config.yaml` | Ruff + mypy pre-commit hooks. |

---

## 2. The strategic context (don't lose this)

`pyflare` is being built as the technical centerpiece of a PyCon Africa
2026 poster submission AND as the seed of a longer-term open-science
initiative aimed at international awards (JOSS, PSF Community Service
Award, Mozilla MOSS, AI for Good). The five-layer architecture is:

1. **Library** (this repo) — v1.0 by October 2026.
2. **Dataset (AFLARED)** — Zenodo-deposited, citable, harmonized 2012-present African flaring observations.
3. **Dashboard (`flarewatch.africa`)** — Streamlit/Dash public dashboard.
4. **Paper (JOSS)** — submission by July 2026.
5. **Community** — country maintainers across 7+ African oil/gas-producing nations.

The poster on 20 May positions pyflare as the **seed** of this
initiative, with credible v0.1 code on GitHub. Reviewers don't expect
v1.0 by then — they expect working v0.1 code, a clear plan, and a
vision big enough to matter.

---

## 3. Hard constraints (do not violate)

- **PyCon Africa CFP rule:** *proposal text written by an LLM is auto-rejected, no second chance.* The poster abstract and elevator pitch MUST be written in Johnpaul's own voice. AI assistance is fine for code, README, and documentation. The line is at proposal-submission text.
- **Scientific integrity:** every numerical default in `analysis.py` cites a peer-reviewed source. New thresholds must do the same. Pyflare *estimates*; it does not *measure*.
- **Africa scope:** the toolkit is for African oil/gas-producing nations. Resist scope creep to other continents — it dilutes the positioning. Global support can come post-v1.0.
- **No EOG credentials in the repo, ever.** Use env vars `EOG_USERNAME` / `EOG_PASSWORD`. The .gitignore already blocks `.env.local`, `secrets.toml`, `*.key`.

---

## 4. Immediate work (next 15 days, in priority order)

### Day 1-2: Finish project hygiene

Use Claude Code with the prompt template at the bottom of this document.

1. Add `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1).
2. Add `CITATION.cff` with metadata for Johnpaul Okeke as author.
3. Add `CHANGELOG.md` with v0.1.0 entry.
4. Add `.github/workflows/ci.yml` matrix-testing on 3.10/3.11/3.12.
5. Add issue + PR templates.
6. Add `.pre-commit-config.yaml` running ruff + mypy.
7. Create the GitHub repo and push.

### Day 3-4: Demo notebook + first chart

8. Create `notebooks/01_niger_delta_quickstart.ipynb` walking through:
   - Install
   - `fetch_ggfr_annual()` → Nigeria trend chart
   - Top-5 African producers comparison
   - Synthetic VNF detection cluster → site aggregation → volume estimate
   - The "wow chart" candidate for the poster
9. Generate the **iconic poster figure** — Africa with all flares glowing,
   using the project palette and `africa_overview()`. Save as PNG at 600 dpi.

### Day 5: Cold emails

10. Email Christopher Elvidge (EOG, Colorado School of Mines) — ask for a quoted endorsement.
11. Email Stakeholder Democracy Network (Niger Delta NGO).
12. Confirm Dr. Adeyanju (UNILAG HOD) institutional support.

### Day 6-10: Dashboard MVP + documentation

13. Add `pyflare/dashboard.py` Streamlit MVP showing one country's
    flaring trend interactively. Local-only is fine — the public
    `flarewatch.africa` deployment can come post-poster.
14. Spin up `docs/` with Sphinx + Furo theme. Auto-generate API docs.
15. Set up ReadTheDocs.
16. Hit JOSS-readiness checklist:
    [https://joss.readthedocs.io/en/latest/submitting.html](https://joss.readthedocs.io/en/latest/submitting.html)

### Day 11-13: Poster artefact

17. Design poster file (A1 portrait, 300 dpi). Use the iconic figure
    from step 9 as the centerpiece.
18. Photographs: hardware-of-platform-style screenshots, code snippets,
    the architecture diagram.

### Day 14: Abstract + elevator pitch (JOHNPAUL'S VOICE ONLY)

19. Draft the 200-word abstract from the scaffold in the prior chat.
20. Draft the 2-sentence elevator pitch.
21. Internal review — friends, family, mentors. NOT another LLM.

### Day 15: Submit

22. Submit poster proposal at https://africa.pycon.org/.
23. Email `team@pycon.africa` to confirm speaker benefits for posters.
24. Apply for the Opportunity Grant separately, citing the poster
    submission.

---

## 5. Open questions Johnpaul needs to answer

These block parts of the work above. Resolve before the Claude Code
session.

1. **GitHub handle.** Currently placeholder `YOUR-HANDLE` throughout
   `README.md`, `CONTRIBUTING.md`, `pyproject.toml`. Search-and-replace
   needed once chosen.
2. **PyPI name availability.** Run `pip search pyflare` (or check
   pypi.org/project/pyflare). If taken, fallbacks: `africaflare`,
   `nightflame`, `pyflare-africa`.
3. **EOG account.** Free registration at https://eogdata.mines.edu/.
   Required to test `fetch_vnf_nightly()` end-to-end.
4. **Project email.** Current `pyproject.toml` uses
   `okekejohnpaul12@gmail.com`. Consider a project-specific address
   like `pyflare@...` for community channel.

---

## 6. Architectural decisions worth preserving

These were considered and chosen during scaffolding. Don't undo them
without good reason:

- **Bounding-box filtering for v0.1, polygon-precise for v0.2.** Bounding
  boxes are honest about overlap (Saudi Arabia falls inside the African
  bbox at 40°E). Polygons require GeoPandas which is heavy.
- **Sync HTTP for v0.1, async for v0.2.** Simpler dependencies, easier
  to test, no real performance need at GFMR-annual scale.
- **Lazy imports for viz dependencies.** Keeps the core package lean for
  data-only users.
- **Greedy single-link clustering for `aggregate_to_sites`.** O(n²) but
  fine for daily VNF (~thousands of detections, not millions). Upgrade
  to ball-tree only if profiling shows it.
- **Methane proxy as a function with configurable slip fraction**, not
  a hardcoded constant. Slip fraction is contested in the literature
  (IPCC 2%, recent satellite work 5%+); we expose the choice.
- **Schema normalization in `data.py` is column-name-tolerant.** GFMR's
  upstream column names have changed several times; pyflare's mapping
  function survives that.

---

## 7. Claude Code session prompt template

Copy-paste this into the Claude Code terminal session to start work:

```
I'm building pyflare, an open Python toolkit for satellite gas flaring
analytics across African oil-producing nations. It's the technical
centerpiece of a PyCon Africa 2026 poster submission (deadline 20 May
2026).

Read these files first to understand the project:
- HANDOFF.md (this is the project brief and todo list)
- README.md (the iconic project README with the vision)
- CONTRIBUTING.md (style guide and Adopt-a-Country programme)
- src/pyflare/__init__.py (public API)
- src/pyflare/data.py, analysis.py, viz.py (the three core modules)

Confirm tests pass with `pytest`, then work through HANDOFF.md
section 4 in priority order. Start with section 4 day 1-2: project
hygiene files (CODE_OF_CONDUCT, CITATION.cff, CHANGELOG, GitHub
Actions, issue templates, pre-commit config).

Hard rules:
- Do NOT modify the abstract, elevator pitch, or poster proposal
  text. That writing is mine alone (PyCon CFP rule).
- Numerical defaults in analysis.py must cite peer-reviewed sources.
- Africa scope only. No global support.
- No real credentials in any committed file.
- Match the existing code style — type hints, NumPy docstrings,
  100-char line length, `from __future__ import annotations` at top
  of every module.

When in doubt, prefer adding a TODO comment to me over guessing.
```

---

## 8. Files and their line counts (current snapshot)

```
pyproject.toml             ~70 lines
LICENSE                    ~22 lines
README.md                 ~150 lines
CONTRIBUTING.md           ~110 lines
.gitignore                 ~75 lines
src/pyflare/__init__.py    ~45 lines
src/pyflare/data.py       ~370 lines
src/pyflare/analysis.py   ~340 lines
src/pyflare/viz.py        ~225 lines
tests/test_data.py        ~135 lines
tests/test_analysis.py    ~165 lines
tests/test_viz.py          ~70 lines
```

Roughly 1,800 lines of code + docs. Not huge, but every line is
intentional.

---

## 9. Quick verification commands

After cloning into a fresh environment:

```bash
git clone <repo-url> pyflare
cd pyflare
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,viz]"
pytest -v                    # should be 38 passed
ruff check .                  # should be clean
python -c "import pyflare; print(pyflare.__version__)"   # → 0.1.0
```
