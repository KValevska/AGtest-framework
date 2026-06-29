# AGtest-framework

Desktop framework for configuring, running, visualizing, and exporting
multi-objective optimization experiments based on `pymoo`.

This README is intentionally implementation-oriented. It explains how the
software is structured and gives exact repository-specific instructions for
adding a new algorithm or a new problem.

## Features

- registry-driven GUI forms for problems, algorithms, and run parameters
- responsive execution through a worker thread and generation-wise callbacks
- live Pareto-front visualization with options to hide the known Pareto front and show the current population
- generation-wise quality metrics with explicit hypervolume reference-point handling
- export of metric history and nondominated solutions to `.xlsx` workbooks
- optional parallel objective evaluation for expensive problems
- `RAN` mode for runs without a GUI-imposed generation limit

## Requirements

Recommended environment:

- Python 3.10 or newer
- graphical desktop environment required by `PyQt5`
- runtime dependencies defined in `pyproject.toml`:
  - `numpy`
  - `matplotlib`
  - `PyQt5`
  - `pyqtgraph`
  - `pymoo`
  - `platypus-opt`

## Install

Install runtime dependencies from the project metadata:

```powershell
pip install .
```

For development and testing, use:

```powershell
pip install -e .[dev]
```

Run tests:

```powershell
pytest
```

## Run

Run the GUI from a source checkout:

```powershell
python run_gui.py
```

Or, after installing the package:

```powershell
AGtest-framework
```

## Example workflow

1. Start the application with `python run_gui.py` or `AGtest-framework`.
2. Select a benchmark problem, for example `Kursawe`.
3. Select an optimization algorithm, for example `SPEA2`.
4. Configure the algorithm parameters and termination settings.
5. Set the hypervolume reference point if `HV` should be computed.
6. Start the run.
7. Inspect the Pareto-front visualization and generation-wise metric table.
8. Export the metric history and nondominated solutions to `.xlsx` files.

This workflow allows the user to run a complete multi-objective optimization
experiment without writing a separate execution script.

## Supported components

### Algorithms

- pymoo-based algorithms: `AGE-MOEA`, `Eps-MOEA`, `Eps-NSGA-II`, `GDE3`, `IBEA`, `LMOEA-DS`, `MOEAD`, `NSGA-II`, `NSGA-III`, `R-NSGA-III`, `RVEA`, `SPEA2`
- framework-specific research implementations: `Learning-across-problems EDMO`, `RNN-guided DMO`, `TS-NSGA`
- adapter-based integration: `MOEA/D (epsilon family)` via Platypus
- optional algorithm entry: `HypE`, when its import path is available at runtime

### Problem families

- local benchmark implementations: `Binh2`, `ConstrEx`, `FON`, `Golinski`, `Kursawe`, `Osyczka2`, `Schaffer`, `Srinivas`, `Tanaka`, `Viennet2`, `Viennet3`, `Water`
- pymoo-backed families: `ZDT1`-`ZDT6`, `DTLZ1`-`DTLZ7`
- local benchmark suites: `LZ09_F1`-`LZ09_F9`, `UF1`-`UF10`
- WFG suite: `WFG1`-`WFG9` in both `2D` and `3D` registry variants

### Quality indicators

- `HV`
- `GD`
- `IGD`
- `GD+`
- `IGD+`
- `Spread`
- `Delta`
- `KKTPM`

## Project layout

- `run_gui.py`: command-line bootstrap that adds `src` to `sys.path` and starts the GUI.
- `src/pymoo_gui/app.py`: main PyQt application window, dynamic forms, run orchestration, worker integration, plotting state, metrics table, and export triggers.
- `src/pymoo_gui/algorithms`: algorithm implementations, adapters, shared callback code, and the algorithm registry.
- `src/pymoo_gui/problems`: local benchmark problem implementations, registry helpers, and known Pareto-front loaders.
- `src/pymoo_gui/metrics`: metric computation and XLSX export helpers.
- `src/pymoo_gui/viz`: Pareto-front visualization widgets and dialogs.
- `src/pymoo_gui/parallel.py`: optional parallel evaluation wrapper for expensive problem evaluations.
- `tests`: registry and runtime smoke tests.

## Architecture overview

The application has five main layers.

### 1. GUI layer

The GUI is implemented in `MainWindow` and is responsible for:

- showing problem and algorithm selectors
- building parameter forms dynamically
- validating run settings
- handling start and stop actions
- showing the Pareto visualization
- showing the generation-wise metric table
- triggering result export

The GUI does not hard-code separate forms for each algorithm or problem. It
builds them from registry metadata and callable signatures.

### 2. Registry layer

