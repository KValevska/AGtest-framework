from __future__ import annotations

from pymoo_gui.algorithms import ALGORITHMS
from pymoo_gui.problems import PROBLEMS


def test_algorithm_registry_has_required_structure() -> None:
    assert ALGORITHMS, "The algorithm registry must not be empty."
    for key, entry in ALGORITHMS.items():
        assert isinstance(key, str) and key
        assert isinstance(entry, dict)
        assert entry.get("label"), f"Algorithm '{key}' is missing a label."
        assert callable(entry.get("factory")), f"Algorithm '{key}' is missing a callable factory."


def test_problem_registry_has_required_structure() -> None:
    assert PROBLEMS, "The problem registry must not be empty."
    for key, entry in PROBLEMS.items():
        assert isinstance(key, str) and key
        assert isinstance(entry, dict)
        assert entry.get("label"), f"Problem '{key}' is missing a label."
        assert callable(entry.get("factory")), f"Problem '{key}' is missing a callable factory."
