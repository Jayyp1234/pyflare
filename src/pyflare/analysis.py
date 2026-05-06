"""Analytical functions for VIIRS Nightfire detections.

Where :mod:`pyflare.data` is concerned with transport and filtering, this
module is concerned with *interpretation* — turning raw thermal anomalies
into the quantities that matter for climate, policy, and journalism work:

* Whether a detection is a flare or a wildfire.
* Whether a location is a persistent flare site.
* How much gas was flared at a site over time (in standard cubic metres).
* How much methane that flaring proxy-emits, given a configurable slip
  fraction.

All thresholds and constants are exposed as keyword arguments with
literature-grounded defaults so users can sensitivity-test or override
them per study area. The methodology follows Elvidge et al. (2013, 2016).

References
----------
Elvidge, C. D., Zhizhin, M., Hsu, F.-C., & Baugh, K. E. (2013). VIIRS
Nightfire: Satellite pyrometry at night. *Remote Sensing*, 5(9), 4423-4449.
https://doi.org/10.3390/rs5094423

Elvidge, C. D., Zhizhin, M., Baugh, K., Hsu, F.-C., & Ghosh, T. (2016).
Methods for global survey of natural gas flaring from VIIRS Nightfire
data. *Energies*, 9(1), 14. https://doi.org/10.3390/en9010014
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants — defaults grounded in Elvidge et al. (2013, 2016)
# ---------------------------------------------------------------------------

#: Lower bound on blackbody temperature (K) for a detection to be considered
#: gas combustion rather than biomass burning. Elvidge et al. (2013) report
#: that flares cluster between roughly 1500–2200 K, while biomass burns at
#: 600–1200 K. 1400 K is conservative and accepts borderline cases.
FLARE_TEMP_THRESHOLD_K: float = 1400.0

#: Upper bound on blackbody temperature (K). Detections above this are
#: typically saturated pixels or instrument artefacts.
FLARE_TEMP_MAX_K: float = 2400.0

#: Default persistence radius (km) for clustering daily detections into a
#: single recurring flare site.
DEFAULT_SITE_RADIUS_KM: float = 1.0

#: Default methane slip fraction used to convert flared gas volume to
#: methane emissions when no site-specific value is supplied. The IPCC
#: AR6 default is 2 percent; recent satellite work (Plant et al., 2022)
#: suggests global means closer to 5 percent. Pyflare uses 5 percent as
#: the default and exposes the parameter for sensitivity analysis.
DEFAULT_METHANE_SLIP: float = 0.05

#: Conversion: 1 megawatt-year of radiant heat ≈ this many m³ of gas
#: combusted, per the Elvidge et al. (2016) regression. Users should
#: treat this as a working approximation; per-flare regressions exist in
#: the literature for higher-fidelity volume estimates.
RH_MWYR_TO_M3_GAS: float = 1.06e6


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify_detection_type(
    df: pd.DataFrame,
    *,
    temp_col: str = "temperature_k",
    flare_min_k: float = FLARE_TEMP_THRESHOLD_K,
    flare_max_k: float = FLARE_TEMP_MAX_K,
) -> pd.DataFrame:
    """Label each detection as ``flare``, ``wildfire``, or ``ambiguous``.

    Adds a ``detection_type`` column to a copy of the input frame using a
    simple temperature threshold rule grounded in Elvidge et al. (2013).
    For higher fidelity, combine with :func:`persistence_score` — true
    flares are at fixed sites whereas wildfires move.

    Parameters
    ----------
    df
        Detection frame containing a temperature column in Kelvin.
    temp_col
        Name of the temperature column.
    flare_min_k, flare_max_k
        Lower and upper bounds for the "flare" classification.

    Returns
    -------
    pandas.DataFrame
        Copy of ``df`` with a new ``detection_type`` column.
    """
    out = df.copy()
    t = out[temp_col]
    out["detection_type"] = np.where(
        t.between(flare_min_k, flare_max_k),
        "flare",
        np.where(t.notna(), "wildfire", "ambiguous"),
    )
    return out


def persistence_score(
    df: pd.DataFrame,
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
    time_col: str | None = None,
    radius_km: float = DEFAULT_SITE_RADIUS_KM,
) -> pd.Series:
    """Compute a per-detection persistence score.

    A detection's score is the number of *other* detections in the frame
    that fall within ``radius_km`` of its location. High scores indicate
    a fixed site (likely a flare); low scores indicate transient hotspots
    (likely wildfires).

    The implementation uses a coarse equirectangular approximation, which
    is accurate to within a few percent at low-to-mid latitudes — fine
    for African producers. For polar work, swap in a proper haversine.

    Parameters
    ----------
    df
        Detection frame.
    lon_col, lat_col
        Coordinate column names.
    time_col
        If supplied, only detections from *different* observation dates
        are counted toward the score. This avoids inflating the score
        with multiple same-night observations of one event.
    radius_km
        Clustering radius.

    Returns
    -------
    pandas.Series
        Integer score per row, aligned to the input index.
    """
    if df.empty:
        return pd.Series([], dtype="Int64", index=df.index)

    lon = df[lon_col].to_numpy()
    lat = df[lat_col].to_numpy()
    n = len(df)

    # Distance in km via equirectangular projection.
    # 1° lat ≈ 110.574 km; 1° lon ≈ 111.320 * cos(lat) km.
    lat_rad = np.radians(lat)
    cos_lat = np.cos(lat_rad)

    scores = np.zeros(n, dtype=np.int64)
    if time_col is not None and time_col in df.columns:
        times = pd.to_datetime(df[time_col]).to_numpy()
    else:
        times = None

    for i in range(n):
        dlon_km = (lon - lon[i]) * 111.320 * cos_lat[i]
        dlat_km = (lat - lat[i]) * 110.574
        dist = np.hypot(dlon_km, dlat_km)
        within = dist <= radius_km
        within[i] = False  # exclude self
        if times is not None:
            within &= times != times[i]
        scores[i] = int(within.sum())

    return pd.Series(scores, index=df.index, name="persistence_score")


def aggregate_to_sites(
    df: pd.DataFrame,
    *,
    lon_col: str = "longitude",
    lat_col: str = "latitude",
    radius_km: float = DEFAULT_SITE_RADIUS_KM,
    rh_col: str | None = "radiant_heat_mw",
) -> pd.DataFrame:
    """Cluster detections into recurring flare sites.

    Greedy single-link clustering: walk the input frame in order, assign
    each detection either to an existing site within ``radius_km`` or to
    a new site. Returns one row per site with summary statistics.

    Parameters
    ----------
    df
        Detection frame, ideally pre-filtered with
        :func:`classify_detection_type` to ``detection_type == "flare"``.
    radius_km
        Clustering radius. Increase for sparse data; decrease for dense.
    rh_col
        Optional radiant-heat column name. If present, mean and total
        radiant heat are added to each site row.

    Returns
    -------
    pandas.DataFrame
        Site-level summary with columns ``site_id``, ``longitude``,
        ``latitude``, ``n_detections``, and (if ``rh_col`` is present)
        ``mean_rh_mw`` and ``total_rh_mw``.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["site_id", "longitude", "latitude", "n_detections"]
        )

    lons = df[lon_col].to_numpy()
    lats = df[lat_col].to_numpy()
    rhs = df[rh_col].to_numpy() if rh_col and rh_col in df.columns else None

    site_lons: list[float] = []
    site_lats: list[float] = []
    site_members: list[list[int]] = []

    for i in range(len(df)):
        assigned = False
        for s in range(len(site_lons)):
            cos_lat = math.cos(math.radians(site_lats[s]))
            dlon_km = (lons[i] - site_lons[s]) * 111.320 * cos_lat
            dlat_km = (lats[i] - site_lats[s]) * 110.574
            if math.hypot(dlon_km, dlat_km) <= radius_km:
                site_members[s].append(i)
                # Update site centroid (running mean).
                k = len(site_members[s])
                site_lons[s] += (lons[i] - site_lons[s]) / k
                site_lats[s] += (lats[i] - site_lats[s]) / k
                assigned = True
                break
        if not assigned:
            site_lons.append(lons[i])
            site_lats.append(lats[i])
            site_members.append([i])

    rows: list[dict[str, float | int]] = []
    for s, members in enumerate(site_members):
        row: dict[str, float | int] = {
            "site_id": s,
            "longitude": site_lons[s],
            "latitude": site_lats[s],
            "n_detections": len(members),
        }
        if rhs is not None:
            site_rhs = rhs[members]
            site_rhs = site_rhs[~np.isnan(site_rhs)]
            if len(site_rhs):
                row["mean_rh_mw"] = float(site_rhs.mean())
                row["total_rh_mw"] = float(site_rhs.sum())
        rows.append(row)

    return pd.DataFrame(rows).sort_values("n_detections", ascending=False).reset_index(drop=True)


