"""Test a copy of the EXE away from the source tree, without Python on PATH."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    build = root / "build"
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="standalone-", dir=build) as directory:
        folder = Path(directory)
        executable = folder / "AGtest-framework.exe"
        shutil.copy2(root / "dist" / executable.name, executable)
        report = folder / "self-test.json"
        env = dict(os.environ)
        for key in list(env):
            if key.upper().startswith(("PYTHON", "QT_", "PYQT")):
                env.pop(key)
        windows = Path(env.get("SystemRoot", r"C:\Windows"))
        env["PATH"] = str(windows / "System32") + os.pathsep + str(windows)
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["MPLCONFIGDIR"] = str(folder / "matplotlib")
        working_dir = folder / "different-working-directory"
        working_dir.mkdir()
        result = subprocess.run(
            [str(executable), "--self-test", str(report)],
            cwd=working_dir, env=env, timeout=240, check=False,
        )
        if not report.exists():
            raise RuntimeError(f"EXE did not produce a report; exit code: {result.returncode}")
        saved_report = build / "standalone-self-test.json"
        shutil.copy2(report, saved_report)
        data = json.loads(report.read_text(encoding="utf-8"))
        if result.returncode or not data["ok"] or not data["frozen"]:
            raise RuntimeError(f"Standalone self-test failed: {data}")
        assert Path(data["results_root"]) == folder
        for run in data["runs"]:
            assert Path(run["metrics_path"]).parent == folder / "metrics_tables"
            assert Path(run["solutions_path"]).parent == folder / "solution_tables"
        print(f"Standalone EXE passed: {data['problem_factories']} problems, "
              f"{len(data['runs'])} algorithm runs, {data['reference_front_files']} reference fronts, "
              "GUI, process/thread evaluation, XLSX exports.")
        print(f"Report: {saved_report}")


if __name__ == "__main__":
    main()
