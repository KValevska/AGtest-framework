from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pymoo_gui.metrics import (
    build_run_id,
    experiment_configuration_table_data,
    metrics_export_path,
    solutions_export_path,
)


def test_run_id_is_utc_stable_and_filename_safe() -> None:
    instant = datetime(2026, 10, 31, 15, 30, 12, tzinfo=timezone.utc)

    run_id = build_run_id("nsga2", "zdt1", 42, now=instant)

    assert run_id == "2026-10-31T15-30-12Z_NSGA2_ZDT1_seed42"
    assert metrics_export_path(Path("results"), "NSGA-II", "ZDT1", run_id=run_id).stem == run_id
    assert solutions_export_path(Path("results"), "NSGA-II", "ZDT1", run_id=run_id).stem == run_id


def test_experiment_configuration_uses_english_labels_and_expands_parameters() -> None:
    headers, rows = experiment_configuration_table_data(
        {
            "run_id": "run-1",
            "random_seed": 42,
            "problem_parameters": {"n_var": 30},
            "algorithm_parameters": {"pop_size": 100, "adaptive": True},
        }
    )

    assert headers == ["Setting", "Value"]
    assert ["Run ID", "run-1"] in rows
    assert ["Random seed", 42] in rows
    assert ["Problem parameter: n_var", 30] in rows
    assert ["Algorithm parameter: adaptive", "true"] in rows
    assert ["Algorithm parameter: pop_size", 100] in rows
