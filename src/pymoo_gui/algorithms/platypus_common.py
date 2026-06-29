# Adapters and validation helpers that let Platypus algorithms run in the pymoo GUI flow.

# ------------------------------------------------------------------------------------
# Module: platypus_common.py
# Summary: adapters between pymoo GUI runtime objects and Platypus algorithms.
# Implementation: pymoo problems are wrapped as Platypus problems and Platypus populations are exposed to callbacks.
# Responsibility: lets selected Platypus optimizers run inside the existing GUI workflow.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math
import random
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Optional

import numpy as np
from pymoo.core.termination import NoTermination
from pymoo.core.result import Result


def _platypus_imports() -> tuple[Any, Any, Any]:
    # Import required Platypus classes lazily and convert missing dependency errors.
    # Importuje klasy Platypus dopiero wtedy, gdy sa potrzebne. Dzieki temu
    # Returns:
    # tuple[Any, Any, Any]: `Direction`, `Problem` and `Real` classes from Platypus.
    # Raises:
    # ImportError: If the optional `platypus-opt` package is missing.
    try:
        from platypus import Direction, Problem, Real
    except ImportError as exc:
        raise ImportError("Install platypus-opt to use Platypus algorithms.") from exc
    return Direction, Problem, Real


def parse_positive_int(value: Any, field_name: str) -> int:
    # Parse a positive integer shared by Platypus-backed factories.
    # Args:
    # value (Any): Raw value to parse.
    # field_name (str): Field name used in validation errors.
    # Returns:
    # int: Parsed integer greater than or equal to 1.
    # Raises:
    # ValueError: If parsing fails or the value is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def parse_positive_float(value: Any, field_name: str) -> float:
    # Parse a strictly positive floating-point option.
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{field_name} must be > 0, got {parsed}")
    return parsed


def parse_probability(value: Any, field_name: str) -> float:
    # Parse a probability constrained to the inclusive range [0, 1].
    # Raises:
    # ValueError: If the value cannot be parsed or is outside the range.
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1], got {parsed}")
    return parsed


def problem_n_obj(problem: Any, algorithm_name: str) -> int:
    # Extract and validate the objective count required by Platypus multiobjective algorithms.
    # moze taki problem obsluzyc.
    # Args:
    # problem (Any): pymoo-like problem exposing `n_obj`.
    # algorithm_name (str): Algorithm label used in error messages.
    # Returns:
    # int: Objective count greater than or equal to 2.
    # Raises:
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"{algorithm_name} requires at least 2 objectives, got {n_obj}")
    return n_obj


def parse_epsilons(value: Any, n_obj: int, field_name: str = "epsilons") -> list[float]:
    # Normalize epsilon settings to one positive value per objective.
    # Args:
    # value (Any): Scalar, text or iterable epsilon input.
    # n_obj (int): Number of objectives that must be covered.
    # field_name (str): Field name used in validation messages.
    # Returns:
    # list[float]: Positive epsilon value for each objective.
    # Raises:
    # ValueError: If values are not positive or the length is neither 1 nor `n_obj`.
    if value is None:
        values: list[Any] = [0.01]
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            values = [0.01]
        else:
            values = [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]
    else:
        try:
            values = list(value)
        except TypeError:
            values = [value]

    eps = [parse_positive_float(item, field_name) for item in values]
    if len(eps) == 1:
        eps = eps * n_obj
    if len(eps) != n_obj:
        raise ValueError(f"{field_name} must have length 1 or n_obj={n_obj}, got {len(eps)}")
    return eps


