"""
EN:
WFG family factory helpers for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: wfg.py
# Contents: WFG factory helpers backed by pymoo.
# What happens here: helper functions choose consistent default WFG dimensions for the GUI registry.
# Role in the framework: exposes WFG problem-family variants together with matching Pareto-front files.
# Author: mgr inz. Kristina Valevska
# Implementation source: pymoo
# ------------------------------------------------------------------------------------

from __future__ import annotations

from pymoo.problems import get_problem


def default_wfg_n_var(n_obj: int) -> int:
    """
    EN:
    Return a standard WFG variable count for the given objective count.

    PL:
    Wyznacza domyslna liczbe zmiennych dla wariantu WFG o danej liczbie celow.
    """
    parsed_n_obj = int(n_obj)
    return 2 * (parsed_n_obj - 1) + 20


def make_wfg_problem(problem_name: str, n_obj: int, n_var: int | None = None):
    """
    EN:
    Instantiate a WFG problem from pymoo with stable GUI defaults.

    PL:
    Tworzy problem WFG z pymoo z domyslna liczba zmiennych zgodna z typowym
    ustawieniem benchmarku.
    """
    parsed_n_obj = int(n_obj)
    parsed_n_var = default_wfg_n_var(parsed_n_obj) if n_var is None else int(n_var)
    return get_problem(problem_name, n_var=parsed_n_var, n_obj=parsed_n_obj)