@dataclass(frozen=True)
class FlaredVolumeEstimate:
    """Result container for :func:`estimate_flared_volume`.

    Carries both the point estimate and the inputs used so the caller can
    audit the calculation. The Elvidge regression has known scatter
    around ±20 percent at the per-flare level, less at country-aggregate
    level — interpret accordingly.
    """

    site_id: int
    total_rh_mwyr: float
    estimated_volume_m3: float
    estimated_volume_bcm: float


def estimate_flared_volume(
    sites: pd.DataFrame,
    *,
    rh_col: str = "total_rh_mw",
    observation_days: int = 365,
    rh_to_volume: float = RH_MWYR_TO_M3_GAS,
) -> pd.DataFrame:
    """Estimate gas volume flared per site from cumulative radiant heat.

    Pyflare uses the Elvidge et al. (2016) linear regression, which
    relates annualised radiant heat (megawatt-years) to flared gas
    volume (cubic metres). The relationship is approximate; expect ±20%
    per-flare scatter, less at country-aggregate level.

    Parameters
    ----------
    sites
        Site-level frame from :func:`aggregate_to_sites`, containing a
        cumulative radiant-heat column.
    rh_col
        Name of the cumulative radiant-heat column (megawatts × n_obs).
    observation_days
        Number of days the cumulative radiant heat covers. Used to
        annualise the radiant heat into MW-years.
    rh_to_volume
        Override the default radiant-heat-to-volume conversion factor.

    Returns
    -------
    pandas.DataFrame
        Copy of ``sites`` with two new columns:
        ``estimated_volume_m3`` and ``estimated_volume_bcm``.
    """
    if rh_col not in sites.columns:
        raise KeyError(f"sites frame is missing required column {rh_col!r}")
    out = sites.copy()
    annualised_mwyr = out[rh_col] * (observation_days / 365.0)
    out["estimated_volume_m3"] = annualised_mwyr * rh_to_volume
    out["estimated_volume_bcm"] = out["estimated_volume_m3"] / 1e9
    return out


def methane_proxy(
    volume_bcm: float | pd.Series,
    *,
    methane_slip: float = DEFAULT_METHANE_SLIP,
    methane_density_kg_per_m3: float = 0.717,
) -> float | pd.Series:
    """Estimate methane mass emissions from flared gas volume.

    A *very* rough proxy: assumes a fixed slip fraction of input gas
    escapes uncombusted as methane. This is a screening-level estimate,
    not a measurement. Site-specific combustion efficiency varies
    enormously (Plant et al., 2022).

    Parameters
    ----------
    volume_bcm
        Flared volume in billion cubic metres (single value or Series).
    methane_slip
        Fraction of input gas that escapes as methane. Default 0.05
        following recent satellite-based estimates; IPCC AR6 default is
        0.02.
    methane_density_kg_per_m3
        Density of methane at standard conditions.

    Returns
    -------
    float or pandas.Series
        Methane mass in tonnes (kilotonnes for large flares).
    """
    volume_m3 = volume_bcm * 1e9
    methane_m3 = volume_m3 * methane_slip
    methane_kg = methane_m3 * methane_density_kg_per_m3
    return methane_kg / 1000.0  # tonnes
