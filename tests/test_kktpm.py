from __future__ import annotations

import numpy as np
from pymoo.constraints.from_bounds import ConstraintsFromBounds
from pymoo.gradient.automatic import AutomaticDifferentiation
from pymoo.indicators.kktpm import KKTPM
from pymoo.problems import get_problem

from pymoo_gui.metrics import compute_kktpm


def test_kktpm_includes_variable_bounds_for_zdt1_pareto_points() -> None:
    X = np.zeros((3, 30), dtype=float)
    X[:, 0] = [0.1, 0.3, 0.7]
    ideal = np.array([0.0, 0.0], dtype=float)

    problem = get_problem("zdt1", n_var=30)
    reference_problem = ConstraintsFromBounds(AutomaticDifferentiation(get_problem("zdt1", n_var=30)))
    expected = KKTPM().calc(X, reference_problem, ideal=ideal.copy())
    actual = compute_kktpm(X, problem, ideal=ideal.copy())

    assert actual is not None
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-10)
    assert np.max(actual) < 1e-10


def test_kktpm_does_not_duplicate_preconverted_bound_constraints() -> None:
    X = np.zeros((2, 30), dtype=float)
    X[:, 0] = [0.2, 0.8]
    ideal = np.array([0.0, 0.0], dtype=float)
    wrapped_problem = ConstraintsFromBounds(AutomaticDifferentiation(get_problem("zdt1", n_var=30)))

    expected = KKTPM().calc(X, wrapped_problem, ideal=ideal.copy())
    actual = compute_kktpm(X, wrapped_problem, ideal=ideal.copy())

    assert actual is not None
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-10)


def test_kktpm_preserves_problem_constraints_when_adding_bounds() -> None:
    X = np.array([[1.0, 1.0], [2.0, 1.0], [3.0, 2.0]], dtype=float)
    ideal = np.array([0.0, 0.0], dtype=float)

    problem = get_problem("bnh")
    reference_problem = ConstraintsFromBounds(AutomaticDifferentiation(get_problem("bnh")))
    expected = KKTPM().calc(X, reference_problem, ideal=ideal.copy())
    actual = compute_kktpm(X, problem, ideal=ideal.copy())

    assert actual is not None
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-9)


def test_default_numerical_step_is_stable_near_zdt1_endpoint() -> None:
    X = np.full((1, 30), 1e-5, dtype=float)
    X[0, 0] = 1.66e-8
    problem = get_problem("zdt1", n_var=30)

    values = compute_kktpm(X, problem, ideal=np.array([0.0, 0.0], dtype=float))

    assert values is not None
    assert values[0] < 1e-3
