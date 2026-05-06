"""Visualization helpers for pyflare.

All functions in this module are *optional*: they require packages
installed via the ``pyflare[viz]`` extra (folium, matplotlib, geopandas).
Imports are lazy so the rest of pyflare can be used without them.

The flagship function in this module is :func:`africa_overview`, which
produces the "Africa is glowing" map intended as the headline visual for
posters and papers built on pyflare.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover
    import folium
    import matplotlib.figure


# ---------------------------------------------------------------------------
# Constants for visual identity
# ---------------------------------------------------------------------------

#: Color palette for pyflare visualizations. Deep night-sky blue with a
#: warm flare-orange accent. Used consistently across maps, plots, and
#: the project's documentation site.
PALETTE: dict[str, str] = {
    "background": "#0b1d3a",
    "land": "#1a2b4a",
    "flare": "#ff7a00",
    "flare_hot": "#ffd166",
    "ocean": "#06112a",
    "text": "#e8eef7",
    "muted": "#7a8aa6",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require_folium() -> Any:
    try:
        import folium
    except ImportError as exc:
        raise ImportError(
            "folium is required for map visualizations. "
            "Install with: pip install 'pyflare[viz]'"
        ) from exc
    return folium


def _require_matplotlib() -> Any:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for plot visualizations. "
            "Install with: pip install 'pyflare[viz]'"
        ) from exc
    return plt


# ---------------------------------------------------------------------------
# Public API — Maps
# ---------------------------------------------------------------------------


def flare_map(
    df: pd.DataFrame,
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
    rh_col: str | None = "radiant_heat_mw",
    label_col: str | None = None,
    center: tuple[float, float] | None = None,
    zoom_start: int = 5,
    tiles: str = "CartoDB dark_matter",
) -> "folium.Map":
    """Plot detections on a Folium map with radiant-heat sized markers.

    Parameters
    ----------
    df
        Detection frame.
    rh_col
        If supplied, marker radius scales with this column.
    label_col
        If supplied, used for marker tooltips.
    center
        (lat, lon) center of the map. Defaults to the centroid of ``df``.

    Returns
    -------
    folium.Map
        Interactive Folium map. Render in a notebook or save with
        ``m.save("flares.html")``.
    """
    folium = _require_folium()

    if center is None:
        center = (df[lat_col].mean(), df[lon_col].mean())

    m = folium.Map(location=center, zoom_start=zoom_start, tiles=tiles)

    # Determine marker sizing
    if rh_col and rh_col in df.columns:
        rh = df[rh_col].fillna(0)
        rh_max = max(rh.max(), 1)
        radii = 3 + 12 * (rh / rh_max)
    else:
        radii = pd.Series([5] * len(df), index=df.index)

    for idx, row in df.iterrows():
        tooltip = str(row[label_col]) if label_col and label_col in df.columns else None
        folium.CircleMarker(
            location=(row[lat_col], row[lon_col]),
            radius=float(radii.loc[idx]),
            color=PALETTE["flare"],
            fill=True,
            fill_color=PALETTE["flare_hot"],
            fill_opacity=0.7,
            weight=1,
            tooltip=tooltip,
        ).add_to(m)

    return m


def africa_overview(
    df: pd.DataFrame,
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
    rh_col: str | None = "radiant_heat_mw",
) -> "folium.Map":
    """The headline "Africa is glowing" visualization.

    Returns a continent-scoped dark-tile Folium map of all detections
    with radiant-heat sized markers, intended as the centerpiece visual
    for posters, papers, and dashboards built on pyflare.

    The visual is opinionated: dark-matter base tiles, the project flare
    palette, no marker labels (for a clean overview), continent zoom.
    For interactive exploration, use :func:`flare_map` with custom
    parameters.
    """
    return flare_map(
        df,
        lon_col=lon_col,
        lat_col=lat_col,
        rh_col=rh_col,
        center=(2.0, 20.0),
        zoom_start=3,
        tiles="CartoDB dark_matter",
    )


# ---------------------------------------------------------------------------
# Public API — Plots
# ---------------------------------------------------------------------------


def country_trend(
    annual_df: pd.DataFrame,
    countries: list[str] | None = None,
    *,
    country_col: str = "country",
    year_col: str = "year",
    value_col: str = "bcm_flared",
    title: str | None = None,
) -> "matplotlib.figure.Figure":
    """Plot annual flared-volume trends for one or more countries.

    Designed for use with :func:`pyflare.fetch_ggfr_annual` output but
    works with any tidy frame keyed on country and year.

    Parameters
    ----------
    annual_df
        Tidy long frame with columns for country, year, and value.
    countries
        Subset to plot. If None, plots all countries in ``annual_df``.
    title
        Plot title. Defaults to a sensible string.
    """
    plt = _require_matplotlib()

    sub = annual_df.copy()
    if countries:
        sub = sub[sub[country_col].isin(countries)]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=PALETTE["background"])
    ax.set_facecolor(PALETTE["background"])

    for country, group in sub.groupby(country_col):
        group = group.sort_values(year_col)
        ax.plot(
            group[year_col],
            group[value_col],
            marker="o",
            linewidth=2,
            label=country,
        )

    ax.set_xlabel("Year", color=PALETTE["text"])
    ax.set_ylabel(f"{value_col} (bcm)", color=PALETTE["text"])
    ax.set_title(
        title or "Annual flared volume",
        color=PALETTE["text"],
        fontsize=14,
        fontweight="bold",
    )
    ax.tick_params(colors=PALETTE["muted"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["muted"])
    legend = ax.legend(
        facecolor=PALETTE["background"],
        edgecolor=PALETTE["muted"],
        labelcolor=PALETTE["text"],
        loc="best",
    )
    if legend:
        legend.get_frame().set_alpha(0.8)
    ax.grid(alpha=0.15, color=PALETTE["muted"])

    fig.tight_layout()
    return fig


def country_comparison(
    annual_df: pd.DataFrame,
    *,
    year: int | None = None,
    top_n: int = 10,
    country_col: str = "country",
    year_col: str = "year",
    value_col: str = "bcm_flared",
) -> "matplotlib.figure.Figure":
    """Horizontal bar chart of top-N countries by flared volume.

    By default plots the most recent year present in ``annual_df``.
    """
    plt = _require_matplotlib()

    if year is None:
        year = int(annual_df[year_col].dropna().max())
    sub = (
        annual_df[annual_df[year_col] == year]
        .nlargest(top_n, value_col)
        .sort_values(value_col)
    )

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=PALETTE["background"])
    ax.set_facecolor(PALETTE["background"])
    ax.barh(sub[country_col], sub[value_col], color=PALETTE["flare"])

    ax.set_xlabel(f"{value_col} (bcm)", color=PALETTE["text"])
    ax.set_title(
        f"Top {top_n} flaring countries — {year}",
        color=PALETTE["text"],
        fontsize=14,
        fontweight="bold",
    )
    ax.tick_params(colors=PALETTE["text"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["muted"])
    ax.grid(axis="x", alpha=0.15, color=PALETTE["muted"])

    fig.tight_layout()
    return fig
