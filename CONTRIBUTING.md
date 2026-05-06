# Contributing to pyflare

Thanks for your interest. `pyflare` exists to make satellite gas flaring data usable by researchers, journalists, regulators, and engineers across Africa — and that goal is only reachable if the project welcomes contributions from across the continent and beyond.

This document covers two things: how to contribute code, and how to become a country maintainer under the **Adopt-a-Country** programme.

---

## Adopt-a-Country

Each African oil/gas-producing country covered by pyflare has a dedicated maintainer slot. A country maintainer is responsible for:

- A country-specific notebook in `notebooks/countries/<country>.ipynb` walking through fetching, filtering, and analyzing data for that nation.
- Local context — known flare sites, regulatory landscape, community-impact references, validation cases.
- Reviewing PRs that touch their country's data or geometry.

We currently have unfilled slots for **Algeria, Angola, Cameroon, Chad, Republic of Congo, DR Congo, Egypt, Equatorial Guinea, Gabon, Ghana, Libya, Mozambique, Niger, Nigeria, South Sudan, Sudan, Tunisia**. To volunteer, open an issue with the title `Country maintainer: <Country>` and a short note about your background.

You don't need to be from the country to maintain it, but a credible local connection (residence, research focus, citizenship, professional experience) is preferred.

---

## Development setup

```bash
git clone https://github.com/YOUR-HANDLE/pyflare.git
cd pyflare
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,viz]"
pre-commit install   # optional but recommended
```

Run the tests:

```bash
pytest
pytest --cov=pyflare    # with coverage
```

Run the linters:

```bash
ruff check .
ruff format .
mypy src/pyflare
```

---

## Filing issues

- **Bugs** — please include the pyflare version (`python -c "import pyflare; print(pyflare.__version__)"`), Python version, OS, a minimal reproducer, and the full traceback.
- **Feature requests** — describe the use case first, the proposed API second. We are conservative about scope: pyflare is satellite gas flaring analytics for Africa, full stop.
- **Data corrections** — if you spot incorrect bounding boxes, flare-classification thresholds, or methodology, please cite a source. Pyflare's defaults must be defensible.

---

## Pull requests

1. Open an issue first for non-trivial changes — we'll often save you work.
2. One logical change per PR. Small, focused PRs land faster.
3. New code must include tests. New public functions must include docstrings (NumPy style) with at least one example.
4. New numerical defaults (thresholds, conversion factors) must cite a peer-reviewed source.
5. Run `pytest` and `ruff check .` locally before pushing.

---

## Style

- Python 3.10+ syntax. Type hints throughout.
- Docstrings: NumPy style. Each public function must include `Parameters`, `Returns`, and at least one `Examples` block.
- Line length: 100 characters.
- Imports: `from __future__ import annotations` at the top of every module.
- No surprise side effects in `__init__.py` — only re-exports.

---

## Scientific integrity

`pyflare` is used to make claims about real-world emissions. We hold ourselves to research-grade standards:

- Methodology must trace to a peer-reviewed source.
- Defaults must be conservative when in doubt.
- Limitations must be documented honestly in docstrings, not hidden.
- Estimates of volume and emissions must be labelled as such — pyflare does not measure, it estimates from satellite observations.

If a contribution risks overstating what pyflare can do, we'll work with you to soften the claim.

---

## Communication

- Issues and PRs: on GitHub.
- Questions: GitHub Discussions (forthcoming).
- Sensitive matters: contact the maintainer directly (see `CODE_OF_CONDUCT.md`).
