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
- [x] **Library bug fixed** — `fetch_ggfr_annual()` URL was 404. Patched to read the 2025 World Bank XLSX release; melts wide → long, normalises country labels. New core dep: `openpyxl`. CHANGELOG entry under `[Unreleased]`.
- [x] **C5 done early** — `notebooks/01_niger_delta.ipynb` built + executed end-to-end via `jupyter nbconvert --execute`. 17 cells, 2 chart images, headline table populated. Runs without EOG creds (synthetic VNF block, replace with real `fetch_vnf_nightly()` once license arrives).
- [x] **G3 GREEN** — `bash scripts/verify.sh G3` passes
- [x] **`notebooks` extras** added to `pyproject.toml` (`jupyter`, `nbconvert`, `ipykernel`, `matplotlib`)
- [x] Local venv set up (`.venv`, Python 3.12); full suite **41 passed, 1 skipped** (viz skipped — folium not installed)

### Headline number — CORRECTED against live GGFR 2025 release

The original PLAN.md figure (7.4 bcm) turned out to be stale. The 2025 GGFR release reports **Nigeria 2024 = 6.48 bcm**. Recomputed:

| Methane slip | Source | MtCO2e / year |
|---|---|---|
| 2 % | IPCC AR6 default | **18.96** |
| 5 % | pyflare default / Plant et al. 2022 mid | **22.62** |
| 9 % | Plant et al. 2022 upper bound | **27.50** |

Headline framing for the poster: **"Nigeria's 2024 gas flaring (6.48 bcm) → 19–28 MtCO2e per year, depending on the methane slip assumption."** Defensible, pre-empts the obvious reviewer question, and the spread is itself the argument for satellite measurement.

**Library bug discovered + fixed in same turn:** `fetch_ggfr_annual()` URL was dead (World Bank moved from CSV to XLSX in the 2025 release). Patched to read XLSX, melt wide → long, normalise country labels. New core dep: `openpyxl`. CHANGELOG updated.

### Not yet committed

The Day 0-evening work is on disk but uncommitted (you do deployment):

```bash
git add .github CODE_OF_CONDUCT.md CITATION.cff CHANGELOG.md .pre-commit-config.yaml \
        STATUS.md src/pyflare/analysis.py src/pyflare/__init__.py tests/test_analysis.py
git commit -m "Day 0: hygiene scaffold + C4 (volume_to_co2eq, gate G2 green)"
git push
```

After push, watch Actions tab — first CI run on 3.10/3.11/3.12 should go green.

### Sent / pending response

- [x] **Y2 (round 1)**: email sent 2026-05-06 12:24, **EOG replied 2026-05-06 16:57** (Tilo) — turnaround was hours, not days. Three required steps:
  1. Register with academic email at https://eogdata.mines.edu/products/register/
  2. Sign + return the academic license PDF (Payne Institute, 2026-01-30)
  3. Send proof of enrollment (University ID etc.)
- [ ] **Y2 (round 2)**: user to complete the 3 steps above. Use-description text drafted at [`drafts/y2_eog_use_description.md`](drafts/y2_eog_use_description.md) for the license PDF.

### Blockers

- [ ] **Y3**: `pyflare` is **taken** on PyPI (owner `jlinn`, last release 2015-09-22, abandoned Cloudflare adapter). **Decision needed** — recommended fallback: `pyflare-africa` (keeps `import pyflare` semantics; only the `pip install` name changes). Alternatives: `africaflare` (cleaner, but rename module too), `flarescope-africa` (longer). User to confirm; Claude will then patch pyproject.toml + README + badge.
- [ ] **Y4**: 3 cold-email drafts ready in `drafts/y4_*.md` ([elvidge](drafts/y4_elvidge.md), [sdn](drafts/y4_sdn.md), [adeyanju](drafts/y4_adeyanju.md)). User to scrub voice tells, fill in named recipients (esp. Adeyanju first name + department), and send.

### Risk register changes

- **EOG license risk upgraded from Med → High** — new license-based flow as of 2025-01-10 has unknown turnaround. Mitigated by Day 0 email + load-bearing synthetic fallback in notebooks. PLAN.md §5 and Y2 row updated.
- **G2 risk retired** — headline number reproducible, citations in place.

### Pace check

We are now **~3 days ahead of the PLAN.md schedule** — Day 0 evening compressed Days 0-3 of automated work (C1, C2, C3, C4, C5; gates G2 + G3 green; Y1 done). User actions (Y2 sent, Y4 drafts ready, Y3 pending) are on track.

### VNF Academic Data Use License — received + compliance landed

The signed license PDF was received by the user 2026-05-06 from EOG (Tilo). Material constraints baked into the project today:

- **`LICENSING_NOTES.md`** ([file](LICENSING_NOTES.md)) — central reference: what every contributor must know; restriction-by-restriction map to the codebase; year-by-year disclosure clearance table (2024 ✅; 2025 ⏳).
- **README acknowledgements** updated with the verbatim §2.a attribution notice + link to `LICENSING_NOTES.md`.
- **Notebook 01** updated: data-attribution markdown cell at top + footer credit; re-executed cleanly, G3 still green.
- **Y4 Elvidge draft revised** for §1.h (no EOG/Mines endorsement framing). Endorsement ask is now explicitly personal-from-Elvidge. Send-after license-approved (looks more credible).
- **Y3 PyPI fallback decision** still pending user.

### Forward-looking impact (G5 onward)

- **G5 iconic Africa map** — must include §2.a credit line in figure footer when rendered.
- **G8 Streamlit dashboard** — **adds a blocker:** requires EOG written approval for the region/refresh scope before public launch (license §1.f.iii). Plan around this.
- **Future AFLARED Zenodo deposit** — must aggregate to flare-site / monthly minimum, no per-detection redistribution.
- **Future poster + JOSS paper** — both must carry the §2.a notice.

### Tomorrow (Day 1, 2026-05-07): keep momentum

- User: send Y4 cold emails (Elvidge, SDN, Adeyanju); pick PyPI name (Y3)
- Claude: build out G4 (3 remaining country notebooks: Angola, Algeria, Libya) — refactor builder to be country-parameterised
- Then: G5 iconic Africa map (poster centerpiece)
- After G4 + G5: poster-quality material is in place even if EOG license never arrives

### Cut-order reminder

If we slip: drop time-lapse → Streamlit → communities-near-sites. Never cut: CO₂-eq function, country notebooks, iconic map, PyPI release.
