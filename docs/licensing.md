# Licensing & data attribution

`pyflare` itself is **MIT-licensed**. Two upstream data sources have their own license terms that propagate to anyone running pyflare with real data, summarised here.

## VIIRS Nightfire (VNF)

VNF nightly detections are the heart of pyflare's per-flare analyses. Use of VNF is governed by the **VIIRS Nightfire Academic Data Use License Agreement** (signed by the project owner on behalf of the University of Lagos in May 2026; one-year renewable academic license).

Key obligations that affect pyflare users:

- **No raw redistribution.** `pyflare.fetch_vnf_nightly()` requires you to supply your own EOG OAuth 2.0 credentials. The library never bundles VNF samples.
- **Attribution required.** Any chart, table, dashboard, or paper you produce from VNF data must carry the notice:

  > *This product was made utilizing VIIRS Nightfire (VNF) nightly data produced by the Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines.*

  Tight-space alternative: *"Source: VIIRS Nightfire, Colorado School of Mines."*

- **Disclosure embargo** (§1.e). You cannot publicly disclose current- or recent-year flared-volume or CO₂ numbers calculated from VNF until EOG has published year-N at <https://eogdata.mines.edu/products/vnf/global_gas_flare.html>. **Currently cleared:** ≤ 2024.
- **Weekly minimum aggregation** (§1.f). Public temporal displays must aggregate VNF detections to weekly or coarser. Sub-weekly is allowed only for internal use, static publications, or interactive services for restricted regions with EOG approval.
- **No EOG/Mines endorsement claims** (§1.h). You cannot claim that EOG or Colorado School of Mines endorses your derived products without specific prior written permission.
- **Citation** (§1.g). At least one of the EOG papers listed in §2.b must be cited in any publication using VNF data. Pyflare's analysis module already cites Elvidge et al. (2013) and Elvidge et al. (2016) — the most common starting point.

The repository's [`LICENSING_NOTES.md`](https://github.com/Jayyp1234/pyflare/blob/main/LICENSING_NOTES.md) contains the developer-facing checklist mapped to specific code paths.

## World Bank GGFR

GGFR annual flared volumes are published openly via the World Bank under the Creative Commons Attribution 4.0 license. `pyflare.fetch_ggfr_annual()` downloads the workbook directly and caches it locally. Citation form on the World Bank's website.

## Pyflare itself

MIT. See [`LICENSE`](https://github.com/Jayyp1234/pyflare/blob/main/LICENSE) at the repo root.
