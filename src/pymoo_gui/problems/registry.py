# Problem registry, factory helpers and known Pareto-front loaders for the GUI.
# Includes helpers for loading known Pareto fronts used by previews and metrics.

# ------------------------------------------------------------------------------------
# Module: registry.py
# Summary: benchmark problem registry, factory functions and known Pareto-front loaders.
# Implementation: local and library-backed problems are described with GUI form fields and optional reference fronts.
# Responsibility: defines the optimization problem catalog for dissertation experiments.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict

import numpy as np
from pymoo.problems import get_problem
from pymoo.util.ref_dirs import get_reference_directions

from .binh2 import Binh2Problem
from .constrex import ConstrExProblem
from .fonseca import FonsecaProblem
from .golinski import GolinskiProblem
from .kursawe import KursaweProblem
from .lz09 import (
    LZ09F1Problem,
    LZ09F2Problem,
    LZ09F3Problem,
    LZ09F4Problem,
    LZ09F5Problem,
    LZ09F6Problem,
    LZ09F7Problem,
    LZ09F8Problem,
    LZ09F9Problem,
)
from .osyczka2 import Osyczka2Problem
from .schaffer import SchafferProblem
from .srinivas import SrinivasProblem
from .tanaka import TanakaProblem
from .uf import (
    UF10Problem,
    UF1Problem,
    UF2Problem,
    UF3Problem,
    UF4Problem,
    UF5Problem,
    UF6Problem,
    UF7Problem,
    UF8Problem,
    UF9Problem,
)
from .viennet2 import Viennet2Problem
from .viennet3 import Viennet3Problem
from .water import WaterProblem
from .wfg import default_wfg_n_var, make_wfg_problem


def _problem_entry(
    label: str,
    factory: Any,
    form_fields: Dict[str, Dict[str, Any]],
    form_note: str,
    known_pf_factory: Any = None,
) -> Dict[str, Any]:
    # Build a normalized registry entry for one selectable optimization problem.
    return {
        "label": label,
        "factory": factory,
        "form_fields": form_fields,
        "form_note": form_note,
        "known_pf_factory": known_pf_factory,
    }


def _normalize_pf(values: Any, expected_n_obj: int | None = None) -> np.ndarray | None:
    # Normalize known Pareto-front data to a finite unique objective matrix.
    if values is None:
        return None
    try:
        data = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        return None
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.ndim != 2 or data.shape[0] == 0:
        return None
    if expected_n_obj is not None and data.shape[1] != expected_n_obj:
        return None
    data = data[np.isfinite(data).all(axis=1)]
    if data.shape[0] == 0:
        return None
    _, first_indices = np.unique(data, axis=0, return_index=True)
    return data[np.sort(first_indices)]


def _load_pf_file(filename: str, expected_n_obj: int | None = None) -> np.ndarray | None:
    # Load a known Pareto-front text file located next to this module.
    pf_path = Path(__file__).with_name(filename)
    if not pf_path.exists():
        return None
    try:
        data = np.loadtxt(pf_path, dtype=float)
    except (OSError, ValueError):
        return None
    return _normalize_pf(data, expected_n_obj=expected_n_obj)


def _pf_file_loader(filename: str, expected_n_obj: int):
    # Create a known Pareto-front loader bound to one local `.pf` file.
    return lambda _problem, pf_name=filename, n_obj=expected_n_obj: _load_pf_file(pf_name, expected_n_obj=n_obj)


def _zdt_known_pf(problem: Any) -> np.ndarray | None:
    # Retrieve and normalize a known two-objective ZDT Pareto front from pymoo.
    pf_fn = getattr(problem, "pareto_front", None)
    if not callable(pf_fn):
        return None
    try:
        pf = pf_fn()
    except (TypeError, ValueError, AttributeError):
        return None
    return _normalize_pf(pf, expected_n_obj=2)


def _dtlz_reference_directions(n_obj: int, target_points: int) -> np.ndarray:
    # Select the densest Das-Dennis grid that stays within the requested point budget.
    n_partitions = 1
    while math.comb(n_partitions + n_obj - 1, n_obj - 1) <= target_points:
        n_partitions += 1
    n_partitions = max(1, n_partitions - 1)
    return get_reference_directions("das-dennis", n_obj, n_partitions=n_partitions)


