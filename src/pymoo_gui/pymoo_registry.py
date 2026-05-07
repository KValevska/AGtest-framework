"""
EN: Dynamic discovery and instantiation helpers for pymoo algorithms and problems.
"""

# ------------------------------------------------------------------------------------
# File: pymoo_registry.py
# Contents: pymoo algorithm and problem discovery utilities plus instantiation helpers.
# What happens here: pymoo modules are scanned, signatures are inspected and reference directions are prepared.
# Role in the framework: supports dynamic integration of pymoo components in the doctoral-dissertation framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from functools import lru_cache
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

import numpy as np

_SCHAFFER_N1_CLASS: Optional[str] = None
_SCHAFFER_N1_ENTRY_KEY: Optional[str] = None
_SCHAFFER_N1_SOURCE: Optional[str] = None


@dataclass(frozen=True)
class AlgorithmEntry:
    """
    EN:
    Registry record describing one discovered pymoo algorithm class.

    PL:
    Przechowuje informacje o znalezionym algorytmie: nazwe dla GUI, klase i modul.
    """

    key: str                 # label do GUI
    cls: Type[Any]           # klasa algorytmu z pymoo
    module: str              # pełna ścieżka modułu


@dataclass(frozen=True)
class ProblemEntry:
    """
    EN:
    Registry record describing one discovered pymoo problem class.

    PL:
    Przechowuje informacje o znalezionym problemie: nazwe dla GUI, klase i modul.
    """

    key: str                 # label do GUI
    cls: Type[Any]           # klasa problemu z pymoo
    module: str              # pełna ścieżka modułu


def _safe_import(name: str) -> Optional[ModuleType]:
    """
    EN:
    Import a module and return `None` instead of propagating import errors.

    PL:
    Probuje zaimportowac modul; gdy sie nie uda, zwraca `None`, aby skanowanie
    moglo isc dalej.
    """
    try:
        return importlib.import_module(name)
    except Exception:
        return None


def _walk_modules(package_name: str) -> Iterable[str]:
    """
    EN:
    Yield fully-qualified module names under an importable package.

    PL:
    Zwraca nazwy modulow znajdujacych sie we wskazanym pakiecie.
    """
    pkg = _safe_import(package_name)
    if pkg is None or not hasattr(pkg, "__path__"):
        return []
    for m in pkgutil.walk_packages(pkg.__path__, package_name + "."):
        yield m.name


def _is_concrete_class(obj: Any) -> bool:
    """
    EN:
    Check whether an object is a non-abstract class.

    PL:
    Sprawdza, czy obiekt jest konkretna klasa, ktora mozna brac pod uwage.
    """
    return inspect.isclass(obj) and not inspect.isabstract(obj)


def _short_module(mod: str, keep: int = 2) -> str:
    """
    EN:
    Shorten a module path to its last components for compact GUI labels.

    PL:
    Skraca dluga sciezke modulu, aby etykieta w GUI byla czytelniejsza.
    """
    parts = mod.split(".")
    return ".".join(parts[-keep:]) if len(parts) >= keep else mod


@lru_cache(maxsize=1)
def discover_algorithms() -> Dict[str, AlgorithmEntry]:
    """
    EN:
    Discover concrete pymoo `Algorithm` subclasses and cache the result.

    PL:
    Automatycznie wyszukuje klasy algorytmow w pymoo. Pierwsze wywolanie moze
    byc wolniejsze, ale potem wynik jest przechowywany w pamieci.

    Auto-discovery wszystkich klas algorytmów w pymoo (subklasy Algorithm).
    """
    try:
        from pymoo.core.algorithm import Algorithm
    except Exception as e:
        raise RuntimeError("Nie można zaimportować pymoo.core.algorithm.Algorithm") from e

    entries: Dict[str, AlgorithmEntry] = {}

    # Przeszukiwanie po pymoo.algorithms.* i zbienie klasy
    for mod_name in _walk_modules("pymoo.algorithms"):
        mod = _safe_import(mod_name)
        if mod is None:
            continue

        for _, obj in inspect.getmembers(mod, _is_concrete_class):
            try:
                if not issubclass(obj, Algorithm):
                    continue
            except Exception:
                continue

            if obj is Algorithm:
                continue
            if obj.__name__.startswith("_"):
                continue

            label = f"{obj.__name__}  [{_short_module(obj.__module__, keep=3)}]"
            # duplikaty: dopinamy licznik
            if label in entries:
                label = f"{label}#{len(entries)}"
            entries[label] = AlgorithmEntry(key=label, cls=obj, module=obj.__module__)

    return dict(sorted(entries.items(), key=lambda kv: kv[0].lower()))


