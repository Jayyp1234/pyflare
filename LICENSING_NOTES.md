# VNF licensing — what pyflare and its users must do

This document is pyflare's working summary of the **VIIRS Nightfire Academic Data Use License Agreement** (dated 2026-01-26, signed by the project owner on behalf of the University of Lagos). It is **not a substitute** for the signed license PDF, which is the legal source of truth — it's a developer-facing checklist so the codebase, notebooks, dashboards, and downstream materials stay compliant by construction.

If anything below conflicts with the signed license, **the license wins**.

---

## TL;DR for contributors

1. **Don't redistribute raw VNF data.** Pyflare's `fetch_vnf_nightly()` requires user-supplied EOG credentials by design — keep it that way.
2. **Carry the attribution notice** on any product (chart, map, table, dashboard, paper) generated with real VNF data.
3. **Don't publish current-year volume or CO₂ numbers calculated from VNF** until EOG has published them at https://eogdata.mines.edu/products/vnf/global_gas_flare.html. The pyflare-computed headline using **GGFR-published** annual volumes (e.g. Nigeria 2024 = 6.48 bcm from the World Bank GGFR 2025 release) is fine because it uses already-public input; the constraint bites if you compute the same thing directly from raw VNF.
4. **Aggregate VNF temporal data to weekly+** before public display. Sub-weekly time steps are restricted to the listed exception cases.
5. **Cite at least one** of the EOG papers listed in the license (we cite Elvidge et al. 2013 + 2016 already; see References below).
6. **Don't claim EOG / Colorado School of Mines endorsement** without specific prior written permission — including how Christopher Elvidge's potential endorsement (Y4) is framed.

---

## Restriction-by-restriction map to the codebase

| License § | Restriction | Pyflare compliance posture |
|---|---|---|
| 1.a | No selling VNF data itself; derived products OK | MIT-licensed library, no resale. ✓ compliant. |
| 1.b | No redistribution in machine-readable form / bulk download | `fetch_vnf_nightly()` requires user creds; no bundled VNF dumps. ✓ compliant. **Action:** never ship sample VNF rows in tests or notebooks. Use synthetic data (as in `notebooks/01_niger_delta.ipynb`). |
| 1.c | Attribution notice on derived products | **Action:** notice appears in [README acknowledgements](README.md), every notebook header, and must be added to the iconic map (G5) and any future Streamlit dashboard (G8). |
| 1.d | VNF is controlled information | We never log or print raw VNF rows in CI. ✓ |
| 1.e | **Don't publish current/recent-year flared-volume or CO₂ numbers from VNF until EOG publishes them** | Headline number in poster + notebook uses **GGFR's published 2024 figure** (Nigeria 6.48 bcm) as input to `volume_to_co2eq()` — that's a public input. Verify against https://eogdata.mines.edu/products/vnf/global_gas_flare.html before publishing any year. **Year currently safe to disclose: ≤ 2024.** |
| 1.f | No sub-weekly temporal profiles publicly | Notebook + future dashboards: aggregate VNF detections to **weekly minimum** before any public chart. Synthetic data unconstrained. **Streamlit dashboard (G8) requires EOG written approval before launch** if it exposes interactive sub-weekly views. |
| 1.g + 2.b | Cite EOG papers | Already in `pyflare/analysis.py` module docstring (Elvidge 2013, 2016). **Action:** consider citing additional papers from §2.b for v0.2 (Zhizhin 2021, 2025; subpixel emitters; etc.). |
| 1.h | No use of EOG / Mines names to endorse/promote without permission | **Action:** revise Y4 Elvidge draft so endorsement is framed as personal-from-Elvidge, not as EOG/Mines endorsing pyflare. README must not say "endorsed by EOG" or use EOG/Mines logos without written permission. |
| 2.a | Mark all products with the notice | Standard text added to README and notebook attribution cells (see below). |

---

## Required attribution notice (verbatim)

For full-format outputs (README, papers, posters, notebook headers):

> This product was made utilizing VIIRS Nightfire (VNF) nightly data produced by the Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines.

For tight space (single images, captions):

> Source: VIIRS Nightfire, Colorado School of Mines.

Logos available from https://eogdata.mines.edu/products/logo/ (use only when room permits and other partner logos are present).

---

## Year-by-year disclosure clearance

Pyflare publishes year-N flared-volume / CO₂ estimates only after confirming year-N appears at https://eogdata.mines.edu/products/vnf/global_gas_flare.html.

| Year | Cleared? | Source check date |
|---|---|---|
| 2024 | ✅ (GGFR 2025 release covers 2024) | 2026-05-06 |
| 2025 | ⏳ pending — re-check before any 2025 publication | n/a |

When updating headline numbers, re-verify the clearance year and update this table.

---

## Module-by-module checklist

### `src/pyflare/data.py`
- [x] `fetch_vnf_nightly()` requires `EOG_USERNAME` / `EOG_PASSWORD` (no fallback).
- [x] No bundled VNF samples.
- [ ] **TODO:** add a docstring note to `fetch_vnf_nightly()` that callers carry the same VNF license obligations as pyflare.

### `src/pyflare/analysis.py`
- [x] Module docstring cites Elvidge 2013 + 2016.
- [ ] **TODO:** consider broader citation set for v0.2.

### `notebooks/01_niger_delta.ipynb`
- [ ] **TODO:** add attribution cell at top + footer reproducing the §2.a notice.
- [x] Uses synthetic VNF data; outputs are not VNF-derived in the published version.
- [ ] **TODO:** when EOG creds arrive, before re-executing with real VNF: aggregate any visible temporal display to weekly+, confirm year is in the clearance table.

### Future: `notebooks/{02,03,04}_*.ipynb` (G4)
- [ ] **TODO:** builder script must include attribution cells by default.

### Future: iconic Africa map (G5)
- [ ] **TODO:** rendered map must carry the §2.a credit line in the figure footer.

### Future: Streamlit dashboard (G8)
- [ ] **BLOCKER:** consult EOG and obtain written approval for the region scope and refresh cadence before public launch (per §1.f.iii).

### Future: AFLARED Zenodo deposit
- [ ] **TODO:** ensure the deposit is aggregated (flare-site / monthly minimum) and cites VNF + the §2.b papers; per-detection redistribution is prohibited (§1.b).

### Future: poster artefact
- [ ] **TODO:** include the §2.a notice in the poster footer.

### Future: JOSS / methods paper
- [ ] **TODO:** cite the §2.b paper set; describe the licensing constraints in the paper's "Data availability" section.

---

## Y4 Elvidge endorsement — framing constraint

§1.h means we can't request a "EOG endorses pyflare" framing. Acceptable framings:

- ✅ Christopher Elvidge personally endorses pyflare's correct implementation of his published methodology.
- ✅ A quote from Elvidge in the README, attributed as "Christopher Elvidge, lead author, *VIIRS Nightfire: Satellite pyrometry at night* (2013)".
- ❌ "Endorsed by NOAA EOG / Colorado School of Mines" (anywhere).
- ❌ Use of EOG / Mines logos without specific prior written permission.

The Y4 Elvidge draft has been revised accordingly. The "bonus ask" (link from the EOG project page to pyflare) requires written permission from EOG/Mines and should be made explicitly through `eog@mines.edu` if Elvidge agrees in principle.

---

## When in doubt

Email `eog@mines.edu` (or `victoria.patti@mines.edu`) with the specific question. EOG's reply turnaround on the initial license request was ~4 hours; they're responsive.