def _dtlz_degenerate_known_pf(n_obj: int, n_points: int = 1000) -> np.ndarray:
    # Generate the analytical degenerate Pareto curve shared by DTLZ5 and DTLZ6.
    theta_1 = np.linspace(0.0, np.pi / 2.0, max(2, int(n_points)))
    thetas = np.column_stack(
        [theta_1] + [np.full(theta_1.shape[0], np.pi / 4.0)] * max(0, n_obj - 2)
    )
    cos_theta = np.cos(thetas)
    sin_theta = np.sin(thetas)
    pf = np.zeros((theta_1.shape[0], n_obj), dtype=float)
    for objective_index in range(n_obj):
        pf[:, objective_index] = np.prod(
            cos_theta[:, : n_obj - 1 - objective_index],
            axis=1,
        )
        if objective_index > 0:
            pf[:, objective_index] *= sin_theta[:, n_obj - 1 - objective_index]
    return pf


def _dtlz7_known_pf(n_obj: int, target_points: int = 2000) -> np.ndarray:
    # Generate a deterministic grid over the disconnected Pareto-optimal intervals of DTLZ7.
    intervals = ((0.0, 0.251412), (0.631627, 0.859401))
    free_dimensions = n_obj - 1
    points_per_interval = max(
        2,
        int((max(1, int(target_points)) / (len(intervals) ** free_dimensions)) ** (1.0 / free_dimensions)),
    )
    axis = np.concatenate(
        [np.linspace(start, stop, points_per_interval) for start, stop in intervals]
    )
    mesh = np.meshgrid(*([axis] * free_dimensions), indexing="ij")
    first_objectives = np.column_stack([values.reshape(-1) for values in mesh])
    last_objective = 2.0 * n_obj - np.sum(
        first_objectives * (1.0 + np.sin(3.0 * np.pi * first_objectives)),
        axis=1,
    )
    return np.column_stack([first_objectives, last_objective])


def _dtlz_known_pf(problem: Any, target_points: int = 2000) -> np.ndarray | None:
    # Generate a dense local Pareto-front approximation without remote reference files.
    try:
        n_obj = int(getattr(problem, "n_obj", 3))
    except (TypeError, ValueError):
        return None
    if n_obj < 2:
        return None

    problem_type = type(problem).__name__.lower()
    if problem_type in {"dtlz5", "dtlz6"}:
        pf = _dtlz_degenerate_known_pf(n_obj)
    elif problem_type == "dtlz7":
        pf = _dtlz7_known_pf(n_obj, target_points=target_points)
    else:
        ref_dirs = _dtlz_reference_directions(n_obj, max(2, int(target_points)))
        try:
            pf = problem.pareto_front(ref_dirs=ref_dirs)
        except (TypeError, ValueError, AttributeError):
            return None
    return _normalize_pf(pf, expected_n_obj=n_obj)


def _readonly_n_obj_field(label: str, n_obj: int) -> Dict[str, Any]:
    return {
        "default": int(n_obj),
        "kind": "int",
        "read_only": True,
        "tooltip": f"Wartość informacyjna dla {label}.",
    }


def _n_var_field(label: str, default: int, minimum: int = 1) -> Dict[str, Any]:
    return {
        "default": int(default),
        "kind": "int",
        "minimum": int(minimum),
        "tooltip": f"Liczba zmiennych przekazywana do problemu {label}.",
    }


def _zdt_entry(name: str, default_n_var: int) -> Dict[str, Any]:
    # Create a GUI registry entry for a pymoo ZDT problem.
    label = name.upper()
    return _problem_entry(
        label=label,
        factory=lambda n_var=default_n_var, problem_name=name: get_problem(problem_name, n_var=int(n_var)),
        form_fields={
            "n_var": _n_var_field(label, default_n_var),
            "n_obj": _readonly_n_obj_field(label, 2),
        },
        form_note=f"{label} używa parametru n_var. Liczba celów pozostaje stała i informacyjna.",
        known_pf_factory=_zdt_known_pf,
    )