@lru_cache(maxsize=1)
def discover_problems() -> Dict[str, ProblemEntry]:
    """
    EN:
    Discover concrete pymoo `Problem` subclasses and cache the result.

    PL:
    Automatycznie wyszukuje problemy dostepne w pymoo i dodatkowo probuje
    odnalezc wariant Schaffera.

    Auto-discovery problemów w pymoo (subklasy Problem).
    """
    try:
        from pymoo.core.problem import Problem
    except Exception as e:
        raise RuntimeError("Nie można zaimportować pymoo.core.problem.Problem") from e

    entries: Dict[str, ProblemEntry] = {}

    for mod_name in _walk_modules("pymoo.problems"):
        mod = _safe_import(mod_name)
        if mod is None:
            continue

        for _, obj in inspect.getmembers(mod, _is_concrete_class):
            try:
                if not issubclass(obj, Problem):
                    continue
            except Exception:
                continue

            if obj is Problem:
                continue
            if obj.__name__.startswith("_"):
                continue

            label = f"{obj.__name__}  [{_short_module(obj.__module__, keep=3)}]"
            if label in entries:
                label = f"{label}#{len(entries)}"
            entries[label] = ProblemEntry(key=label, cls=obj, module=obj.__module__)

    def _evaluate_F(inst, X: np.ndarray) -> Optional[np.ndarray]:
        """
        EN:
        Evaluate objective values with either public `evaluate` or private `_evaluate` fallback.

        PL:
        Liczy funkcje celu problemu, uzywajac zwyklego API albo awaryjnego sposobu.
        """
        try:
            return inst.evaluate(X, return_values_of=["F"])
        except Exception:
            try:
                out: Dict[str, Any] = {}
                inst._evaluate(X, out)
                return out.get("F")
            except Exception:
                return None

    def _is_schaffer_n1(cls: Type[Any]) -> bool:
        """
        EN:
        Detect whether a problem class behaves like the two-objective Schaffer N1 benchmark.

        PL:
        Sprawdza, czy dana klasa problemu odpowiada znanemu problemowi Schaffera.
        """
        try:
            inst = instantiate_with_params(cls, {})
        except Exception:
            return False
        try:
            if int(getattr(inst, "n_obj", 0)) != 2:
                return False
        except Exception:
            return False
        X = np.array([[0.0], [2.0]], dtype=float)
        F = _evaluate_F(inst, X)
        if F is None:
            return False
        arr = np.asarray(F)
        if arr.ndim != 2 or arr.shape[1] != 2:
            return False
        target = np.array([[0.0, 4.0], [4.0, 0.0]], dtype=float)
        return np.allclose(arr, target, atol=1e-6, rtol=1e-6)

    global _SCHAFFER_N1_CLASS, _SCHAFFER_N1_ENTRY_KEY, _SCHAFFER_N1_SOURCE
    _SCHAFFER_N1_CLASS = None
    _SCHAFFER_N1_ENTRY_KEY = None
    _SCHAFFER_N1_SOURCE = None
    for entry in entries.values():
        name = entry.cls.__name__
        if "schaffer" not in name.lower():
            continue
        if _is_schaffer_n1(entry.cls):
            _SCHAFFER_N1_CLASS = name
            _SCHAFFER_N1_ENTRY_KEY = entry.key
            break

    if _SCHAFFER_N1_CLASS is None:
        factory = try_get_problem_factory()
        if factory is not None:
            for name in ("schaffer", "schaffer_n1"):
                try:
                    inst = factory(name)
                except Exception:
                    continue
                try:
                    if int(getattr(inst, "n_obj", 0)) != 2:
                        continue
                except Exception:
                    continue
                n_var = getattr(inst, "n_var", None)
                try:
                    n_var = int(n_var) if n_var is not None else 1
                except Exception:
                    n_var = 1
                if n_var < 1:
                    n_var = 1
                X = np.zeros((2, n_var))
                X[1, 0] = 2.0
                F = _evaluate_F(inst, X)
                if F is None:
                    continue
                arr = np.asarray(F)
                if arr.ndim != 2 or arr.shape[1] != 2:
                    continue
                target = np.array([[0.0, 4.0], [4.0, 0.0]])
                if not np.allclose(arr, target, atol=1e-3, rtol=1e-3):
                    continue
                key = f"SchafferN1  [get_problem:{name}]"
                entries[key] = ProblemEntry(key=key, cls=type(inst), module=type(inst).__module__)
                _SCHAFFER_N1_CLASS = type(inst).__name__
                _SCHAFFER_N1_ENTRY_KEY = key
                _SCHAFFER_N1_SOURCE = name
                print(f"Schaffer loaded via get_problem('{name}') -> {type(inst).__name__}")
                break
        if _SCHAFFER_N1_CLASS is None:
            print("Schaffer not available in this pymoo")

    return dict(sorted(entries.items(), key=lambda kv: kv[0].lower()))


