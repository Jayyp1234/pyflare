# Quickstart

A 5-minute end-to-end walkthrough using the public GGFR dataset, plus a synthetic VNF stand-in for the per-flare detection pipeline (real VNF requires an EOG academic license — see {doc}`licensing`).

## Install

The package ships on PyPI as `pyflare-africa` (the `pyflare` name was already taken). The Python import name stays `pyflare`.

```bash
pip install pyflare-africa                  # core
pip install 'pyflare-africa[viz]'           # map + plot helpers
pip install 'pyflare-africa[notebooks]'     # to run the country notebooks
pip install 'pyflare-africa[dev]'           # for contributors
```

## Annual flaring trend, no credentials required

```python
import pyflare as pf

annual = pf.fetch_ggfr_annual()
nigeria = annual[annual["country"] == "Nigeria"].sort_values("year")
print(nigeria.tail(5))
```

```{tip}
The first call downloads the World Bank GGFR XLSX (~70 KB) and caches it
in `~/.cache/pyflare/`. Subsequent calls read from cache.
```

## Headline number — CO₂-equivalent for one country

```python
from pyflare.analysis import volume_to_co2eq

ng_2024 = float(nigeria.loc[nigeria["year"] == 2024, "bcm_flared"].iloc[0])

for slip, label in [(0.02, "IPCC AR6"), (0.05, "Plant 2022 mid"), (0.09, "Plant 2022 high")]:
    mt = volume_to_co2eq(ng_2024, slip)
    print(f"  slip={slip:.2f} ({label}): {mt:.2f} MtCO2e")
```

For Nigeria in 2024 (6.48 bcm) this prints roughly:

```
  slip=0.02 (IPCC AR6): 18.96 MtCO2e
  slip=0.05 (Plant 2022 mid): 22.62 MtCO2e
  slip=0.09 (Plant 2022 high): 27.50 MtCO2e
```

The spread between these is the headline argument for satellite-grounded flare measurement.

## Per-flare classification, clustering, exposure

```python
from pyflare.analysis import (
    classify_detection_type, aggregate_to_sites, communities_near_sites
)

# `detections` here would normally come from `pf.fetch_vnf_nightly(...)`.
# See notebooks/01_niger_delta.ipynb for a synthetic stand-in that runs
# end-to-end without EOG credentials.

classified = classify_detection_type(detections)
flares = classified[classified["detection_type"] == "flare"]
sites = aggregate_to_sites(flares)

exposure = communities_near_sites(sites, radius_km=10)
print(exposure[["site_id", "n_communities_within_radius", "population_exposed", "nearest_community"]])
```

## Where to look next

- The four country quickstart notebooks under `notebooks/` (Niger Delta, Angola, Algeria, Libya) — all run end-to-end, no credentials.
- {doc}`api` — full API reference, auto-generated from NumPy-style docstrings.
- {doc}`licensing` — VNF Academic Data Use License obligations.
