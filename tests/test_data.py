"""Tests for pyflare.data.

These tests deliberately avoid network calls. The transport functions
(`fetch_ggfr_annual`, `fetch_vnf_nightly`) are exercised in integration
tests under tests/integration/, gated on the EOG_USERNAME env var.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from pyflare.data import (
    AFRICA_BBOX,
    AFRICAN_PRODUCERS_BBOX,
    _coerce_date,
    _match_country,
    _standardize_ggfr_schema,
    filter_africa,
    filter_bbox,
    filter_country,
    list_supported_countries,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def detections() -> pd.DataFrame:
    """Synthetic detection frame spanning four continents."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "longitude": [6.5, 12.0, -100.0, 75.0, 10.0, 8.0],   # NG, AO, USA, IN, DE, NG
            "latitude": [5.5, -8.0, 35.0, 20.0, 51.0, 4.5],
            "temperature_k": [1800, 1750, 600, 1900, 400, 1850],
        }
    )


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------


def test_filter_africa_keeps_only_african_rows(detections: pd.DataFrame) -> None:
    africa = filter_africa(detections)
    # Three of the six points fall inside the continental bbox: NG x2 + AO.
    assert len(africa) == 3
    assert set(africa["id"]) == {1, 2, 6}


def test_filter_country_nigeria(detections: pd.DataFrame) -> None:
    nigeria = filter_country(detections, "Nigeria")
    assert set(nigeria["id"]) == {1, 6}


@pytest.mark.parametrize(
    "alias,expected",
    [
        ("nigeria", "Nigeria"),
        ("NIGERIA", "Nigeria"),
        ("DRC", "DR Congo"),
        ("Democratic Republic of Congo", "DR Congo"),
        ("congo-brazzaville", "Republic of Congo"),
    ],
)
def test_match_country_aliases(alias: str, expected: str) -> None:
    assert _match_country(alias) == expected


def test_match_country_rejects_unknown() -> None:
    with pytest.raises(KeyError, match="Belgium"):
        _match_country("Belgium")


def test_filter_bbox_inclusive_on_edges() -> None:
    df = pd.DataFrame({"longitude": [0.0, 10.0, 10.0001], "latitude": [0.0, 0.0, 0.0]})
    out = filter_bbox(df, (0.0, -1.0, 10.0, 1.0))
    assert len(out) == 2  # the third point is just outside the eastern edge


def test_filter_bbox_drops_missing_coordinates() -> None:
    df = pd.DataFrame(
        {"longitude": [0.0, None, 5.0], "latitude": [0.0, 0.0, None]}
    )
    out = filter_bbox(df, (-10.0, -10.0, 10.0, 10.0))
    assert len(out) == 1


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


def test_standardize_ggfr_schema_handles_variant_columns() -> None:
    raw = pd.DataFrame(
        {
            "Country Name": ["Nigeria", "Angola"],
            "ISO_A3": ["NGA", "AGO"],
            "Year": ["2023", "2023"],
            "Flaring (bcm)": ["7.4", "3.5"],
        }
    )
    out = _standardize_ggfr_schema(raw)
    assert list(out.columns) == ["country", "iso3", "year", "bcm_flared"]
    assert out["year"].dtype == "Int64"
    assert out["bcm_flared"].dtype == float
    assert out.loc[0, "bcm_flared"] == pytest.approx(7.4)


def test_standardize_ggfr_schema_preserves_unknown_columns() -> None:
    raw = pd.DataFrame(
        {
            "country": ["Nigeria"],
            "year": [2023],
            "bcm_flared": [7.4],
            "extra_meta": ["irrelevant"],
        }
    )
    out = _standardize_ggfr_schema(raw)
    assert "extra_meta" in out.columns


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def test_coerce_date_accepts_iso_string() -> None:
    assert _coerce_date("2024-08-15") == date(2024, 8, 15)


def test_coerce_date_accepts_date() -> None:
    assert _coerce_date(date(2024, 8, 15)) == date(2024, 8, 15)


def test_coerce_date_rejects_int() -> None:
    with pytest.raises(TypeError):
        _coerce_date(20240815)  # type: ignore[arg-type]


def test_supported_countries_includes_top_producers() -> None:
    countries = list_supported_countries()
    for must_have in ("Nigeria", "Algeria", "Angola", "Libya"):
        assert must_have in countries


def test_africa_bbox_constants_are_consistent() -> None:
    min_lon, min_lat, max_lon, max_lat = AFRICA_BBOX
    assert min_lon < max_lon
    assert min_lat < max_lat
    # Every per-country box should sit inside the continental box.
    for name, (lo_lon, lo_lat, hi_lon, hi_lat) in AFRICAN_PRODUCERS_BBOX.items():
        assert min_lon <= lo_lon <= hi_lon <= max_lon, name
        assert min_lat <= lo_lat <= hi_lat <= max_lat, name
