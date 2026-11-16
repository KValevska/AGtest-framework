from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
from pymoo.core.problem import Problem
from pymoo.problems import get_problem

from pymoo_gui.algorithms import minimize
from pymoo_gui.algorithms.diskplus import cdipd_sort, make_diskplus
from pymoo_gui.algorithms.eps_nsga2 import make_eps_nsga2
from pymoo_gui.algorithms.learning_edmo import (
    CentralizedClassifier,
    LearningAcrossProblemsEDMO,
    make_learning_edmo,
)
from pymoo_gui.algorithms.maotspp import make_maotspp, tsp_penalty_sort
from pymoo_gui.algorithms.rnn_guided_dmo import make_rnn_guided_dmo
from pymoo_gui.algorithms.ts_nsga import lpd_ranks, make_ts_nsga, spd_ranks


REWRITTEN_MODULES = (
    "eps_nsga2.py",
    "diskplus.py",
    "learning_edmo.py",
    "maotspp.py",
    "rnn_guided_dmo.py",
    "ts_nsga.py",
)


def test_rewritten_algorithms_do_not_import_ready_algorithm_packages() -> None:
    root = Path(__file__).parents[1] / "src" / "pymoo_gui" / "algorithms"
    forbidden = ("pymoo.algorithms", "platypus", "sklearn", "platemo")
    for filename in REWRITTEN_MODULES:
        tree = ast.parse((root / filename).read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        assert not any(name.lower().startswith(forbidden) for name in imported), filename


class SwitchingProblem(Problem):
    def __init__(self) -> None:
        super().__init__(n_var=3, n_obj=2, xl=np.zeros(3), xu=np.ones(3))
        self.environment = 0.0

    def _evaluate(self, X, out, *args, **kwargs) -> None:
        shift = float(self.environment)
        out["F"] = np.column_stack(
            (np.sum((X - 0.2 * shift) ** 2, axis=1), np.sum((X - 1.0 + 0.1 * shift) ** 2, axis=1))
        )


def test_epsilon_nsga2_performs_connected_run_restart() -> None:
    problem = get_problem("zdt1", n_var=5)
    algorithm = make_eps_nsga2(
        problem,
        population_size=8,
        epsilons=0.05,
        window_size=1,
        improvement_threshold=100.0,
        minimum_population_size=4,
        maximum_population_size=16,
    )
    result = minimize(problem, algorithm, ("n_gen", 1), seed=3, verbose=False)

    assert result.F is not None
    assert algorithm.restart_count == 1
    assert algorithm.population_size <= 16


def test_diskplus_cdipd_and_runtime_are_constraint_aware() -> None:
    decisions = np.array([[0.1, 0.1], [0.9, 0.9]])
    objectives = np.array([[1.0, 1.0], [0.0, 0.0]])
    variance = np.full((2, 2), 0.1)
    constraints = np.array([[-0.1], [0.5]])
    fronts = cdipd_sort(
        decisions,
        objectives,
        variance,
        constraints,
        np.array([0.1, 0.1]),
        np.eye(2),
    )
    assert fronts[0] < fronts[1]

    result = minimize(
        get_problem("tnk"),
        make_diskplus(population_size=8, surrogate_generations=2, infill_batch_size=2),
        ("n_gen", 1),
        seed=4,
        verbose=False,
    )
    assert result.F.shape == (8, 2)


def test_learning_edmo_trains_central_model_and_transfers_between_dimensions() -> None:
    LearningAcrossProblemsEDMO.CENTRAL_MODEL = CentralizedClassifier()
    LearningAcrossProblemsEDMO.KNOWLEDGE_BASE = []
    first = make_learning_edmo(population_size=10, archive_size=10, learning_epochs=3)
    minimize(get_problem("zdt1", n_var=4), first, ("n_gen", 2), seed=8, verbose=False)

    assert first.classification_updates > 0
    assert LearningAcrossProblemsEDMO.KNOWLEDGE_BASE

    second = make_learning_edmo(population_size=10, archive_size=10, learning_epochs=3)
    result = minimize(get_problem("zdt1", n_var=7), second, ("n_gen", 1), seed=9, verbose=False)
    assert result.X.shape == (10, 7)
    assert second.evaluator.n_eval > 20


def test_maotspp_penalty_prioritizes_feasibility_and_runs() -> None:
    fronts = tsp_penalty_sort(
        np.zeros((2, 1)),
        np.array([[9.0, 9.0], [0.0, 0.0]]),
        np.ones((2, 2)),
        np.array([[-1.0], [1.0]]),
        np.ones((2, 1)),
        phase=2,
    )
    np.testing.assert_array_equal(fronts, [1, 2])

    result = minimize(
        get_problem("tnk"),
        make_maotspp(population_size=8, surrogate_generations=2, infill_batch_size=2),
        ("n_gen", 1),
        seed=5,
        verbose=False,
    )
    assert result.F.shape == (8, 2)


def test_rnn_guided_dmo_detects_changes_and_trains_weights_online() -> None:
    problem = SwitchingProblem()
    algorithm = make_rnn_guided_dmo(
        population_size=8,
        neighborhood_size=4,
        hidden_size=5,
        training_epochs=3,
        detector_fraction=0.5,
    )
    algorithm.setup_rng(6)
    algorithm.initialize(problem)
    initial_weights = algorithm.Wxh.copy()

    problem.environment = 1.0
    algorithm.step()
    problem.environment = 2.0
    algorithm.step()

    assert algorithm.detected_changes == 2
    assert algorithm.online_updates == 1
    assert algorithm.mutation_rate == 1.0 / problem.n_var
    assert not np.allclose(initial_weights, algorithm.Wxh)


def test_ts_nsga_implements_spd_lpd_and_stage_switch() -> None:
    objectives = np.array([[0.2, 0.2], [0.5, 0.5], [0.2, 0.8]])
    vectors = np.array([[0.5, 0.5], [0.1, 0.9]])
    ranks, d2, subregions = spd_ranks(objectives, np.zeros(3), vectors, theta=5.0)
    assert subregions[0] == subregions[1]
    assert ranks[0] < ranks[1]
    assert d2[0] < d2[1]

    lpd = lpd_ranks(
        np.array([[2.5, 0.0], [1.0, 1.0], [0.2, 1.0], [1.5, 0.2]]),
        np.zeros(4),
        division_level=3,
    )
    assert lpd[3] < lpd[0]

    problem = get_problem("dtlz2", n_var=8, n_obj=3)
    algorithm = make_ts_nsga(population_size=12, n_partitions=2)
    result = minimize(problem, algorithm, ("n_gen", 3), seed=7, verbose=False)
    assert result.F.shape == (12, 3)
    assert algorithm.stage == 2
    assert algorithm.mutation_rate == 1.0 / problem.n_var
