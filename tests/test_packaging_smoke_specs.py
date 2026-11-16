from __future__ import annotations

from pymoo_gui.algorithms import ALGORITHMS, validate_algorithm_problem
from pymoo_gui.multi import build_multi_run_specs
from pymoo_gui.packaging_smoke import _algorithm_smoke_specs
from pymoo_gui.problems import PROBLEMS


def test_standalone_smoke_pairs_every_algorithm_with_a_compatible_problem() -> None:
    specs = _algorithm_smoke_specs(ALGORITHMS, PROBLEMS, build_multi_run_specs)

    assert {spec.algorithm_key for spec in specs} == set(ALGORITHMS)
    for spec in specs:
        problem = PROBLEMS[spec.problem_key]["factory"]()
        validate_algorithm_problem(ALGORITHMS[spec.algorithm_key], problem)
