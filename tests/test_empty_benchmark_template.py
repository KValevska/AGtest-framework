from __future__ import annotations

import numpy as np
import pytest

from pymoo_gui.problems.empty_benchmark_template import (
    EMPTY_BENCHMARK_TEMPLATE_DEFINITION,
    EmptyBenchmarkTemplate,
    empty_benchmark_known_pf,
    make_empty_benchmark_template,
)


def test_empty_benchmark_template_evaluates_vectorized_objectives() -> None:
    problem = EmptyBenchmarkTemplate(n_var=3, n_obj=4, lower_bound=-2.0, upper_bound=2.0)
    out: dict[str, np.ndarray] = {}

    problem._evaluate(np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]), out)

    assert problem.n_var == 3
    assert problem.n_obj == 4
    assert problem.n_ieq_constr == 0
    assert out["F"].shape == (2, 4)
    assert np.isfinite(out["F"]).all()


def test_empty_benchmark_template_validates_configuration() -> None:
    with pytest.raises(ValueError, match="n_var"):
        EmptyBenchmarkTemplate(n_var=0)
    with pytest.raises(ValueError, match="n_obj"):
        EmptyBenchmarkTemplate(n_obj=1)
    with pytest.raises(ValueError, match="lower_bound"):
        EmptyBenchmarkTemplate(lower_bound=1.0, upper_bound=1.0)


def test_empty_benchmark_template_exposes_registration_contract() -> None:
    problem = make_empty_benchmark_template()

    assert EMPTY_BENCHMARK_TEMPLATE_DEFINITION["factory"] is make_empty_benchmark_template
    assert EMPTY_BENCHMARK_TEMPLATE_DEFINITION["known_pf_factory"] is empty_benchmark_known_pf
    assert empty_benchmark_known_pf(problem) is None
