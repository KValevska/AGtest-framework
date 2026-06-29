from __future__ import annotations

from pymoo_gui.algorithms import minimize
from pymoo_gui.algorithms.lmoea_ds import make_lmoea_ds
from pymoo_gui.problems import make_schaffer


def test_lmoea_ds_runtime_on_schaffer() -> None:
    problem = make_schaffer()
    algorithm = make_lmoea_ds(problem=problem, population_size=24, archive_size=24, guiding_vector_count=6, samples_per_direction=4, seed=1)
    result = minimize(problem, algorithm, ("n_gen", 2), seed=1, verbose=False)

    assert result.X is not None
    assert result.F is not None
    assert result.CV is not None
    assert result.X.shape[0] == 24
    assert result.F.shape[0] == 24
    assert result.CV.shape[0] == 24
