"""Streamlit dashboard MVP for pyflare.

Run locally with::

    pip install 'pyflare-africa[dashboard]'
    streamlit run src/pyflare/dashboard.py
    # or, in a checkout:
    #   python -m streamlit run src/pyflare/dashboard.py

This MVP uses the public World Bank GFMR dataset (no credentials) and
the curated `KNOWN_AFRICAN_SETTLEMENTS` reference. Real VNF integration
is intentionally absent: per the VNF Academic Data Use License §1.f.iii,
public deployment of an interactive service exposing VNF data requires
prior written EOG approval. This file is the local-only foundation; a
public deployment to ``flarewatch.africa`` will follow once that approval
is in hand. See ``LICENSING_NOTES.md`` for the full constraint set.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

import pyflare as pf
from pyflare.analysis import communities_near_sites, volume_to_co2eq
from pyflare.data import AFRICAN_PRODUCERS_BBOX


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="pyflare — African gas flaring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ICONIC_MAP = REPO_ROOT / "assets" / "africa_overview_600dpi.png"
TIMELAPSE_GIF = REPO_ROOT / "assets" / "africa_timelapse.gif"


# ---------------------------------------------------------------------------
# Custom CSS — gradient cards, oversized headline numbers, tight typography
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
/* Hero card — for the continent-wide CO2e headline */
.pyflare-hero {
    background: linear-gradient(135deg, #1a0500 0%, #2a1505 45%, #4a2510 100%);
    padding: 3.5rem 2rem;
    border-radius: 1rem;
    border: 1px solid #3a2515;
    text-align: center;
    margin: 1.5rem 0 2rem 0;
    box-shadow: 0 0 60px rgba(212, 69, 0, 0.15);
}
.pyflare-hero-eyebrow {
    color: #b8a890;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin-bottom: 0.75rem;
}
.pyflare-hero-number {
    font-size: 7.5rem;
    font-weight: 800;
    color: #ffaa44;
    line-height: 1;
    text-shadow: 0 0 40px rgba(255, 90, 0, 0.55);
    letter-spacing: -0.03em;
}
.pyflare-hero-unit {
    font-size: 1.6rem;
    color: #f0e8d8;
    margin-top: 0.5rem;
    font-weight: 500;
}
.pyflare-hero-detail {
    color: #c8b8a0;
    margin-top: 1rem;
    font-size: 0.95rem;
    max-width: 640px;
    margin-left: auto;
    margin-right: auto;
}

/* Smaller metric card for country drill-down */
.pyflare-card {
    background: #1a1208;
    padding: 1.75rem 1.5rem;
    border-radius: 0.75rem;
    border: 1px solid #3a2515;
    height: 100%;
}
.pyflare-card-eyebrow {
    color: #b8a890;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
.pyflare-card-number {
    font-size: 3.75rem;
    font-weight: 700;
    color: #ffaa44;
    line-height: 1;
    margin: 0.5rem 0;
    letter-spacing: -0.02em;
}
.pyflare-card-unit {
    color: #f0e8d8;
    font-size: 1rem;
    font-weight: 500;
}
.pyflare-card-detail {
    color: #b8a890;
    font-size: 0.85rem;
    margin-top: 0.6rem;
}

/* Section label */
.pyflare-section {
    color: #ffaa44;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.85rem;
    margin: 2.5rem 0 0.5rem 0;
    border-top: 1px solid #2a2018;
    padding-top: 1.5rem;
}

/* Tighten Streamlit's default block spacing */
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Cached data loaders
# ---------------------------------------------------------------------------


@st.cache_data(ttl=24 * 3600, show_spinner="Loading GFMR data…")
def load_gfmr() -> pd.DataFrame:
    return pf.fetch_gfmr_annual()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("pyflare")
st.sidebar.caption(f"v{pf.__version__} · open-source Python toolkit")
st.sidebar.markdown(
    "Satellite-based gas flaring analytics for African oil-producing nations. "
    "[GitHub](https://github.com/Jayyp1234/pyflare) · "
    "[Docs](https://pyflare.readthedocs.io)"
)

st.sidebar.divider()
st.sidebar.subheader("Drill down")

producers: list[str] = sorted(AFRICAN_PRODUCERS_BBOX.keys())
default_country = "Nigeria" if "Nigeria" in producers else producers[0]
country = st.sidebar.selectbox(
    "Country",
    producers,
    index=producers.index(default_country),
)

slip_pct = st.sidebar.slider(
    "Methane slip (%)",
    min_value=0.0,
    max_value=10.0,
    value=5.0,
    step=0.5,
    help=(
        "IPCC AR6 default = 2 %. Plant et al. 2022 satellite-derived basin "
        "estimates centre on 5 %, reach 9 %."
    ),
)
slip = slip_pct / 100.0

st.sidebar.divider()
st.sidebar.caption(
    "**Source:** VIIRS Nightfire, Colorado School of Mines · "
    "**Boundaries:** Natural Earth · "
    "**Volumes:** World Bank GFMR 2025 release."
)


# ---------------------------------------------------------------------------
# Hero — iconic map
# ---------------------------------------------------------------------------

if ICONIC_MAP.exists():
    st.image(str(ICONIC_MAP), use_container_width=True)
else:
    st.warning(
        f"Iconic map not found at `{ICONIC_MAP}`. "
        "Run `python scripts/_build_iconic_africa_map.py` to regenerate."
    )


# ---------------------------------------------------------------------------
# Continent-wide headline
# ---------------------------------------------------------------------------

annual = load_gfmr()
latest_year = int(annual["year"].max())
african = annual[(annual["country"].isin(producers)) & (annual["year"] == latest_year)]
african = african.dropna(subset=["bcm_flared"])
continent_bcm = float(african["bcm_flared"].sum())
continent_co2e = volume_to_co2eq(continent_bcm, slip)
n_active = int((african["bcm_flared"] > 0.05).sum())

st.markdown(
    f"""
