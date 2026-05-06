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
    "https://www.worldbank.org/content/dam/sites/ggfr/data/"
    "global-gas-flaring-volumes-by-country.csv"
)
"""Public GGFR annual flared-volume table. The exact URL is updated by the
World Bank annually; users may need to override via the ``url`` parameter
of :func:`fetch_ggfr_annual` if the path changes."""

VNF_BASE_URL = "https://eogdata.mines.edu/wwwdata/viirs_products/vnf/v30/csv"
"""Base URL for VIIRS Nightfire v3.0 CSV archive at NOAA EOG.

Daily files follow the pattern::

    {VNF_BASE_URL}/{satellite}/{year}/VNF_{satellite}_d{YYYYMMDD}_noaa_v30.csv.gz

EOG requires free registration for bulk archive access; pass credentials
via the ``EOG_USERNAME`` and ``EOG_PASSWORD`` environment variables, or as
arguments to :func:`fetch_vnf_nightly`. See https://eogdata.mines.edu/.
"""

# Default cache lives under the user's home directory; configurable per call.
DEFAULT_CACHE = Path.home() / ".cache" / "pyflare"


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
) -> pd.DataFrame | FetchResult:
    """Fetch World Bank GGFR annual flared-volume table.

    Returns a tidy DataFrame with one row per country-year and the columns
    ``country``, ``iso3``, ``year``, ``bcm_flared`` (billion cubic metres),
    where present in the source. Additional columns from the upstream file
    are preserved unchanged.

    Parameters
    ----------
    url
        Override the default data URL. Useful when the World Bank rotates
        the CSV path between annual updates.
    cache_dir
        Directory to cache the raw CSV. Defaults to ``~/.cache/pyflare``.
    refresh
        If True, bypass the cache and re-download.
    return_metadata
        If True, return a :class:`FetchResult` with provenance fields
        instead of a bare DataFrame.
    timeout
        HTTP timeout in seconds.

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
    cache_file = cache_root / "ggfr_annual.csv"

    if refresh or not cache_file.exists():
        logger.info("Downloading GGFR annual data from %s", url)
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)
    else:
        logger.debug("Reading GGFR annual data from cache: %s", cache_file)

    df = pd.read_csv(cache_file)
    df = _standardize_ggfr_schema(df)

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

    Parameters
    ----------
    obs_date
        Observation date. Either a :class:`datetime.date` or an ISO string
        such as ``"2024-08-15"``.
    satellite
        Satellite identifier. ``"snpp"`` (Suomi NPP, 2012-present) or
        ``"j01"`` (NOAA-20 / JPSS-1, 2018-present).
    username, password
        EOG credentials. If omitted, falls back to ``EOG_USERNAME`` and
        ``EOG_PASSWORD`` environment variables. Register free at
        https://eogdata.mines.edu/.
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
    requests.HTTPError
        If EOG returns an error status (commonly 401 if credentials are
        missing or 404 if the date has no data due to cloud cover).
    """
    import os

    obs = _coerce_date(obs_date)
    sat = satellite.lower()
    if sat not in {"snpp", "j01"}:
        raise ValueError(f"satellite must be 'snpp' or 'j01', got {satellite!r}")

    # Build the canonical EOG URL.
    fname = f"VNF_{sat}_d{obs:%Y%m%d}_noaa_v30.csv.gz"
    url = f"{VNF_BASE_URL}/{sat}/{obs:%Y}/{fname}"

    user = username or os.environ.get("EOG_USERNAME")
    pwd = password or os.environ.get("EOG_PASSWORD")
    if not (user and pwd):
        raise RuntimeError(
            "EOG credentials required. Register at https://eogdata.mines.edu/ "
            "and pass username/password or set EOG_USERNAME / EOG_PASSWORD."
        )

    cache_root = Path(cache_dir) if cache_dir else DEFAULT_CACHE / "vnf"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_file = cache_root / fname

    if refresh or not cache_file.exists():
        logger.info("Downloading VNF for %s (%s) from %s", obs, sat, url)
        resp = requests.get(url, auth=(user, pwd), timeout=timeout)
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)

    with gzip.open(cache_file, "rt") as fh:
        df = pd.read_csv(fh)

    df = _standardize_vnf_schema(df, obs_date=obs, satellite=sat)
    return df


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
