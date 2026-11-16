from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest
from pymoo.problems import get_problem

from pymoo_gui.algorithms import ALGORITHMS, minimize
from pymoo_gui.problems import PROBLEMS


STANDALONE_KEYS = (
    "age",
    "eps_moea",
    "eps_nsga2",
    "moead",
    "nsga2",
    "nsga3",
    "moead_iepsilon",
    "rnsga3",
    "rvea",
    "spea2",
    "hype",
)

SMOKE_PARAMETERS = {
    "age": {"pop_size": 12},
    "eps_moea": {"population_size": 12, "epsilons": 0.05},
    "eps_nsga2": {"population_size": 12, "epsilons": 0.05},
    "moead": {"n_partitions": 11, "n_neighbors": 4},
    "nsga2": {"pop_size": 12},
    "nsga3": {"pop_size": 12, "n_partitions": 11},
    "moead_iepsilon": {"population_size": 12, "neighborhood_size": 4},
    "rnsga3": {"ref_points": [[0.2, 0.8], [0.8, 0.2]], "pop_per_ref_point": 5},
    "rvea": {"pop_size": 12, "n_partitions": 11},
    "spea2": {"pop_size": 12},
    "hype": {"pop_size": 12, "n_samples": 100},
}


@pytest.mark.parametrize("algorithm_key", STANDALONE_KEYS)
def test_registered_algorithm_does_not_import_ready_algorithm(algorithm_key: str) -> None:
    factory = ALGORITHMS[algorithm_key]["factory"]
    source_path = Path(inspect.getsourcefile(factory))
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    forbidden = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            forbidden.extend(alias.name for alias in node.names if alias.name == "platypus")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("pymoo.algorithms") or module.startswith("pymoo.operators") or module == "platypus":
                forbidden.append(module)
    assert forbidden == []


@pytest.mark.parametrize("algorithm_key", STANDALONE_KEYS)
def test_registered_standalone_algorithm_completes_two_generations(algorithm_key: str) -> None:
    problem = get_problem("zdt1", n_var=6)
    factory = ALGORITHMS[algorithm_key]["factory"]
    kwargs = dict(SMOKE_PARAMETERS[algorithm_key])
    if "problem" in inspect.signature(factory).parameters:
        kwargs["problem"] = problem
    algorithm = factory(**kwargs)
    result = minimize(problem, algorithm, ("n_gen", 2), seed=7, verbose=False)

    assert result.X.shape == (12, 6)
    assert result.F.shape == (12, 2)
    assert algorithm.evaluator.n_eval >= 36
    assert callable(getattr(algorithm, "gui_minimize", None))


@pytest.mark.parametrize("problem_key,n_obj", [("dtlz2", 3), ("water", 5)])
def test_reference_direction_algorithms_adapt_to_objective_count(problem_key: str, n_obj: int) -> None:
    problem = PROBLEMS[problem_key]["factory"]()

    rnsga3 = ALGORITHMS["rnsga3"]["factory"](problem=problem, pop_per_ref_point=3)
    assert rnsga3.ref_points.shape[1] == n_obj

    nsga3 = ALGORITHMS["nsga3"]["factory"](problem=problem, pop_size=20, n_partitions=12)
    result = minimize(problem, nsga3, ("n_gen", 1), seed=11, verbose=False)
    assert result.F.shape == (20, n_obj)