class PlatypusProblemAdapter:
    # Convert a pymoo problem into a Platypus `Problem` with matching variables,
    # objective directions and constraints.
    # Tlumaczy problem z formatu pymoo na format Platypus, aby algorytmy z drugiej

    def __init__(self, pymoo_problem: Any):
        # Build the Platypus problem wrapper and validate decision-variable bounds.
        # Args:
        # pymoo_problem (Any): Source pymoo problem to adapt.
        # Raises:
        # ValueError: If variables, objectives or finite bounds are invalid.
        # ImportError: If Platypus classes cannot be imported.
        Direction, Problem, Real = _platypus_imports()
        self.pymoo_problem = pymoo_problem
        self.n_var = parse_positive_int(getattr(pymoo_problem, "n_var", None), "n_var")
        self.n_obj = problem_n_obj(pymoo_problem, "Platypus")
        self.n_ieq_constr = int(getattr(pymoo_problem, "n_ieq_constr", getattr(pymoo_problem, "n_constr", 0)) or 0)
        self.n_eq_constr = int(getattr(pymoo_problem, "n_eq_constr", 0) or 0)
        self.n_constr = self.n_ieq_constr + self.n_eq_constr

        xl = np.asarray(getattr(pymoo_problem, "xl", None), dtype=float).reshape(-1)
        xu = np.asarray(getattr(pymoo_problem, "xu", None), dtype=float).reshape(-1)
        if xl.size == 1:
            xl = np.repeat(xl, self.n_var)
        if xu.size == 1:
            xu = np.repeat(xu, self.n_var)
        if xl.size != self.n_var or xu.size != self.n_var:
            raise ValueError("Platypus adapter requires finite lower and upper bounds for every variable.")
        if not np.isfinite(xl).all() or not np.isfinite(xu).all():
            raise ValueError("Platypus adapter requires finite lower and upper bounds.")

        self.problem = Problem(self.n_var, self.n_obj, self.n_constr)
        self.problem.types[:] = [Real(float(lo), float(hi)) for lo, hi in zip(xl, xu)]
        self.problem.directions[:] = [Direction.MINIMIZE for _ in range(self.n_obj)]
        if self.n_ieq_constr:
            self.problem.constraints[: self.n_ieq_constr] = ["<=0" for _ in range(self.n_ieq_constr)]
        if self.n_eq_constr:
            self.problem.constraints[self.n_ieq_constr :] = ["==0" for _ in range(self.n_eq_constr)]
        self.problem.function = self._evaluate

    def _evaluate(self, variables: Iterable[Any]) -> Any:
        # Evaluate one Platypus solution by delegating to the wrapped pymoo problem.
        # Args:
        # variables (Iterable[Any]): Decision-variable values from Platypus.
        # Returns:
        # Any: Objective values, optionally paired with constraint values for Platypus.
        x = np.asarray(list(variables), dtype=float).reshape(1, -1)
        return_values = ["F"]
        if self.n_ieq_constr:
            return_values.append("G")
        if self.n_eq_constr:
            return_values.append("H")

        out = self.pymoo_problem.evaluate(
            x,
            return_values_of=return_values,
            return_as_dictionary=True,
        )
        f = np.asarray(out.get("F"), dtype=float).reshape(1, -1)[0].tolist()
        constraints: list[float] = []
        if self.n_ieq_constr:
            constraints.extend(np.asarray(out.get("G"), dtype=float).reshape(1, -1)[0].tolist())
        if self.n_eq_constr:
            constraints.extend(np.asarray(out.get("H"), dtype=float).reshape(1, -1)[0].tolist())
        return (f, constraints) if self.n_constr else f


class PlatypusPopulationView:
    # pymoo-like read-only view over Platypus solution collections.
    # Udostepnia populacje Platypus w podobny sposob jak pymoo, aby callbacki GUI

    def __init__(self, solutions: Iterable[Any]):
        # Store a snapshot of Platypus solutions.
        self.solutions = list(solutions)

    def get(self, name: str) -> Optional[np.ndarray]:
        # Return a population matrix compatible with pymoo's `Population.get` API.
        # Args:
        # name (str): Requested field name, usually `X`, `F` or `CV`.
        # Returns:
        # Optional[np.ndarray]: Numeric matrix/vector or `None` when unavailable.
        key = str(name).upper()
        if not self.solutions:
            return None
        if key == "X":
            return np.asarray([list(solution.variables) for solution in self.solutions], dtype=float)
        if key == "F":
            return np.asarray([list(solution.objectives) for solution in self.solutions], dtype=float)
        if key == "CV":
            return np.asarray([float(getattr(solution, "constraint_violation", 0.0)) for solution in self.solutions])
        return None


