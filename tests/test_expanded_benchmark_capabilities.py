from __future__ import annotations

import inspect

import numpy as np
import pytest

from pymoo_gui.algorithms import (
    ALGORITHMS,
    AlgorithmProblemCompatibilityError,
    compatibility_matrix,
    minimize,
    validate_algorithm_problem,
)
from pymoo_gui.algorithms.encoding_operators import bitflip_mutation, binary_crossover
from pymoo_gui.metrics.quality import compute_dynamic_average, compute_igdx, compute_psp
from pymoo_gui.problems import PROBLEMS
from pymoo_gui.problems.dynamic import DynamicDFProblem


def _make(key: str):
    entry = PROBLEMS[key]
    signature = inspect.signature(entry["factory"])
    values = {
        name: spec["default"]
        for name, spec in entry.get("form_fields", {}).items()
        if isinstance(spec, dict) and "default" in spec and name in signature.parameters
    }
    return entry["factory"](**values)


def test_every_problem_and_algorithm_declares_capabilities() -> None:
    for key, entry in PROBLEMS.items():
        caps = entry["capabilities"]
        assert caps["variable_type"] in {"real", "binary", "integer", "mixed"}, key
        assert caps["recommended_metrics"], key
    for key, entry in ALGORITHMS.items():
        assert entry["capabilities"]["variable_types"], key


@pytest.mark.parametrize("key", [*(f"dascmop{i}" for i in range(1, 10)), "c1dtlz1", "c2dtlz2", "dc3dtlz3"])
def test_local_constrained_families_have_finite_objectives_and_constraints(key: str) -> None:
    problem = _make(key)
    rng = np.random.default_rng(7)
    X = rng.uniform(problem.xl, problem.xu, size=(12, problem.n_var))
    values = problem.evaluate(X, return_as_dictionary=True)
    assert np.asarray(values["F"]).shape == (12, problem.n_obj)
    assert np.asarray(values["G"]).shape == (12, problem.n_ieq_constr)
    assert np.isfinite(values["F"]).all()
    assert np.isfinite(values["G"]).all()


@pytest.mark.parametrize("key", [f"mw{i}" for i in range(1, 15)])
def test_local_mw_objectives_and_constraints(key: str) -> None:
    problem = _make(key)
    assert type(problem).__module__ == "pymoo_gui.problems.mw"
    X = np.random.default_rng(9).uniform(problem.xl, problem.xu, size=(8, problem.n_var))
    values = problem.evaluate(X, return_as_dictionary=True)
    assert np.asarray(values["F"]).shape == (8, problem.n_obj)
    assert np.asarray(values["G"]).shape == (8, problem.n_ieq_constr)
    assert np.isfinite(values["F"]).all() and np.isfinite(values["G"]).all()


@pytest.mark.parametrize("key", ["dascmop1", "dascmop9", "c1dtlz1", "c2dtlz2", "dtlz2_ls500", "mmf1", "df1", "df9", "zdt5"])
def test_new_known_fronts_are_finite_and_dimensionally_correct(key: str) -> None:
    entry, problem = PROBLEMS[key], _make(key)
    front = entry["known_pf_factory"](problem)
    assert front is not None and len(front) > 0
    assert np.asarray(front).ndim == 2
    assert np.asarray(front).shape[1] == problem.n_obj
    assert np.isfinite(front).all()


def test_zdt5_is_local_binary_and_only_encoding_aware_algorithms_are_allowed() -> None:
    problem = _make("zdt5")
    assert type(problem).__module__ == "pymoo_gui.problems.discrete"
    validate_algorithm_problem(ALGORITHMS["nsga2"], problem)
    with pytest.raises(AlgorithmProblemCompatibilityError, match="binary"):
        validate_algorithm_problem(ALGORITHMS["pimd"], problem)
    algorithm = ALGORITHMS["nsga2"]["factory"](pop_size=12)
    result = minimize(problem, algorithm, ("n_gen", 2), seed=3)
    assert set(np.unique(result.X)).issubset({0, 1})


def test_binary_operators_never_create_fractional_values() -> None:
    rng = np.random.default_rng(2)
    X = rng.integers(0, 2, size=(10, 30))
    pairs = np.column_stack((np.arange(10), np.roll(np.arange(10), 1)))
    children = binary_crossover(X, pairs, 1.0, rng)
    mutated = bitflip_mutation(children, 0.2, rng)
    assert set(np.unique(mutated)).issubset({0, 1})


def test_dynamic_problem_advances_and_population_is_reevaluated() -> None:
    problem = DynamicDFProblem(1, change_period=1, severity=10)
    algorithm = ALGORITHMS["nsga2"]["factory"](pop_size=10)
    minimize(problem, algorithm, ("n_gen", 2), seed=4)
    assert problem.time == pytest.approx(0.2)
    assert algorithm.evaluator.n_eval == 10 + 2 * 10 + 2 * 10


def test_dynamic_and_encoding_incompatibilities_have_explicit_reasons() -> None:
    with pytest.raises(AlgorithmProblemCompatibilityError, match="dynamic-response"):
        validate_algorithm_problem(ALGORITHMS["umaoea"], _make("df1"))
    rows = compatibility_matrix({"zdt5": PROBLEMS["zdt5"], "df1": PROBLEMS["df1"]})
    assert any(row["status"] == "blocked" and row["reason"] for row in rows)
    assert any(row["status"] == "supported" for row in rows)


def test_dynamic_algorithms_are_available_for_dynamic_benchmarks() -> None:
    problem = _make("df1")
    validate_algorithm_problem(ALGORITHMS["learning_edmo"], problem)
    validate_algorithm_problem(ALGORITHMS["rnn_guided_dmo"], problem)


@pytest.mark.parametrize(
    "key,parameters",
    [
        (
            "learning_edmo",
            {
                "population_size": 10,
                "archive_size": 10,
                "candidate_multiplier": 1,
                "learning_epochs": 1,
                "knowledge_size": 4,
            },
        ),
        (
            "rnn_guided_dmo",
            {
                "population_size": 10,
                "neighborhood_size": 4,
                "hidden_size": 4,
                "training_epochs": 1,
            },
        ),
    ],
)
def test_dynamic_algorithms_advance_and_respond_to_df_environment(key: str, parameters: dict) -> None:
    problem = DynamicDFProblem(1, change_period=1, severity=10)
    algorithm = ALGORITHMS[key]["factory"](**parameters)

    result = minimize(problem, algorithm, ("n_gen", 2), seed=17, verbose=False)

    assert problem.time == pytest.approx(0.2)
    assert np.isfinite(result.F).all()
    if key == "rnn_guided_dmo":
        assert algorithm.detected_changes == 2


def test_surrogate_constraint_contracts_match_algorithm_scope() -> None:
    constrained = _make("tanaka")
    unconstrained = _make("kursawe")
    with pytest.raises(AlgorithmProblemCompatibilityError, match="unconstrained"):
        validate_algorithm_problem(ALGORITHMS["disk"], constrained)
    for key in ("peaplus", "tea", "tspp"):
        with pytest.raises(AlgorithmProblemCompatibilityError, match="requires"):
            validate_algorithm_problem(ALGORITHMS[key], unconstrained)


def test_multimodal_and_dynamic_metrics() -> None:
    problem = _make("mmf1")
    reference = problem.pareto_set(100)
    assert compute_igdx(reference, reference) == pytest.approx(0.0)
    assert compute_psp(reference, reference) == pytest.approx(1.0)
    assert compute_dynamic_average([0.3, None, 0.1, np.nan]) == pytest.approx(0.2)

