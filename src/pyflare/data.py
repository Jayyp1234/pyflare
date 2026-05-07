"""Data fetching and spatial filtering for NOAA VIIRS Nightfire and GGFR products.

This module exposes a thin, well-typed Python interface to two complementary
satellite-derived datasets used to monitor global gas flaring:

1. **VIIRS Nightfire (VNF)** — nightly per-detection observations produced by
   the Earth Observation Group at the Colorado School of Mines. Each row is
   a single thermal anomaly with a measured radiant heat, blackbody
   temperature, and emitting area. Distinguishing flares from wildfires
   downstream of VNF requires temporal persistence and temperature filters
   (handled in `pyflare.analysis`).

2. **Global Gas Flaring Reduction (GGFR) annual estimates** — country-level
   annual flared volumes (in billion cubic metres) published by the World
   Bank's GGFR Partnership using the VNF methodology. This is the headline
   dataset for the AFLARED study and the easiest entry point for users who
   are not yet ready to handle daily satellite observations.

The pyflare project uses GGFR as the v0.1 default because (a) it requires no
authentication, (b) the schema is stable, and (c) the country-year resolution
maps cleanly onto the policy and journalism use cases the project targets.

References
----------
Elvidge, C. D., Zhizhin, M., Hsu, F.-C., & Baugh, K. E. (2013). VIIRS
Nightfire: Satellite pyrometry at night. *Remote Sensing*, 5(9), 4423-4449.
https://doi.org/10.3390/rs5094423

World Bank Global Gas Flaring Reduction Partnership.
https://www.worldbank.org/en/programs/gasflaringreduction
"""

from __future__ import annotations

import gzip
import io
import logging
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Geographic constants
# ---------------------------------------------------------------------------

#: Bounding box of the African continent in (min_lon, min_lat, max_lon, max_lat).
#: Generous buffer on the eastern edge to include Madagascar and offshore EEZs.
AFRICA_BBOX: tuple[float, float, float, float] = (-25.0, -40.0, 60.0, 40.0)

#: Approximate bounding boxes for African oil- and gas-producing nations.
#: Source: Natural Earth Data, simplified to (min_lon, min_lat, max_lon, max_lat).
#: These are coarse — for production work, swap to GeoPandas country geometries.
AFRICAN_PRODUCERS_BBOX: dict[str, tuple[float, float, float, float]] = {
    "Algeria":            (-8.7,  19.0,  12.0, 37.1),
    "Angola":             (11.7, -18.0,  24.1, -4.4),
    "Cameroon":           ( 8.5,   1.7,  16.2, 13.1),
    "Chad":               (13.5,   7.5,  24.0, 23.5),
    "Republic of Congo":  (11.1,  -5.1,  18.6,  3.7),
    "DR Congo":           (12.2, -13.5,  31.3,  5.4),
    "Egypt":              (24.7,  21.7,  37.0, 31.7),
    "Equatorial Guinea":  ( 5.5,  -1.5,  11.4,  3.8),
    "Gabon":              ( 8.7,  -3.9,  14.5,  2.3),
    "Ghana":              (-3.3,   4.7,   1.2, 11.2),
    "Libya":              ( 9.4,  19.5,  25.2, 33.2),
    "Mozambique":         (30.2, -26.9,  40.8, -10.5),
    "Niger":              ( 0.2,  11.7,  16.0, 23.5),
    "Nigeria":            ( 2.7,   4.3,  14.7, 13.9),
    "South Sudan":        (24.1,   3.5,  35.9, 12.2),
    "Sudan":              (21.8,   8.7,  38.6, 22.0),
    "Tunisia":            ( 7.5,  30.2,  11.6, 37.5),
}

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

GGFR_DATA_URL = (
    "https://thedocs.worldbank.org/en/doc/"
    "bd2432bbb0e514986f382f61b14b2608-0400072025/related/"
    "Flare-volume-and-intensity-estimates-2012-2024.xlsx"
)
"""Public GGFR annual flared-volume table.

As of the 2025 release the World Bank publishes this dataset as an
``.xlsx`` workbook with three sheets — ``Flare volume``, ``Flaring
intensity``, and ``Oil production`` — each in wide format (one row per
country, year columns). :func:`fetch_ggfr_annual` reads ``Flare volume``
and melts to a tidy long-format frame. The URL is rotated annually; pass
the ``url`` keyword to :func:`fetch_ggfr_annual` to override.
"""

