# pyflare

> Open Python toolkit for satellite-based gas flaring analytics across African oil-producing nations.

`pyflare` turns NOAA's VIIRS Nightfire (VNF) detections and the World Bank's Global Gas Flaring Reduction (GGFR) annual estimates into a small, well-tested Python interface designed for African researchers, journalists, regulators, and engineers.

It is the technical centerpiece of a longer-term initiative aimed at:

1. A peer-reviewed methods paper at the *Journal of Open Source Software* (target: July 2026).
2. The **AFLARED** harmonised African flaring dataset on Zenodo with a citable DOI (target: late 2026).
3. A `flarewatch.africa` public dashboard (target: post-v1.0).
4. A community of country maintainers — one Pythonista per producing nation.

## Headline numbers

For Nigeria's 2024 gas flaring (GGFR-published 6.48 bcm), `pyflare` produces:

| Climate frame | 19–28 MtCO₂e per year |
| --- | --- |
| **Public-health frame** | **322,000 people within 5 km of a major flare facility (Niger Delta synthetic exposure); 2.2 M within 25 km** |

The CO₂-equivalent range is driven by the methane slip assumption — IPCC AR6 conservative (2 %) versus recent satellite-derived estimates (5–9 %, Plant et al. 2022). The spread is itself the argument for satellite measurement.

## Where to next

```{toctree}
:maxdepth: 2

quickstart
api
licensing
```

## Citing pyflare

If you use `pyflare` in research or reporting, please cite the project software entry plus at least one of the underlying VNF methodology papers:

- Elvidge, C. D., et al. (2013). VIIRS Nightfire: Satellite pyrometry at night. *Remote Sensing*, 5(9), 4423-4449.
- Elvidge, C. D., et al. (2016). Methods for global survey of natural gas flaring from VIIRS Nightfire data. *Energies*, 9(1), 14.

A machine-readable citation is in [`CITATION.cff`](https://github.com/Jayyp1234/pyflare/blob/main/CITATION.cff). A formal DOI will follow the AFLARED Zenodo deposit and JOSS paper.

## Acknowledgements

> This product was made utilizing VIIRS Nightfire (VNF) nightly data produced by the Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines.

`pyflare` would not exist without the methodology developed and freely documented by Christopher Elvidge and colleagues. See the {doc}`licensing` page for the full set of VNF Academic Data Use License obligations.
