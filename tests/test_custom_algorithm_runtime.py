from __future__ import annotations

import numpy as np

from pymoo_gui.algorithms import minimize
from pymoo_gui.algorithms.gde3 import make_gde3
from pymoo_gui.algorithms.ibea import make_ibea
from pymoo_gui.algorithms.piea import make_piea
from pymoo_gui.algorithms.ssde import make_ssde
from pymoo_gui.algorithms.tea import make_tea
from pymoo_gui.problems import TanakaProblem, make_schaffer


def test_ibea_runtime_on_schaffer() -> None:
    problem = make_schaffer()
    algorithm = make_ibea(pop_size=16, seed=1)
    result = minimize(problem, algorithm, ("n_gen", 2), seed=1, verbose=False)

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape[0] == 16
    assert result.F.shape[0] == 16
    assert result.CV.shape[0] == 16


def test_gde3_runtime_on_schaffer() -> None:
    problem = make_schaffer()
    algorithm = make_gde3(pop_size=16, seed=1)
    result = minimize(problem, algorithm, ("n_gen", 2), seed=1, verbose=False)

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape[0] == 16
    assert result.F.shape[0] == 16
    assert result.CV.shape[0] == 16


def test_piea_runtime_on_schaffer() -> None:
    problem = make_schaffer()
    algorithm = make_piea(
        population_size=8,
        eta=3,
        surrogate_generations=2,
        adaptation_window=4,
        seed=1,
    )
    result = minimize(problem, algorithm, ("n_gen", 2), seed=1, verbose=False)

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape == (8, 1)
    assert result.F.shape == (8, 2)
    assert algorithm.evaluator.n_eval == 10
    assert np.isclose(algorithm.indicator_probabilities.sum(), 1.0)


def test_tea_runtime_on_schaffer() -> None:
    problem = make_schaffer()
    algorithm = make_tea(
        population_size=8,
        surrogate_generations=2,
        infill_batch_size=2,
        seed=1,
    )
    result = minimize(problem, algorithm, ("n_gen", 2), seed=1, verbose=False)

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape == (8, 1)
    assert result.F.shape == (8, 2)
    assert algorithm.evaluator.n_eval > 8
    assert algorithm.evaluator.n_eval <= 12


def test_tea_preserves_individual_problem_constraints() -> None:
    algorithm = make_tea(
        population_size=8,
        surrogate_generations=1,
        infill_batch_size=2,
        seed=2,
    )
    result = minimize(TanakaProblem(), algorithm, ("n_gen", 1), seed=2, verbose=False)

    assert result.F is not None
    assert algorithm._constraint_values.shape == (algorithm.evaluator.n_eval, 2)
    assert np.all(algorithm.archive_CV >= 0.0)


def test_ssde_runtime_on_schaffer() -> None:
    problem = make_schaffer()
    algorithm = make_ssde(
        population_size=8,
        num_nodes=8,
        learning_rate=0.2,
        neighborhood_radius=8.0,
        training_epochs=2,
        seed=4,
    )
    result = minimize(problem, algorithm, ("n_gen", 2), seed=4, verbose=False)

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape == (8, 1)
    assert result.F.shape == (8, 2)
    assert algorithm.evaluator.n_eval > 8
    assert algorithm.weights.shape == (8, 3)
    assert np.all(np.isfinite(algorithm.weights))
