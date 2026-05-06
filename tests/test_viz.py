"""Smoke tests for pyflare.viz.

These tests are gated on the presence of the ``pyflare[viz]`` extras
(folium, matplotlib). When the extras are not installed, the tests are
skipped rather than failing — keeping CI green for users who only need
the core data layer.
"""

from __future__ import annotations

import pandas as pd
import pytest

from pyflare.viz import (
    PALETTE,
    africa_overview,
    country_comparison,
    country_trend,
    flare_map,
)

folium = pytest.importorskip("folium")
matplotlib = pytest.importorskip("matplotlib")


@pytest.fixture()
def detections() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "longitude": [6.5, 6.6, 12.0],
            "latitude":  [5.5, 5.4, -8.0],
            "radiant_heat_mw": [50.0, 55.0, 30.0],
        }
    )


@pytest.fixture()
def annual() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "country": ["Nigeria", "Nigeria", "Angola", "Angola"],
            "year": [2022, 2023, 2022, 2023],
            "bcm_flared": [7.0, 7.4, 3.2, 3.5],
        }
    )


def test_palette_has_required_keys() -> None:
    for key in ("background", "flare", "flare_hot", "text"):
        assert key in PALETTE


def test_flare_map_returns_folium_map(detections: pd.DataFrame) -> None:
    m = flare_map(detections)
    assert isinstance(m, folium.Map)


def test_africa_overview_returns_folium_map(detections: pd.DataFrame) -> None:
    m = africa_overview(detections)
    assert isinstance(m, folium.Map)


def test_country_trend_returns_figure(annual: pd.DataFrame) -> None:
    fig = country_trend(annual, ["Nigeria"])
    import matplotlib.figure

    assert isinstance(fig, matplotlib.figure.Figure)


def test_country_comparison_returns_figure(annual: pd.DataFrame) -> None:
    fig = country_comparison(annual, year=2023, top_n=2)
    import matplotlib.figure

    assert isinstance(fig, matplotlib.figure.Figure)