def get_schaffer_n1_class_name() -> Optional[str]:
    """
    EN:
    Return the discovered Schaffer N1 class name, if available.

    PL:
    Zwraca nazwe znalezionej klasy Schaffera, jesli udalo sie ja wykryc.
    """
    return _SCHAFFER_N1_CLASS


def get_schaffer_n1_entry_key() -> Optional[str]:
    """
    EN:
    Return the GUI registry key for discovered Schaffer N1.

    PL:
    Zwraca klucz wpisu Schaffera w rejestrze GUI.
    """
    return _SCHAFFER_N1_ENTRY_KEY


def get_schaffer_n1_source() -> Optional[str]:
    """
    EN:
    Return the `get_problem` source name used for Schaffer N1 fallback discovery.

    PL:
    Zwraca nazwe uzyta do pobrania problemu Schaffera przez `get_problem`.
    """
    return _SCHAFFER_N1_SOURCE


def class_signature(cls: Type[Any]) -> inspect.Signature:
    """
    EN:
    Return the constructor signature without `self`.

    PL:
    Zwraca liste parametrow konstruktora bez `self`, co pozwala zbudowac
    formularz ustawien w GUI.

    Zwraca podpis konstruktora (bez self). Przydaje się do generowania formularza parametrów.
    """
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return inspect.Signature()
    params = [p for p in sig.parameters.values() if p.name != "self"]
    return sig.replace(parameters=params)


def can_instantiate_with_defaults(cls: Type[Any]) -> bool:
    """
    EN:
    Check whether a class constructor can be called without required user parameters.

    PL:
    Sprawdza, czy klase mozna utworzyc tylko z wartosciami domyslnymi.
    """
    sig = class_signature(cls)
    for p in sig.parameters.values():
        if p.default is inspect._empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY):
            return False
    return True


def instantiate_with_params(cls: Type[Any], params: Dict[str, Any]) -> Any:
    """
    EN:
    Instantiate a class using only parameters accepted by its constructor.

    PL:
    Tworzy obiekt klasy, przekazujac tylko te parametry, ktore konstruktor rozumie.

    Tworzy instancję klasy, filtrując parametry po podpisie.
    """
    sig = class_signature(cls)
    filtered = {k: v for k, v in params.items() if k in sig.parameters and v is not None}
    return cls(**filtered)


