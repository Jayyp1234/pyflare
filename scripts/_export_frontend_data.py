"""Export pyflare-derived JSON for the Next.js frontend.

The frontend at ``frontend/`` is fully static: all data is resolved at
build time, so the only runtime dependency is the user's browser. This
script runs pyflare against the live GFMR dataset, computes derived
exposure tables for the four priority countries, and writes JSON files
under ``frontend/lib/data/`` plus a few static assets the frontend reads
from ``frontend/public/``.

Re-run whenever GFMR publishes a new annual release, or whenever pyflare's
facility / settlement reference is updated::

    python scripts/_export_frontend_data.py

Outputs:

  frontend/lib/data/ggfr.json        — per-country annual flared volume
  frontend/lib/data/countries.json   — pyflare producer metadata + top-5
  frontend/lib/data/exposure.json    — per-priority-country exposure
  frontend/public/africa-overview.png    — symlink/copy of iconic map
  frontend/public/africa-timelapse.gif   — symlink/copy of timelapse
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

import pyflare as pf
from pyflare.analysis import communities_near_sites
from pyflare.data import AFRICAN_PRODUCERS_BBOX


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DATA = REPO_ROOT / "frontend" / "lib" / "data"
FRONTEND_PUBLIC = REPO_ROOT / "frontend" / "public"
ASSETS = REPO_ROOT / "assets"


# Priority countries get a per-facility exposure breakdown; others just
# show the GFMR trend.
PRIORITY_COUNTRIES: dict[str, list[tuple[str, float, float]]] = {
    "Nigeria": [
        ("Bonny LNG",  7.16, 4.41),
        ("Forcados",   5.36, 5.34),
        ("Brass",      6.24, 4.32),
        ("Escravos",   5.18, 5.65),
        ("Onne",       7.16, 4.71),
        ("Soku",       6.66, 4.38),
    ],
    "Angola": [
        ("Soyo LNG",          12.37, -6.13),
        ("Cabinda Onshore",   12.19, -5.55),
        ("Greater Plutonio",  12.00, -7.00),
        ("Pazflor / Dalia",   11.50, -6.80),
        ("Kizomba",           11.83, -7.95),
        ("Block 31 BBLT",     10.90, -7.35),
    ],
    "Algeria": [
        ("Hassi Messaoud",        6.07, 31.69),
        ("Hassi R'Mel",           3.27, 32.93),
        ("In Salah",              2.47, 27.20),
        ("Rhourde Nouss",         6.85, 31.20),
        ("Tin Fouye Tabankort",   8.55, 28.43),
        ("Berkine East",          8.50, 31.00),
    ],
    "Libya": [
        ("Es Sider Terminal",   18.65, 30.62),
        ("Ras Lanuf",           18.55, 30.50),
        ("Marsa el Brega LNG",  19.62, 30.41),
        ("Sahabi",              19.20, 28.80),
        ("Hofra",               19.20, 29.10),
        ("El Sharara (Murzuq)", 12.20, 27.81),
    ],
}

# Country narrative hooks, copied from the country-notebook builder.
NARRATIVE: dict[str, str] = {
    "Nigeria": (
        "Nigerian flaring is concentrated in the Niger Delta, where the "
        "proximity of flare stacks to coastal communities makes the climate "
        "impact compound with a public-health one."
    ),
    "Angola": (
        "Angolan flaring is dominated by deepwater offshore production. "
        "Most facilities are tens of km off the Atlantic coast — a different "
        "ground-truth landscape than Nigeria's onshore Delta."
    ),
    "Algeria": (
        "Algerian flaring is desert-basin gas: Hassi Messaoud, Hassi R'Mel, "
        "In Salah. Africa's largest 2024 flarer (7.88 bcm), narrowly ahead of "
        "Nigeria."
    ),
    "Libya": (
        "Libyan flaring is split between the Sirte basin and coastal export "
        "terminals. Despite political instability, Libya ranks just behind "
        "Nigeria in 2024 (6.28 bcm)."
    ),
}


# ---------------------------------------------------------------------------
# Build payloads
# ---------------------------------------------------------------------------


def _build_ggfr_payload(annual: pd.DataFrame, producers: list[str]) -> dict:
    """Per-country annual flared-volume series."""
    african = annual[annual["country"].isin(producers)].dropna(subset=["bcm_flared"])
    series_by_country: list[dict] = []
    for country in producers:
        country_df = african[african["country"] == country].sort_values("year")
        if country_df.empty:
            continue
        series_by_country.append({
            "country": country,
            "series": [
                {"year": int(row["year"]), "bcm": round(float(row["bcm_flared"]), 4)}
                for _, row in country_df.iterrows()
            ],
        })

    latest_year = int(african["year"].max())
    latest = african[african["year"] == latest_year].sort_values("bcm_flared", ascending=False)
    top5 = [
        {"country": row["country"], "bcm": round(float(row["bcm_flared"]), 4)}
        for _, row in latest.head(5).iterrows()
    ]
    continent_total = round(float(latest["bcm_flared"].sum()), 3)

    return {
        "latest_year": latest_year,
        "continent_total_bcm_latest": continent_total,
        "top5_latest": top5,
        "by_country": series_by_country,
    }


def _build_countries_payload(producers: list[str]) -> list[dict]:
    """Static metadata per supported producer."""
    out: list[dict] = []
    for country in producers:
        bbox = AFRICAN_PRODUCERS_BBOX[country]
        out.append({
            "country": country,
            "slug": country.lower().replace(" ", "-").replace("'", ""),
            "bbox": list(bbox),
            "centroid": [
                round((bbox[0] + bbox[2]) / 2, 3),
                round((bbox[1] + bbox[3]) / 2, 3),
            ],
            "narrative": NARRATIVE.get(country),
            "is_priority": country in PRIORITY_COUNTRIES,
            "facility_count": len(PRIORITY_COUNTRIES.get(country, [])),
        })
    return out


def _build_exposure_payload() -> dict:
    """Per-priority-country exposure across radii."""
    out: dict[str, dict] = {}
    for country, facilities in PRIORITY_COUNTRIES.items():
        sites_df = pd.DataFrame(
            [(i, name, lon, lat) for i, (name, lon, lat) in enumerate(facilities)],
            columns=["site_id", "facility", "longitude", "latitude"],
        )

        per_radius: dict[str, dict] = {}
        for radius in (5, 10, 25, 50):
            expo = communities_near_sites(sites_df, radius_km=float(radius))
            expo_full = expo.merge(
                sites_df[["site_id", "facility", "longitude", "latitude"]],
                on="site_id",
            )
            per_radius[str(radius)] = {
                "total_population_exposed": int(expo_full["population_exposed"].sum()),
                "by_facility": [
                    {
                        "facility": row["facility"],
                        "longitude": round(float(row["longitude"]), 4),
                        "latitude": round(float(row["latitude"]), 4),
                        "n_communities": int(row["n_communities_within_radius"]),
                        "population_exposed": int(row["population_exposed"]),
                        "nearest_community": row["nearest_community"] or None,
                        "nearest_distance_km": (
                            round(float(row["nearest_distance_km"]), 2)
                            if pd.notna(row["nearest_distance_km"])
                            else None
                        ),
                    }
                    for _, row in expo_full.iterrows()
                ],
            }

        out[country] = {
            "facilities": [
                {"name": name, "longitude": lon, "latitude": lat}
                for name, lon, lat in facilities
            ],
            "exposure_by_radius_km": per_radius,
        }
    return out


# ---------------------------------------------------------------------------
# Static asset copy
# ---------------------------------------------------------------------------


def _copy_static_assets() -> None:
    FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in [
        ("africa_overview_600dpi.png", "africa-overview.png"),
        ("africa_timelapse.gif", "africa-timelapse.gif"),
    ]:
        src = ASSETS / src_name
        dst = FRONTEND_PUBLIC / dst_name
        if not src.exists():
            print(f"  WARN: {src} missing — skipping copy")
            continue
        shutil.copy2(src, dst)
        print(f"  copied {src.name} → {dst.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    FRONTEND_DATA.mkdir(parents=True, exist_ok=True)

    print("Loading GFMR data…")
    annual = pf.fetch_gfmr_annual()
    producers = sorted(AFRICAN_PRODUCERS_BBOX.keys())

    print("Building ggfr.json…")
    ggfr_payload = _build_ggfr_payload(annual, producers)
    (FRONTEND_DATA / "ggfr.json").write_text(json.dumps(ggfr_payload, indent=2))
    print(f"  → {FRONTEND_DATA / 'ggfr.json'}")
    print(f"  latest year: {ggfr_payload['latest_year']}")
    print(f"  continent total: {ggfr_payload['continent_total_bcm_latest']:.2f} bcm")
    print(f"  top5: {[r['country'] for r in ggfr_payload['top5_latest']]}")

    print("Building countries.json…")
    countries = _build_countries_payload(producers)
    (FRONTEND_DATA / "countries.json").write_text(json.dumps(countries, indent=2))
    print(f"  → {len(countries)} producers, {sum(c['is_priority'] for c in countries)} priority")

    print("Building exposure.json…")
    exposure = _build_exposure_payload()
    (FRONTEND_DATA / "exposure.json").write_text(json.dumps(exposure, indent=2))
    for country, data in exposure.items():
        for radius, payload in data["exposure_by_radius_km"].items():
            print(f"  {country:8} @ {radius:>2} km: {payload['total_population_exposed']:>10,} people")

    print("Copying static assets…")
    _copy_static_assets()

    print("Done. Re-run after GFMR or pyflare facility updates.")


if __name__ == "__main__":
    main()
