"""Render the iconic 'Africa glowing' poster centrepiece at 600 dpi.

Approach:

* Country outlines come from the public ``world.geo.json`` (Natural Earth
  derived, simplified). Cached to ``~/.cache/pyflare/world.geo.json`` on
  first run.
* All African countries are drawn in a low-key dark fill.
* The 17 oil/gas-producing nations supported by pyflare are highlighted
  with a slight warm tint.
* Synthetic flare-site dots from the four priority countries (Niger
  Delta + Angola + Algeria + Libya) are scattered with a layered alpha
  pass to fake a 'glow' effect.
* Output saved at 600 dpi, ≥ 3000 × 3000 px (gate G5 in
  ``scripts/verify.sh``).

Run from the repo root::

    python scripts/_build_iconic_africa_map.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

GEOJSON_URL = (
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
)
CACHE_FILE = Path.home() / ".cache" / "pyflare" / "world.geo.json"

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "assets" / "africa_overview_600dpi.png"

# Africa bounding box (matches pyflare.data.AFRICA_BBOX).
AFRICA_BBOX = (-25.0, -40.0, 60.0, 40.0)

# 17 supported African oil/gas-producing nations (match pyflare's
# AFRICAN_PRODUCERS_BBOX keys, but using Natural Earth ISO names where
# they differ).
PRODUCER_COUNTRIES_NE = {
    "Algeria", "Angola", "Cameroon", "Chad",
    "Republic of the Congo", "Democratic Republic of the Congo",
    "Egypt", "Equatorial Guinea", "Gabon", "Ghana",
    "Libya", "Mozambique", "Niger", "Nigeria",
    "South Sudan", "Sudan", "Tunisia",
}

# Approximate facility coordinates from the four priority country notebooks
# — kept in sync with scripts/_build_country_notebooks.py. The synthetic
# 'glow' uses a small radius of jitter around each anchor.
FACILITIES: list[tuple[str, float, float]] = [
    # Niger Delta
    ("Bonny LNG",  7.16, 4.41),
    ("Forcados",   5.36, 5.34),
    ("Brass",      6.24, 4.32),
    ("Escravos",   5.18, 5.65),
    ("Onne",       7.16, 4.71),
    ("Soku",       6.66, 4.38),
    # Angola
    ("Soyo LNG",          12.37, -6.13),
    ("Cabinda Onshore",   12.19, -5.55),
    ("Greater Plutonio",  12.00, -7.00),
    ("Pazflor / Dalia",   11.50, -6.80),
    ("Kizomba",           11.83, -7.95),
    ("Block 31 BBLT",     10.90, -7.35),
    # Algeria
    ("Hassi Messaoud",        6.07, 31.69),
    ("Hassi R'Mel",           3.27, 32.93),
    ("In Salah",              2.47, 27.20),
    ("Rhourde Nouss",         6.85, 31.20),
    ("Tin Fouye Tabankort",   8.55, 28.43),
    ("Berkine East",          8.50, 31.00),
    # Libya
    ("Es Sider Terminal",   18.65, 30.62),
    ("Ras Lanuf",           18.55, 30.50),
    ("Marsa el Brega LNG",  19.62, 30.41),
    ("Sahabi",              19.20, 28.80),
    ("Hofra",               19.20, 29.10),
    ("El Sharara (Murzuq)", 12.20, 27.81),
]

# Project palette.
COLOR_BG = "#0a0a0a"
COLOR_LAND_NEUTRAL = "#1c1c1c"
COLOR_LAND_PRODUCER = "#2a2018"
COLOR_BORDER = "#3a3a3a"
COLOR_FLARE_CORE = "#ffaa44"
COLOR_FLARE_HALO = "#ff5500"
COLOR_TITLE = "#f0e8d8"
COLOR_SUBTITLE = "#b8a890"


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def _load_world_geojson() -> dict:
    if not CACHE_FILE.exists():
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading world geometry from {GEOJSON_URL}")
        resp = requests.get(GEOJSON_URL, timeout=60)
        resp.raise_for_status()
        CACHE_FILE.write_bytes(resp.content)
    return json.loads(CACHE_FILE.read_text())


def _is_african(feature: dict) -> bool:
    """Heuristic: any geometry that overlaps the Africa bbox."""
    min_lon, min_lat, max_lon, max_lat = AFRICA_BBOX
    geom = feature["geometry"]
    geom_type = geom["type"]
    coords_list = (
        [geom["coordinates"]] if geom_type == "Polygon" else geom["coordinates"]
    )
    for poly in coords_list:
        # Outer ring is poly[0]; sample a few points to test bbox overlap.
        for lon, lat in poly[0][::10] or poly[0]:
            if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                return True
    return False


def _polygon_to_path(poly_coords: list) -> MplPath:
    """Convert one Polygon's coordinate list (outer + holes) to a matplotlib Path."""
    verts: list[tuple[float, float]] = []
    codes: list[int] = []
    for ring in poly_coords:
        ring = list(ring)
        if not ring:
            continue
        verts.extend(ring)
        codes.append(MplPath.MOVETO)
        codes.extend([MplPath.LINETO] * (len(ring) - 2))
        codes.append(MplPath.CLOSEPOLY)
    return MplPath(verts, codes)


