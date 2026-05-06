# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
