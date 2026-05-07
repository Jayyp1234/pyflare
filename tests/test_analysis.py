"""Tests for pyflare.analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyflare.analysis import (
    CO2_PER_M3_GAS_KG,
    DEFAULT_METHANE_SLIP,
    FLARE_TEMP_THRESHOLD_K,
    KNOWN_AFRICAN_SETTLEMENTS,
    METHANE_DENSITY_KG_PER_M3,
    METHANE_GWP100_FOSSIL,
    aggregate_to_sites,
    classify_detection_type,
    communities_near_sites,
    estimate_flared_volume,
    methane_proxy,
    persistence_score,
    volume_to_co2eq,
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


# ---------------------------------------------------------------------------
# volume_to_co2eq — the headline-number function (gate G2)
# ---------------------------------------------------------------------------


def test_volume_to_co2eq_returns_positive_for_sample() -> None:
    # Mirrors scripts/verify.sh G2: Nigeria-scale volume + IPCC AR6 slip.
    mt = volume_to_co2eq(7.4, 0.02)
    assert mt > 0


def test_volume_to_co2eq_matches_hand_calculation() -> None:
    # 7.4 bcm flared, 2% slip:
    #   burned   = 7.4e9 * 0.98 m³ → 7.252e9 m³  → 7.252e9 * 2.55 = 1.84926e10 kg CO2
    #   slipped  = 7.4e9 * 0.02 m³ → 1.48e8 m³   → 1.48e8 * 0.717 = 1.06116e8 kg CH4
    #   ch4 → eq = 1.06116e8 * 29.8                                 = 3.16226e9 kg CO2e
    #   total    = 1.84926e10 + 3.16226e9                            = 2.16548e10 kg
    #   in Mt    = 21.6548
    mt = volume_to_co2eq(7.4, 0.02)
    assert mt == pytest.approx(21.6548, rel=1e-4)


def test_volume_to_co2eq_zero_volume_zero_emissions() -> None:
    assert volume_to_co2eq(0.0, 0.02) == 0.0
    assert volume_to_co2eq(0.0, 0.5) == 0.0


def test_volume_to_co2eq_zero_slip_is_combustion_only() -> None:
    # With zero slip, the answer is just volume × combustion EF (in Mt).
    mt = volume_to_co2eq(1.0, 0.0)
    expected_kg = 1e9 * CO2_PER_M3_GAS_KG  # bcm → m³ × kg/m³
    assert mt == pytest.approx(expected_kg / 1e9)


def test_volume_to_co2eq_higher_slip_higher_emissions() -> None:
    # Slipped CH4 carries ~8× the climate impact of burned CO2 per m³,
    # so any monotonic slip increase strictly raises the headline.
    low = volume_to_co2eq(1.0, 0.02)
    mid = volume_to_co2eq(1.0, 0.05)
    high = volume_to_co2eq(1.0, 0.10)
    assert low < mid < high


def test_volume_to_co2eq_handles_series() -> None:
    s = pd.Series([1.0, 7.4, 0.0])
    out = volume_to_co2eq(s, 0.02)
    assert isinstance(out, pd.Series)
    assert len(out) == 3
    assert out.iloc[2] == 0.0
    assert out.iloc[1] > out.iloc[0]


def test_volume_to_co2eq_rejects_invalid_slip() -> None:
    with pytest.raises(ValueError, match="methane_slip"):
        volume_to_co2eq(1.0, -0.1)
    with pytest.raises(ValueError, match="methane_slip"):
        volume_to_co2eq(1.0, 1.5)


def test_volume_to_co2eq_constants_match_published_values() -> None:
    # Guard against silent edits to the documented IPCC defaults.
    assert CO2_PER_M3_GAS_KG == 2.55  # IPCC 2006 Guidelines
    assert METHANE_GWP100_FOSSIL == 29.8  # IPCC AR6 WG1 Ch.7
    assert METHANE_DENSITY_KG_PER_M3 == 0.717  # std conditions


# ---------------------------------------------------------------------------
# communities_near_sites — second wow-shot (gate G6)
# ---------------------------------------------------------------------------


def test_communities_near_sites_returns_expected_columns() -> None:
    sites = pd.DataFrame({
        "site_id": [0, 1],
        "longitude": [7.16, 5.18],
        "latitude":  [4.41, 5.65],
    })
    out = communities_near_sites(sites, radius_km=10.0)
    assert set(out.columns) == {
        "site_id",
        "n_communities_within_radius",
        "population_exposed",
        "communities",
        "nearest_community",
        "nearest_distance_km",
    }
    assert len(out) == 2


def test_communities_near_sites_finds_bonny_for_bonny_lng() -> None:
    sites = pd.DataFrame({
        "site_id": [42],
        "longitude": [7.16],
        "latitude":  [4.41],
    })
    out = communities_near_sites(sites, radius_km=10.0)
    row = out.iloc[0]
    assert row["nearest_community"] == "Bonny Town"
    assert row["nearest_distance_km"] < 5.0
    assert row["population_exposed"] >= 215_000  # Bonny Town alone


def test_communities_near_sites_handles_remote_site() -> None:
    # Empty quarter of Algeria — no settlement within 10 km.
    sites = pd.DataFrame({
        "site_id": [99],
        "longitude": [4.0],
        "latitude":  [25.0],
    })
    out = communities_near_sites(sites, radius_km=10.0)
    row = out.iloc[0]
    assert row["n_communities_within_radius"] == 0
    assert row["population_exposed"] == 0
    assert row["nearest_community"] == ""


def test_communities_near_sites_radius_increases_match_count() -> None:
    sites = pd.DataFrame({
        "site_id": [0],
        "longitude": [7.05],  # Port Harcourt centre
        "latitude":  [4.83],
    })
    small = communities_near_sites(sites, radius_km=5.0)
    big = communities_near_sites(sites, radius_km=50.0)
    assert big.iloc[0]["n_communities_within_radius"] >= small.iloc[0]["n_communities_within_radius"]
    assert big.iloc[0]["population_exposed"] >= small.iloc[0]["population_exposed"]


def test_communities_near_sites_handles_empty_input() -> None:
    sites = pd.DataFrame(columns=["site_id", "longitude", "latitude"])
    out = communities_near_sites(sites)
    assert out.empty
    # Schema preserved on empty.
    assert "population_exposed" in out.columns


def test_communities_near_sites_accepts_custom_settlement_dict() -> None:
    sites = pd.DataFrame({
        "site_id": [0],
        "longitude": [0.0],
        "latitude":  [0.0],
    })
    custom = {"Synthetic Town": (0.05, 0.0, 12_345)}
    out = communities_near_sites(sites, radius_km=20.0, settlements=custom)
    row = out.iloc[0]
    assert row["nearest_community"] == "Synthetic Town"
    assert row["population_exposed"] == 12_345


def test_known_african_settlements_covers_priority_countries() -> None:
    # Sanity: at least one entry per priority producer country region.
    names_lower = {n.lower() for n in KNOWN_AFRICAN_SETTLEMENTS}
    must_have = {
        "port harcourt",   # Niger Delta
        "hassi messaoud",  # Algeria Sahara
        "brega",           # Libya
        "soyo",            # Angola
    }
    assert must_have.issubset(names_lower)
