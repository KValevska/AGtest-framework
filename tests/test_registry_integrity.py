from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

from pymoo_gui.algorithms import ALGORITHMS
from pymoo_gui.metrics import resolve_hv_config
from pymoo_gui.problems import PROBLEMS


def test_algorithm_and_problem_modules_declare_provenance() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src" / "pymoo_gui"
    modules = [
        *sorted((source_root / "algorithms").glob("*.py")),
        *sorted((source_root / "problems").glob("*.py")),
    ]

    assert modules
    for module in modules:
        header = "\n".join(module.read_text(encoding="utf-8").splitlines()[:20])
        assert "Provenance:" in header, module.relative_to(source_root)


def test_algorithm_registry_has_required_structure() -> None:
    assert ALGORITHMS, "The algorithm registry must not be empty."
    implementation_types = {
        "pymoo", "adapter", "faithful_port", "adapted_port", "framework_variant"
    }
    for key, entry in ALGORITHMS.items():
        assert isinstance(key, str) and key
        assert isinstance(entry, dict)
        assert entry.get("label"), f"Algorithm '{key}' is missing a label."
        assert callable(entry.get("factory")), f"Algorithm '{key}' is missing a callable factory."
        assert entry.get("implementation_type") in implementation_types, key
        assert entry.get("reference"), key
        assert "source_commit" in entry, key
        assert entry.get("verified_against"), key

    assert "platypus_moead" not in ALGORITHMS
    assert "moead_iepsilon" in ALGORITHMS


def test_problem_registry_has_required_structure() -> None:
    assert PROBLEMS, "The problem registry must not be empty."
    for key, entry in PROBLEMS.items():
        assert isinstance(key, str) and key
        assert isinstance(entry, dict)
        assert entry.get("label"), f"Problem '{key}' is missing a label."
        assert callable(entry.get("factory")), f"Problem '{key}' is missing a callable factory."


def test_classical_constrained_problems_are_marked_for_gui_filtering() -> None:
    constrained_keys = {
        "binh2",
        "constrex",
        "golinski",
        "osyczka2",
        "srinivas",
        "tanaka",
        "water",
    }
    for key in constrained_keys:
        capabilities = PROBLEMS[key]["capabilities"]
        assert capabilities["constrained"] is True, key
        assert "cv" in capabilities["recommended_metrics"], key


def test_known_fronts_are_finite_unique_and_nondominated() -> None:
    for key, entry in PROBLEMS.items():
        loader = entry.get("known_pf_factory")
        if not callable(loader):
            continue
        factory = entry["factory"]
        defaults = {
            name: spec["default"]
            for name, spec in (entry.get("form_fields") or {}).items()
            if isinstance(spec, dict) and "default" in spec
        }
        accepted = {name: value for name, value in defaults.items() if name in inspect.signature(factory).parameters}
        problem = factory(**accepted)
        front = loader(problem)
        if front is None:
            continue
        front = np.asarray(front, dtype=float)
        assert front.ndim == 2 and front.shape[1] == problem.n_obj, key
        assert np.isfinite(front).all(), key
        assert len(np.unique(front, axis=0)) == len(front), key
        nondominated = NonDominatedSorting().do(front, only_non_dominated_front=True)
        assert len(nondominated) == len(front), key
        hv_config = resolve_hv_config(entry.get("label", key), problem.n_obj, pareto_front=front)
        assert hv_config is not None, key
        assert np.all(front < hv_config.raw_reference_point[None, :]), key
        assert np.all(hv_config.transform(front) < hv_config.reference_point[None, :]), key


def test_wfg3_2d_reference_front_stays_inside_analytical_objective_ranges() -> None:
    entry = PROBLEMS["wfg3_2d"]
    problem = entry["factory"]()
    front = np.asarray(entry["known_pf_factory"](problem), dtype=float)

    assert np.all(front >= -1e-12)
    assert np.max(front[:, 0]) <= 2.0 + 1e-12
    assert np.max(front[:, 1]) <= 4.0 + 1e-12
