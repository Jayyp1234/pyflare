"""pyflare: Satellite gas flaring analytics for African oil-producing nations.

A Python toolkit for working with NOAA's VIIRS Nightfire (VNF) and Global Gas
Flaring Reduction (GGFR) data, with first-class support for African contexts.

Quick start
-----------
    >>> import pyflare as pf
    >>> df = pf.fetch_ggfr_annual()
    >>> nigeria = pf.filter_country(df, "Nigeria")
    >>> nigeria[["year", "bcm_flared"]].tail()
"""

from pyflare.analysis import (
    aggregate_to_sites,
    classify_detection_type,
    estimate_flared_volume,
    methane_proxy,
    persistence_score,
)
from pyflare.data import (
    fetch_ggfr_annual,
    fetch_vnf_nightly,
    filter_africa,
    filter_bbox,
    filter_country,
    list_supported_countries,
)

__version__ = "0.1.0"

__all__ = [
    # Data
    "fetch_ggfr_annual",
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
    # Meta
    "__version__",
]

