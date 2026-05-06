# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (licensing compliance)
- `LICENSING_NOTES.md` — developer-facing summary of the VNF Academic
  Data Use License obligations (no raw redistribution, attribution
  required, weekly minimum public temporal aggregation, year-N volume
  publication only after EOG publishes year-N, EOG/Mines endorsement
  framing, year-by-year disclosure clearance table).
- README acknowledgements expanded with the verbatim VNF attribution
  notice (license §2.a) and a link to `LICENSING_NOTES.md`.
- Notebook header includes a data-attribution cell that activates when
  the synthetic VNF block is replaced with `pf.fetch_vnf_nightly()`.

### Fixed
- `fetch_ggfr_annual()` now points at the 2025 World Bank GGFR XLSX release
  (the previous CSV URL returns 404). The fetch reads sheet ``Flare volume``
  and melts the wide format to a tidy ``country`` / ``year`` / ``bcm_flared``
  frame. World Bank country labels are normalised to pyflare's canonical
  set so the result composes with `filter_country()`.

### Added
- `pyflare.analysis.volume_to_co2eq()` — combustion + methane-slip
  CO2-equivalent estimator. IPCC 2006 (combustion EF 2.55 kg/m³) +
  IPCC AR6 (GWP-100 fossil CH4 = 29.8) + configurable slip. Returns
  megatonnes CO2-equivalent.
- New module constants: `CO2_PER_M3_GAS_KG`, `METHANE_GWP100_FOSSIL`,
  `METHANE_DENSITY_KG_PER_M3` (the last shared with `methane_proxy`).
- `notebooks/01_niger_delta.ipynb` — end-to-end Niger Delta walkthrough:
  GGFR trend → African context → synthetic VNF pipeline → CO2-eq
  headline. Runs without EOG credentials.
- New core dependency: `openpyxl>=3.1` (for the GGFR XLSX).

## [0.1.0] - 2026-05-16

### Added
- Initial public scaffold.
- `pyflare.data`: GGFR annual fetch, VNF nightly fetch, country and bbox
  filters, schema normalization for 17 African oil/gas-producing nations.
- `pyflare.analysis`: detection-type classification (Elvidge et al. 2013),
  persistence scoring, greedy single-link site clustering, flared-volume
  estimation, configurable methane proxy with literature-cited slip fraction.
- `pyflare.viz`: Folium maps, matplotlib trend charts, project palette,
  Africa-overview map.
- 38 unit tests; no network dependency in the suite.
- Contributor Covenant 2.1 code of conduct.
- CI matrix on Python 3.10 / 3.11 / 3.12 with ruff.
- Pre-commit config (ruff, mypy, standard hygiene hooks).
- Adopt-a-Country contributor programme.