def _dtlz_entry(name: str, default_n_var: int, default_n_obj: int = 3) -> Dict[str, Any]:
    # Create a GUI registry entry for a pymoo DTLZ problem.
    label = name.upper()
    return _problem_entry(
        label=label,
        factory=lambda n_var=default_n_var, n_obj=default_n_obj, problem_name=name: get_problem(
            problem_name,
            n_var=int(n_var),
            n_obj=int(n_obj),
        ),
        form_fields={
            "n_var": _n_var_field(label, default_n_var, minimum=3),
            "n_obj": {
                "default": default_n_obj,
                "kind": "int",
                "minimum": 2,
                "tooltip": f"Liczba celów dla {label}.",
            },
        },
        form_note=f"{label} przekazuje do pymoo zarówno n_var, jak i n_obj.",
        known_pf_factory=_dtlz_known_pf,
    )


def _local_entry(
    key_label: str,
    factory: Any,
    n_obj: int,
    pf_filename: str,
    n_var_default: int | None = None,
    n_var_minimum: int = 1,
    form_note: str | None = None,
) -> Dict[str, Any]:
    fields: Dict[str, Dict[str, Any]] = {"n_obj": _readonly_n_obj_field(key_label, n_obj)}
    if n_var_default is not None:
        fields = {
            "n_var": _n_var_field(key_label, n_var_default, minimum=n_var_minimum),
            "n_obj": _readonly_n_obj_field(key_label, n_obj),
        }
    return _problem_entry(
        label=key_label,
        factory=factory,
        form_fields=fields,
        form_note=form_note or f"{key_label} używa konfiguracji zgodnej z lokalną implementacją frameworka.",
        known_pf_factory=_pf_file_loader(pf_filename, expected_n_obj=n_obj),
    )


def _wfg_entry(problem_name: str, n_obj: int) -> Dict[str, Any]:
    label = f"{problem_name.upper()} ({n_obj}D)"
    default_n_var = default_wfg_n_var(n_obj)
    pf_filename = f"{problem_name.upper()}.{n_obj}D.pf"
    return _problem_entry(
        label=label,
        factory=lambda n_var=default_n_var, p_name=problem_name, objective_count=n_obj: make_wfg_problem(
            p_name,
            n_obj=objective_count,
            n_var=int(n_var),
        ),
        form_fields={
            "n_var": {
                "default": default_n_var,
                "kind": "int",
                "minimum": 2,
                "tooltip": f"Liczba zmiennych przekazywana do pymoo.get_problem('{problem_name}', ...).",
            },
            "n_obj": _readonly_n_obj_field(label, n_obj),
        },
        form_note=f"{label} korzysta bezpośrednio z implementacji pymoo i lokalnego pliku frontu Pareto.",
        known_pf_factory=_pf_file_loader(pf_filename, expected_n_obj=n_obj),
    )


def make_kursawe(n_var: int = 3) -> KursaweProblem:
    return KursaweProblem(n_var=int(n_var))


def make_schaffer() -> SchafferProblem:
    return SchafferProblem()


def make_zdt5():
    return get_problem("zdt5")