Problems and algorithms are exposed through two dictionaries:

- `PROBLEMS`
- `ALGORITHMS`

Each entry contains at least:

- `label`: text shown in the GUI
- `factory`: callable used to create the runtime object

Optional metadata includes:

- `form_fields`: explicit field definitions for the dynamic form
- `form_note`: descriptive note used by the GUI
- `known_pf_factory`: function returning a known Pareto front for preview and metrics

Because the GUI depends on these registries instead of directly importing one
algorithm or one problem, extending the framework usually means adding one new
module and one new registry entry.

### 3. Runtime execution layer

The optimization run is executed in `OptimizationWorker`, which subclasses
`QThread`. This keeps the GUI responsive while the optimization is running.

The worker:

- creates the selected problem from `PROBLEMS`
- optionally wraps the problem for parallel evaluation
- creates the selected algorithm from `ALGORITHMS`
- creates a generation callback
- runs the optimization
- emits generation payloads back to the GUI
- emits final success, cancellation, or failure signals

### 4. Monitoring and metrics layer

A shared callback collects generation-level state from the optimizer. It reads:

- current generation number
- number of evaluations
- current population in decision space
- current population in objective space
- constraint-violation data

It then:

- filters feasible solutions
- extracts the feasible nondominated set
- computes supported quality indicators
- assembles a normalized payload for the GUI

This callback is shared across algorithms, which avoids duplicating monitoring
logic in every implementation.

### 5. Export layer

The framework exports results as `.xlsx` files. It writes:

- a metrics workbook containing the generation history table
- a solutions workbook containing nondominated solutions, either for the final epoch or for selected epochs

The export code builds minimal Excel-compatible XML files and packages them into
an `.xlsx` archive. It does not depend on pandas or openpyxl.

## How the GUI uses registry metadata

When the user selects a problem or algorithm:

1. The GUI reads the registry entry.
2. It inspects the `factory` signature.
3. It merges the signature with explicit `form_fields`.
4. It builds a `ParamForm` dynamically.
5. It reads the widget values back into Python objects before starting a run.

This means the registry is not just a list of available options. It also drives
the form-generation logic.

## Exact structure of a registry entry

### Algorithm entry

Typical structure:

```python
MY_ALGORITHM_DEFINITION = {
    "label": "My Algorithm",
    "factory": make_my_algorithm,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 1},
        "alpha": {"default": 0.5, "kind": "float", "minimum": 0.0},
    },
    "form_note": "Short description shown in the GUI.",
}
```

### Problem entry

Typical structure:

```python
PROBLEMS["my_problem"] = {
    "label": "My Problem",
    "factory": make_my_problem,
    "form_fields": {
        "n_var": {"default": 10, "kind": "int", "minimum": 1},
        "n_obj": {"default": 2, "kind": "int", "read_only": True},
    },
    "form_note": "Problem description shown in the GUI.",
    "known_pf_factory": my_known_pf_loader,
}
```

## How to add a new algorithm

There are three supported patterns. Choose the simplest one that matches your
algorithm.

### Pattern A. Native pymoo algorithm

Use this when your algorithm can be represented directly as a standard pymoo
algorithm object.

Examples in the repository follow this pattern for simple baselines such as
NSGA-II.

Steps:

1. Create a new module in `src/pymoo_gui/algorithms`, for example `my_algo.py`.
2. Add a factory function, for example:

```python
from typing import Any, Dict
from pymoo.algorithms.moo.nsga2 import NSGA2


def make_my_algo(pop_size: int = 100) -> NSGA2:
    return NSGA2(pop_size=int(pop_size))


MY_ALGO_DEFINITION: Dict[str, Any] = {
    "label": "My Algo",
    "factory": make_my_algo,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 1},
    },
    "form_note": "Short GUI description.",
}
```

3. Import `MY_ALGO_DEFINITION` in `src/pymoo_gui/algorithms/__init__.py`.
4. Add it to the `ALGORITHMS` dictionary.
5. Run `pytest`.

Notes:

- The GUI will automatically create form fields from the factory signature and
  `form_fields`.
- The worker will pass `seed`, `verbose`, `termination`, and `callback` when the
  run starts. Your factory does not have to accept these because they are passed
  to `minimize`, not to the factory itself.

### Pattern B. Custom research algorithm built inside this framework

Use this when you are implementing your own evolutionary loop and want to reuse
the framework's shared runtime helpers.

The recommended starting point is:

- `src/pymoo_gui/algorithms/empty_algorithm_template.py`
- `src/pymoo_gui/algorithms/research_common.py`

Steps:

