from pathlib import Path
import sys

from pymoo_gui.runtime import results_root


def test_source_results_stay_in_project(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert results_root() == Path(__file__).resolve().parents[1]


def test_frozen_results_survive_bundle_cleanup(monkeypatch, tmp_path):
    executable_dir = tmp_path / "Portable App"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path / "temporary-bundle"), raising=False)
    monkeypatch.setattr(sys, "executable", str(executable_dir / "AGtest-framework.exe"))
    monkeypatch.chdir(tmp_path)
    assert results_root() == executable_dir
