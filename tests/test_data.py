"""Tests for pyflare.data.

Network calls in transport functions (``fetch_gfmr_annual``,
``fetch_vnf_nightly``, ``_get_eog_access_token``) are mocked here; live
integration tests live under ``tests/integration/`` and are gated on the
EOG credential env vars.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import pyflare.data as pf_data
from pyflare.data import (
    AFRICA_BBOX,
    AFRICAN_PRODUCERS_BBOX,
    _coerce_date,
    _get_eog_access_token,
    _match_country,
    _melt_gfmr_wide,
    _standardize_gfmr_schema,
    fetch_vnf_nightly,
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


def test_standardize_gfmr_schema_handles_variant_columns() -> None:
    raw = pd.DataFrame(
        {
            "Country Name": ["Nigeria", "Angola"],
            "ISO_A3": ["NGA", "AGO"],
            "Year": ["2023", "2023"],
            "Flaring (bcm)": ["7.4", "3.5"],
        }
    )
    out = _standardize_gfmr_schema(raw)
    assert list(out.columns) == ["country", "iso3", "year", "bcm_flared"]
    assert out["year"].dtype == "Int64"
    assert out["bcm_flared"].dtype == float
    assert out.loc[0, "bcm_flared"] == pytest.approx(7.4)


def test_standardize_gfmr_schema_preserves_unknown_columns() -> None:
    raw = pd.DataFrame(
        {
            "country": ["Nigeria"],
            "year": [2023],
            "bcm_flared": [7.4],
            "extra_meta": ["irrelevant"],
        }
    )
    out = _standardize_gfmr_schema(raw)
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


# ---------------------------------------------------------------------------
# GFMR (formerly GGFR) XLSX → long melt
# ---------------------------------------------------------------------------


def test_melt_gfmr_wide_pivots_to_long_format() -> None:
    raw = pd.DataFrame(
        {
            "Country, bcm": ["Nigeria", "Angola", "Congo, Rep."],
            2023: [5.786, 1.837, 1.671],
            2024: [6.480, 2.061, 1.936],
        }
    )
    out = _melt_gfmr_wide(raw)
    assert set(out.columns) == {"country", "year", "bcm_flared"}
    assert len(out) == 6  # 3 countries × 2 years
    nigeria_2024 = out[(out["country"] == "Nigeria") & (out["year"] == 2024)]
    assert nigeria_2024["bcm_flared"].iloc[0] == pytest.approx(6.480)
    # World Bank → pyflare canonical name normalisation.
    rep_congo = out[out["country"] == "Republic of Congo"]
    assert len(rep_congo) == 2


# ---------------------------------------------------------------------------
# OAuth 2.0 — _get_eog_access_token
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_token_cache() -> None:
    """Reset the in-process OAuth token cache between tests."""
    pf_data._EOG_TOKEN_CACHE.clear()


def _mock_token_response(token: str = "test-token-abc", expires_in: int = 300) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value={
        "access_token": token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    })
    return resp


def test_get_eog_access_token_calls_keycloak_with_password_grant() -> None:
    with patch("pyflare.data.requests.post", return_value=_mock_token_response()) as mock_post:
        token = _get_eog_access_token(
            client_id="cid", client_secret="csec",
            username="user", password="pwd",
        )

    assert token == "test-token-abc"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0].endswith("/openid-connect/token")
    assert kwargs["data"] == {
        "client_id": "cid",
        "client_secret": "csec",
        "username": "user",
        "password": "pwd",
        "grant_type": "password",
    }


def test_get_eog_access_token_caches_within_ttl() -> None:
    with patch("pyflare.data.requests.post", return_value=_mock_token_response()) as mock_post:
        first = _get_eog_access_token(
            client_id="cid", client_secret="csec",
            username="user", password="pwd",
        )
        second = _get_eog_access_token(
            client_id="cid", client_secret="csec",
            username="user", password="pwd",
        )

    assert first == second
    assert mock_post.call_count == 1  # token reused, not re-fetched


def test_get_eog_access_token_refetches_after_expiry() -> None:
    # Tiny TTL forces immediate expiry on the next call.
    with patch("pyflare.data.requests.post", return_value=_mock_token_response(expires_in=1)) as mock_post:
        _get_eog_access_token(
            client_id="cid", client_secret="csec",
            username="user", password="pwd",
        )
        # Patch time so the cached token looks expired.
        with patch("pyflare.data.time.time", return_value=10**12):  # type: ignore[attr-defined]
            _get_eog_access_token(
                client_id="cid", client_secret="csec",
                username="user", password="pwd",
            )

    assert mock_post.call_count == 2


def test_get_eog_access_token_keys_cache_by_client_and_user() -> None:
    with patch("pyflare.data.requests.post", return_value=_mock_token_response()) as mock_post:
        _get_eog_access_token(client_id="cid1", client_secret="s", username="u1", password="p")
        _get_eog_access_token(client_id="cid1", client_secret="s", username="u2", password="p")
        _get_eog_access_token(client_id="cid2", client_secret="s", username="u1", password="p")

    assert mock_post.call_count == 3  # three distinct cache keys


# ---------------------------------------------------------------------------
# fetch_vnf_nightly — credential handling
# ---------------------------------------------------------------------------


def test_fetch_vnf_nightly_raises_when_credentials_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("EOG_CLIENT_ID", "EOG_CLIENT_SECRET", "EOG_USERNAME", "EOG_PASSWORD"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(RuntimeError, match="EOG OAuth2 credentials required"):
        fetch_vnf_nightly("2024-08-15")


def test_fetch_vnf_nightly_rejects_unknown_satellite() -> None:
    with pytest.raises(ValueError, match="satellite"):
        fetch_vnf_nightly(
            "2024-08-15",
            satellite="unknown",
            client_id="x", client_secret="x", username="x", password="x",
        )
