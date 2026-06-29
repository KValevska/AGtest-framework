# WFG family factory helpers for pymoo.

# ------------------------------------------------------------------------------------
# Module: wfg.py
# Summary: WFG factory helpers backed by pymoo.
# Implementation: helper functions choose consistent default WFG dimensions for the GUI registry.
# Responsibility: exposes WFG problem-family variants together with matching Pareto-front files.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: pymoo
# ------------------------------------------------------------------------------------

from __future__ import annotations

from pymoo.problems import get_problem


def default_wfg_n_var(n_obj: int) -> int:
    # Return a standard WFG variable count for the given objective count.
    parsed_n_obj = int(n_obj)
    return 2 * (parsed_n_obj - 1) + 20


def make_wfg_problem(problem_name: str, n_obj: int, n_var: int | None = None):
    # Instantiate a WFG problem from pymoo with stable GUI defaults.
    parsed_n_obj = int(n_obj)
    parsed_n_var = default_wfg_n_var(parsed_n_obj) if n_var is None else int(n_var)
    return get_problem(problem_name, n_var=parsed_n_var, n_obj=parsed_n_obj)