<div class="pyflare-hero">
  <div class="pyflare-hero-eyebrow">African gas flaring &middot; {latest_year}</div>
  <div class="pyflare-hero-number">{continent_co2e:.0f}</div>
  <div class="pyflare-hero-unit">megatonnes CO₂-equivalent per year</div>
  <div class="pyflare-hero-detail">
    {continent_bcm:.1f} bcm of gas flared across {n_active} African producers in {latest_year}
    &middot; methane slip = {slip_pct:.1f}% &middot; drag the slider to test the assumption.
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Country drill-down
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="pyflare-section">{country} &middot; annual flaring trend</div>',
    unsafe_allow_html=True,
)

country_df = annual[annual["country"] == country].sort_values("year")
country_df = country_df.dropna(subset=["bcm_flared"])

if country_df.empty:
    st.info(
        f"No GFMR rows for **{country}** in the loaded dataset. "
        "The World Bank may not yet publish flared volumes for every supported producer."
    )
else:
    latest = country_df[country_df["year"] == latest_year]
    latest_bcm = float(latest["bcm_flared"].iloc[0]) if not latest.empty else float("nan")
    country_co2e = volume_to_co2eq(latest_bcm, slip) if not latest.empty else float("nan")

    chart_col, metric_col = st.columns([2, 1], gap="large")

    with chart_col:
        trend = country_df.set_index("year")["bcm_flared"]
        st.line_chart(trend, height=320, color="#d44500")

    with metric_col:
        if not latest.empty:
            st.markdown(
                f"""
<div class="pyflare-card">
  <div class="pyflare-card-eyebrow">{country} &middot; {latest_year}</div>
  <div class="pyflare-card-number">{country_co2e:.1f}</div>
  <div class="pyflare-card-unit">MtCO₂e per year</div>
  <div class="pyflare-card-detail">{latest_bcm:.2f} bcm flared (GFMR-published) &middot; slip {slip_pct:.1f}%</div>
</div>
""",
                unsafe_allow_html=True,
            )

    if not latest.empty:
        st.markdown(
            f'<div class="pyflare-section">{country} {latest_year} &middot; CO₂e across published slip assumptions</div>',
            unsafe_allow_html=True,
        )
        scenarios = [
            (0.02, "IPCC AR6 default"),
            (0.05, "pyflare default / Plant et al. 2022 mid"),
            (0.09, "Plant et al. 2022 upper bound"),
        ]
        scen_df = pd.DataFrame(
            {
                "slip": [f"{s*100:.0f}%" for s, _ in scenarios],
                "source": [label for _, label in scenarios],
                "MtCO₂e / year": [
                    round(volume_to_co2eq(latest_bcm, s), 2) for s, _ in scenarios
                ],
            }
        )
        st.dataframe(scen_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Top-5 producers
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="pyflare-section">Top African producers &middot; {latest_year}</div>',
    unsafe_allow_html=True,
)

