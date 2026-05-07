"""Render the African flaring time-lapse GIF (gate G7).

Five keyframes — 2012, 2015, 2018, 2021, 2024 — show how flaring volumes
in the four priority African producers (Nigeria, Angola, Algeria, Libya)
changed over the GGFR record. Each facility's glow brightness scales
with its country's GGFR-reported volume in that year, normalised against
the highest annual volume seen by any African producer in the dataset.

Run from the repo root::

    python scripts/_build_iconic_timelapse.py

Output: ``assets/africa_timelapse.gif`` (5 frames, ~1.5 s per frame).

This script duplicates a small amount of geometry-rendering machinery
from ``_build_iconic_africa_map.py``. The duplication is intentional in
v0.1; both scripts are one-off poster-asset generators and the shared
code is ~50 lines.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

GEOJSON_URL = (
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
)
CACHE_FILE = Path.home() / ".cache" / "pyflare" / "world.geo.json"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "assets" / "africa_timelapse.gif"

AFRICA_BBOX = (-25.0, -40.0, 60.0, 40.0)

# Match pyflare.data.AFRICAN_PRODUCERS_BBOX keys (canonical pyflare names).
PYFLARE_PRODUCERS = {
    "Algeria", "Angola", "Cameroon", "Chad", "Republic of Congo", "DR Congo",
    "Egypt", "Equatorial Guinea", "Gabon", "Ghana", "Libya", "Mozambique",
    "Niger", "Nigeria", "South Sudan", "Sudan", "Tunisia",
}

# Natural Earth's labels for the same set, for shading the basemap.
PRODUCER_COUNTRIES_NE = {
    "Algeria", "Angola", "Cameroon", "Chad",
    "Republic of the Congo", "Democratic Republic of the Congo",
    "Egypt", "Equatorial Guinea", "Gabon", "Ghana",
    "Libya", "Mozambique", "Niger", "Nigeria",
    "South Sudan", "Sudan", "Tunisia",
}

# Approximate facility coordinates by country — kept in sync with
# scripts/_build_country_notebooks.py and _build_iconic_africa_map.py.
FACILITIES_BY_COUNTRY: dict[str, list[tuple[str, float, float]]] = {
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

YEARS = [2012, 2015, 2018, 2021, 2024]
FRAME_DURATION_MS = 1500  # ~0.67 fps — readable but not glacial

# Project palette (matched to _build_iconic_africa_map.py).
COLOR_BG = "#0a0a0a"
COLOR_LAND_NEUTRAL = "#1c1c1c"
COLOR_LAND_PRODUCER = "#2a2018"
COLOR_BORDER = "#3a3a3a"
COLOR_FLARE_CORE = "#ffaa44"
COLOR_FLARE_HALO = "#ff5500"
COLOR_TITLE = "#f0e8d8"
COLOR_SUBTITLE = "#b8a890"
COLOR_YEAR = "#ffaa44"


# ---------------------------------------------------------------------------
# Geometry helpers (duplicated from _build_iconic_africa_map.py)
# ---------------------------------------------------------------------------


def _load_world_geojson() -> dict:
    if not CACHE_FILE.exists():
        import requests
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(GEOJSON_URL, timeout=60)
        resp.raise_for_status()
        CACHE_FILE.write_bytes(resp.content)
    return json.loads(CACHE_FILE.read_text())


def _is_african(feature: dict) -> bool:
    min_lon, min_lat, max_lon, max_lat = AFRICA_BBOX
    geom = feature["geometry"]
    geom_type = geom["type"]
    coords_list = (
        [geom["coordinates"]] if geom_type == "Polygon" else geom["coordinates"]
    )
    for poly in coords_list:
        for lon, lat in poly[0][::10] or poly[0]:
            if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                return True
    return False


def _polygon_to_path(poly_coords: list) -> MplPath:
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
    geom = feature["geometry"]
    if geom["type"] == "Polygon":
        return [_polygon_to_path(geom["coordinates"])]
    if geom["type"] == "MultiPolygon":
        return [_polygon_to_path(poly) for poly in geom["coordinates"]]
    return []


# ---------------------------------------------------------------------------
# Frame rendering
# ---------------------------------------------------------------------------


def _draw_basemap(ax, african_features) -> None:
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


def _draw_country_dots(
    ax,
    facilities: list[tuple[str, float, float]],
    intensity: float,
    *,
    rng: np.random.Generator,
    base_jitter: float = 0.05,
) -> None:
    """Render glow dots for one country, scaled by ``intensity`` in [0, 1]."""
    if not facilities or intensity <= 0.001:
        return
    lons = np.array([f[1] for f in facilities]) + rng.normal(0, base_jitter, size=len(facilities))
    lats = np.array([f[2] for f in facilities]) + rng.normal(0, base_jitter, size=len(facilities))

    # Layered glow — each layer's size and alpha scaled by intensity.
    layers = [
        (1500, 0.06, COLOR_FLARE_HALO),
        ( 700, 0.12, COLOR_FLARE_HALO),
        ( 300, 0.30, COLOR_FLARE_HALO),
        ( 110, 0.65, COLOR_FLARE_CORE),
        (  35, 1.00, "#ffe6c0"),
    ]
    for size, alpha, color in layers:
        ax.scatter(
            lons, lats,
            s=size * intensity,
            c=color,
            alpha=alpha * (0.3 + 0.7 * intensity),  # don't go fully invisible
            edgecolors="none",
            zorder=10,
        )


def _render_frame(
    year: int,
    *,
    african_features: list[dict],
    annual: "dict[tuple[str, int], float]",
    max_vol: float,
) -> Image.Image:
    """Return one PIL frame for the given year."""
    fig = plt.figure(figsize=(8, 9), dpi=150, facecolor=COLOR_BG)
    ax = fig.add_axes([0.02, 0.05, 0.96, 0.84])
    ax.set_facecolor(COLOR_BG)

    _draw_basemap(ax, african_features)

    rng = np.random.default_rng(42)  # deterministic jitter — frames align
    for country, facilities in FACILITIES_BY_COUNTRY.items():
        vol = annual.get((country, year), 0.0)
        intensity = vol / max_vol if max_vol > 0 else 0.0
        _draw_country_dots(ax, facilities, intensity, rng=rng)

    min_lon, min_lat, max_lon, max_lat = AFRICA_BBOX
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.5, 0.945,
        "African gas flaring, by satellite",
        ha="center", va="center",
        color=COLOR_TITLE, fontsize=18, fontweight="bold",
    )
    fig.text(
        0.5, 0.910,
        f"{year}",
        ha="center", va="center",
        color=COLOR_YEAR, fontsize=24, fontweight="bold",
    )
    fig.text(
        0.5, 0.025,
        "Source: VIIRS Nightfire, Colorado School of Mines  ·  Boundaries: Natural Earth",
        ha="center", va="center",
        color=COLOR_SUBTITLE, fontsize=7,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("P", palette=Image.Palette.ADAPTIVE, colors=128)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import pyflare as pf

    geojson = _load_world_geojson()
    african_features = [f for f in geojson["features"] if _is_african(f)]

    df = pf.fetch_ggfr_annual()
    df_african = df[df["country"].isin(PYFLARE_PRODUCERS)]
    annual = {
        (row["country"], int(row["year"])): float(row["bcm_flared"])
        for _, row in df_african.iterrows()
        if not (row["bcm_flared"] != row["bcm_flared"])  # skip NaNs
    }
    max_vol = float(df_african["bcm_flared"].max())
    print(f"African producer max volume: {max_vol:.2f} bcm")

    frames = []
    for year in YEARS:
        print(f"Rendering frame {year}...")
        frames.append(
            _render_frame(
                year,
                african_features=african_features,
                annual=annual,
                max_vol=max_vol,
            )
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
    )
    print(f"wrote {OUTPUT_PATH} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