VNF_BASE_URL = "https://eogdata.mines.edu/wwwdata/viirs_products/vnf/v30/csv"
"""Base URL for VIIRS Nightfire v3.0 CSV archive at NOAA EOG.

Daily files follow the pattern::

    {VNF_BASE_URL}/{satellite}/{year}/VNF_{satellite}_d{YYYYMMDD}_noaa_v30.csv.gz

EOG access uses OAuth 2.0 (Keycloak password grant) as of 2026.
:func:`fetch_vnf_nightly` resolves credentials from the environment
(``EOG_CLIENT_ID``, ``EOG_CLIENT_SECRET``, ``EOG_USERNAME``,
``EOG_PASSWORD``) or keyword arguments. See
https://eogdata.mines.edu/products/vnf/subscribers/.
"""

EOG_TOKEN_URL = (
    "https://eogauth-new.mines.edu/realms/eog/protocol/openid-connect/token"
)
"""Keycloak OAuth 2.0 token endpoint for the EOG VNF API.

The password-grant flow exchanges (client_id, client_secret, username,
password) for a short-lived JWT access token (typical TTL: 5 minutes).
Pyflare caches tokens in-process and attaches them as ``Bearer`` headers
on VNF downloads. Client credentials are issued by EOG on request once
the academic license is approved — email ``eog@mines.edu``.
"""

# Default cache lives under the user's home directory; configurable per call.
DEFAULT_CACHE = Path.home() / ".cache" / "pyflare"

# OAuth token cache, keyed by (client_id, username). In-process only —
# tokens are never persisted to disk because they grant data access.
_EOG_TOKEN_CACHE: dict[tuple[str, str], tuple[str, float]] = {}
_EOG_TOKEN_TTL_BUFFER_SECONDS: int = 30


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FetchResult:
    """Lightweight container describing the provenance of a fetched dataset.

    Returned alongside DataFrames when the caller asks for richer context
    via ``return_metadata=True``. Useful for citation and reproducibility
    in the AFLARED dataset paper.
    """

    df: pd.DataFrame
    source_url: str
    fetched_at: datetime
    cache_path: Path | None
    rows: int


def fetch_ggfr_annual(
    *,
    url: str = GGFR_DATA_URL,
    cache_dir: Path | str | None = None,
    refresh: bool = False,
    return_metadata: bool = False,
    timeout: int = 60,
    sheet_name: str = "Flare volume",
) -> pd.DataFrame | FetchResult:
    """Fetch World Bank GGFR annual flared-volume table.

    Returns a tidy DataFrame with one row per country-year and the columns
    ``country``, ``year``, ``bcm_flared`` (billion cubic metres). Country
    names are normalised to pyflare's canonical set (matching
    :data:`AFRICAN_PRODUCERS_BBOX` keys) so the result composes cleanly
    with :func:`filter_country`.

    The upstream source has been an ``.xlsx`` workbook since the 2025
    release; reading it requires ``openpyxl`` (a core pyflare dependency).

    Parameters
    ----------
    url
        Override the default data URL. Useful when the World Bank rotates
        the path between annual updates.
    cache_dir
        Directory to cache the raw XLSX. Defaults to ``~/.cache/pyflare``.
    refresh
        If True, bypass the cache and re-download.
    return_metadata
        If True, return a :class:`FetchResult` with provenance fields
        instead of a bare DataFrame.
    timeout
        HTTP timeout in seconds.
    sheet_name
        Workbook sheet to read. Defaults to ``"Flare volume"``; other
        sheets in the GGFR workbook are ``"Flaring intensity"`` and
        ``"Oil production"``.

    Returns
    -------
    pandas.DataFrame or FetchResult
        Tidy table of annual flared volumes.

    Examples
    --------
    >>> import pyflare as pf
    >>> df = pf.fetch_ggfr_annual()                       # doctest: +SKIP
    >>> df[df["country"] == "Nigeria"].tail()             # doctest: +SKIP
    """
    cache_root = Path(cache_dir) if cache_dir else DEFAULT_CACHE
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_file = cache_root / "ggfr_annual.xlsx"

    if refresh or not cache_file.exists():
        logger.info("Downloading GGFR annual data from %s", url)
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)
    else:
        logger.debug("Reading GGFR annual data from cache: %s", cache_file)

    raw = pd.read_excel(cache_file, sheet_name=sheet_name)
    df = _melt_ggfr_wide(raw)

    if return_metadata:
        return FetchResult(
            df=df,
            source_url=url,
            fetched_at=datetime.utcnow(),
            cache_path=cache_file,
            rows=len(df),
        )
    return df