1. Copy `empty_algorithm_template.py` to a new file.
2. Rename the class, factory, and registry constant.
3. Implement or override the relevant hooks:
   - `after_initialize`
   - `guided_candidates`
   - `create_offspring`
   - `environmental_selection`
   - `after_generation`
4. Keep the factory focused on configuration only.
5. Define the registry entry.
6. Import it in `algorithms/__init__.py` and add it to `ALGORITHMS`.
7. Run tests and at least one short GUI run.

This pattern is useful because the shared base already provides:

- bounds handling
- problem evaluation
- nondominated sorting
- feasibility-first logic
- deterministic loop structure compatible with the GUI callback model

### Pattern C. Adapter around a non-pymoo runtime

Use this when the underlying algorithm comes from another library or uses a
different iteration API.

In this case, your runtime object should expose a `gui_minimize(...)` method.
The framework checks for this method first. If it exists, it is used instead of
standard `pymoo.optimize.minimize`.

This is how the repository integrates Platypus-based algorithms.

Requirements for `gui_minimize(...)`:

- accept `problem`
- accept `termination`
- accept optional `seed`
- accept optional `callback`
- update enough state for the callback to read:
  - `n_gen`
  - `evaluator.n_eval`
  - `pop.get("X")`
  - `pop.get("F")`
  - `pop.get("CV")`

If those fields are missing, the shared callback cannot construct the monitoring
payload correctly.

## Algorithm checklist

Before registering a new algorithm, check all of the following:

- the factory is callable
- the registry entry has a `label`
- the factory signature matches the parameters you want in the GUI
- `form_fields` use correct `kind` values such as `int`, `float`, `bool`, or `choice`
- the algorithm can run with the selected problem
- the callback can read generation state
- short runs complete without exceptions

## How to add a new problem

There are two supported patterns.

### Pattern A. Local problem class

Use this when you want the problem to live inside the repository.

Steps:

1. Create a new file in `src/pymoo_gui/problems`, for example `my_problem.py`.
2. Implement a class derived from `pymoo.core.problem.Problem`.
3. In `__init__`, define:
   - `n_var`
   - `n_obj`
   - constraint counts if needed
   - lower and upper bounds
4. Implement `_evaluate(self, X, out, *args, **kwargs)`.
5. Write objective values to `out["F"]`.
6. If the problem has inequality constraints, write them to `out["G"]`.
7. If the problem has equality constraints, expose them consistently with the
   rest of the framework if needed by your algorithm path.
8. Add a factory function if you want argument conversion or defaults.
9. Register the problem in `PROBLEMS`.
10. If you want the class publicly re-exported, add it to `problems/__init__.py`.

Minimal example:

```python
import numpy as np
from pymoo.core.problem import Problem


class MyProblem(Problem):
    def __init__(self, n_var: int = 10):
        super().__init__(n_var=int(n_var), n_obj=2, n_constr=0, xl=-1.0, xu=1.0)

    def _evaluate(self, X, out, *args, **kwargs):
        f1 = np.sum(X ** 2, axis=1)
        f2 = np.sum((X - 1.0) ** 2, axis=1)
        out["F"] = np.column_stack([f1, f2])
```

### Pattern B. Wrapper around an existing pymoo problem

Use this when pymoo already provides the problem.

In that case, the registry entry can use a lambda or factory around
`pymoo.problems.get_problem(...)`.

This is how many ZDT, DTLZ, and WFG entries are added.

## Problem checklist

Before registering a new problem, check all of the following:

- the factory is callable
- the registry entry has a `label`
- `n_var` and `n_obj` are correct
- bounds are defined if the algorithm expects them
- `_evaluate` handles batched input `X`
- `out["F"]` has shape `(n_points, n_obj)`
- constraint outputs are consistent
- the problem works in a short standalone evaluation

## How to register a new problem

If the problem is local and has a known Pareto-front file:

1. Put the `.pf` file in `src/pymoo_gui/problems`.
2. Register the problem with `known_pf_factory=_pf_file_loader("MyProblem.pf", expected_n_obj=2)`.

If the problem has no known Pareto front:

- omit `known_pf_factory`
- the GUI will still run the optimization, but some metrics may remain unavailable

Recommended fields:

- `n_var`: editable integer if the number of variables is configurable
- `n_obj`: editable integer only if the problem really supports changing it
- `n_obj` as `read_only=True` when it is fixed and only informational

## How the worker thread works

The worker thread is the runtime bridge between GUI configuration and actual
optimization.

Sequence:

1. The GUI validates user input.
2. The GUI prepares export paths and run state.
3. The GUI creates `OptimizationWorker`.
4. The worker creates the problem instance from the problem registry.
5. The worker loads the known Pareto front if a loader is available.
6. The worker optionally wraps the problem in `ParallelProblem`.
7. The worker creates the algorithm instance from the algorithm registry.
8. The worker creates the shared generation callback.
9. The worker launches the optimization.
10. The callback emits generation payloads to the GUI.
11. The worker emits one of:
    - `done`
    - `cancelled`
    - `failed`

Cancellation is cooperative. The worker stores a cancellation flag and checks it
between payload emissions. This means cancellation is safe, but it usually takes
effect after the current generation finishes.

## How metrics are computed

The framework computes metrics from the feasible nondominated approximation set
available in each generation.

The shared callback:

- reads `X`, `F`, and `CV` from the current population
- normalizes objective data
- filters invalid rows
- builds a feasibility mask from constraint violation
- computes the feasible nondominated subset
- maps nondominated objective rows back to their decision vectors
- computes supported indicators
- emits a normalized payload

Supported metrics include:

- `HV`
- `GD`
- `IGD`
- `GD+`
- `IGD+`
- `Spread`
- `Delta`
- `KKTPM`

Important behavior:

- `HV` requires a valid reference point
- `GD`, `IGD`, `GD+`, and `IGD+` require a known Pareto front
- `Delta` is only enabled in the callback path where it is meaningful
- `KKTPM` requires decision vectors and a compatible problem definition

## How metrics and solutions are exported

### Metrics export

The GUI stores generation payloads in a table. At the end of the run, the table
is exported to an `.xlsx` workbook.

The exported table contains:

- generation number
- evaluation count
- nondominated count
- metric values in the GUI table order

### Nondominated solution export

The GUI can export nondominated solutions:

- only for the final epoch
- every `N` epochs
- in cascade mode

Each exported row may contain:

- `id`
- `f1`, `f2`, ...
- `x1`, `x2`, ... when decision vectors are available

If multiple epochs are exported, the solutions workbook contains multiple
worksheets named by epoch.

## Result formats produced by the framework

The framework produces both in-memory and on-disk results.

### In-memory runtime data

- generation payloads
- current plot state
- metrics table contents
- final payload kept by the worker

### Exported files

- metrics workbook: `.xlsx`
- nondominated solutions workbook: `.xlsx`

### Known Pareto-front inputs

The framework can also consume reference fronts from:

- local `.pf` text files stored next to problem modules
- problem methods such as `pareto_front(...)` when available

## Naming and output directories

Metrics workbooks are written to:

- `metrics_tables`

Solution workbooks are written to:

- `solution_tables`

The filename includes sanitized algorithm and problem names. If a file already
exists, the exporter appends `_1`, `_2`, and so on.

These directory names are part of the current implementation. They are created
automatically by the application when exports are
written.

## Parallel evaluation support

The run form can enable parallel evaluation of the problem.

Behavior:

- `thread` backend uses a `ThreadPool`
- `process` backend uses `multiprocessing` with the `spawn` start method
- the original problem is wrapped in `ParallelProblem`
- rows of `X` are evaluated independently and then reassembled into pymoo-style
  arrays

Use this only when objective evaluation is expensive enough to compensate for
parallel overhead.

## Recommended validation after adding a new algorithm or problem

After any extension, do all of the following:

1. Run `pytest`.
2. Start the GUI.
3. Select the new problem or algorithm.
4. Check that the form renders correctly.
5. Run a short optimization, for example `n_gen=2`.
6. Confirm that:
   - the run starts
   - the plot updates
   - the metrics table gets rows
   - export files are created
   - no callback diagnostics indicate broken state

## Notes

- The canonical package name is `algorithms`; the old `algoritms` alias is kept for backward compatibility.
- Runtime export directories are intentionally ignored by Git.
- Registry integrity is covered by tests, so missing labels or factories should be caught early.

## Known limitations

- Some quality indicators require a known Pareto front or reference approximation set.
- Hypervolume computation requires a valid reference point.
- `KKTPM` requires decision vectors and a compatible problem definition.
- Exported solution workbooks contain nondominated solutions, not necessarily the full population.
- Parallel evaluation is useful only when objective-function evaluation is sufficiently expensive to compensate for parallelization overhead.

## License

This repository does not currently include a `LICENSE` file. Add the intended
license before public release or SoftwareX submission, then update this section
to point to that file explicitly.

## Citation

If you use this software in academic work, cite the associated SoftwareX
article, repository release, or both. Update the entry below with the final
repository URL and DOI when they become available.

```bibtex
@software{agtest_framework,
  title = {AGtest-framework},
  author = {Kristina Valevska},
  year = {2026},
  url = {https://github.com/<user>/<repo>}
}
```
