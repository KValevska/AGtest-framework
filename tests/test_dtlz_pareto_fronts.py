from __future__ import annotations

import numpy as np
import pytest

from pymoo_gui.problems import PROBLEMS


def _dtlz_front(problem_key: str, n_obj: int = 3) -> np.ndarray:
    entry = PROBLEMS[problem_key]
    problem = entry["factory"](n_obj=n_obj)
    front = entry["known_pf_factory"](problem)
    assert front is not None
    return np.asarray(front, dtype=float)


@pytest.mark.parametrize("problem_key", [f"dtlz{index}" for index in range(1, 8)])
def test_dtlz_fronts_are_dense_finite_and_three_dimensional(problem_key: str) -> None:
    front = _dtlz_front(problem_key)

    assert front.ndim == 2
    assert front.shape[0] >= 900
    assert front.shape[1] == 3
    assert np.isfinite(front).all()


def test_dtlz_fronts_follow_their_expected_geometry() -> None:
    dtlz1 = _dtlz_front("dtlz1")
    assert np.allclose(np.sum(dtlz1, axis=1), 0.5)

    for problem_key in ("dtlz2", "dtlz3", "dtlz4", "dtlz5", "dtlz6"):
        front = _dtlz_front(problem_key)
        assert np.allclose(np.linalg.norm(front, axis=1), 1.0)

    for problem_key in ("dtlz5", "dtlz6"):
        front = _dtlz_front(problem_key)
        assert np.allclose(front[:, 0], front[:, 1])


def test_dtlz7_front_uses_only_the_disconnected_optimal_intervals() -> None:
    front = _dtlz_front("dtlz7")
    first_objectives = front[:, :-1]
    in_first_interval = (first_objectives >= 0.0) & (first_objectives <= 0.251412)
    in_second_interval = (first_objectives >= 0.631627) & (first_objectives <= 0.859401)
    expected_last = 6.0 - np.sum(
        first_objectives * (1.0 + np.sin(3.0 * np.pi * first_objectives)),
        axis=1,
    )

    assert np.all(in_first_interval | in_second_interval)
    assert np.allclose(front[:, -1], expected_last)