PROBLEMS: Dict[str, Dict[str, Any]] = {
    "kursawe": _local_entry(
        "Kursawe",
        make_kursawe,
        n_obj=2,
        pf_filename="KUR.pf",
        n_var_default=3,
        form_note="Kursawe używa parametru n_var. Liczba celów pozostaje stała i informacyjna.",
    ),
    "schaffer": _problem_entry(
        label="Schaffer",
        factory=make_schaffer,
        form_fields={"n_obj": _readonly_n_obj_field("Schaffer", 2)},
        form_note="Schaffer używa domyślnej konfiguracji lokalnej implementacji.",
        known_pf_factory=_pf_file_loader("SCH1.pf", expected_n_obj=2),
    ),
    "binh2": _local_entry("Binh2", Binh2Problem, n_obj=2, pf_filename="Binh2.pf"),
    "constrex": _local_entry("ConstrEx", ConstrExProblem, n_obj=2, pf_filename="ConstrEx.pf"),
    "fon": _local_entry(
        "FON",
        lambda n_var=3: FonsecaProblem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="FON.pf",
        n_var_default=3,
        form_note="FON pozwala zmienić liczbę zmiennych, ale domyślnie używa klasycznej konfiguracji n_var=3.",
    ),
    "golinski": _local_entry("Golinski", GolinskiProblem, n_obj=2, pf_filename="Golinski.pf"),
    "osyczka2": _local_entry("Osyczka2", Osyczka2Problem, n_obj=2, pf_filename="Osyczka2.pf"),
    "srinivas": _local_entry("Srinivas", SrinivasProblem, n_obj=2, pf_filename="Srinivas.pf"),
    "tanaka": _local_entry("Tanaka", TanakaProblem, n_obj=2, pf_filename="Tanaka.pf"),
    "viennet2": _local_entry("Viennet2", Viennet2Problem, n_obj=3, pf_filename="Viennet2.pf"),
    "viennet3": _local_entry("Viennet3", Viennet3Problem, n_obj=3, pf_filename="Viennet3.pf"),
    "water": _local_entry("Water", WaterProblem, n_obj=5, pf_filename="Water.pf"),
    "zdt1": _zdt_entry("zdt1", 30),
    "zdt2": _zdt_entry("zdt2", 30),
    "zdt3": _zdt_entry("zdt3", 30),
    "zdt4": _zdt_entry("zdt4", 10),
    "zdt5": _problem_entry(
        label="ZDT5",
        factory=make_zdt5,
        form_fields={"n_obj": _readonly_n_obj_field("ZDT5", 2)},
        form_note="ZDT5 jest problemem dyskretnym i w tym GUI używa domyślnej konfiguracji pymoo.",
    ),
    "zdt6": _zdt_entry("zdt6", 10),
    "dtlz1": _dtlz_entry("dtlz1", 7),
    "dtlz2": _dtlz_entry("dtlz2", 12),
    "dtlz3": _dtlz_entry("dtlz3", 12),
    "dtlz4": _dtlz_entry("dtlz4", 12),
    "dtlz5": _dtlz_entry("dtlz5", 12),
    "dtlz6": _dtlz_entry("dtlz6", 12),
    "dtlz7": _dtlz_entry("dtlz7", 22),
    "lz09_f1": _local_entry(
        "LZ09_F1",
        lambda n_var=10: LZ09F1Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F1.pf",
        n_var_default=10,
    ),
    "lz09_f2": _local_entry(
        "LZ09_F2",
        lambda n_var=30: LZ09F2Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F2.pf",
        n_var_default=30,
    ),
    "lz09_f3": _local_entry(
        "LZ09_F3",
        lambda n_var=30: LZ09F3Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F3.pf",
        n_var_default=30,
    ),
    "lz09_f4": _local_entry(
        "LZ09_F4",
        lambda n_var=30: LZ09F4Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F4.pf",
        n_var_default=30,
    ),
    "lz09_f5": _local_entry(
        "LZ09_F5",
        lambda n_var=30: LZ09F5Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F5.pf",
        n_var_default=30,
    ),
    "lz09_f6": _local_entry(
        "LZ09_F6",
        lambda n_var=10: LZ09F6Problem(n_var=int(n_var)),
        n_obj=3,
        pf_filename="LZ09_F6.pf",
        n_var_default=10,
    ),
    "lz09_f7": _local_entry(
        "LZ09_F7",
        lambda n_var=10: LZ09F7Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F7.pf",
        n_var_default=10,
    ),
    "lz09_f8": _local_entry(
        "LZ09_F8",
        lambda n_var=10: LZ09F8Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F8.pf",
        n_var_default=10,
    ),
    "lz09_f9": _local_entry(
        "LZ09_F9",
        lambda n_var=30: LZ09F9Problem(n_var=int(n_var)),
        n_obj=2,
        pf_filename="LZ09_F9.pf",
        n_var_default=30,
    ),
    "uf1": _local_entry("UF1", lambda n_var=30: UF1Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF1.pf", n_var_default=30),
    "uf2": _local_entry("UF2", lambda n_var=30: UF2Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF2.pf", n_var_default=30),
    "uf3": _local_entry("UF3", lambda n_var=30: UF3Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF3.pf", n_var_default=30),
    "uf4": _local_entry("UF4", lambda n_var=30: UF4Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF4.pf", n_var_default=30),
    "uf5": _local_entry("UF5", lambda n_var=30: UF5Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF5.pf", n_var_default=30),
    "uf6": _local_entry("UF6", lambda n_var=30: UF6Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF6.pf", n_var_default=30),
    "uf7": _local_entry("UF7", lambda n_var=30: UF7Problem(n_var=int(n_var)), n_obj=2, pf_filename="UF7.pf", n_var_default=30),
    "uf8": _local_entry("UF8", lambda n_var=30: UF8Problem(n_var=int(n_var)), n_obj=3, pf_filename="UF8.pf", n_var_default=30),
    "uf9": _local_entry("UF9", lambda n_var=30: UF9Problem(n_var=int(n_var)), n_obj=3, pf_filename="UF9.pf", n_var_default=30),
    "uf10": _local_entry("UF10", lambda n_var=30: UF10Problem(n_var=int(n_var)), n_obj=3, pf_filename="UF10.pf", n_var_default=30),
    "wfg1_2d": _wfg_entry("wfg1", 2),
    "wfg1_3d": _wfg_entry("wfg1", 3),
    "wfg2_2d": _wfg_entry("wfg2", 2),
    "wfg2_3d": _wfg_entry("wfg2", 3),
    "wfg3_2d": _wfg_entry("wfg3", 2),
    "wfg3_3d": _wfg_entry("wfg3", 3),
    "wfg4_2d": _wfg_entry("wfg4", 2),
    "wfg4_3d": _wfg_entry("wfg4", 3),
    "wfg5_2d": _wfg_entry("wfg5", 2),
    "wfg5_3d": _wfg_entry("wfg5", 3),
    "wfg6_2d": _wfg_entry("wfg6", 2),
    "wfg6_3d": _wfg_entry("wfg6", 3),
    "wfg7_2d": _wfg_entry("wfg7", 2),
    "wfg7_3d": _wfg_entry("wfg7", 3),
    "wfg8_2d": _wfg_entry("wfg8", 2),
    "wfg8_3d": _wfg_entry("wfg8", 3),
    "wfg9_2d": _wfg_entry("wfg9", 2),
    "wfg9_3d": _wfg_entry("wfg9", 3),
}

for key, entry in PROBLEMS.items():
    label = str(entry.get("label", key))
    fields = entry.get("form_fields") or {}
    n_var = fields.get("n_var")
    if isinstance(n_var, dict):
        n_var["tooltip"] = f"Number of variables passed to the {label} problem."
    n_obj = fields.get("n_obj")
    if isinstance(n_obj, dict):
        if n_obj.get("read_only"):
            n_obj["tooltip"] = f"Informational value for {label}."
        else:
            n_obj["tooltip"] = f"Number of objectives for {label}."

    if key.startswith("zdt") and key != "zdt5":
        entry["form_note"] = (
            f"{label} uses the n_var parameter. The number of objectives remains fixed and informational."
        )
    elif key.startswith("dtlz"):
        entry["form_note"] = f"{label} passes both n_var and n_obj to pymoo."
    elif key.startswith("wfg"):
        entry["form_note"] = (
            f"{label} uses the pymoo implementation directly together with a local Pareto-front file."
        )
    elif key == "kursawe":
        entry["form_note"] = (
            "Kursawe uses the n_var parameter. The number of objectives remains fixed and informational."
        )
    elif key == "schaffer":
        entry["form_note"] = "Schaffer uses the default local implementation settings."
    elif key == "fon":
        entry["form_note"] = (
            "FON allows the number of variables to be changed, but defaults to the classical n_var=3 configuration."
        )
    elif key == "zdt5":
        entry["form_note"] = "ZDT5 is a discrete problem and uses the default pymoo configuration in this GUI."
    else:
        entry["form_note"] = f"{label} uses the configuration defined by the local framework implementation."


__all__ = ["PROBLEMS", "make_kursawe", "make_schaffer", "make_zdt5"]