top5 = (
    annual[(annual["country"].isin(producers)) & (annual["year"] == latest_year)]
    .nlargest(5, "bcm_flared")
    .set_index("country")["bcm_flared"]
)
st.bar_chart(top5, height=280, color="#d44500")


# ---------------------------------------------------------------------------
# Communities exposure
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="pyflare-section">{country} &middot; communities near major flare facilities</div>',
    unsafe_allow_html=True,
)

PRIORITY_SITES: dict[str, list[tuple[str, float, float]]] = {
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
    ],
    "Algeria": [
        ("Hassi Messaoud",        6.07, 31.69),
        ("Hassi R'Mel",           3.27, 32.93),
        ("In Salah",              2.47, 27.20),
    ],
    "Libya": [
        ("Es Sider Terminal",   18.65, 30.62),
        ("Ras Lanuf",           18.55, 30.50),
        ("Marsa el Brega LNG",  19.62, 30.41),
    ],
}

facilities = PRIORITY_SITES.get(country)
if facilities:
    radius_km = st.slider("Exposure radius (km)", min_value=2, max_value=50, value=10)
    sites_df = pd.DataFrame(
        [(i, name, lon, lat) for i, (name, lon, lat) in enumerate(facilities)],
        columns=["site_id", "facility", "longitude", "latitude"],
    )
    expo = communities_near_sites(sites_df, radius_km=float(radius_km))
    expo = expo.merge(sites_df[["site_id", "facility"]], on="site_id")
    total_exposed = int(expo["population_exposed"].sum())

    expo_col, metric_col = st.columns([2, 1], gap="large")

    with expo_col:
        st.dataframe(
            expo[
                [
                    "facility",
                    "n_communities_within_radius",
                    "population_exposed",
                    "nearest_community",
                    "nearest_distance_km",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    with metric_col:
        st.markdown(
            f"""
<div class="pyflare-card">
  <div class="pyflare-card-eyebrow">Within {radius_km} km &middot; {country}</div>
  <div class="pyflare-card-number">{total_exposed:,}</div>
  <div class="pyflare-card-unit">people exposed</div>
  <div class="pyflare-card-detail">curated settlement reference &middot; v0.2 will swap to WorldPop for full coverage</div>
</div>
""",
            unsafe_allow_html=True,
        )
else:
    st.info(
        f"Pyflare's curated facility list doesn't yet cover **{country}**. "
        "Country maintainers wanted — see "
        "[CONTRIBUTING.md](https://github.com/Jayyp1234/pyflare/blob/main/CONTRIBUTING.md#adopt-a-country)."
    )


# ---------------------------------------------------------------------------
# Timelapse
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="pyflare-section">How African flaring shifted &middot; 2012 → 2024</div>',
    unsafe_allow_html=True,
)

if TIMELAPSE_GIF.exists():
    st.image(str(TIMELAPSE_GIF), use_container_width=True)
else:
    st.warning(
        f"Timelapse GIF not found at `{TIMELAPSE_GIF}`. "
        "Run `python scripts/_build_iconic_timelapse.py` to regenerate."
    )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption(
    "This dashboard is a local-only MVP. A public deployment requires prior written EOG "
    "approval per VNF Academic Data Use License §1.f.iii — see "
    "[`LICENSING_NOTES.md`](https://github.com/Jayyp1234/pyflare/blob/main/LICENSING_NOTES.md)."
)
st.caption(
    "Source: VIIRS Nightfire, Colorado School of Mines  ·  "
    "Boundaries: Natural Earth  ·  "
    "Annual volumes: World Bank Global Flaring and Methane Reduction "
    "Partnership (GFMR)."
)