class PlatypusAlgorithmAdapter:
    # pymoo-compatible facade around a stateful Platypus optimization algorithm.
    # Opakowuje algorytm Platypus tak, aby GUI widzialo go podobnie jak algorytm pymoo.

    def __init__(self, pymoo_problem: Any, algorithm_factory: Callable[[Any], Any]):
        # Adapt the problem and instantiate the underlying Platypus algorithm.
        # Args:
        # pymoo_problem (Any): Source problem from the GUI registry.
        # algorithm_factory (Callable[[Any], Any]): Factory receiving the adapted Platypus problem.
        self.pymoo_problem = pymoo_problem
        self.problem_adapter = PlatypusProblemAdapter(pymoo_problem)
        self.platypus_algorithm = algorithm_factory(self.problem_adapter.problem)
        self.n_gen = 0
        self.evaluator = SimpleNamespace(n_eval=0)
        self.pop = PlatypusPopulationView([])

    def _sync_state(self) -> None:
        # Synchronize evaluation count and population view after a Platypus step.
        self.evaluator.n_eval = int(getattr(self.platypus_algorithm, "nfe", 0))
        result = getattr(self.platypus_algorithm, "result", None) or getattr(self.platypus_algorithm, "population", [])
        self.pop = PlatypusPopulationView(result)

    def _should_stop(self, termination: Any, max_generations: Optional[int]) -> bool:
        # Decide whether the generation limit extracted from termination has been reached.
        if max_generations is None:
            return False
        return self.n_gen >= max_generations

    def gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int] = None, callback: Any = None, **kwargs: Any) -> Result:
        # Run the Platypus algorithm step-by-step and expose a pymoo `Result`.
        # Args:
        # problem (Any): Original problem associated with the run.
        # termination (Any): pymoo-style termination criterion.
        # seed (Optional[int]): Random seed for reproducible Platypus and NumPy behavior.
        # callback (Any): Optional generation callback called after each step.
        # **kwargs (Any): Ignored compatibility options accepted by pymoo minimize calls.
        # Returns:
        # Result: pymoo result object containing final `X`, `F` and `CV`.
        if seed is not None:
            random.seed(int(seed))
            np.random.seed(int(seed))

        max_generations = termination_generations(termination)
        while not self._should_stop(termination, max_generations):
            self.platypus_algorithm.step()
            self.n_gen += 1
            self._sync_state()
            if callback is not None:
                callback(self)

        result = Result()
        result.algorithm = self
        result.problem = problem
        result.X = self.pop.get("X")
        result.F = self.pop.get("F")
        result.CV = self.pop.get("CV")
        return result


def termination_generations(termination: Any) -> Optional[int]:
    # Extract a maximum generation count from common pymoo termination representations.
    # Args:
    # termination (Any): `None`, tuple, `NoTermination` or termination object.
    # Returns:
    # Optional[int]: Maximum generation count, or `None` for unbounded runs.
    # Raises:
    # ValueError: If an exposed generation count is not positive.
    if termination is None:
        return None
    if isinstance(termination, tuple) and len(termination) >= 2 and str(termination[0]).lower() == "n_gen":
        return parse_positive_int(termination[1], "n_gen")
    if isinstance(termination, NoTermination) or termination.__class__.__name__ == "NoTermination":
        return None
    n_max_gen = getattr(termination, "n_max_gen", None)
    if n_max_gen is not None and math.isfinite(float(n_max_gen)):
        return parse_positive_int(n_max_gen, "n_max_gen")
    return None
