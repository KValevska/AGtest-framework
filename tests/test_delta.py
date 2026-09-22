from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest
from pymoo.core.population import Population

from pymoo_gui.algorithms import ALGORITHMS, make_generation_callback
from pymoo_gui.metrics import compute_delta, compute_metrics, is_delta_supported


def test_classical_delta_keeps_endpoint_and_spacing_penalties() -> None:
    pf = np.array([[0.0, 1.0], [1.0, 0.0]])
    uneven = np.array([[0.0, 1.0], [0.25, 0.75], [1.0, 0.0]])
    truncated = np.array([[0.25, 0.75], [0.5, 0.5], [0.75, 0.25]])

    assert compute_delta(pf, pf) == pytest.approx(0.0)
    assert compute_delta(uneven, pf) == pytest.approx(0.5)
    assert compute_delta(truncated, pf) == pytest.approx(0.5)
    assert compute_delta(uneven[::-1], pf[::-1]) == pytest.approx(0.5)
    assert compute_metrics(uneven, pf).delta == pytest.approx(0.5)


@pytest.mark.parametrize("n_obj", [3, 5, 10])
def test_generalized_delta_penalizes_missing_extremes(n_obj: int) -> None:
    pf = np.eye(n_obj)
    assert compute_delta(pf, pf) == pytest.approx(0.0)
    assert compute_delta(pf[:-1], pf) == pytest.approx(1.0 / n_obj)
    assert compute_delta(pf[:-1][::-1], pf[::-1]) == pytest.approx(1.0 / n_obj)
    assert compute_metrics(pf[:-1], pf).delta == pytest.approx(1.0 / n_obj)


def test_generalized_delta_measures_nonuniform_spacing() -> None:
    pf = np.eye(3)
    front = np.vstack([pf, [0.5, 0.5, 0.0]])
    # Three nearest distances are sqrt(1/2); the fourth is sqrt(3/2).
    small, large = np.sqrt(0.5), np.sqrt(1.5)
    expected = 1.5 * (large - small) / (3.0 * small + large)
    assert compute_delta(front, pf) == pytest.approx(expected)
    assert compute_delta(np.repeat(pf[:1], 3, axis=0), pf) == pytest.approx(1.0)
    assert np.isfinite(compute_delta(np.vstack([front, front[0]]), pf))


@pytest.mark.parametrize("n_obj", [2, 3])
def test_delta_requires_valid_reference_and_enough_feasible_points(n_obj: int) -> None:
    pf = np.eye(n_obj)
    assert compute_delta(pf[:1], pf) is None
    assert compute_delta(pf, pf[:1]) is None
    assert compute_delta(pf, np.eye(n_obj + 1)) is None
    assert compute_metrics(pf, None).delta is None
    assert compute_metrics(pf, pf, cv=np.ones(n_obj)).delta is None
    assert compute_metrics(pf, pf, cv=np.arange(n_obj)).delta is None
    dirty = np.vstack([pf, np.full(n_obj, np.nan)])
    assert compute_delta(dirty, dirty) == pytest.approx(0.0)


@pytest.mark.parametrize("algorithm_key", [*ALGORITHMS, None, "custom_algorithm"])
@pytest.mark.parametrize("n_obj", [2, 3])
def test_generation_callback_computes_delta_for_every_algorithm(algorithm_key, n_obj: int) -> None:
    pf = np.eye(n_obj)
    population = Population.new("F", pf, "CV", np.zeros((n_obj, 1)))
    algorithm = SimpleNamespace(pop=population, n_gen=1, evaluator=SimpleNamespace(n_eval=n_obj))
    payloads = []
    callback = make_generation_callback(
        payloads.append,
        SimpleNamespace(n_obj=n_obj, n_var=1),
        known_pf=pf,
        algorithm_key=algorithm_key,
    )

    callback.notify(algorithm)

    assert is_delta_supported(algorithm_key, n_obj)
    assert payloads[0]["delta"] == pytest.approx(0.0)
    assert payloads[0]["n_nds"] == n_obj
    assert payloads[0]["diagnostics"] == []