def needs_reference_directions(algorithm_cls: Type[Any]) -> bool:
    """
    EN:
    Detect whether an algorithm constructor requires `ref_dirs`.

    PL:
    Sprawdza, czy algorytm potrzebuje kierunkow odniesienia, np. NSGA-III lub MOEA/D.

    Wykrywa algorytmy typu NSGA3/MOEAD, ktore chca ref_dirs (czesto obowiazkowo).
    """
    sig = class_signature(algorithm_cls)
    uses_ref_dirs = "ref_dirs" in sig.parameters
    if "ref_dirs" in sig.parameters:
        p = sig.parameters["ref_dirs"]
        return p.default is inspect._empty
    return False


def make_reference_directions(n_obj: int, method: str = "das-dennis", n_partitions: int = 12, seed: int = 1) -> np.ndarray:
    """
    EN:
    Generate pymoo reference directions for many-objective algorithms.

    PL:
    Tworzy kierunki odniesienia potrzebne algorytmom wielokryterialnym.

    Generator ref_dirs do algorytmow many-objective.

    pymoo pokazuje uzycie get_reference_directions(...) dla NSGA-III i MOEA/D.
    """
    from pymoo.util.ref_dirs import get_reference_directions

    return get_reference_directions(method, n_obj, n_partitions=n_partitions, seed=seed)