def fetch_vnf_nightly(
    obs_date: date | str,
    *,
    satellite: str = "snpp",
    client_id: str | None = None,
    client_secret: str | None = None,
    username: str | None = None,
    password: str | None = None,
    cache_dir: Path | str | None = None,
    refresh: bool = False,
    timeout: int = 120,
) -> pd.DataFrame:
    """Fetch one nightly VIIRS Nightfire CSV from NOAA EOG.

    Each detection in the returned frame is a thermal anomaly — *not* a
    confirmed flare. Wildfire / flare classification is the caller's
    responsibility (see :mod:`pyflare.analysis`). This function only
    handles transport, decompression, and schema parsing.

    Authentication uses the OAuth 2.0 password-grant flow: pyflare
    exchanges your credentials for a short-lived JWT access token
    (cached in-process for ~5 minutes) and attaches it as a ``Bearer``
    header. Client credentials are issued by EOG on request once the
    academic license is approved.

    Parameters
    ----------
    obs_date
        Observation date. Either a :class:`datetime.date` or an ISO string
        such as ``"2024-08-15"``.
    satellite
        Satellite identifier. ``"snpp"`` (Suomi NPP, 2012-present) or
        ``"j01"`` (NOAA-20 / JPSS-1, 2018-present).
    client_id, client_secret
        OAuth 2.0 client credentials. Fall back to ``EOG_CLIENT_ID`` /
        ``EOG_CLIENT_SECRET`` environment variables. Email
        ``eog@mines.edu`` to obtain these once your license is signed.
    username, password
        EOG account credentials (the pair you registered at
        https://eogdata.mines.edu/products/register/). Fall back to
        ``EOG_USERNAME`` / ``EOG_PASSWORD``.
    cache_dir
        Directory to cache compressed nightly files.
    refresh
        Re-download even if cached.
    timeout
        HTTP timeout in seconds.

    Returns
    -------
    pandas.DataFrame
        VNF detection frame indexed by detection ID, with one row per
        thermal anomaly.

    Raises
    ------
    RuntimeError
        If any of the four credential parts (client_id, client_secret,
        username, password) is missing.
    requests.HTTPError
        If EOG returns an error status (commonly 401 from the token
        endpoint if credentials are wrong, or 404 if the requested date
        has no data due to cloud cover).
    """
    import os

    obs = _coerce_date(obs_date)
    sat = satellite.lower()
    if sat not in {"snpp", "j01"}:
        raise ValueError(f"satellite must be 'snpp' or 'j01', got {satellite!r}")

    cid = client_id or os.environ.get("EOG_CLIENT_ID")
    csec = client_secret or os.environ.get("EOG_CLIENT_SECRET")
    user = username or os.environ.get("EOG_USERNAME")
    pwd = password or os.environ.get("EOG_PASSWORD")
    if not all((cid, csec, user, pwd)):
        raise RuntimeError(
            "EOG OAuth2 credentials required. Register at "
            "https://eogdata.mines.edu/products/register/ , sign the "
            "academic license, then email eog@mines.edu for a Client ID. "
            "Set EOG_CLIENT_ID, EOG_CLIENT_SECRET, EOG_USERNAME, "
            "EOG_PASSWORD (or pass as keyword arguments)."
        )

    # Build the canonical EOG URL.
    fname = f"VNF_{sat}_d{obs:%Y%m%d}_noaa_v30.csv.gz"
    url = f"{VNF_BASE_URL}/{sat}/{obs:%Y}/{fname}"

    cache_root = Path(cache_dir) if cache_dir else DEFAULT_CACHE / "vnf"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_file = cache_root / fname

    if refresh or not cache_file.exists():
        token = _get_eog_access_token(
            client_id=cid,  # type: ignore[arg-type]
            client_secret=csec,  # type: ignore[arg-type]
            username=user,  # type: ignore[arg-type]
            password=pwd,  # type: ignore[arg-type]
            timeout=timeout,
        )
        logger.info("Downloading VNF for %s (%s) from %s", obs, sat, url)
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)

    with gzip.open(cache_file, "rt") as fh:
        df = pd.read_csv(fh)

    df = _standardize_vnf_schema(df, obs_date=obs, satellite=sat)
    return df


