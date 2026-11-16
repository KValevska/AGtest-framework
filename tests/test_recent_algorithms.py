from __future__ import annotations

import numpy as np
import pytest

from pymoo_gui.algorithms import ALGORITHMS, minimize, validate_algorithm_problem
from pymoo_gui.algorithms.disk import distribution_weights, make_disk
from pymoo_gui.algorithms.diskplus import make_diskplus
from pymoo_gui.algorithms.maotspp import make_maotspp
from pymoo_gui.algorithms.peaplus import cppd, make_peaplus
from pymoo_gui.algorithms.piea import make_piea
from pymoo_gui.algorithms.surrogate_common import (
    Kriging,
    dominance,
    graph_sort,
    probability_leq,
)
from pymoo_gui.algorithms.ssde import make_ssde
from pymoo_gui.algorithms.tea import make_tea
from pymoo_gui.algorithms.tspp import make_tspp, tspp_sort
from pymoo_gui.problems import TanakaProblem, make_schaffer


RECENT_KEYS = (
    "piea",
    "tea",
    "ssde",
    "disk",
    "diskplus",
    "peaplus",
    "tspp",
    "maotspp",
)


@pytest.mark.parametrize("algorithm_key", RECENT_KEYS)
def test_recent_algorithm_registry_entries_document_provenance(algorithm_key: str) -> None:
    entry = ALGORITHMS[algorithm_key]

    assert entry["implementation_type"] == "adapted_port"
    assert entry["reference"]
    assert entry["verified_against"]
    assert "no claim" in entry["verified_against"] or algorithm_key == "tea"


def test_probability_and_dominance_mechanisms() -> None:
    objectives = np.array([[0.0, 1.0], [1.0, 0.0], [2.0, 2.0], [0.0, 0.0]])
    np.testing.assert_array_equal(graph_sort(dominance(objectives)), [2, 2, 3, 1])

    constraints = np.array([[-1.0], [-1.0], [0.2], [0.2]])
    assert not dominance(objectives, constraints)[3, 2]
    assert dominance(objectives, constraints)[0, 3]
    np.testing.assert_equal(
        probability_leq(np.array([-1.0, 0.0, 1.0]), np.zeros(3)),
        [1.0, 0.5, 0.0],
    )


def test_disk_density_and_constrained_probability_order() -> None:
    decisions = np.array([[0.0], [1.0], [2.0]])
    weights = distribution_weights(decisions, np.zeros(1), np.ones((1, 1)))
    np.testing.assert_allclose(weights, np.exp(-np.array([0.0, 0.5, 2.0])), rtol=1e-8)

    fronts = cppd(
        np.zeros((2, 2)),
        np.ones((2, 2)),
        np.array([[-1.0], [1.0]]),
        np.ones((2, 1)),
    )
    np.testing.assert_array_equal(fronts, [1, 2])


def test_tspp_phase_two_prioritizes_feasibility() -> None:
    fronts = tspp_sort(
        np.zeros((2, 1)),
        np.array([[9.0, 9.0], [0.0, 0.0]]),
        np.ones((2, 2)),
        np.array([[-1.0], [1.0]]),
        np.ones((2, 1)),
        2,
    )
    np.testing.assert_array_equal(fronts, [1, 2])


def test_ported_kriging_interpolates_linear_trend() -> None:
    rng = np.random.default_rng(5)
    decisions = rng.random((12, 2))
    targets = 2.0 + 3.0 * decisions[:, 0] - decisions[:, 1]
    model = Kriging().fit(decisions, targets)
    query = rng.random((5, 2))
    mean, variance = model.predict(query)

    np.testing.assert_allclose(mean, 2.0 + 3.0 * query[:, 0] - query[:, 1], atol=1e-6)
    assert np.all(variance >= 0.0)


@pytest.mark.parametrize(
    ("factory", "problem", "extra"),
    [
        (make_disk, make_schaffer, {}),
        (make_diskplus, TanakaProblem, {}),
        (make_peaplus, TanakaProblem, {}),
        (make_tspp, TanakaProblem, {}),
        (make_maotspp, TanakaProblem, {}),
    ],
)
def test_new_surrogate_algorithm_runtime(factory, problem, extra) -> None:
    algorithm = factory(
        population_size=8,
        surrogate_generations=2,
        infill_batch_size=2,
        seed=11,
        **extra,
    )
    payload_generations: list[int] = []

    def callback(current) -> None:
        payload_generations.append(current.n_gen)

    result = minimize(
        problem(),
        algorithm,
        ("n_gen", 2),
        seed=11,
        verbose=False,
        callback=callback,
    )

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape[0] == 8
    assert result.F.shape[1] == 2
    assert np.all(np.isfinite(result.F))
    assert payload_generations == [1, 2]
    assert algorithm.evaluator.n_eval > 8


def test_constrained_only_algorithms_are_rejected_before_factory_execution() -> None:
    with pytest.raises(ValueError, match="requires a benchmark"):
        validate_algorithm_problem(ALGORITHMS["diskplus"], make_schaffer())

    validate_algorithm_problem(ALGORITHMS["diskplus"], TanakaProblem())
    validate_algorithm_problem(ALGORITHMS["maotspp"], TanakaProblem())


@pytest.mark.parametrize(
    ("factory", "kwargs"),
    [
        (make_piea, {"eta": 3, "adaptation_window": 4}),
        (make_tea, {"infill_batch_size": 2}),
        (
            make_ssde,
            {
                "num_nodes": 8,
                "learning_rate": 0.2,
                "neighborhood_radius": 8.0,
                "training_epochs": 2,
            },
        ),
    ],
)
def test_stage_one_recent_algorithms_are_reproducible(factory, kwargs) -> None:
    common = {"population_size": 8, "surrogate_generations": 2, "seed": 17}
    if factory is make_ssde:
        common.pop("surrogate_generations")
    first = factory(**common, **kwargs)
    second = factory(**common, **kwargs)
    first_result = minimize(make_schaffer(), first, ("n_gen", 2), seed=17, verbose=False)
    second_result = minimize(make_schaffer(), second, ("n_gen", 2), seed=17, verbose=False)

    np.testing.assert_allclose(first_result.X, second_result.X)
    np.testing.assert_allclose(first_result.F, second_result.F)
