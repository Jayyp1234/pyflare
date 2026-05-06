"""Tests for pyflare.analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyflare.analysis import (
    DEFAULT_METHANE_SLIP,
    FLARE_TEMP_THRESHOLD_K,
    aggregate_to_sites,
    classify_detection_type,
    estimate_flared_volume,
    methane_proxy,
    persistence_score,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mixed_detections() -> pd.DataFrame:
    """Detections at three locations: a flare, a wildfire, an ambiguous case."""
    return pd.DataFrame(
        {
            "longitude": [6.5, 6.5, 6.5, -120.0, -120.005, 0.0],
            "latitude":  [5.5, 5.5, 5.5,   38.0,   38.005, 0.0],
            "temperature_k": [1800, 1820, 1750, 800, 850, np.nan],
            "radiant_heat_mw": [50.0, 55.0, 48.0, 30.0, 32.0, np.nan],
            "obs_date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03",
                 "2024-07-01", "2024-07-02", "2024-01-01"]
            ),
        }
    )


# ---------------------------------------------------------------------------
# classify_detection_type
# ---------------------------------------------------------------------------


def test_classify_detection_type_labels(mixed_detections: pd.DataFrame) -> None:
    out = classify_detection_type(mixed_detections)
    types = out["detection_type"].tolist()
    assert types[0] == "flare"
    assert types[3] == "wildfire"
    assert types[5] == "ambiguous"


def test_classify_does_not_mutate_input(mixed_detections: pd.DataFrame) -> None:
    before = mixed_detections.copy()
    classify_detection_type(mixed_detections)
    pd.testing.assert_frame_equal(mixed_detections, before)


def test_classify_threshold_kwargs() -> None:
    df = pd.DataFrame({"temperature_k": [1300, 1500]})
    out = classify_detection_type(df, flare_min_k=1200)
    assert (out["detection_type"] == "flare").all()


# ---------------------------------------------------------------------------
# persistence_score
# ---------------------------------------------------------------------------


def test_persistence_isolates_recurring_sites(mixed_detections: pd.DataFrame) -> None:
    score = persistence_score(mixed_detections, time_col="obs_date")
    # The three Niger Delta detections sit on top of each other on different
    # nights, so each should see two neighbours.
    assert score.iloc[:3].tolist() == [2, 2, 2]
    # The two wildfire points are also close, but the ambiguous point is alone.
    assert score.iloc[5] == 0


def test_persistence_handles_empty_frame() -> None:
    out = persistence_score(pd.DataFrame({"longitude": [], "latitude": []}))
    assert out.empty


def test_persistence_excludes_same_day_when_time_provided() -> None:
    df = pd.DataFrame(
        {
            "longitude": [0.0, 0.0],
            "latitude": [0.0, 0.0],
            "obs_date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
        }
    )
    score = persistence_score(df, time_col="obs_date")
    assert score.tolist() == [0, 0]


# ---------------------------------------------------------------------------
# aggregate_to_sites
# ---------------------------------------------------------------------------


def test_aggregate_to_sites_clusters_by_radius(mixed_detections: pd.DataFrame) -> None:
    sites = aggregate_to_sites(mixed_detections.iloc[:5])
    # Three Niger Delta detections + two wildfire detections → two sites.
    assert len(sites) == 2
    assert sites["n_detections"].max() == 3
    assert sites["n_detections"].min() == 2


def test_aggregate_to_sites_includes_radiant_heat(mixed_detections: pd.DataFrame) -> None:
    sites = aggregate_to_sites(mixed_detections.iloc[:5])
    assert "mean_rh_mw" in sites.columns
    assert "total_rh_mw" in sites.columns
    biggest = sites.iloc[0]
    assert biggest["total_rh_mw"] == pytest.approx(50.0 + 55.0 + 48.0)


def test_aggregate_to_sites_handles_empty() -> None:
    sites = aggregate_to_sites(pd.DataFrame({"longitude": [], "latitude": []}))
    assert sites.empty


# ---------------------------------------------------------------------------
# estimate_flared_volume
# ---------------------------------------------------------------------------


def test_estimate_flared_volume_adds_columns() -> None:
    sites = pd.DataFrame(
        {"site_id": [0, 1], "total_rh_mw": [100.0, 50.0]}
    )
    out = estimate_flared_volume(sites)
    assert "estimated_volume_m3" in out.columns
    assert "estimated_volume_bcm" in out.columns
    assert out.loc[0, "estimated_volume_bcm"] > out.loc[1, "estimated_volume_bcm"]


def test_estimate_flared_volume_raises_on_missing_column() -> None:
    sites = pd.DataFrame({"site_id": [0]})
    with pytest.raises(KeyError, match="total_rh_mw"):
        estimate_flared_volume(sites)


# ---------------------------------------------------------------------------
# methane_proxy
# ---------------------------------------------------------------------------


def test_methane_proxy_scales_linearly() -> None:
    one = methane_proxy(1.0)
    two = methane_proxy(2.0)
    assert two == pytest.approx(2 * one)


def test_methane_proxy_respects_slip_argument() -> None:
    base = methane_proxy(1.0, methane_slip=0.05)
    half = methane_proxy(1.0, methane_slip=0.025)
    assert half == pytest.approx(0.5 * base)


def test_methane_proxy_default_constant_matches_module() -> None:
    # Sanity check that the documented default is what the function uses.
    explicit = methane_proxy(1.0, methane_slip=DEFAULT_METHANE_SLIP)
    implicit = methane_proxy(1.0)
    assert explicit == implicit


def test_methane_proxy_handles_series() -> None:
    s = pd.Series([1.0, 2.0, 3.0])
    out = methane_proxy(s)
    assert isinstance(out, pd.Series)
    assert len(out) == 3


# ---------------------------------------------------------------------------
# Defaults sanity
# ---------------------------------------------------------------------------


def test_flare_temp_threshold_in_realistic_range() -> None:
    # Sanity check on the documented default — should sit in the gap between
    # biomass burning (~600-1200 K) and saturation (>2400 K).
    assert 1200 < FLARE_TEMP_THRESHOLD_K < 2400