def _get_eog_access_token(
    *,
    client_id: str,
    client_secret: str,
    username: str,
    password: str,
    timeout: int = 30,
) -> str:
    """Obtain (or return cached) an EOG OAuth 2.0 access token.

    Uses the resource-owner password-credentials grant against the
    Keycloak realm at :data:`EOG_TOKEN_URL`. The returned token is a JWT
    that should be sent as ``Authorization: Bearer <token>`` on
    subsequent VNF requests. Tokens are cached in-process by
    ``(client_id, username)`` and refreshed 30 seconds before expiry.

    Parameters
    ----------
    client_id, client_secret
        OAuth client credentials issued by EOG.
    username, password
        EOG account credentials.
    timeout
        HTTP timeout in seconds.

    Returns
    -------
    str
        Bearer access token.

    Raises
    ------
    requests.HTTPError
        If the token endpoint returns a non-2xx status (typically 401
        for bad credentials).
    """
    cache_key = (client_id, username)
    now = time.time()
    cached = _EOG_TOKEN_CACHE.get(cache_key)
    if cached and cached[1] > now:
        return cached[0]

    resp = requests.post(
        EOG_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
            "grant_type": "password",
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    payload = resp.json()
    token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 300))
    expiry = now + max(expires_in - _EOG_TOKEN_TTL_BUFFER_SECONDS, 0)
    _EOG_TOKEN_CACHE[cache_key] = (token, expiry)
    return token


def filter_bbox(
    df: pd.DataFrame,
    bbox: tuple[float, float, float, float],
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
) -> pd.DataFrame:
    """Filter a detection frame to a (min_lon, min_lat, max_lon, max_lat) box.

    Inclusive on all edges. Rows missing either coordinate are dropped.
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    mask = (
        df[lon_col].between(min_lon, max_lon)
        & df[lat_col].between(min_lat, max_lat)
    )
    return df.loc[mask].reset_index(drop=True)


def filter_africa(
    df: pd.DataFrame,
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
) -> pd.DataFrame:
    """Filter a detection frame to the African continent bounding box.

    Convenience wrapper around :func:`filter_bbox` using
    :data:`AFRICA_BBOX`. For sub-continental precision, supply a country
    name to :func:`filter_country` instead.
    """
    return filter_bbox(df, AFRICA_BBOX, lon_col=lon_col, lat_col=lat_col)


def filter_country(
    df: pd.DataFrame,
    country: str,
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
) -> pd.DataFrame:
    """Filter to one African oil/gas-producing country by bounding box.

    The bounding box is approximate (rectangular) and may include offshore
    waters and small portions of neighbouring countries. For exact polygon
    filtering, use the optional ``[viz]`` extras and supply a GeoPandas
    geometry.

    Parameters
    ----------
    country
        Country name, case-insensitive. See
        :data:`AFRICAN_PRODUCERS_BBOX` for supported countries.

    Raises
    ------
    KeyError
        If ``country`` is not in :data:`AFRICAN_PRODUCERS_BBOX`.
    """
    key = _match_country(country)
    bbox = AFRICAN_PRODUCERS_BBOX[key]
    return filter_bbox(df, bbox, lon_col=lon_col, lat_col=lat_col)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _coerce_date(value: date | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise TypeError(f"obs_date must be date or ISO string, got {type(value).__name__}")


def _match_country(country: str) -> str:
    """Resolve a user-supplied country name to a key in AFRICAN_PRODUCERS_BBOX.

    Case-insensitive; tolerates a couple of common alternate spellings.
    """
    aliases = {
        "drc": "DR Congo",
        "democratic republic of congo": "DR Congo",
        "democratic republic of the congo": "DR Congo",
        "congo-kinshasa": "DR Congo",
        "congo-brazzaville": "Republic of Congo",
        "congo": "Republic of Congo",
    }
    norm = country.strip().lower()
    if norm in aliases:
        return aliases[norm]
    for key in AFRICAN_PRODUCERS_BBOX:
        if key.lower() == norm:
            return key
    raise KeyError(
        f"{country!r} is not a recognised African producer. "
        f"Supported: {sorted(AFRICAN_PRODUCERS_BBOX)}"
    )


#: World Bank GGFR uses idiosyncratic country labels; this map normalises
#: them to pyflare's canonical names (matching :data:`AFRICAN_PRODUCERS_BBOX`).
#: Names not in the map pass through unchanged.
_WB_TO_PYFLARE_COUNTRY: dict[str, str] = {
    "Congo, Rep.": "Republic of Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "Egypt, Arab Rep.": "Egypt",
    "Iran, Islamic Rep.": "Iran",
    "Russian Federation": "Russia",
    "Syrian Arab Republic": "Syria",
    "Venezuela, RB": "Venezuela",
    "Yemen, Rep.": "Yemen",
}


def _canonicalise_wb_country(name: object) -> object:
    """Map a single World Bank country label to pyflare's canonical form."""
    if not isinstance(name, str):
        return name
    return _WB_TO_PYFLARE_COUNTRY.get(name, name)


