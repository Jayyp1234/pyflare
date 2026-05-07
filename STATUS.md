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

### Headline number — CORRECTED against live GFMR 2025 release

The original PLAN.md figure (7.4 bcm) turned out to be stale. The 2025 GFMR release reports **Nigeria 2024 = 6.48 bcm**. Recomputed:

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

- [x] **Y2 (round 1)**: email sent 2026-05-06 12:24, **EOG replied 2026-05-06 16:57** (Tilo) — turnaround was hours, not days.
- [x] **Y2 (round 2)**: license signed + returned, EOG approved access 2026-05-06 19:14. Tilo confirmed CSV/KMZ browser downloads work; programmatic access requires a Client ID issued by Greg G.
- [ ] **Y2 (round 3)**: user to email `eog@mines.edu` (reply in same thread) requesting the OAuth Client ID + secret. Draft at [`drafts/y2_eog_client_id.md`](drafts/y2_eog_client_id.md).

### Blockers

- [ ] **Y3**: `pyflare` is **taken** on PyPI (owner `jlinn`, last release 2015-09-22, abandoned Cloudflare adapter). **Decision needed** — recommended fallback: `pyflare-africa` (keeps `import pyflare` semantics; only the `pip install` name changes). Alternatives: `africaflare` (cleaner, but rename module too), `flarescope-africa` (longer). User to confirm; Claude will then patch pyproject.toml + README + badge.
- [ ] **Y4**: 3 cold-email drafts ready in `drafts/y4_*.md` ([elvidge](drafts/y4_elvidge.md), [sdn](drafts/y4_sdn.md), [adeyanju](drafts/y4_adeyanju.md)). User to scrub voice tells, fill in named recipients (esp. Adeyanju first name + department), and send.

### Risk register changes

- **EOG license risk upgraded from Med → High** — new license-based flow as of 2025-01-10 has unknown turnaround. Mitigated by Day 0 email + load-bearing synthetic fallback in notebooks. PLAN.md §5 and Y2 row updated.
- **G2 risk retired** — headline number reproducible, citations in place.

### Pace check

**~9 days ahead of the PLAN.md schedule.** Day 0 + Day 1 has compressed Days 0-9 of automated work into ~24 hours real time. Gates green: **G2, G3, G4, G5, G6, G7, G8, G9** (8 of 14). C1-C11 effectively done. Y1 + Y3 done. Y2 license approved (Client ID pending). Y4 drafts ready, Y5 still on user track.

`bash scripts/verify.sh` summary: **20 passed, 0 failed, 6 pending.** All 6 pendings are user-action or composite (G10 awaiting `git tag v0.1.0`; G11 poster file; G12 composite; G13 human review of abstract; G14 submission confirmation).

### Day 1 evening (now): C5 wave 2 + C6 + bug fix + OAuth migration

- [x] **G4 GREEN** — country-parameterised notebook builder produces 4 working notebooks (Niger Delta, Angola, Algeria, Libya); all execute cleanly via `jupyter nbconvert --execute`.
- [x] **G5 GREEN** — iconic Africa map at 3600×4200 px / 600 dpi; layered-alpha flare glow on four priority countries' synthetic facility coords; §2.a footer attribution baked in.
- [x] **G6 GREEN** — `analysis.communities_near_sites()` shipped with curated `KNOWN_AFRICAN_SETTLEMENTS` reference + 7 unit tests. Niger Delta synthetic exposure: **322,000 people within 10 km, 2.2 M within 25 km** of the 6 priority facilities.
- [x] **G7 GREEN** — `assets/africa_timelapse.gif` rendered: 5 keyframes (2012/2015/2018/2021/2024), per-country GFMR volumes drive dot intensity, Libya's 2015 civil-war dip reads cleanly mid-loop.
- [x] **G8 GREEN** — `src/pyflare/dashboard.py` Streamlit MVP shipped (local-only per VNF §1.f.iii). Country selector, slip slider, GFMR trend, top-5 comparison, communities-near table.
- [x] **G9 GREEN** — Sphinx + Furo docs scaffold (`docs/conf.py`, `index.md`, `quickstart.md`, `api.rst`, `licensing.md`) builds clean locally. RTD config at repo root.
- [x] **G10 prep done (gate awaits `git tag v0.1.0`)** — wheel + sdist built (`dist/pyflare_africa-0.1.0-{whl,tar.gz}`), smoke-installed in a fresh venv, `volume_to_co2eq(6.48, 0.05) == 22.62 MtCO₂e` end-to-end. Release runbook at [`RELEASE.md`](RELEASE.md).
- [x] **OAuth 2.0 refactor for `fetch_vnf_nightly()`** — Keycloak password grant, in-process token caching, 5 new mocked-HTTP tests.
- [x] **GFMR data fix** — World Bank moved CSV → XLSX in 2025; URL repaired, schema normalised.
- [x] **Y3 done** — PyPI distribution name locked: **`pyflare-africa`** (import stays `pyflare`). pyproject.toml + README + badge + docs updated.
- [x] **Y2 round 3 draft** — Client ID request email at [`drafts/y2_eog_client_id.md`](drafts/y2_eog_client_id.md). User to send.

### Library refactor for OAuth 2.0 (today)

EOG's VNF API moved to OAuth 2.0 (Keycloak password grant) in early 2026; basic auth is dead. Pyflare's `fetch_vnf_nightly()` refactored:

- New helper `_get_eog_access_token()` — exchanges credentials for a JWT, caches by `(client_id, username)` for ~5 min, refreshes 30 s before expiry.
- New env vars: `EOG_CLIENT_ID`, `EOG_CLIENT_SECRET` (in addition to `EOG_USERNAME`, `EOG_PASSWORD`).
- 5 new mocked-HTTP tests cover token fetch, caching, expiry refresh, multi-user cache keying, and the missing-credential error path.
- `time` and `_EOG_TOKEN_CACHE` exposed as module attributes for testability.
- Full suite: **48 passed, 1 skipped** (was 41 before today).

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

### Tomorrow (Day 2, 2026-05-08): keep momentum

All bounded automated work is done. Remaining gates are **user-action** or **composite**.

**User priority (today/tomorrow):**

1. **Send Y2 round 3** (Client ID email) — [`drafts/y2_eog_client_id.md`](drafts/y2_eog_client_id.md)
2. **Send Y4 cold emails** when ready — [`drafts/y4_elvidge.md`](drafts/y4_elvidge.md), [`drafts/y4_sdn.md`](drafts/y4_sdn.md), [`drafts/y4_adeyanju.md`](drafts/y4_adeyanju.md)
3. **Commit + push** the Day 1 work; verify CI runs green on GitHub Actions
4. **Walk through `RELEASE.md`** once happy — produces v0.1.0 tag + PyPI listing + GitHub Release. Steps 1-3 (checklist + clean build + smoke install) are already verified locally; remaining steps need your PyPI account.

**Claude can help with (when asked):**

- Y4 voice-tell scrub of your edited drafts (without rewriting — just flag tells)
- ReadTheDocs activation walkthrough (one-time GitHub OAuth flow)
- v0.2 roadmap items: WorldPop integration, polygon-precise filtering via GeoPandas, additional country maintainers' notebooks
- Post-poster: JOSS paper draft (`paper.md`, `paper.bib`, GitHub Action for PDF preview)

### Cut-order reminder

If we slip: drop time-lapse → Streamlit → communities-near-sites. Never cut: CO₂-eq function, country notebooks, iconic map, PyPI release.
