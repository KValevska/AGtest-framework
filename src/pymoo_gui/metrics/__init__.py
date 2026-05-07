"""
EN:
Public metrics API for quality indicators and spreadsheet export helpers.

PL:
Udostepnia funkcje liczace metryki oraz zapisujace tabele wynikow do pliku.
"""

# ------------------------------------------------------------------------------------
# File: __init__.py
# Contents: public exports for metrics computation and metrics-table export helpers.
# What happens here: quality indicators and XLSX export functions are re-exported for GUI modules.
# Role in the framework: provides a stable metrics API for dissertation experiment reporting.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from .export import (
    EXPORT_DIR_NAME,
    SOLUTIONS_EXPORT_DIR_NAME,
    date_for_filename,
    metrics_export_path,
    next_available_export_path,
    safe_filename_part,
    solutions_export_path,
    timestamp_for_filename,
    write_xlsx_table,
    write_xlsx_workbook,
)
from .quality import (
    METRIC_DISPLAY_ORDER,
    METRIC_LABELS,
    METRIC_TABLE_ORDER,
    MetricResult,
    compute_delta,
    compute_kktpm,
    compute_metrics,
    compute_spread,
    fixed_ref_point_for_problem,
    get_hv_ref_point,
)

__all__ = [
    "EXPORT_DIR_NAME",
    "METRIC_DISPLAY_ORDER",
    "METRIC_LABELS",
    "METRIC_TABLE_ORDER",
    "MetricResult",
    "SOLUTIONS_EXPORT_DIR_NAME",
    "compute_delta",
    "compute_kktpm",
    "compute_metrics",
    "compute_spread",
    "date_for_filename",
    "fixed_ref_point_for_problem",
    "get_hv_ref_point",
    "metrics_export_path",
    "next_available_export_path",
    "safe_filename_part",
    "solutions_export_path",
    "timestamp_for_filename",
    "write_xlsx_table",
    "write_xlsx_workbook",
]