def _melt_ggfr_wide(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert the World Bank GGFR wide-format sheet to tidy long format.

    Source layout: one row per country with year columns (``2012`` through
    the latest year covered). Output columns: ``country``, ``year``,
    ``bcm_flared`` — one row per country-year. Country names are normalised
    via :data:`_WB_TO_PYFLARE_COUNTRY`.
    """
    country_col = raw.columns[0]  # WB labels this 'Country, bcm' / similar
    year_cols = [c for c in raw.columns[1:] if isinstance(c, (int, float))]
    long = raw.melt(
        id_vars=[country_col],
        value_vars=year_cols,
        var_name="year",
        value_name="bcm_flared",
    ).rename(columns={country_col: "country"})
    long["country"] = long["country"].apply(_canonicalise_wb_country)
    long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
    long["bcm_flared"] = pd.to_numeric(long["bcm_flared"], errors="coerce")
    return long.dropna(subset=["country", "year"]).reset_index(drop=True)


def _standardize_ggfr_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise GGFR column names across World Bank annual releases.

    The upstream CSV has changed column casing and naming several times
    since 2017. This function maps any of the known variants to the
    canonical pyflare schema: ``country``, ``iso3``, ``year``, ``bcm_flared``.
    Unknown extra columns are preserved.
    """
    rename_map: dict[str, str] = {}
    for col in df.columns:
        lower = col.lower().strip()
        if lower in {"country", "country name", "country_name"}:
            rename_map[col] = "country"
        elif lower in {"iso3", "iso_a3", "iso3 code", "iso3_code"}:
            rename_map[col] = "iso3"
        elif lower in {"year"}:
            rename_map[col] = "year"
        elif "bcm" in lower or "flaring" in lower or "flared" in lower:
            # Many possible variants: "Flaring (bcm)", "Volume bcm", etc.
            rename_map.setdefault(col, "bcm_flared")
    out = df.rename(columns=rename_map)
    if "year" in out.columns:
        out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    if "bcm_flared" in out.columns:
        out["bcm_flared"] = pd.to_numeric(out["bcm_flared"], errors="coerce")
    return out


def _standardize_vnf_schema(
    df: pd.DataFrame,
    *,
    obs_date: date,
    satellite: str,
) -> pd.DataFrame:
    """Map raw VNF columns to pyflare's canonical names and add provenance.

    Pyflare keeps the upstream column set intact but exposes lowercase
    aliases for the most-used fields so user code is portable across
    minor VNF version bumps.
    """
    aliases = {
        "Lat_GMTCO": "latitude",
        "Lon_GMTCO": "longitude",
        "Date_Mscan": "scan_time_utc",
        "Temp_BB": "temperature_k",
        "Area_BB": "source_area_m2",
        "RH": "radiant_heat_mw",
        "RHI": "radiant_heat_intensity",
    }
    out = df.copy()
    for src, dst in aliases.items():
        if src in out.columns and dst not in out.columns:
            out[dst] = out[src]
    out["pyflare_obs_date"] = pd.Timestamp(obs_date)
    out["pyflare_satellite"] = satellite
    return out


def list_supported_countries() -> list[str]:
    """Return the sorted list of African producer countries supported by
    :func:`filter_country`."""
    return sorted(AFRICAN_PRODUCERS_BBOX)