def instantiate_algorithm_for_problem(algorithm_cls: Type[Any], problem_n_obj: int, user_params: Dict[str, Any]) -> Any:
    """
    EN:
    Instantiate an algorithm and generate valid reference directions when required.

    PL:
    Tworzy algorytm dla problemu. Jesli algorytm potrzebuje kierunkow odniesienia,
    funkcja przygotowuje je automatycznie.

    Specjalny helper: jesli algorytm wymaga ref_dirs, to generujemy.
    """
    params = dict(user_params)

    ref_dir_algos = {
        "NSGA3",
        "RNSGA3",
        "UNSGA3",
        "CTAEA",
        "RVEA",
        "MOEAD",
        "ParallelMOEAD",
    }
    sig = class_signature(algorithm_cls)
    uses_ref_dirs = "ref_dirs" in sig.parameters

    if algorithm_cls.__name__ in ref_dir_algos and uses_ref_dirs:
        object_params = {
            "sampling",
            "selection",
            "crossover",
            "mutation",
            "output",
            "repair",
            "survival",
        }
        for key in list(params.keys()):
            if key in object_params:
                val = params.get(key)
                if val is None or isinstance(val, str):
                    params.pop(key, None)
            elif isinstance(params.get(key), str):
                val = params[key].strip()
                if val == "" or val.lower() == "none":
                    params.pop(key, None)


    ref_dir_method = params.get("ref_dir_method", "das-dennis")
    try:
        ref_dir_method = str(ref_dir_method)
    except Exception:
        ref_dir_method = "das-dennis"
    try:
        n_partitions = int(params.get("n_partitions", 12))
    except Exception:
        n_partitions = 12
    try:
        seed = int(params.get("seed", 1))
    except Exception:
        seed = 1

    def _is_missing_ref_dirs(val):
        """
        EN:
        Check whether a `ref_dirs` value should be regenerated.

        PL:
        Sprawdza, czy kierunki odniesienia sa puste i trzeba je utworzyc.
        """
        if val is None:
            return True
        if isinstance(val, str):
            return val.strip() == ""
        return False

    if "ref_dirs" in sig.parameters and _is_missing_ref_dirs(params.get("ref_dirs")):
        # Ref_dirs albo wymagane, albo brak. Generujemy sensownie.
        params["ref_dirs"] = make_reference_directions(
            problem_n_obj,
            method=ref_dir_method,
            n_partitions=n_partitions,
            seed=seed,
        )

        # sporo algorytmow sugeruje pop_size = liczba ref_dirs (czesto + wyrownanie)
        if "pop_size" in params:
            try:
                pop_size = int(params["pop_size"]) if params["pop_size"] is not None else None
            except Exception:
                pop_size = None
            if pop_size is None or pop_size <= 0:
                params["pop_size"] = int(np.asarray(params["ref_dirs"]).shape[0])

        params.pop("ref_dir_method", None)
        params.pop("n_partitions", None)
        ref_dirs = params.get("ref_dirs")
        ref_dirs_arr = None
        invalid_reason = None
        if not _is_missing_ref_dirs(ref_dirs):
            try:
                ref_dirs_arr = np.asarray(ref_dirs, dtype=float)
            except Exception:
                ref_dirs_arr = None
                invalid_reason = "coerce"
        if ref_dirs_arr is None:
            invalid_reason = invalid_reason or "missing"
        else:
            if ref_dirs_arr.ndim != 2 or ref_dirs_arr.shape[1] != int(problem_n_obj):
                invalid_reason = "shape"
            elif not np.isfinite(ref_dirs_arr).all():
                invalid_reason = "finite"

        if invalid_reason is not None:
            params["ref_dirs"] = make_reference_directions(
                problem_n_obj,
                method=ref_dir_method,
                n_partitions=n_partitions,
                seed=seed,
            )
            ref_dirs_arr = np.asarray(params["ref_dirs"], dtype=float)
            print(f"{algorithm_cls.__name__} ref_dirs regenerated (reason={invalid_reason})")
        else:
            params["ref_dirs"] = ref_dirs_arr

        ref_count = None
        try:
            ref_count = int(ref_dirs_arr.shape[0])
        except Exception:
            ref_count = None
        if ref_count is not None and ref_count > 0:
            pop_raw = params.get("pop_size")
            try:
                pop_size = int(pop_raw) if pop_raw is not None else None
            except Exception:
                pop_size = None
            if pop_size is None or pop_size <= 0:
                params["pop_size"] = ref_count
                print(f"{algorithm_cls.__name__} pop_size set to {ref_count} (ref_dirs length)")
            elif pop_size < ref_count:
                params["pop_size"] = ref_count
                print(f"{algorithm_cls.__name__} pop_size increased to {ref_count} (ref_dirs length)")

        ref_shape = None
        ref_dtype = None
        ref_min = None
        ref_max = None
        ref_finite = None
        if ref_dirs_arr is not None:
            ref_shape = tuple(ref_dirs_arr.shape)
            ref_dtype = str(ref_dirs_arr.dtype)
            ref_finite = bool(np.isfinite(ref_dirs_arr).all())
            if ref_dirs_arr.size > 0:
                try:
                    ref_min = float(np.min(ref_dirs_arr))
                    ref_max = float(np.max(ref_dirs_arr))
                except Exception:
                    ref_min = None
                    ref_max = None

        def _cls_name(obj):
            """
            EN:
            Return a short class name for debug output.

            PL:
            Zwraca krotka nazwe klasy do komunikatu diagnostycznego.
            """
            return type(obj).__name__ if obj is not None else "None"

        print(
            f"{algorithm_cls.__name__} validated: "
            f"n_obj={int(problem_n_obj)}, "
            f"n_var={params.get("n_var")}, "
            f"pop_size={params.get("pop_size")}, "
            f"eliminate_duplicates={params.get("eliminate_duplicates")}, "
            f"sampling={_cls_name(params.get("sampling"))}, "
            f"crossover={_cls_name(params.get("crossover"))}, "
            f"mutation={_cls_name(params.get("mutation"))}, "
            f"ref_dirs_shape={ref_shape}, "
            f"ref_dirs_dtype={ref_dtype}, "
            f"ref_dirs_min={ref_min}, "
            f"ref_dirs_max={ref_max}, "
            f"ref_dirs_finite={ref_finite}"
        )

    return instantiate_with_params(algorithm_cls, params)


def try_get_problem_factory() -> Optional[Callable[..., Any]]:
    """
    EN:
    Return `pymoo.problems.get_problem` when it is available.

    PL:
    Pobiera fabryke problemow z pymoo, jesli dana wersja biblioteki ja udostepnia.

    W nowszym pymoo istnieje pymoo.problems.get_problem (wg dokumentacji),
    ale bywa, że ktoś może mieć starszą wersję lub inny import. 
    """
    mod = _safe_import("pymoo.problems")
    if mod is None:
        return None
    fn = getattr(mod, "get_problem", None)
    if callable(fn):
        return fn
    return None
