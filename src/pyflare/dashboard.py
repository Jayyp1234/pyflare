"""Streamlit dashboard MVP for pyflare.

Run locally with::

    pip install 'pyflare-africa[dashboard]'
    streamlit run -m pyflare.dashboard
    # or:  python -m streamlit run src/pyflare/dashboard.py

This MVP uses the public World Bank GGFR dataset (no credentials) and
the curated `KNOWN_AFRICAN_SETTLEMENTS` reference. Real VNF integration
is intentionally absent: per the VNF Academic Data Use License §1.f.iii,
public deployment of an interactive service exposing VNF data requires
prior written EOG approval. This file is the local-only foundation; a
public deployment to ``flarewatch.africa`` will follow once that approval
is in hand. See ``LICENSING_NOTES.md`` for the full constraint set.
"""

from __future__ import annotations

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
)

PROJECT_ORANGE = "#d44500"


# ---------------------------------------------------------------------------
# Cached data loaders
# ---------------------------------------------------------------------------


@st.cache_data(ttl=24 * 3600, show_spinner="Loading GGFR data…")
def load_ggfr() -> pd.DataFrame:
    """Pull the World Bank GGFR XLSX once per day (cached on disk)."""
    return pf.fetch_ggfr_annual()


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

st.sidebar.title("pyflare")
st.sidebar.markdown(
    "Open-source toolkit for satellite-based gas flaring analytics across "
    "**African oil-producing nations**."
)
st.sidebar.markdown(f"Version `{pf.__version__}`")

st.sidebar.header("Filters")

producers: list[str] = sorted(AFRICAN_PRODUCERS_BBOX.keys())
default_country = "Nigeria" if "Nigeria" in producers else producers[0]
country = st.sidebar.selectbox(
    "Country",
    producers,
    index=producers.index(default_country),
)

slip_pct = st.sidebar.slider(
    "Methane slip assumption (%)",
    min_value=0.0,
    max_value=10.0,
    value=5.0,
    step=0.5,
    help=(
        "IPCC AR6 default is 2 %. Plant et al. 2022 satellite-derived basin "
        "estimates centre around 5 % and reach 9 %."
    ),
)
slip = slip_pct / 100.0

st.sidebar.divider()
st.sidebar.markdown(
    "**Source:** VIIRS Nightfire, Colorado School of Mines · "
    "**Boundaries:** Natural Earth · **Annual volumes:** World Bank GGFR (2025 release)."
)


# ---------------------------------------------------------------------------
# Main column layout
# ---------------------------------------------------------------------------

st.title("African gas flaring — by satellite")
st.caption(
    "Synthetic preview — replace per-flare detection sources with real "
    "VNF data once your EOG license + Client ID are in place."
)

annual = load_ggfr()
country_df = annual[annual["country"] == country].sort_values("year")

if country_df.empty:
    st.warning(
        f"No GGFR rows for **{country}** in the loaded dataset. "
        f"Pyflare currently supports {len(producers)} producers; the "
        f"World Bank may not yet publish flared volumes for every one."
    )
    st.stop()


# --- Headline metrics ------------------------------------------------------

latest_row = country_df.iloc[-1]
latest_year = int(latest_row["year"])
latest_bcm = float(latest_row["bcm_flared"])
co2eq_mt = volume_to_co2eq(latest_bcm, slip)

m1, m2, m3 = st.columns(3)
m1.metric(
    f"Flared volume, {latest_year}",
    f"{latest_bcm:.2f} bcm",
    help="World Bank GGFR-published annual flared volume.",
)
m2.metric(
    "CO₂-equivalent (this slip)",
    f"{co2eq_mt:.1f} MtCO₂e",
    help=(
        f"Computed by `volume_to_co2eq({latest_bcm:.2f}, {slip:.3f})` — "
        "combustion factor 2.55 kg CO₂/m³ (IPCC 2006), GWP-100 fossil "
        "methane 29.8 (IPCC AR6)."
    ),
)
m3.metric(
    "Slip assumption",
    f"{slip_pct:.1f} %",
)


# --- Annual trend ---------------------------------------------------------

st.subheader(f"Annual flaring trend — {country}")
trend_view = country_df.set_index("year")["bcm_flared"].rename("bcm flared")
st.line_chart(trend_view, height=280, color=PROJECT_ORANGE)


# --- Top-5 producer comparison --------------------------------------------

st.subheader(f"Top African producers, {latest_year}")
top5 = (
    annual[(annual["country"].isin(producers)) & (annual["year"] == latest_year)]
    .nlargest(5, "bcm_flared")
    .set_index("country")["bcm_flared"]
)
st.bar_chart(top5, height=280, color=PROJECT_ORANGE)


# --- Per-slip CO₂-equivalent table ----------------------------------------

st.subheader(f"CO₂-equivalent across published slip assumptions — {country} {latest_year}")
scenarios = [
    (0.02, "IPCC AR6 default"),
    (0.05, "pyflare default / Plant et al. 2022 mid"),
    (0.09, "Plant et al. 2022 upper bound"),
]
scenario_df = pd.DataFrame(
    {
        "slip": [s for s, _ in scenarios],
        "source": [label for _, label in scenarios],
        "MtCO₂e": [round(volume_to_co2eq(latest_bcm, s), 2) for s, _ in scenarios],
    }
)
st.dataframe(scenario_df, use_container_width=True, hide_index=True)


# --- Communities near priority facilities ---------------------------------

st.subheader(f"Communities near major flare sites — {country}")

# Lightweight per-country facility lookup. Keep in sync with
# scripts/_build_country_notebooks.py and _build_iconic_africa_map.py.
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
    radius_km = st.slider(
        "Exposure radius (km)", min_value=2, max_value=50, value=10,
    )
    sites_df = pd.DataFrame(
        [(i, name, lon, lat) for i, (name, lon, lat) in enumerate(facilities)],
        columns=["site_id", "facility", "longitude", "latitude"],
    )
    expo = communities_near_sites(sites_df, radius_km=float(radius_km))
    expo = expo.merge(sites_df[["site_id", "facility"]], on="site_id")
    expo_view = expo[
        ["facility", "n_communities_within_radius", "population_exposed",
         "nearest_community", "nearest_distance_km"]
    ]
    st.dataframe(expo_view, use_container_width=True, hide_index=True)
    total_exposed = int(expo["population_exposed"].sum())
    st.markdown(
        f"**{total_exposed:,} people** within {radius_km} km of a major "
        f"flare facility in {country} (synthetic facility list, curated "
        "settlement reference — see `LICENSING_NOTES.md`)."
    )
else:
    st.info(
        f"Pyflare's curated facility list doesn't yet cover {country}. "
        "Country maintainers wanted — see CONTRIBUTING.md "
        "([Adopt-a-Country](https://github.com/Jayyp1234/pyflare#contributing))."
    )


# --- Footer attribution ----------------------------------------------------

st.divider()
st.caption(
    "This dashboard is a local-only MVP. A public deployment requires "
    "prior written EOG approval per VNF Academic Data Use License "
    "§1.f.iii — see "
    "[`LICENSING_NOTES.md`](https://github.com/Jayyp1234/pyflare/blob/main/LICENSING_NOTES.md)."
)
st.caption(
    "Source: VIIRS Nightfire, Colorado School of Mines  ·  "
    "Boundaries: Natural Earth  ·  "
    "Annual volumes: World Bank Global Gas Flaring Reduction Partnership."
)
