# Public exports for benchmark problem classes and problem registry factories.

# ------------------------------------------------------------------------------------
# Module: __init__.py
# Summary: public exports for benchmark problem classes, factories and the problem registry.
# Implementation: local problem definitions and registry factory functions are re-exported.
# Responsibility: exposes benchmark problems used by the doctoral-dissertation GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

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
    LZ09Problem,
)
from .osyczka2 import Osyczka2Problem
from .registry import PROBLEMS, make_kursawe, make_schaffer, make_zdt5
from .schaffer import SchafferProblem
from .srinivas import SrinivasProblem
from .tanaka import TanakaProblem
from .uf import (
    PlatypusUFProblem,
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

__all__ = [
    "PROBLEMS",
    "Binh2Problem",
    "ConstrExProblem",
    "FonsecaProblem",
    "GolinskiProblem",
    "KursaweProblem",
    "LZ09Problem",
    "LZ09F1Problem",
    "LZ09F2Problem",
    "LZ09F3Problem",
    "LZ09F4Problem",
    "LZ09F5Problem",
    "LZ09F6Problem",
    "LZ09F7Problem",
    "LZ09F8Problem",
    "LZ09F9Problem",
    "Osyczka2Problem",
    "PlatypusUFProblem",
    "SchafferProblem",
    "SrinivasProblem",
    "TanakaProblem",
    "UF1Problem",
    "UF2Problem",
    "UF3Problem",
    "UF4Problem",
    "UF5Problem",
    "UF6Problem",
    "UF7Problem",
    "UF8Problem",
    "UF9Problem",
    "UF10Problem",
    "Viennet2Problem",
    "Viennet3Problem",
    "WaterProblem",
    "default_wfg_n_var",
    "make_kursawe",
    "make_schaffer",
    "make_wfg_problem",
    "make_zdt5",
]
