"""pyflare: Satellite gas flaring analytics for African oil-producing nations.

A Python toolkit for working with VIIRS Nightfire (VNF) — produced by the
Earth Observation Group (EOG) at the Colorado School of Mines — and World
Bank GFMR (Global Flaring and Methane Reduction Partnership; formerly the
Global Gas Flaring Reduction Partnership / GGFR) annual flared volumes,
with first-class support for African contexts.

Pyflare is a thin client. It does **not** bundle, redistribute, or rehost
VNF data; each user must hold their own VNF Academic Data Use License from
EOG (`eog@mines.edu`). See ``LICENSING_NOTES.md`` for the full terms.

Quick start
-----------
    >>> import pyflare as pf
    >>> df = pf.fetch_gfmr_annual()
    >>> nigeria = pf.filter_country(df, "Nigeria")
    >>> nigeria[["year", "bcm_flared"]].tail()
"""

from pyflare.analysis import (
    aggregate_to_sites,
    classify_detection_type,
    communities_near_sites,
    estimate_flared_volume,
    methane_proxy,
    persistence_score,
    volume_to_co2eq,
)
from pyflare.data import (
    fetch_gfmr_annual,
    fetch_ggfr_annual,  # deprecated alias for fetch_gfmr_annual
    fetch_vnf_nightly,
    filter_africa,
    filter_bbox,
    filter_country,
    list_supported_countries,
)

__version__ = "0.1.0"

__all__ = [
    # Data
    "fetch_gfmr_annual",
    "fetch_ggfr_annual",  # deprecated alias; will be removed in v0.3
    "fetch_vnf_nightly",
    "filter_africa",
    "filter_country",
    "filter_bbox",
    "list_supported_countries",
    # Analysis
    "classify_detection_type",
    "persistence_score",
    "aggregate_to_sites",
    "estimate_flared_volume",
    "methane_proxy",
    "volume_to_co2eq",
    "communities_near_sites",
    # Meta
    "__version__",
]
