"""Generate notebooks/01_niger_delta.ipynb from a Python source-of-truth.

Editing raw .ipynb JSON is painful. This script keeps the notebook content
readable as Python lists of (cell_type, source) tuples and serialises to a
valid v4.5 notebook. Run from the repo root::

    python scripts/_build_niger_delta_notebook.py

Then execute the notebook in place to populate outputs::

    jupyter nbconvert --to notebook --execute --inplace notebooks/01_niger_delta.ipynb
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


def md(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": _split_lines(textwrap.dedent(text).strip("\n") + "\n"),
    }


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _split_lines(textwrap.dedent(text).strip("\n") + "\n"),
    }


def _split_lines(text: str) -> list[str]:
    """Notebook source format: list of strings, each line ending in \\n
    except optionally the last."""
    lines = text.splitlines(keepends=True)
    return lines


CELLS = [
    md("""
        # Niger Delta — pyflare quickstart

        > A 5-minute end-to-end walkthrough: from the World Bank's annual
        > GGFR estimates to a peer-reviewable CO₂-equivalent headline number
        > for Nigerian gas flaring. Runs without EOG credentials by using a
        > synthetic VNF detection dataset for the Niger Delta — replace the
        > synthetic block with `pf.fetch_vnf_nightly()` once your EOG
        > license is approved.

        **Status:** validated against pyflare v0.1.0 + 2025 GGFR release
        (data through 2024).
    """),
    md("""
        ## Setup

        ```bash
        pip install pyflare-africa[viz,notebooks]   # or `pip install -e ".[viz,notebooks]"` if developing
        ```

        This notebook assumes `matplotlib` is available; everything else is
        in pyflare's core install.
    """),
    md("""
        ## Data attribution

        This notebook is structured around the VIIRS Nightfire (VNF)
        product. The synthetic VNF block in §3 is a stand-in until your
        EOG academic license is approved. **When you swap that block for
        `pf.fetch_vnf_nightly()`, the following attribution applies to
        every chart and table rendered below it:**

        > This product was made utilizing VIIRS Nightfire (VNF) nightly
        > data produced by the Earth Observation Group, Payne Institute
        > for Public Policy, Colorado School of Mines.

        For tight space, use: *"Source: VIIRS Nightfire, Colorado School
        of Mines."*

        Annual flaring volumes are published by the World Bank
        Global Gas Flaring Reduction Partnership. Pyflare cites
        Elvidge et al. (2013) and Elvidge et al. (2016) — see
        [`LICENSING_NOTES.md`](../LICENSING_NOTES.md) for the full set of
        VNF license obligations (including: no raw VNF redistribution,
        weekly-minimum public temporal aggregation, year-N volume
        publication only after EOG publishes year-N).
    """),
    code("""
        from __future__ import annotations

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt

        import pyflare as pf
        from pyflare.analysis import (
            classify_detection_type,
            aggregate_to_sites,
            estimate_flared_volume,
            volume_to_co2eq,
        )

        print(f"pyflare {pf.__version__}")
    """),
    md("""
        ## 1. Annual flaring trend, Nigeria 2012–2024

        `fetch_ggfr_annual()` pulls the live World Bank GGFR workbook,
        melts it to long format, and normalises country names. No
        authentication required.
    """),
    code("""
        annual = pf.fetch_ggfr_annual()
        nigeria = annual[annual["country"] == "Nigeria"].sort_values("year")
        nigeria_recent = nigeria.tail(8).reset_index(drop=True)
        nigeria_recent
    """),
    code("""
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(nigeria["year"], nigeria["bcm_flared"], marker="o", color="#d44500", linewidth=2)
        ax.set_title("Nigeria — annual gas flaring volume (GGFR)", loc="left", fontsize=12, fontweight="bold")
        ax.set_xlabel("Year")
        ax.set_ylabel("Flared volume (bcm)")
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)
        plt.tight_layout()
        plt.show()
    """),
    md("""
        ## 2. African context — top-5 producers in 2024
    """),
    code("""
        african_producers = pf.list_supported_countries()
        top5 = (
            annual[(annual["country"].isin(african_producers)) & (annual["year"] == 2024)]
            .nlargest(5, "bcm_flared")
            .reset_index(drop=True)
        )
        top5
    """),
    code("""
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(top5["country"][::-1], top5["bcm_flared"][::-1], color="#d44500")
        ax.set_title("Top 5 African gas-flaring producers, 2024", loc="left", fontsize=12, fontweight="bold")
        ax.set_xlabel("Flared volume in 2024 (bcm)")
        for bar, val in zip(bars, top5["bcm_flared"][::-1]):
            ax.text(val + 0.1, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=9)
        ax.set_xlim(right=top5["bcm_flared"].max() * 1.15)
        plt.tight_layout()
        plt.show()
    """),
    md("""
        ## 3. Per-flare detail — synthetic VNF stand-in

        The real `pf.fetch_vnf_nightly()` call requires EOG credentials
        (currently pending under the new VNF license-based flow as of Jan
        2025). Until those arrive, we synthesise a plausible Niger Delta
        nightly detection set so the rest of the pipeline can be exercised
        end-to-end. **Replace the next cell with the real fetch once your
        license is in hand:**

        ```python
        import os
        os.environ["EOG_USERNAME"] = "..."
        os.environ["EOG_PASSWORD"] = "..."
        detections = pf.fetch_vnf_nightly("2024-08-15", satellite="snpp")
        nigerian_detections = pf.filter_country(detections, "Nigeria")
        ```
    """),
    code("""
        rng = np.random.default_rng(42)

        # Approximate coordinates of major Niger Delta flare facilities.
        sites_truth = [
            ("Bonny LNG",  7.16, 4.41),
            ("Forcados",   5.36, 5.34),
            ("Brass",      6.24, 4.32),
            ("Escravos",   5.18, 5.65),
            ("Onne",       7.16, 4.71),
            ("Soku",       6.66, 4.38),
        ]

        records = []
        for name, lon, lat in sites_truth:
            n = rng.integers(8, 16)  # 8-15 nightly observations per site
            for _ in range(n):
                records.append({
                    "site_truth": name,
                    "longitude": lon + rng.normal(0, 0.005),  # ~500m jitter
                    "latitude":  lat + rng.normal(0, 0.005),
                    "temperature_k":   max(1500, rng.normal(1850, 150)),
                    "radiant_heat_mw": rng.uniform(20, 80),
                    "obs_date": pd.Timestamp("2024-08-15") + pd.Timedelta(days=int(rng.integers(0, 14))),
                })
        # Sprinkle in some wildfires for the classifier to reject.
        for _ in range(15):
            records.append({
                "site_truth": "wildfire",
                "longitude": rng.uniform(2.7, 14.7),
                "latitude":  rng.uniform(4.3, 13.9),
                "temperature_k":   rng.normal(900, 100),
                "radiant_heat_mw": rng.uniform(5, 25),
                "obs_date": pd.Timestamp("2024-08-15") + pd.Timedelta(days=int(rng.integers(0, 14))),
            })

        vnf_synthetic = pd.DataFrame(records)
        print(f"Synthesised {len(vnf_synthetic)} detections "
              f"(mean temp {vnf_synthetic['temperature_k'].mean():.0f} K)")
    """),
    md("""
        ### Classify, filter, cluster

        Threshold-based classification (Elvidge et al., 2013) splits the
        detections into flares vs wildfires; greedy clustering rolls
        co-located nightly detections into persistent flare sites.
    """),
    code("""
        classified = classify_detection_type(vnf_synthetic)
        flares = classified[classified["detection_type"] == "flare"].copy()
        sites = aggregate_to_sites(flares)

        print(f"  Total detections:  {len(vnf_synthetic)}")
        print(f"  Classified flares: {len(flares)}")
        print(f"  Clustered sites:   {len(sites)} (truth: 6 facilities)")
        sites
    """),
    code("""
        # Estimate volumes per site (Elvidge et al., 2016 RH→volume regression).
        volumes = estimate_flared_volume(sites, observation_days=14)
        site_total_bcm = volumes["estimated_volume_bcm"].sum()
        print(f"Sum of synthetic-site flared volume estimates: {site_total_bcm:.4f} bcm")
        print("(Synthetic, not comparable to GGFR Nigeria-wide total — illustrative only.)")
        volumes[["site_id", "longitude", "latitude", "n_detections", "estimated_volume_bcm"]]
    """),
    md("""
        ## 4. Headline number — Niger Delta CO₂-equivalent, 2024

        Using `volume_to_co2eq()` against the **GGFR-reported** Nigeria
        2024 flared volume (not the synthetic per-site sum), under three
        published methane-slip assumptions.
    """),
    code("""
        ng_2024_bcm = float(nigeria.loc[nigeria["year"] == 2024, "bcm_flared"].iloc[0])

        scenarios = [
            (0.02, "IPCC AR6 default"),
            (0.05, "pyflare default / Plant et al. 2022 mid"),
            (0.09, "Plant et al. 2022 upper bound"),
        ]

        rows = []
        for slip, label in scenarios:
            mt = volume_to_co2eq(ng_2024_bcm, slip)
            rows.append({"slip": slip, "source": label, "MtCO2e": round(mt, 2)})

        headline = pd.DataFrame(rows)
        print(f"Nigeria flared volume (GGFR 2024): {ng_2024_bcm:.2f} bcm")
        print()
        headline
    """),
    md("""
        ### Poster framing candidate

        > **Nigeria's 2024 gas flaring (6.48 bcm of natural gas) translates
        > to roughly 19–28 megatonnes of CO₂-equivalent emissions per year,
        > depending on which methane slip assumption you adopt. The spread
        > is itself the argument for satellite measurement: the answer is
        > not in dispute by an order of magnitude, but the difference
        > between the IPCC AR6 default (2 %) and recent satellite-derived
        > slip rates (5–9 %) is roughly 50 % of the headline.**

        The defensible quote for the poster is the range, with the slip
        choice made explicit. Reviewers from atmospheric chemistry will
        nod; reviewers from advocacy will appreciate the upper bound.

        ## 5. Next steps

        - Replace the synthetic VNF cell with `pf.fetch_vnf_nightly()` once
          the EOG license arrives. **Before re-publishing this notebook
          with real VNF outputs, confirm:** (a) the displayed year is
          cleared at https://eogdata.mines.edu/products/vnf/global_gas_flare.html,
          (b) any temporal display is aggregated to weekly minimum, and
          (c) the data-attribution cell above is in place.
        - Run the same notebook for Algeria, Libya, and Angola
          (`02_angola.ipynb`, `03_algeria.ipynb`, `04_libya.ipynb`) —
          target gate G4.
        - Cross-validate the synthetic-site clustering against ground-truth
          facility coordinates (Bonny LNG, Forcados, Brass, etc.) once VNF
          detections are real.

        ---

        *Source: VIIRS Nightfire, Colorado School of Mines.* (Applies once
        the synthetic VNF block above is replaced with real EOG data.)
    """),
]


def main() -> None:
    nb = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = Path(__file__).resolve().parents[1] / "notebooks" / "01_niger_delta.ipynb"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(nb, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
