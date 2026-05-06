# pyflare execution status

> Living log. Updated at end of each phase. For the full plan see [`PLAN.md`](PLAN.md).

**Last updated:** 2026-05-06 (Day 0, late evening)
**Current phase:** Day 0 — Foundation (running ahead: C4 / G2 already landed)
**Days to PyCon Africa deadline:** 14
**Submission target date:** 2026-05-20

---

## Day 0 (2026-05-06) — Foundation

### Landed today

- [x] Strategic plan written ([`PLAN.md`](PLAN.md))
- [x] Verification system designed ([`scripts/verify.sh`](scripts/verify.sh))
- [x] Project hygiene scaffolded:
  - [x] `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1, contact set to okekejohnpaul12@gmail.com)
  - [x] `CITATION.cff` (machine-citable, points to v0.1.0 / 2026-05-16)
  - [x] `CHANGELOG.md` (Keep-a-Changelog, [0.1.0] entry drafted)
  - [x] `.github/workflows/ci.yml` (matrix on 3.10/3.11/3.12 + ruff)
  - [x] `.github/ISSUE_TEMPLATE/{bug_report,feature_request,country_maintainer}.md`
  - [x] `.github/PULL_REQUEST_TEMPLATE.md`
  - [x] `.pre-commit-config.yaml` (ruff, mypy, standard hygiene hooks)
- [x] `YOUR-HANDLE` placeholders replaced with `jayyp1234` in `README.md`, `CONTRIBUTING.md`
- [x] `pyproject.toml` URLs harmonized to `jayyp1234` (was `jpokekeebube`)
- [x] **Y1 done early** — repo created at https://github.com/Jayyp1234/pyflare; remote configured; first commits pushed
- [x] **C4 done early** — `analysis.volume_to_co2eq()` implemented with IPCC AR6 GWP-100 (29.8) + IPCC 2006 combustion EF (2.55 kg CO2/m³) + 8 unit tests
- [x] **G2 GREEN** — `bash scripts/verify.sh G2` passes 3/3
- [x] Local venv set up (`.venv`, Python 3.12); full suite **41 passed, 1 skipped** (viz skipped — folium not installed)

### Headline number, first cut (Niger Delta / Nigeria, 7.4 bcm/yr GGFR 2024)

| Methane slip | Source | MtCO2e / year |
|---|---|---|
| 2 % | IPCC AR6 default | **21.7** |
| 5 % | pyflare default / Plant et al. 2022 mid | **25.8** |
| 9 % | Plant et al. 2022 upper bound | **31.4** |

Headline framing for the poster: **"Nigeria's gas flaring → 22–31 MtCO2e per year, depending on the methane slip assumption."** Defensible, pre-empts the obvious reviewer question, and the spread is itself the argument for satellite measurement.

### Not yet committed

The Day 0-evening work is on disk but uncommitted (you do deployment):

```bash
git add .github CODE_OF_CONDUCT.md CITATION.cff CHANGELOG.md .pre-commit-config.yaml \
        STATUS.md src/pyflare/analysis.py src/pyflare/__init__.py tests/test_analysis.py
git commit -m "Day 0: hygiene scaffold + C4 (volume_to_co2eq, gate G2 green)"
git push
```

After push, watch Actions tab — first CI run on 3.10/3.11/3.12 should go green.

### Blockers

- [ ] **Y2**: EOG account registration at https://eogdata.mines.edu/ (lead time 2-7 days — start ASAP)
- [ ] **Y3**: confirm `pyflare` available on PyPI (or pick fallback: `africaflare`, `flarescope-africa`)

### Tomorrow (Day 1, 2026-05-07): Gate G1 + start G3

- AM: Y2 EOG registration (background task — does not block code work)
- AM: Y3 PyPI name check
- AM: Y4 cold-email drafts (Claude drafts; Johnpaul edits voice + sends)
- PM: C5 Niger Delta notebook (`notebooks/01_niger_delta.ipynb`) targeting G3
- PM: `bash scripts/verify.sh G1 G3` to track progress

### Risk register changes

- **G2 risk retired** — headline number reproducible, citations in place.

### Cut-order reminder

If we slip: drop time-lapse → Streamlit → communities-near-sites. Never cut: CO₂-eq function, country notebooks, iconic map, PyPI release.
