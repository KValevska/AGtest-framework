# Public metrics API for quality indicators and spreadsheet export helpers.

# ------------------------------------------------------------------------------------
# Module: __init__.py
# Summary: public exports for metrics computation and metrics-table export helpers.
# Implementation: quality indicators and XLSX export functions are re-exported for GUI modules.
# Responsibility: provides a stable metrics API for dissertation experiment reporting.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from .export import (
    EXPORT_DIR_NAME,
    SOLUTIONS_EXPORT_DIR_NAME,
    build_run_id,
    date_for_filename,
    experiment_configuration_table_data,
    git_commit_for_path,
    metrics_export_path,
    next_available_export_path,
    safe_filename_part,
    solutions_export_path,
    timestamp_for_filename,
    runtime_dependency_versions,
    write_xlsx_table,
    write_xlsx_workbook,
)
from .quality import (
    METRIC_DISPLAY_ORDER,
    METRIC_LABELS,
    METRIC_TABLE_ORDER,
    HypervolumeConfig,
    MetricResult,
    compute_delta,
    compute_kktpm,
    compute_mean_normalized_pairwise_separation,
    compute_metrics,
    compute_spread,
    fixed_ref_point_for_problem,
    get_hv_ref_point,
    is_delta_supported,
    resolve_hv_config,
)

__all__ = [
    "EXPORT_DIR_NAME",
    "METRIC_DISPLAY_ORDER",
    "METRIC_LABELS",
    "METRIC_TABLE_ORDER",
    "HypervolumeConfig",
    "MetricResult",
    "SOLUTIONS_EXPORT_DIR_NAME",
    "build_run_id",
    "compute_delta",
    "compute_kktpm",
    "compute_mean_normalized_pairwise_separation",
    "compute_metrics",
    "compute_spread",
    "date_for_filename",
    "experiment_configuration_table_data",
    "git_commit_for_path",
    "fixed_ref_point_for_problem",
    "get_hv_ref_point",
    "is_delta_supported",
    "resolve_hv_config",
    "metrics_export_path",
    "next_available_export_path",
    "safe_filename_part",
    "runtime_dependency_versions",
    "solutions_export_path",
    "timestamp_for_filename",
    "write_xlsx_table",
    "write_xlsx_workbook",
]