def _feature_paths(feature: dict) -> list[MplPath]:
    """Return one matplotlib Path per Polygon in a Polygon/MultiPolygon feature."""
    geom = feature["geometry"]
    if geom["type"] == "Polygon":
        return [_polygon_to_path(geom["coordinates"])]
    if geom["type"] == "MultiPolygon":
        return [_polygon_to_path(poly) for poly in geom["coordinates"]]
    return []


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def render() -> Path:
    geojson = _load_world_geojson()

    fig = plt.figure(figsize=(6, 7), dpi=600, facecolor=COLOR_BG)
    ax = fig.add_axes([0.02, 0.05, 0.96, 0.86])
    ax.set_facecolor(COLOR_BG)

    african_features = [f for f in geojson["features"] if _is_african(f)]
    print(f"Rendering {len(african_features)} African countries")

    for feature in african_features:
        name = feature.get("properties", {}).get("name", "")
        is_producer = name in PRODUCER_COUNTRIES_NE
        face = COLOR_LAND_PRODUCER if is_producer else COLOR_LAND_NEUTRAL
        for path in _feature_paths(feature):
            ax.add_patch(
                PathPatch(
                    path,
                    facecolor=face,
                    edgecolor=COLOR_BORDER,
                    linewidth=0.4,
                    antialiased=True,
                )
            )

    # Synthetic flare points with a layered glow (cheap radial halo).
    rng = np.random.default_rng(42)
    lons = np.array([f[1] for f in FACILITIES]) + rng.normal(0, 0.05, size=len(FACILITIES))
    lats = np.array([f[2] for f in FACILITIES]) + rng.normal(0, 0.05, size=len(FACILITIES))

    for size, alpha, color in [
        (1500, 0.06, COLOR_FLARE_HALO),
        ( 700, 0.12, COLOR_FLARE_HALO),
        ( 300, 0.30, COLOR_FLARE_HALO),
        ( 110, 0.65, COLOR_FLARE_CORE),
        (  35, 1.00, "#ffe6c0"),
    ]:
        ax.scatter(lons, lats, s=size, c=color, alpha=alpha, edgecolors="none", zorder=10)

    # Frame.
    min_lon, min_lat, max_lon, max_lat = AFRICA_BBOX
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Title block.
    fig.text(
        0.5, 0.94,
        "African gas flaring, by satellite",
        ha="center", va="center",
        color=COLOR_TITLE, fontsize=20, fontweight="bold",
    )
    fig.text(
        0.5, 0.91,
        "Synthetic preview · pyflare v0.1 · GGFR 2024 · "
        f"{len(PRODUCER_COUNTRIES_NE)} producing nations",
        ha="center", va="center",
        color=COLOR_SUBTITLE, fontsize=10,
    )

    # Attribution footer (per VNF license §2.a — applicable when real VNF
    # data replaces the synthetic dots above).
    fig.text(
        0.5, 0.025,
        "Source: VIIRS Nightfire, Colorado School of Mines  ·  Boundaries: Natural Earth",
        ha="center", va="center",
        color=COLOR_SUBTITLE, fontsize=7,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=600, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"wrote {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    render()
