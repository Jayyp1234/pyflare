# pyflare

> Open Python toolkit for satellite-based gas flaring analytics across African oil-producing nations.

[![CI](https://github.com/jayyp1234/pyflare/actions/workflows/ci.yml/badge.svg)](https://github.com/jayyp1234/pyflare/actions)
[![PyPI](https://img.shields.io/pypi/v/pyflare-africa.svg)](https://pypi.org/project/pyflare-africa/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Why this exists

Africa accounts for a significant share of global gas flaring — the deliberate burning of natural gas at oil and gas facilities. Flaring releases CO₂, unburned methane, and a long tail of local air pollutants into communities that, in many cases, live within walking distance of the flare stack.

Satellite-based monitoring of flares has existed for over a decade, principally through **VIIRS Nightfire (VNF)** — produced by the Earth Observation Group (EOG) at the Payne Institute, Colorado School of Mines, using data from the VIIRS instrument aboard Suomi NPP and JPSS-1 — and the World Bank's annual flaring estimates from the **Global Flaring and Methane Reduction Partnership (GFMR**, formerly the Global Gas Flaring Reduction Partnership / GGFR**)**. The science is solid. What has been missing is an open Python interface to make the data usable for African researchers, journalists, regulators, and engineers without paywalls or proprietary GIS software.

> **Important — pyflare does not bundle, redistribute, or rehost VIIRS Nightfire data.** The library is a thin client; each user must obtain their own VNF Academic Data Use License directly from EOG (`eog@mines.edu`) and supply their own credentials. See [`LICENSING_NOTES.md`](LICENSING_NOTES.md).

`pyflare` is that interface.

> **Maintainer note:** the paragraphs above are placeholder framing. Replace this section with your own origin story — why you built this, what you saw, what you want it to change. Reviewers and users respond to specific, personal voice. The rest of this README is reference material that benefits from being mostly factual.

---

## What it does

- **Fetches** VIIRS Nightfire daily detections (using user-supplied EOG credentials — pyflare does not redistribute VNF) and GFMR annual flared volumes.
- **Filters** to the African continent or any of 17 African oil/gas-producing countries.
- **Classifies** detections as flares vs. wildfires using temperature signatures from Elvidge et al. (2013).
- **Clusters** recurring detections into persistent flare sites.
- **Estimates** flared gas volumes and methane emissions using published regressions (Elvidge et al., 2016).
- **Visualizes** results as Folium maps and matplotlib plots, including the headline "Africa overview" map.

---

## Install

The package is published on PyPI as `pyflare-africa` (the `pyflare` name was already taken by an unrelated, abandoned project). The Python import name stays `pyflare`.

```bash
pip install pyflare-africa                     # core
pip install 'pyflare-africa[viz]'              # with map and plot helpers
pip install 'pyflare-africa[notebooks]'        # to run the country notebooks
pip install 'pyflare-africa[dev]'              # for contributors
```

```python
import pyflare as pf  # import name unchanged
```

---

## Quick start

```python
import pyflare as pf

# Annual flared volumes by country (no auth required)
annual = pf.fetch_ggfr_annual()

# Filter to one country
nigeria = annual[annual["country"] == "Nigeria"]
print(nigeria[["year", "bcm_flared"]].tail())

# Plot the trend
from pyflare.viz import country_trend
fig = country_trend(annual, ["Nigeria", "Algeria", "Libya"])
fig.savefig("trend.png", dpi=200)

# Daily detections (requires free EOG account at eogdata.mines.edu)
import os
os.environ["EOG_USERNAME"] = "..."
os.environ["EOG_PASSWORD"] = "..."

detections = pf.fetch_vnf_nightly("2024-08-15", satellite="snpp")
delta = pf.filter_country(detections, "Nigeria")

# Classify and cluster
from pyflare.analysis import classify_detection_type, aggregate_to_sites
classified = classify_detection_type(delta)
flares = classified[classified["detection_type"] == "flare"]
sites = aggregate_to_sites(flares)

# Map the result
from pyflare.viz import africa_overview
m = africa_overview(flares)
m.save("niger-delta.html")
```

---

## Architecture

```
pyflare/
├── data.py        # Fetchers (GFMR, VNF) + spatial filters
├── analysis.py    # Classification, clustering, volume + methane estimates
└── viz.py         # Folium maps and matplotlib plots
```

Three modules, three responsibilities. `data` doesn't know about analysis;
`analysis` doesn't know about visualization. Each module has its own test
file and can be used independently.

---

## Supported countries

Bounding-box filtering is provided for: Algeria, Angola, Cameroon, Chad,
Republic of Congo, DR Congo, Egypt, Equatorial Guinea, Gabon, Ghana,
Libya, Mozambique, Niger, Nigeria, South Sudan, Sudan, Tunisia.

For polygon-precise filtering (excludes overlapping waters and neighbouring
countries), the v0.2 release will integrate Natural Earth country geometries
via GeoPandas.

---

## Roadmap

- [x] **v0.1** — GFMR + VNF transport, bbox filtering, classification, site clustering, Folium maps
- [ ] **v0.2** — Polygon-precise country filtering via Natural Earth + GeoPandas
- [ ] **v0.3** — Streamlit dashboard scaffolding (`pyflare.dashboard`) for `flarewatch.africa`
- [ ] **v0.4** — Zenodo deposit of the AFLARED harmonized dataset (with DOI)
- [ ] **v0.5** — JOSS submission
- [ ] **v1.0** — Public dashboard live, country contributors recruited

---

## Citing

If you use `pyflare` in research, please cite both the underlying VNF /
GFMR methodologies and the toolkit:

```bibtex
@software{pyflare,
  author  = {Okeke, Johnpaul},
  title   = {pyflare: Open Python toolkit for satellite-based gas flaring
             analytics across African oil-producing nations},
  year    = {2026},
  url     = {https://github.com/jayyp1234/pyflare}
}
```

A formal citation with DOI will be available after the Zenodo and JOSS
submissions land. See `CITATION.cff` for the machine-readable record.

---

## Contributing

We are actively recruiting **country maintainers** — one Pythonista per
African oil/gas-producing nation to maintain country-specific notebooks
and validation cases. See `CONTRIBUTING.md`.

All participation is governed by `CODE_OF_CONDUCT.md` (Contributor
Covenant 2.1).

---

## Acknowledgements & data attribution

> This product was made utilizing VIIRS Nightfire (VNF) nightly data produced by the Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines.

VIIRS Nightfire is produced by **EOG at the Colorado School of Mines** — not by NOAA. The VIIRS instrument aboard the Suomi NPP and JPSS-1 satellites supplies the underlying observations; the Nightfire algorithm and product are EOG's.

Annual flaring volumes are published by the World Bank's
[Global Flaring and Methane Reduction Partnership (GFMR)](https://www.worldbank.org/en/programs/gasflaringreduction)
(formerly the Global Gas Flaring Reduction Partnership, GGFR).

This project would not exist without the methodology developed and freely
documented by Christopher Elvidge and colleagues.

Pyflare users who fetch raw VNF data via `fetch_vnf_nightly()` are bound
by the same VIIRS Nightfire Academic Data Use License terms — see
[`LICENSING_NOTES.md`](LICENSING_NOTES.md) for the developer-facing
summary of the constraints (no raw redistribution, attribution required
on derived products, weekly minimum temporal aggregation for public
charts, year-N flared-volume publication only after EOG has published
year-N at https://eogdata.mines.edu/products/vnf/global_gas_flare.html).

---

## License

MIT. See `LICENSE`.
