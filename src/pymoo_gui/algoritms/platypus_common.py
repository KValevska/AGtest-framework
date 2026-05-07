"""
EN: Adapters and validation helpers that let Platypus algorithms run in the pymoo GUI flow.
"""

# ------------------------------------------------------------------------------------
# File: platypus_common.py
# Contents: adapters between pymoo GUI runtime objects and Platypus algorithms.
# What happens here: pymoo problems are wrapped as Platypus problems and Platypus populations are exposed to callbacks.
# Role in the framework: lets selected Platypus optimizers run inside the existing GUI workflow.
# Author: mgr inz. Kristina Valevska
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
    """
    EN:
    Import required Platypus classes lazily and convert missing dependency errors.

    PL:
    Importuje klasy Platypus dopiero wtedy, gdy sa potrzebne. Dzieki temu
    aplikacja moze dzialac, nawet jesli uzytkownik nie wybiera algorytmow Platypus.

    Returns:
        tuple[Any, Any, Any]: EN: `Direction`, `Problem` and `Real` classes from Platypus.
                             PL: Klasy potrzebne do opisania problemu w bibliotece Platypus.

    Raises:
        ImportError: EN: If the optional `platypus-opt` package is missing.
                     PL: Gdy biblioteka Platypus nie jest zainstalowana.
    """
    try:
        from platypus import Direction, Problem, Real
    except ImportError as exc:
        raise ImportError("Install platypus-opt to use Platypus algorithms.") from exc
    return Direction, Problem, Real


def parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Parse a positive integer shared by Platypus-backed factories.

    PL:
    Sprawdza, czy parametr dla algorytmu Platypus jest dodatnia liczba calkowita.

    Args:
        value (Any): EN: Raw value to parse.
                     PL: Wartosc podana przez uzytkownika albo kod.
        field_name (str): EN: Field name used in validation errors.
                          PL: Nazwa pola w komunikacie bledu.

    Returns:
        int: EN: Parsed integer greater than or equal to 1.
             PL: Poprawna liczba calkowita co najmniej rowna 1.

    Raises:
        ValueError: EN: If parsing fails or the value is below 1.
                    PL: Gdy wartosc jest niepoprawna.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def parse_positive_float(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a strictly positive floating-point option.

    PL:
    Sprawdza, czy parametr jest liczba wieksza od zera.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{field_name} must be > 0, got {parsed}")
    return parsed


def parse_probability(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a probability constrained to the inclusive range [0, 1].

    PL:
    Sprawdza, czy parametr jest prawdopodobienstwem od 0 do 1.

    Raises:
        ValueError: EN: If the value cannot be parsed or is outside the range.
                    PL: Gdy wartosc nie jest liczba albo wykracza poza zakres.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1], got {parsed}")
    return parsed


def problem_n_obj(problem: Any, algorithm_name: str) -> int:
    """
    EN:
    Extract and validate the objective count required by Platypus multiobjective algorithms.

    PL:
    Pobiera liczbe funkcji celu z problemu i sprawdza, czy algorytm Platypus
    moze taki problem obsluzyc.

    Args:
        problem (Any): EN: pymoo-like problem exposing `n_obj`.
                       PL: Problem wybrany w aplikacji.
        algorithm_name (str): EN: Algorithm label used in error messages.
                              PL: Nazwa algorytmu do komunikatu bledu.

    Returns:
        int: EN: Objective count greater than or equal to 2.
             PL: Liczba funkcji celu, co najmniej 2.

    Raises:
        ValueError: EN: If `n_obj` is missing, invalid or below 2.
                    PL: Gdy problem nie ma poprawnej liczby celow.
    """
    try:
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selected problem does not expose a valid n_obj") from exc
    if n_obj < 2:
        raise ValueError(f"{algorithm_name} requires at least 2 objectives, got {n_obj}")
    return n_obj


def parse_epsilons(value: Any, n_obj: int, field_name: str = "epsilons") -> list[float]:
    """
    EN:
    Normalize epsilon settings to one positive value per objective.

    PL:
    Zamienia wpis epsilon na liste wartosci, po jednej dla kazdej funkcji celu.

    Args:
        value (Any): EN: Scalar, text or iterable epsilon input.
                     PL: Pojedyncza wartosc, tekst albo lista wartosci epsilon.
        n_obj (int): EN: Number of objectives that must be covered.
                     PL: Liczba celow, dla ktorych trzeba przygotowac epsilony.
        field_name (str): EN: Field name used in validation messages.
                          PL: Nazwa pola w komunikacie bledu.

    Returns:
        list[float]: EN: Positive epsilon value for each objective.
                     PL: Lista dodatnich epsilonow dla wszystkich celow.

    Raises:
        ValueError: EN: If values are not positive or the length is neither 1 nor `n_obj`.
                    PL: Gdy wartosci sa zle albo lista ma niepasujaca dlugosc.
    """
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
    """
    EN:
    Convert a pymoo problem into a Platypus `Problem` with matching variables,
    objective directions and constraints.

    PL:
    Tlumaczy problem z formatu pymoo na format Platypus, aby algorytmy z drugiej
    biblioteki mogly obliczac te same funkcje celu.
    """

    def __init__(self, pymoo_problem: Any):
        """
        EN:
        Build the Platypus problem wrapper and validate decision-variable bounds.

        PL:
        Przygotowuje opis problemu dla Platypus i sprawdza, czy kazda zmienna ma
        dolna i gorna granice.

        Args:
            pymoo_problem (Any): EN: Source pymoo problem to adapt.
                                 PL: Problem pymoo wybrany w aplikacji.

        Raises:
            ValueError: EN: If variables, objectives or finite bounds are invalid.
                        PL: Gdy brakuje poprawnych granic zmiennych albo liczby celow.
            ImportError: EN: If Platypus classes cannot be imported.
                         PL: Gdy biblioteka Platypus jest niedostepna.
        """
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
        """
        EN:
        Evaluate one Platypus solution by delegating to the wrapped pymoo problem.

        PL:
        Liczy wartosci funkcji celu dla jednego rozwiazania, korzystajac z
        oryginalnego problemu pymoo.

        Args:
            variables (Iterable[Any]): EN: Decision-variable values from Platypus.
                                       PL: Wartosci zmiennych sprawdzanego rozwiazania.

        Returns:
            Any: EN: Objective values, optionally paired with constraint values for Platypus.
                 PL: Wyniki funkcji celu, a przy ograniczeniach takze wartosci ograniczen.
        """
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
    """
    EN:
    pymoo-like read-only view over Platypus solution collections.

    PL:
    Udostepnia populacje Platypus w podobny sposob jak pymoo, aby callbacki GUI
    mogly pobierac `X`, `F` i `CV`.
    """

    def __init__(self, solutions: Iterable[Any]):
        """
        EN:
        Store a snapshot of Platypus solutions.

        PL:
        Zapamietuje aktualna liste rozwiazan z algorytmu Platypus.
        """
        self.solutions = list(solutions)

    def get(self, name: str) -> Optional[np.ndarray]:
        """
        EN:
        Return a population matrix compatible with pymoo's `Population.get` API.

        PL:
        Zwraca wybrane dane populacji: zmienne `X`, cele `F` albo naruszenia
        ograniczen `CV`.

        Args:
            name (str): EN: Requested field name, usually `X`, `F` or `CV`.
                        PL: Nazwa danych, ktore maja zostac pobrane.

        Returns:
            Optional[np.ndarray]: EN: Numeric matrix/vector or `None` when unavailable.
                                  PL: Tabela liczb albo `None`, jesli takich danych nie ma.
        """
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
    """
    EN:
    pymoo-compatible facade around a stateful Platypus optimization algorithm.

    PL:
    Opakowuje algorytm Platypus tak, aby GUI widzialo go podobnie jak algorytm pymoo.
    """

    def __init__(self, pymoo_problem: Any, algorithm_factory: Callable[[Any], Any]):
        """
        EN:
        Adapt the problem and instantiate the underlying Platypus algorithm.

        PL:
        Przygotowuje problem dla Platypus i tworzy wybrany algorytm.

        Args:
            pymoo_problem (Any): EN: Source problem from the GUI registry.
                                 PL: Problem wybrany w GUI.
            algorithm_factory (Callable[[Any], Any]): EN: Factory receiving the adapted Platypus problem.
                                                      PL: Funkcja tworzaca algorytm Platypus.
        """
        self.pymoo_problem = pymoo_problem
        self.problem_adapter = PlatypusProblemAdapter(pymoo_problem)
        self.platypus_algorithm = algorithm_factory(self.problem_adapter.problem)
        self.n_gen = 0
        self.evaluator = SimpleNamespace(n_eval=0)
        self.pop = PlatypusPopulationView([])

    def _sync_state(self) -> None:
        """
        EN:
        Synchronize evaluation count and population view after a Platypus step.

        PL:
        Aktualizuje liczbe ocen i populacje po kolejnym kroku algorytmu.
        """
        self.evaluator.n_eval = int(getattr(self.platypus_algorithm, "nfe", 0))
        result = getattr(self.platypus_algorithm, "result", None) or getattr(self.platypus_algorithm, "population", [])
        self.pop = PlatypusPopulationView(result)

    def _should_stop(self, termination: Any, max_generations: Optional[int]) -> bool:
        """
        EN:
        Decide whether the generation limit extracted from termination has been reached.

        PL:
        Sprawdza, czy algorytm wykonal juz wymagana liczbe generacji.
        """
        if max_generations is None:
            return False
        return self.n_gen >= max_generations

    def gui_minimize(self, *, problem: Any, termination: Any, seed: Optional[int] = None, callback: Any = None, **kwargs: Any) -> Result:
        """
        EN:
        Run the Platypus algorithm step-by-step and expose a pymoo `Result`.

        PL:
        Uruchamia algorytm Platypus krok po kroku, wysyla dane do GUI i na koncu
        zwraca wynik podobny do wyniku pymoo.

        Args:
            problem (Any): EN: Original problem associated with the run.
                           PL: Oryginalny problem optymalizacyjny.
            termination (Any): EN: pymoo-style termination criterion.
                               PL: Warunek zakonczenia obliczen.
            seed (Optional[int]): EN: Random seed for reproducible Platypus and NumPy behavior.
                                  PL: Ziarno losowe pozwalajace powtorzyc przebieg.
            callback (Any): EN: Optional generation callback called after each step.
                            PL: Funkcja wywolywana po kazdej generacji.
            **kwargs (Any): EN: Ignored compatibility options accepted by pymoo minimize calls.
                            PL: Dodatkowe opcje pozostawione dla zgodnosci z pymoo.

        Returns:
            Result: EN: pymoo result object containing final `X`, `F` and `CV`.
                    PL: Wynik z koncowymi zmiennymi, wartosciami celow i ograniczeniami.
        """
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
    """
    EN:
    Extract a maximum generation count from common pymoo termination representations.

    PL:
    Odczytuje limit generacji z roznych formatow warunku stopu uzywanych przez pymoo.

    Args:
        termination (Any): EN: `None`, tuple, `NoTermination` or termination object.
                           PL: Warunek stopu przekazany przez GUI lub pymoo.

    Returns:
        Optional[int]: EN: Maximum generation count, or `None` for unbounded runs.
                       PL: Liczba generacji albo `None`, gdy nie ma limitu.

    Raises:
        ValueError: EN: If an exposed generation count is not positive.
                    PL: Gdy podany limit generacji jest niepoprawny.
    """
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
