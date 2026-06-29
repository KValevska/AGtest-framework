from __future__ import annotations

from pymoo_gui.algorithms import minimize
from pymoo_gui.algorithms.gde3 import make_gde3
from pymoo_gui.algorithms.ibea import make_ibea
from pymoo_gui.problems import make_schaffer


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
