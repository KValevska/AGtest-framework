from __future__ import annotations

from importlib import import_module

import pymoo_gui


def test_top_level_exports_match_active_modules() -> None:
    expected = {"algorithms", "app", "metrics", "parallel", "problems", "viz"}
    assert set(pymoo_gui.__all__) == expected


def test_historical_algoritms_alias_still_imports() -> None:
    legacy_pkg = import_module("pymoo_gui.algoritms")
    legacy_submodule = import_module("pymoo_gui.algoritms.gde3")
    canonical_submodule = import_module("pymoo_gui.algorithms.gde3")

    assert hasattr(legacy_pkg, "ALGORITHMS")
    assert legacy_submodule is canonical_submodule
