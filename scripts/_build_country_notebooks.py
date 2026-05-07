"""Generate per-country pyflare quickstart notebooks.

Each notebook follows the same structure (GFMR trend → African context →
synthetic VNF pipeline → CO₂-equivalent headline) and is parameterised by
country: a configured set of approximate facility coordinates plus a
narrative hook. Run from the repo root::

    python scripts/_build_country_notebooks.py

Then execute each notebook in place to populate outputs::

    for nb in notebooks/0*_*.ipynb; do
        jupyter nbconvert --to notebook --execute --inplace "$nb"
    done

Editing rules:

- Markdown cells use Python f-strings for substitution (controlled here).
- Code cells use plain triple-quoted strings and ``__PLACEHOLDER__``
  tokens that are replaced after dedent — this avoids any conflict
  between this script's f-string substitution and the ``f"..."`` /
  ``{var}`` syntax inside the notebook code itself.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Per-country configuration
# ---------------------------------------------------------------------------

# Facility coordinates are approximate, sourced from public references for
# major flare/oil/gas facilities. Per-coordinate accuracy is unimportant
# for the synthetic walkthrough; the point is to land the detections inside
# the country bbox so the rest of the pipeline produces sensible numbers.

COUNTRIES: dict[str, dict[str, Any]] = {
    "01_niger_delta": {
        "country_name": "Nigeria",
        "region_label": "Niger Delta",
        "facilities": [
            ("Bonny LNG",  7.16, 4.41),
            ("Forcados",   5.36, 5.34),
            ("Brass",      6.24, 4.32),
            ("Escravos",   5.18, 5.65),
            ("Onne",       7.16, 4.71),
            ("Soku",       6.66, 4.38),
        ],
        "wildfire_lon_range": (2.7, 14.7),
        "wildfire_lat_range": (4.3, 13.9),
        "narrative_hook": (
            "Nigerian flaring is concentrated in the Niger Delta, where "
            "the proximity of flare stacks to coastal communities makes "
            "the climate impact compound with a public-health one."
        ),
    },
    "02_angola": {
        "country_name": "Angola",
        "region_label": "Angola — offshore + Cabinda",
        "facilities": [
            ("Soyo LNG",          12.37, -6.13),
            ("Cabinda Onshore",   12.19, -5.55),
            ("Greater Plutonio",  12.00, -7.00),
            ("Pazflor / Dalia",   11.50, -6.80),
            ("Kizomba",           11.83, -7.95),
            ("Block 31 BBLT",     10.90, -7.35),
        ],
        "wildfire_lon_range": (12.0, 20.0),
        "wildfire_lat_range": (-13.0, -8.0),
        "narrative_hook": (
            "Angolan flaring is dominated by deepwater offshore production. "
            "Most facilities are tens of km off the Atlantic coast — a "
            "different ground-truth landscape than Nigeria's onshore Delta."
        ),
    },
    "03_algeria": {
        "country_name": "Algeria",
        "region_label": "Algeria — Sahara basins",
        "facilities": [
            ("Hassi Messaoud",        6.07, 31.69),
            ("Hassi R'Mel",           3.27, 32.93),
            ("In Salah",              2.47, 27.20),
            ("Rhourde Nouss",         6.85, 31.20),
            ("Tin Fouye Tabankort",   8.55, 28.43),
            ("Berkine East",          8.50, 31.00),
        ],
        "wildfire_lon_range": (1.0, 9.0),
        "wildfire_lat_range": (35.0, 37.0),
        "narrative_hook": (
            "Algerian flaring is desert-basin gas: Hassi Messaoud, "
            "Hassi R'Mel, In Salah. Africa's largest 2024 flarer "
            "(7.88 bcm), narrowly ahead of Nigeria."
        ),
    },
    "04_libya": {
        "country_name": "Libya",
        "region_label": "Libya — Sirte basin + coastal terminals",
        "facilities": [
            ("Es Sider Terminal",   18.65, 30.62),
            ("Ras Lanuf",           18.55, 30.50),
            ("Marsa el Brega LNG",  19.62, 30.41),
            ("Sahabi",              19.20, 28.80),
            ("Hofra",               19.20, 29.10),
            ("El Sharara (Murzuq)", 12.20, 27.81),
        ],
        "wildfire_lon_range": (10.0, 25.0),
        "wildfire_lat_range": (30.0, 33.0),
        "narrative_hook": (
            "Libyan flaring is split between the Sirte basin and coastal "
            "export terminals. Despite political instability, Libya ranks "
            "just behind Nigeria in 2024 (6.28 bcm)."
        ),
    },
}


# ---------------------------------------------------------------------------
# Cell builders
# ---------------------------------------------------------------------------


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
    return text.splitlines(keepends=True)


def _facilities_literal(facilities: list[tuple[str, float, float]]) -> str:
    """Render the facility list as a Python list-of-tuples literal."""
    name_width = max(len(name) for name, _, _ in facilities) + 2
    lines = []
    for name, lon, lat in facilities:
        quoted = f'"{name}",'
        lines.append(f"    ({quoted:<{name_width + 1}} {lon:>6.2f}, {lat:>6.2f})")
    return "[\n" + ",\n".join(lines) + ",\n]"


def make_cells(slug: str, cfg: dict) -> list[dict]:
    country = cfg["country_name"]
    region = cfg["region_label"]
    hook = cfg["narrative_hook"]
    facilities_py = _facilities_literal(cfg["facilities"])
    lon_lo, lon_hi = cfg["wildfire_lon_range"]
    lat_lo, lat_hi = cfg["wildfire_lat_range"]

    synth_code = textwrap.dedent("""
        rng = np.random.default_rng(42)

        # Approximate coordinates of major __REGION__ flare facilities
        # (public references; exact accuracy not relevant for the synthetic
        # walkthrough, only that detections land inside the country bbox).
        sites_truth = __FACILITIES__

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
                "longitude": rng.uniform(__LON_LO__, __LON_HI__),
                "latitude":  rng.uniform(__LAT_LO__, __LAT_HI__),
                "temperature_k":   rng.normal(900, 100),
                "radiant_heat_mw": rng.uniform(5, 25),
                "obs_date": pd.Timestamp("2024-08-15") + pd.Timedelta(days=int(rng.integers(0, 14))),
            })

        vnf_synthetic = pd.DataFrame(records)
        print(f"Synthesised {len(vnf_synthetic)} detections "
              f"(mean temp {vnf_synthetic['temperature_k'].mean():.0f} K)")
    """).strip("\n") + "\n"
    synth_code = (
        synth_code
        .replace("__REGION__", region)
        .replace("__FACILITIES__", facilities_py)
        .replace("__LON_LO__", str(lon_lo))
        .replace("__LON_HI__", str(lon_hi))
        .replace("__LAT_LO__", str(lat_lo))
        .replace("__LAT_HI__", str(lat_hi))
    )

    return [
        md(f"""
            # {region} — pyflare quickstart

            > A 5-minute walkthrough: from the World Bank's annual GFMR
            > estimates to a peer-reviewable CO₂-equivalent headline number
            > for {country}'s gas flaring. Runs without EOG credentials by
            > using a synthetic VNF detection set for the region — replace
            > the synthetic block with `pf.fetch_vnf_nightly()` once your
            > EOG license + Client ID are in place.

            **Why this country:** {hook}

            **Status:** validated against pyflare v0.1.0 + 2025 GFMR release
            (data through 2024).
        """),
        md("""
            ## Setup

            ```bash
            pip install pyflare-africa[viz,notebooks]   # or `pip install -e ".[viz,notebooks]"` if developing
            ```

            This notebook assumes `matplotlib` is available; everything else
            is in pyflare's core install.
        """),
        md("""
            ## Data attribution

            This notebook is structured around the VIIRS Nightfire (VNF)
            product. The synthetic VNF block in §3 is a stand-in until your
            EOG academic license + Client ID are in place. **When you swap
            that block for `pf.fetch_vnf_nightly()`, the following
            attribution applies to every chart and table rendered below it:**

            > This product was made utilizing VIIRS Nightfire (VNF) nightly
            > data produced by the Earth Observation Group, Payne Institute
            > for Public Policy, Colorado School of Mines.

            For tight space, use: *"Source: VIIRS Nightfire, Colorado School
            of Mines."*

            See [`LICENSING_NOTES.md`](../LICENSING_NOTES.md) for the full
            set of VNF license obligations.
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
        md(f"""
            ## 1. Annual flaring trend, {country} 2012–2024

            `fetch_gfmr_annual()` pulls the live World Bank GFMR workbook,
            melts it to long format, and normalises country names. No
            authentication required.
        """),
        code(f"""
            annual = pf.fetch_gfmr_annual()
            country_df = annual[annual["country"] == "{country}"].sort_values("year")
            country_df.tail(8).reset_index(drop=True)
        """),
        code(f"""
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(country_df["year"], country_df["bcm_flared"], marker="o", color="#d44500", linewidth=2)
            ax.set_title("{country} — annual gas flaring volume (GFMR)", loc="left", fontsize=12, fontweight="bold")
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
        code(f"""
            african_producers = pf.list_supported_countries()
            top5 = (
                annual[(annual["country"].isin(african_producers)) & (annual["year"] == 2024)]
                .nlargest(5, "bcm_flared")
                .reset_index(drop=True)
            )
            top5
        """),
        code(f"""
            fig, ax = plt.subplots(figsize=(8, 4))
            highlight = ["#d44500" if c == "{country}" else "#7a7a7a" for c in top5["country"][::-1]]
            bars = ax.barh(top5["country"][::-1], top5["bcm_flared"][::-1], color=highlight)
            ax.set_title("Top 5 African gas-flaring producers, 2024", loc="left", fontsize=12, fontweight="bold")
            ax.set_xlabel("Flared volume in 2024 (bcm)")
            for bar, val in zip(bars, top5["bcm_flared"][::-1]):
                ax.text(val + 0.1, bar.get_y() + bar.get_height() / 2, f"{{val:.2f}}", va="center", fontsize=9)
            ax.set_xlim(right=top5["bcm_flared"].max() * 1.15)
            plt.tight_layout()
            plt.show()
        """),
        md(f"""
            ## 3. Per-flare detail — synthetic VNF stand-in

            The real `pf.fetch_vnf_nightly()` call requires EOG OAuth 2.0
            credentials (Client ID issued separately by EOG once the
            academic license is signed). Until those arrive, we synthesise
            a plausible {region} nightly detection set so the rest of the
            pipeline can be exercised end-to-end. **Replace the next cell
            with the real fetch once credentials are in hand:**

            ```python
            import os
            os.environ["EOG_CLIENT_ID"]     = "..."
            os.environ["EOG_CLIENT_SECRET"] = "..."
            os.environ["EOG_USERNAME"]      = "..."
            os.environ["EOG_PASSWORD"]      = "..."
            detections = pf.fetch_vnf_nightly("2024-08-15", satellite="snpp")
            country_detections = pf.filter_country(detections, "{country}")
            ```
        """),
        code(synth_code),
        md("""
            ### Classify, filter, cluster

            Threshold-based classification (Elvidge et al., 2013) splits
            detections into flares vs wildfires; greedy clustering rolls
            co-located nightly detections into persistent flare sites.
        """),
        code(f"""
            classified = classify_detection_type(vnf_synthetic)
            flares = classified[classified["detection_type"] == "flare"].copy()
            sites = aggregate_to_sites(flares)

            print(f"  Total detections:  {{len(vnf_synthetic)}}")
            print(f"  Classified flares: {{len(flares)}}")
            print(f"  Clustered sites:   {{len(sites)}} (truth: {len(cfg["facilities"])} facilities)")
            sites
        """),
        code("""
            volumes = estimate_flared_volume(sites, observation_days=14)
            site_total_bcm = volumes["estimated_volume_bcm"].sum()
            print(f"Sum of synthetic-site flared volume estimates: {site_total_bcm:.4f} bcm")
            print("(Synthetic, not comparable to GFMR country-wide total — illustrative only.)")
            volumes[["site_id", "longitude", "latitude", "n_detections", "estimated_volume_bcm"]]
        """),
        md(f"""
            ## 4. Headline number — {country} CO₂-equivalent, 2024

            Using `volume_to_co2eq()` against the **GFMR-reported** {country}
            2024 flared volume (not the synthetic per-site sum), under three
            published methane-slip assumptions.
        """),
        code(f"""
            country_2024_bcm = float(country_df.loc[country_df["year"] == 2024, "bcm_flared"].iloc[0])

            scenarios = [
                (0.02, "IPCC AR6 default"),
                (0.05, "pyflare default / Plant et al. 2022 mid"),
                (0.09, "Plant et al. 2022 upper bound"),
            ]

            rows = []
            for slip, label in scenarios:
                mt = volume_to_co2eq(country_2024_bcm, slip)
                rows.append({{"slip": slip, "source": label, "MtCO2e": round(mt, 2)}})

            headline = pd.DataFrame(rows)
            print(f"{country} flared volume (GFMR 2024): {{country_2024_bcm:.2f}} bcm")
            print()
            headline
        """),
        md(f"""
            ### Poster framing candidate

            > **{country}'s 2024 gas flaring translates to a range of
            > megatonnes of CO₂-equivalent emissions per year, depending
            > on which methane slip assumption you adopt. The spread is
            > itself the argument for satellite measurement: the answer
            > is not in dispute by an order of magnitude, but the
            > difference between the IPCC AR6 default (2 %) and recent
            > satellite-derived slip rates (5–9 %) drives the headline.**

            The defensible quote for the poster is the range, with the
            slip choice made explicit. Reviewers from atmospheric
            chemistry will nod; reviewers from advocacy will appreciate
            the upper bound.

            ## 5. Next steps

            - Replace the synthetic VNF cell with `pf.fetch_vnf_nightly()`
              once the EOG OAuth credentials arrive. **Before re-publishing
              this notebook with real VNF outputs, confirm:** (a) the
              displayed year is cleared at
              https://eogdata.mines.edu/products/vnf/global_gas_flare.html,
              (b) any temporal display is aggregated to weekly minimum,
              and (c) the data-attribution cell above is in place.
            - Cross-validate the synthetic-site clustering against
              ground-truth facility coordinates (the `sites_truth` list
              above) once VNF detections are real.

            ---

            *Source: VIIRS Nightfire, Colorado School of Mines.* (Applies
            once the synthetic VNF block above is replaced with real EOG
            data.)
        """),
    ]


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "notebooks"
    out_dir.mkdir(exist_ok=True)
    for slug, cfg in COUNTRIES.items():
        nb = {
            "cells": make_cells(slug, cfg),
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
        out = out_dir / f"{slug}.ipynb"
        out.write_text(json.dumps(nb, indent=1))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
