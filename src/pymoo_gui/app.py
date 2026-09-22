# PyQt5 desktop application for configuring, running, visualizing and exporting multiobjective optimization experiments.

# ------------------------------------------------------------------------------------
# Module: app.py
# Summary: PyQt5 main window, dynamic parameter forms, optimization worker, plotting and metrics UI logic.
# Implementation: user-selected problems and algorithms are configured, executed in a thread, visualized and exported.
# Responsibility: provides the interactive desktop interface for dissertation optimization experiments.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import ast
import inspect
import math
import os
import re
import sys
import threading
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np
from PyQt5.QtCore import QLocale, QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
try:
    from pymoo.core.termination import NoTermination
except Exception:
    class NoTermination:  # type: ignore[override]
        # Compatibility fallback for pymoo versions without `NoTermination`.

        def __init__(self):
            # Initialize the fallback termination state.
            self.force_termination = False
            self.perc = 0.0

        def update(self, algorithm):
            # Update fallback progress from the forced-termination flag.
            self.perc = 1.0 if self.force_termination else 0.0
            return self.perc

        def has_terminated(self):
            # Report whether the fallback termination has completed.
            return self.perc >= 1.0

        def do_continue(self):
            # Return whether optimization should continue.
            return not self.has_terminated()

if __package__ in (None, ""):
    _src_root = Path(__file__).resolve().parents[1]
    if str(_src_root) not in sys.path:
        sys.path.insert(0, str(_src_root))
    __package__ = "pymoo_gui"

from .algorithms import ALGORITHMS, known_pareto_front, make_generation_callback, minimize
from . import __version__
from .metrics import (
    METRIC_DISPLAY_ORDER,
    METRIC_LABELS,
    METRIC_TABLE_ORDER,
    metrics_export_path,
    next_available_export_path,
    solutions_export_path,
    write_xlsx_table,
    write_xlsx_workbook,
)
from .multi import MultiExperimentWorker, build_multi_run_specs
from .parallel import make_parallel_problem
from .problems import PROBLEMS
from .runtime import results_root
from .viz.metric_trajectories import MetricTrajectoriesWidget
from .viz.pareto_dialogs import UnifiedParetoWidget

EMPTY = inspect.Signature.empty
APPLICATION_NAME = "AGtest-framework"
APPLICATION_TITLE = f"{APPLICATION_NAME} v{__version__}"
ND_SAVE_LAST_EPOCH = "last_epoch"
ND_SAVE_EVERY_N_EPOCHS = "every_n_epochs"
ND_SAVE_CASCADE = "cascade"
PARAM_PL = {
    "n_var": "Liczba zmiennych",
    "n_obj": "Liczba funkcji celu",
    "seed": "Ziarno losowości",
    "verbose": "Tryb gadatliwy",
    "n_gen": "Liczba generacji",
    "ran": "RAN",
    "pop_size": "Rozmiar populacji",
    "population_size": "Rozmiar populacji",
    "n_partitions": "Liczba partycji",
    "n_neighbors": "Liczba sąsiadów",
    "prob_neighbor_mating": "Prawdopodobieństwo kojarzenia sąsiadów",
    "neighborhood_size": "Rozmiar sąsiedztwa",
    "epsilons": "Epsilony",
    "ref_points": "Punkty odniesienia",
    "pop_per_ref_point": "Populacja na punkt odniesienia",
    "mu": "Parametr mu",
    "references": "Liczba próbek HV",
    "n_samples": "Liczba próbek MC",
    "reference_point": "Punkt referencyjny",
    "reference_set": "Zbiór referencyjny",
    "kappa": "Parametr kappa",
    "f_weight": "Waga F",
    "guiding_vector_count": "Liczba wektorów kierujących",
    "samples_per_direction": "Próbki na kierunek",
    "selection_threshold_ratio": "Próg selekcji",
    "mutation_rate": "Współczynnik mutacji",
    "eta": "Parametr eta",
    "alpha": "Parametr alpha",
    "adapt_freq": "Częstotliwość adaptacji",
    "parallel_eval": "Ewaluacja równoległa",
    "parallel_workers": "Liczba workerów",
    "parallel_backend": "Backend równoległy",
}
DEFAULT_PARALLEL_WORKERS = max(1, min(4, os.cpu_count() or 1))
RUN_FORM_FIELDS = {
    "seed": {"default": 1, "kind": "int", "minimum": 0},
    "n_gen": {"default": 10, "kind": "int", "minimum": 1},
    "ran": {
        "default": False,
        "kind": "bool",
        "tooltip": "Brak limitu generacji z GUI. Przebieg zatrzymasz przyciskiem Stop.",
    },
    "verbose": {"default": True, "kind": "bool"},
    "parallel_eval": {
        "default": False,
        "kind": "bool",
        "tooltip": "Równoległa ewaluacja osobników na CPU. Najbardziej przydatna dla drogich funkcji celu.",
    },
    "parallel_workers": {
        "default": DEFAULT_PARALLEL_WORKERS,
        "kind": "int",
        "minimum": 1,
        "tooltip": "Liczba procesów albo wątków używanych do ewaluacji funkcji celu.",
    },
    "parallel_backend": {
        "default": "process",
        "kind": "choice",
        "choices": ("process", "thread"),
        "tooltip": "process = multiprocessing; thread = ThreadPool z mniejszym narzutem.",
    },
}

PARAM_PL.update(
    {
        "n_var": "Number of variables",
        "n_obj": "Number of objectives",
        "seed": "Random seed",
        "verbose": "Verbose mode",
        "n_gen": "Number of generations",
        "pop_size": "Population size",
        "population_size": "Population size",
        "n_partitions": "Number of partitions",
        "n_neighbors": "Number of neighbors",
        "prob_neighbor_mating": "Neighbor mating probability",
        "neighborhood_size": "Neighborhood size",
        "epsilons": "Epsilons",
        "ref_points": "Reference points",
        "pop_per_ref_point": "Population per reference point",
        "mu": "Mu parameter",
        "references": "Number of HV samples",
        "n_samples": "Number of MC samples",
        "reference_point": "Reference point",
        "reference_set": "Reference set",
        "kappa": "Kappa parameter",
        "f_weight": "F weight",
        "guiding_vector_count": "Number of guiding vectors",
        "samples_per_direction": "Samples per direction",
        "selection_threshold_ratio": "Selection threshold",
        "mutation_rate": "Mutation rate",
        "eta": "Eta parameter",
        "alpha": "Alpha parameter",
        "adapt_freq": "Adaptation frequency",
        "parallel_eval": "Parallel evaluation",
        "parallel_workers": "Number of workers",
        "parallel_backend": "Parallel backend",
    }
)
RUN_FORM_FIELDS["ran"]["tooltip"] = "No generation limit is enforced by the GUI. Stop the run with the Stop button."
RUN_FORM_FIELDS["parallel_eval"]["tooltip"] = (
    "Evaluate individuals in parallel on the CPU. Most useful for expensive objective functions."
)
RUN_FORM_FIELDS["parallel_workers"]["tooltip"] = (
    "Number of processes or threads used to evaluate objective functions."
)
RUN_FORM_FIELDS["parallel_backend"]["tooltip"] = (
    "process = multiprocessing; thread = ThreadPool with lower overhead."
)

UI_TEXT_REPLACEMENTS = {
    "Brak wykresu - uruchom optymalizacjÄ™": "No plot available. Start an optimization run.",
    "RÄ™czny ref point": "Manual ref point",
    "HV ref point (aktywny): -": "HV ref point (active): -",
    "Aktualizuj wykres w trakcie": "Update plot during run",
    "PokaĹĽ populacjÄ™": "Show population",
    "Zapis rozwiÄ…zaĹ„ niezdominowanych": "Nondominated solution export",
    "Konsola": "Console",
    "Ukryj konsole": "Hide console",
    "Pokaz konsole": "Show console",
    "Status: bezczynny": "Status: idle",
    "Tryb zapisu rozwiÄ…zaĹ„ niezdominowanych jest niepoprawny.": "Invalid nondominated-solution export mode.",
    "Nie moĹĽna przygotowaÄ‡ podglÄ…du Pareto.": "Unable to prepare the Pareto preview.",
    "Podaj ref_point albo wybierz tryb Auto.": "Enter a ref_point or switch to Auto mode.",
    "Start: uruchomienie juĹĽ trwa.": "Start: a run is already in progress.",
    "BĹ‚Ä™dny ref point": "Invalid ref point",
    "Niepoprawny ref_point.": "Invalid ref_point.",
    "HV ref_point: start zablokowany.": "HV ref_point: start blocked.",
    "Brak konfiguracji": "Missing configuration",
    "Wybierz problem i algorytm przed uruchomieniem.": "Select a problem and an algorithm before starting the run.",
    "Start: brak wybranego problemu lub algorytmu.": "Start: no problem or algorithm is selected.",
    "BĹ‚Ä™dne dane wejĹ›ciowe": "Invalid input data",
    "BĹ‚Ä™dne ustawienia zapisu": "Invalid export settings",
    "BĹ‚Ä™dne dane algorytmu": "Invalid algorithm data",
    "BĹ‚Ä™dne dane problemu": "Invalid problem data",
    "dziaĹ‚a": "running",
    "zakoĹ„czono": "completed",
    "zatrzymano": "stopped",
    "bĹ‚Ä…d": "error",
    "Stop: brak aktywnego uruchomienia.": "Stop: no active run.",
    "Status: zatrzymywanie": "Status: stopping",
    "Stop: wysĹ‚ano zadanie zatrzymania; oczekiwanie na zakoĹ„czenie bieĹĽÄ…cej generacji.": (
        "Stop: cancellation requested; waiting for the current generation to finish."
    ),
    "BĹ‚Ä…d optymalizacji": "Optimization error",
    "Eksport metryk pominiÄ™ty: tabela historii jest pusta.": "Metrics export skipped: the history table is empty.",
    "RozwiÄ…zania": "Solutions",
}


def translate_ui_text(text: Any) -> str:
    # Translate user-visible GUI text to English.
    out = "" if text is None else str(text)
    out = UI_TEXT_REPLACEMENTS.get(out, out)
    replacements = (
        ("WĹ‚Ä…cza odĹ›wieĹĽanie wykresu Pareto w trakcie kolejnych generacji.", "Refresh the Pareto plot after each generation."),
        ("Pokazuje lub ukrywa peĹ‚nÄ… populacjÄ™ na wykresie Pareto.", "Show or hide the full population in the Pareto plot."),
        (
            "Ukrywa znany front Pareto, ale nie usuwa go z danych uĹĽywanych przez metryki.",
            "Hide the Pareto front without removing it from the data used by the metrics.",
        ),
        (
            "Jednorazowo dopasowuje zakres osi dla aktualnego widoku Pareto, bez przeliczania przy kaĹĽdej generacji.",
            "Fit the axis ranges for the current Pareto view without recomputing them on every generation.",
        ),
        ("Wybiera, dla ktĂłrych epok zapisywaÄ‡ front niezdominowany.", "Choose for which epochs the nondominated front should be saved."),
        ("Dodatnia liczba caĹ‚kowita uĹĽywana tylko w trybie 'Co N epok'.", "Positive integer used only in the 'Every N epochs' mode."),
        ("show_population={checked} (pelna populacja jako osobna warstwa)", "show_population={checked} (full population as a separate layer)"),
        ("Dla liczb z przecinkiem oddziel wymiary spacjÄ… lub ';', np. '0,6 0,7'.", "For decimal commas, separate dimensions with spaces or ';', e.g. '0,6 0,7'."),
        ("HV ref point (aktywny): INVALID", "HV ref point (active): INVALID"),
        ("HV ref point (aktywny): [", "HV ref point (active): ["),
        ("PodglÄ…d Pareto niedostÄ™pny dla ", "Pareto preview is unavailable for "),
        (" celĂłw. Gen=", " objectives. Gen="),
        ("Eksport metryk nie powiĂłdĹ‚ siÄ™: ", "Metrics export failed: "),
        ("Eksport metryk zapisany: ", "Metrics export saved: "),
        ("Epoka ", "Epoch "),
        ("Eksport punktĂłw niezdominowanych nie powiĂłdĹ‚ siÄ™: ", "Nondominated-point export failed: "),
        ("Eksport punktĂłw niezdominowanych nie utworzyĹ‚ pliku: ", "Nondominated-point export did not create a file: "),
        ("Utworzony plik Excel z punktami niezdominowanymi: ", "Created Excel file with nondominated points: "),
        ("Liczba zapisanych punktĂłw: ", "Number of saved points: "),
        ("Dane pochodzÄ… z uruchomienia: ", "Data source run: "),
        ("Eksport punktĂłw niezdominowanych dla epoki ", "Nondominated-point export for epoch "),
        (" nie powiĂłdĹ‚ siÄ™: ", " failed: "),
        ("Zapisano punkty niezdominowane w arkuszu dla epoki ", "Saved nondominated points in the worksheet for epoch "),
        ("Eksport punktĂłw niezdominowanych dla ostatniej epoki ", "Nondominated-point export for the final epoch "),
        ("Zapisano punkty niezdominowane dla ostatniej epoki ", "Saved nondominated points for the final epoch "),
        (": brak poprawnej liczby caĹ‚kowitej.", ": invalid integer value."),
        (": wartoĹ›Ä‡ musi byÄ‡ >= ", ": value must be >= "),
        ("Liczba generacji", "Number of generations"),
        ("Liczba workerĂłw", "Number of workers"),
        ("Backend rĂłwnolegĹ‚y: nieobsĹ‚ugiwana wartoĹ›Ä‡ ", "Parallel backend: unsupported value "),
        ("Rozmiar populacji", "Population size"),
        ("ref_point ma dĹ‚ugoĹ›Ä‡ ", "ref_point has length "),
        (", oczekiwano M=", "; expected M="),
        ("Nie moĹĽna odczytaÄ‡ liczby '", "Unable to parse the number '"),
        ("'. UĹĽyj np. '0,6 0,7' albo '0.6,0.7'.", "'. Use, for example, '0,6 0,7' or '0.6,0.7'."),
        ("Brak poprawnego factory problemu.", "No valid problem factory is available."),
    )
    for source, target in replacements:
        out = out.replace(source, target)
    out = re.sub(
        r"PodglÄ…d Pareto jest dostÄ™pny tylko dla 2 lub 3 celĂłw\. Wybrany problem ma ([^.]*)\.",
        r"Pareto preview is available only for 2 or 3 objectives. The selected problem has \1.",
        out,
    )
    return out


def pl_param_label(name: str) -> str:
    # Return a GUI label for a technical parameter name.
    return PARAM_PL.get(name) or f"{name.replace('_', ' ').capitalize()} ({name})"


def callable_signature(obj: Any) -> inspect.Signature:
    # Return the callable signature used to build dynamic parameter forms.
    return inspect.signature(obj)


def filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> Dict[str, Any]:
    # Keep only keyword arguments accepted by a callable's signature.
    sig = callable_signature(fn)
    accepted = {}
    for param in sig.parameters.values():
        if param.name == "self" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.name in params:
            accepted[param.name] = params[param.name]
    return accepted


def _literal_or_str(value: str) -> Any:
    # Parse GUI text as a Python literal when possible, otherwise keep it as text.
    text = value.strip()
    if not text:
        return None
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return text


def should_save_nondominated_solutions_for_epoch(epoch: Any, mode: str, step: int = 1, *, is_final: bool = False) -> bool:
    # Decide whether nondominated solutions should be exported for a given epoch.
    try:
        epoch_number = int(epoch)
    except (TypeError, ValueError):
        return False
    if epoch_number < 1:
        return False
    if mode in {ND_SAVE_LAST_EPOCH, "every_epoch"}:
        return bool(is_final)
    if mode == ND_SAVE_EVERY_N_EPOCHS:
        return epoch_number == 1 or (step >= 1 and epoch_number % step == 0)
    if mode == ND_SAVE_CASCADE:
        if epoch_number == 1:
            return True
        if epoch_number < 10:
            return False
        threshold = 10 ** (len(str(epoch_number)) - 1)
        return epoch_number % threshold == 0
    return True


@dataclass(frozen=True)
class FieldSpec:
    # Declarative description of one dynamic form field.

    name: str
    default: Any = None
    kind: str = "any"
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    read_only: bool = False
    tooltip: Optional[str] = None
    choices: Optional[Sequence[str]] = None


@dataclass
class WidgetBinding:
    # Binding between a form field specification and the created Qt widget.

    name: str
    widget: Any
    kind: str
    spec: FieldSpec


def _specs(raw_specs: Optional[Any]) -> list[FieldSpec]:
    # Normalize registry form-field definitions into `FieldSpec` objects.
    if not raw_specs:
        return []
    out = []
    if isinstance(raw_specs, Mapping):
        iterator = raw_specs.items()
    else:
        iterator = ((item["name"], item) for item in raw_specs if isinstance(item, Mapping) and "name" in item)
    for name, raw in iterator:
        if isinstance(raw, FieldSpec):
            out.append(raw)
        elif isinstance(raw, Mapping):
            choices = raw.get("choices")
            out.append(
                FieldSpec(
                    name=str(name),
                    default=raw.get("default"),
                    kind=str(raw.get("kind", "any")),
                    minimum=raw.get("minimum"),
                    maximum=raw.get("maximum"),
                    read_only=bool(raw.get("read_only", False)),
                    tooltip=raw.get("tooltip"),
                    choices=tuple(choices) if choices else None,
                )
            )
        elif isinstance(raw, tuple) and len(raw) >= 2:
            out.append(FieldSpec(name=str(name), default=raw[0], kind=str(raw[1])))
        else:
            out.append(FieldSpec(name=str(name), default=raw))
    return out


class ParamForm(QGroupBox):
    # Dynamic Qt form that builds parameter widgets from signatures or field specs.

    def __init__(self, title: str, parent=None):
        # Initialize an empty parameter form.
        super().__init__(title, parent)
        self.form = QFormLayout(self)
        self.form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.form.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self._bindings: Dict[str, WidgetBinding] = {}

    def clear(self) -> None:
        # Remove all rows and widget bindings from the form.
        while self.form.rowCount():
            self.form.removeRow(0)
        self._bindings.clear()

    def binding(self, name: str) -> Optional[WidgetBinding]:
        # Return the binding for one field name.
        return self._bindings.get(name)

    def bindings(self) -> Sequence[WidgetBinding]:
        # Return all field-to-widget bindings.
        return tuple(self._bindings.values())

    def build_for_callable(self, fn: Any, extra_fields: Optional[Any] = None) -> None:
        # Build form fields from a callable signature and explicit field specs.
        self.build_for_signature(callable_signature(fn), extra_fields)

    def build_for_signature(self, sig: inspect.Signature, extra_fields: Optional[Any] = None) -> None:
        # Build form fields from an inspected signature.
        self.clear()
        added_names = set()
        for spec in _specs(extra_fields):
            self._add_field(spec)
            added_names.add(spec.name)
        for param in sig.parameters.values():
            if param.name in {"self", "problem"} or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            if param.name in added_names:
                continue
            default = None if param.default is EMPTY else param.default
            self._add_field(FieldSpec(param.name, default, self._kind(param.annotation, default)))

    def build_from_specs(self, raw_specs: Optional[Any]) -> None:
        # Build form fields directly from registry field specifications.
        self.clear()
        for spec in _specs(raw_specs):
            self._add_field(spec)

    def _kind(self, annotation: Any, default: Any) -> str:
        # Infer the widget kind from type annotation or default value.
        if annotation in (bool, "bool") or isinstance(default, bool):
            return "bool"
        if annotation in (int, "int") or isinstance(default, int):
            return "int"
        if annotation in (float, "float") or isinstance(default, float):
            return "float"
        if annotation in (str, "str") or isinstance(default, str):
            return "str"
        return "any"

    def _bounds(self, spec: FieldSpec) -> Tuple[float, float]:
        # Determine numeric widget bounds from a field specification.
        minimum = spec.minimum
        maximum = spec.maximum
        if spec.kind == "int":
            if minimum is None:
                if spec.name in {"n_gen", "pop_size", "n_var", "n_obj"}:
                    minimum = 1
                elif spec.name == "seed":
                    minimum = 0
                else:
                    minimum = -10**9
            if maximum is None:
                maximum = 10**9
        else:
            minimum = -1e12 if minimum is None else minimum
            maximum = 1e12 if maximum is None else maximum
        return float(minimum), float(maximum)

    def _apply_read_only(self, widget: Any, spec: FieldSpec) -> None:
        # Apply a read-only state to a widget according to the field spec.
        if not spec.read_only:
            return
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setReadOnly(True)
            widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
            widget.setFocusPolicy(Qt.NoFocus)
        elif isinstance(widget, QLineEdit):
            widget.setReadOnly(True)
        else:
            widget.setEnabled(False)

    def _add_field(self, spec: FieldSpec) -> None:
        # Create one Qt widget for a field specification and add it to the form.
        label = QLabel(pl_param_label(spec.name))
        if spec.tooltip:
            label.setToolTip(translate_ui_text(spec.tooltip))
        if spec.kind == "choice" or spec.choices:
            widget = QComboBox()
            for choice in spec.choices or ():
                widget.addItem(str(choice))
            if spec.default in (spec.choices or ()):
                widget.setCurrentIndex((spec.choices or ()).index(spec.default))
            kind = "choice"
        elif spec.kind == "int":
            widget = QSpinBox()
            lo, hi = self._bounds(spec)
            widget.setRange(int(lo), int(hi))
            if spec.default is not None:
                widget.setValue(int(spec.default))
            kind = "int"
        elif spec.kind == "float":
            widget = QDoubleSpinBox()
            lo, hi = self._bounds(spec)
            widget.setDecimals(10)
            widget.setRange(lo, hi)
            if spec.default is not None:
                widget.setValue(float(spec.default))
            kind = "float"
        elif spec.kind == "bool":
            widget = QCheckBox()
            widget.setChecked(bool(spec.default))
            kind = "bool"
        else:
            widget = QLineEdit("" if spec.default is None else str(spec.default))
            if spec.default is None:
                widget.setPlaceholderText("None")
            kind = spec.kind
        if spec.tooltip:
            widget.setToolTip(translate_ui_text(spec.tooltip))
        self._apply_read_only(widget, spec)
        self.form.addRow(label, widget)
        self._bindings[spec.name] = WidgetBinding(spec.name, widget, kind, spec)

    def values(self) -> Dict[str, Any]:
        # Read all form widget values and convert them to Python objects.
        out: Dict[str, Any] = {}
        for name, binding in self._bindings.items():
            widget = binding.widget
            if binding.kind == "int":
                out[name] = int(widget.value())
            elif binding.kind == "float":
                out[name] = float(widget.value())
            elif binding.kind == "bool":
                out[name] = bool(widget.isChecked())
            elif binding.kind == "choice":
                out[name] = str(widget.currentText())
            elif binding.kind == "str":
                text = widget.text().strip()
                out[name] = text or None
            else:
                out[name] = _literal_or_str(widget.text())
        return out

class OptimizationCancelled(Exception):
    # Signal cooperative cancellation of an optimization run.

    pass


class OptimizationWorker(QThread):
    # Run optimization in the background and emit payloads back to the GUI.

    generation = pyqtSignal(object)
    done = pyqtSignal(dict)
    cancelled = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(
        self,
        problem_key: str,
        alg_key: str,
        problem_params: Mapping[str, Any],
        algorithm_params: Mapping[str, Any],
        n_gen: Optional[int],
        seed: int,
        verbose: bool,
        hv_ref_point: Optional[list[float]],
        parallel_eval: bool = False,
        parallel_workers: int = 1,
        parallel_backend: str = "process",
        parent=None,
        step_mode: bool = False,
    ):
        # Store all configuration needed for one optimization run.
        super().__init__(parent)
        self._problem_key = str(problem_key)
        self._alg_key = str(alg_key)
        self._problem_params = dict(problem_params)
        self._algorithm_params = dict(algorithm_params)
        self._n_gen = int(n_gen) if n_gen is not None else None
        self._seed = int(seed)
        self._verbose = bool(verbose)
        self._hv_ref_point = hv_ref_point
        self._parallel_eval = bool(parallel_eval)
        self._parallel_workers = int(parallel_workers)
        self._parallel_backend = str(parallel_backend)
        self._last_payload: dict = {}
        self._cancel_requested = threading.Event()
        self.step_mode = bool(step_mode)
        self._step_condition = threading.Condition()
        self.waiting_for_step = False

    def request_cancel(self) -> None:
        # Request cooperative cancellation of the running optimization.
        self._cancel_requested.set()
        self.requestInterruption()
        with self._step_condition:
            self._step_condition.notify_all()

    def request_next_epoch(self) -> bool:
        # Consume one click only while paused; rapid clicks cannot queue epochs.
        with self._step_condition:
            if not self.waiting_for_step or self._cancel_pending():
                return False
            self.waiting_for_step = False
            self._step_condition.notify_all()
            return True

    def _cancel_pending(self) -> bool:
        # Return whether the worker has received a cancellation request.
        return self._cancel_requested.is_set() or self.isInterruptionRequested()

    def _emit_generation(self, payload: dict) -> None:
        # Emit one generation payload unless cancellation is pending.
        if self._cancel_pending():
            raise OptimizationCancelled()
        self._last_payload = payload or {}
        with self._step_condition:
            self.waiting_for_step = self.step_mode and (
                self._n_gen is None or int(payload.get("n_gen", 0)) < self._n_gen
            )
            self.generation.emit(self._last_payload)
            while self.waiting_for_step and not self._cancel_pending():
                self._step_condition.wait()
            self.waiting_for_step = False
        if self._cancel_pending():
            raise OptimizationCancelled()

    def run(self) -> None:
        # Build runtime objects, execute optimization, and emit result signals.
        problem = None
        try:
            if self._cancel_pending():
                raise OptimizationCancelled()
            problem_entry = PROBLEMS[self._problem_key]
            problem_factory = problem_entry["factory"]
            problem = problem_factory(**filter_callable_kwargs(problem_factory, self._problem_params))
            known_pf_factory = problem_entry.get("known_pf_factory")
            known_pf = None
            if callable(known_pf_factory):
                known_pf = known_pf_factory(problem)
            if self._parallel_eval:
                problem = make_parallel_problem(
                    problem,
                    workers=self._parallel_workers,
                    backend=self._parallel_backend,
                )

            algorithm_entry = ALGORITHMS[self._alg_key]
            algorithm_factory = algorithm_entry["factory"]
            algorithm_params = dict(self._algorithm_params)
            algorithm_params["problem"] = problem
            algorithm = algorithm_factory(**filter_callable_kwargs(algorithm_factory, algorithm_params))
            if self._n_gen is None:
                algorithm.termination = NoTermination()
            callback = make_generation_callback(
                self._emit_generation,
                problem=problem,
                hv_ref_point=self._hv_ref_point,
                known_pf=known_pf,
                algorithm_key=self._alg_key,
            )
            termination = ("n_gen", self._n_gen) if self._n_gen is not None else NoTermination()
            minimize(problem, algorithm, termination, seed=self._seed, verbose=self._verbose, callback=callback)
            if self._cancel_pending():
                raise OptimizationCancelled()
            self.done.emit(dict(self._last_payload))
        except OptimizationCancelled:
            self.cancelled.emit(dict(self._last_payload))
        except Exception as exc:
            self.failed.emit(repr(exc))
        finally:
            close = getattr(problem, "close", None)
            if callable(close):
                close()


class MainWindow(QMainWindow):
    # Main application window for configuration, execution, plotting, and export.

    def __init__(self):
        # Initialize widgets, runtime state, and initial previews.
        super().__init__()
        self.setWindowTitle(APPLICATION_TITLE)
        self.resize(1200, 1200)
        self._thread: Optional[OptimizationWorker] = None
        self._multi_thread: Optional[MultiExperimentWorker] = None
        self._multi_result_rows: dict[tuple[str, str], int] = {}
        self._n_obj_widget: Optional[QSpinBox] = None
        self._last_gen_appended: Optional[int] = None
        self._plot_widget: Optional[UnifiedParetoWidget] = None
        self._plot_widget_dim: Optional[int] = None
        self._plot_known_pf: Optional[np.ndarray] = None
        self._plot_feasible_nd_F: Optional[np.ndarray] = None
        self._plot_population_F: Optional[np.ndarray] = None
        self._plot_generation: Optional[int] = None
        self._plot_n_obj: Optional[int] = None
        self._epoch_history: dict[int, dict] = {}
        self._run_algorithm_key: Optional[str] = None
        self._run_algorithm_name: Optional[str] = None
        self._run_problem_name: Optional[str] = None
        self._run_nd_save_mode = ND_SAVE_LAST_EPOCH
        self._run_nd_save_step = 1
        self._run_metrics_export_path: Optional[Path] = None
        self._run_solutions_export_path: Optional[Path] = None
        self._nd_solution_sheets: dict[int, tuple[list[str], list[list[object]]]] = {}
        self._square_geometry_applied = False
        self._build_ui()
        self._apply_english_ui_texts()
        self._connect_signals()
        self._configure_placeholders()
        self._rebuild_problem_form()
        self._rebuild_alg_form()
        self._update_hv_ref_point_label()
        self._update_plot_status()
        self._update_run_button_state()
        self._apply_default_window_geometry()

    def _apply_default_window_geometry(self) -> None:
        # Size the completed interface as a square and keep the console shallow.
        minimum = self.minimumSizeHint()
        side = max(1200, minimum.width(), minimum.height())
        self.resize(side, side)
        self.console_dock.setMaximumHeight(160)
        self.resizeDocks([self.console_dock], [120], Qt.Vertical)

    def showEvent(self, event) -> None:
        # Apply the square size after Qt has resolved the platform layout constraints.
        super().showEvent(event)
        if not self._square_geometry_applied:
            self._square_geometry_applied = True
            QTimer.singleShot(0, self._make_window_square)

    def _make_window_square(self) -> None:
        side = max(self.width(), self.height())
        self.resize(side, side)
        self.resizeDocks([self.console_dock], [120], Qt.Vertical)

    def _build_ui(self) -> None:
        # Build browser-style tabs containing the existing Main view and the Multi view.
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.screenshot_btn = QToolButton()
        self.screenshot_btn.setText("Screenshot")
        self.screenshot_btn.setToolTip("Save the entire application window as a PNG image.")
        self.screenshot_btn.setAccessibleName("Save application screenshot")
        self.tabs.setCornerWidget(self.screenshot_btn, Qt.TopRightCorner)
        self.setCentralWidget(self.tabs)

        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Horizontal)
        controls_panel = self._build_controls_panel()
        results_panel = self._build_results_panel()
        splitter.addWidget(controls_panel)
        splitter.addWidget(results_panel)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([440, 1060])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        self.tabs.addTab(main_tab, "Main")
        self.tabs.addTab(self._build_multi_panel(), "Multi")
        self.metric_trajectories = MetricTrajectoriesWidget()
        self.tabs.addTab(self.metric_trajectories, "Metric trajectories")

    def _build_checkable_registry_list(self, registry: Mapping[str, Dict[str, Any]]) -> QListWidget:
        # Build a list whose entries can be checked independently without modifier keys.
        widget = QListWidget()
        widget.setAlternatingRowColors(True)
        for key, entry in registry.items():
            item = QListWidgetItem(str(entry.get("label", key)))
            item.setData(Qt.UserRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            widget.addItem(item)
        return widget

    def _build_multi_selection_group(self, title: str, widget: QListWidget) -> QGroupBox:
        # Wrap a checkable registry list with Select all and Clear controls.
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        buttons = QHBoxLayout()
        select_all = QPushButton("Select all")
        clear = QPushButton("Clear")
        select_all.clicked.connect(lambda: self._set_all_multi_items(widget, True))
        clear.clicked.connect(lambda: self._set_all_multi_items(widget, False))
        buttons.addWidget(select_all)
        buttons.addWidget(clear)
        layout.addLayout(buttons)
        return group

    def _build_multi_panel(self) -> QWidget:
        # Build the non-visual batch experiment tab.
        panel = QWidget()
        layout = QVBoxLayout(panel)

        description = QLabel(
            "Select one or more algorithms and problems. Multi runs every selected algorithm on every "
            "selected problem, uses registry defaults, and saves metrics plus final nondominated solutions."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        self.multi_algorithm_list = self._build_checkable_registry_list(ALGORITHMS)
        self.multi_problem_list = self._build_checkable_registry_list(PROBLEMS)
        selectors = QHBoxLayout()
        self.multi_algorithm_group = self._build_multi_selection_group("Algorithms", self.multi_algorithm_list)
        self.multi_problem_group = self._build_multi_selection_group("Problems", self.multi_problem_list)
        selectors.addWidget(self.multi_algorithm_group, 1)
        selectors.addWidget(self.multi_problem_group, 1)
        layout.addLayout(selectors, 2)

        settings_group = QGroupBox("Experiment settings")
        settings = QFormLayout(settings_group)
        self.multi_n_gen_spin = QSpinBox()
        self.multi_n_gen_spin.setRange(1, 10**9)
        self.multi_n_gen_spin.setValue(100)
        self.multi_n_gen_spin.setToolTip("Required upper generation limit for every run in the Multi experiment.")
        self.multi_seed_spin = QSpinBox()
        self.multi_seed_spin.setRange(0, 2**31 - 1)
        self.multi_seed_spin.setValue(1)
        self.multi_seed_spin.setToolTip("The same seed is used for each combination to support fair comparisons.")
        self.multi_selection_lbl = QLabel("0 algorithms × 0 problems = 0 runs")
        settings.addRow("Maximum epochs (generations):", self.multi_n_gen_spin)
        settings.addRow("Seed:", self.multi_seed_spin)
        settings.addRow("Selection:", self.multi_selection_lbl)
        layout.addWidget(settings_group)

        button_row = QHBoxLayout()
        self.multi_start_btn = QPushButton("Start Multi")
        self.multi_stop_btn = QPushButton("Stop Multi")
        self.multi_stop_btn.setEnabled(False)
        button_row.addWidget(self.multi_start_btn)
        button_row.addWidget(self.multi_stop_btn)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.multi_progress = QProgressBar()
        self.multi_progress.setRange(0, 1)
        self.multi_progress.setValue(0)
        self.multi_status_lbl = QLabel("Status: idle")
        layout.addWidget(self.multi_progress)
        layout.addWidget(self.multi_status_lbl)

        self.multi_results_table = QTableWidget()
        self.multi_results_table.setColumnCount(10)
        self.multi_results_table.setHorizontalHeaderLabels(
            [
                "#",
                "Problem",
                "Algorithm",
                "Status",
                "Generation",
                "Evaluations",
                "NDS",
                "Metrics file",
                "Solutions file",
                "Error",
            ]
        )
        self.multi_results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.multi_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.multi_results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        multi_header = self.multi_results_table.horizontalHeader()
        multi_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        for column in (1, 2, 7, 8, 9):
            multi_header.setSectionResizeMode(column, QHeaderView.Stretch)
        layout.addWidget(self.multi_results_table, 2)

        self.multi_log = QTextEdit()
        self.multi_log.setReadOnly(True)
        self.multi_log.setPlaceholderText("Multi experiment messages appear here.")
        self.multi_log.setMaximumHeight(150)
        layout.addWidget(self.multi_log)
        return panel

    def _apply_english_ui_texts(self) -> None:
        # Normalize GUI captions and labels to English after widget construction.
        self._plot_placeholder.setText("No plot available. Start an optimization run.")
        self.problem_form.setTitle("Problem parameters")
        self.alg_form.setTitle("Algorithm parameters")
        self.run_form.setTitle("Run")
        self.hv_manual_radio.setText("Manual ref point")
        self.hv_manual_edit.setPlaceholderText("0.6 0.6 0.6 or 0.6,0.6,0.6")
        self.hv_ref_lbl.setText("HV ref point (active): -")
        self.live_updates.setText("Update plot during run")
        self.show_population_cb.setText("Show population")
        self.hide_pareto_front_cb.setText("Hide Pareto front")
        self.auto_scale_axes.setText("Auto-scale axes")
        self.nd_save_group.setTitle("Nondominated solution export")
        self.nd_save_mode_combo.setItemText(0, "Last epoch")
        self.nd_save_mode_combo.setItemText(1, "Every N epochs")
        self.nd_save_mode_combo.setItemText(2, "Cascade")
        self.console_btn.setText("Console")
        self.console_dock.setWindowTitle("Console")

    def _build_controls_panel(self) -> QWidget:
        # Build the left-side controls panel.
        panel = QWidget()
        panel.setMinimumWidth(440)
        panel.setMaximumWidth(440)
        self._left = QVBoxLayout(panel)
        self._build_problem_controls()
        self._build_hv_controls()
        self._build_run_controls()
        self._build_console()
        return panel

    def _build_results_panel(self) -> QWidget:
        # Build the right-side plot and metrics-history panel.
        self._plot_panel = QWidget()
        self._plot_layout = QVBoxLayout(self._plot_panel)
        self._plot_placeholder = QLabel("No plot available. Start an optimization run.")
        self._plot_placeholder.setAlignment(Qt.AlignCenter)
        self._plot_placeholder.setWordWrap(True)
        self._plot_layout.setContentsMargins(0, 0, 0, 0)
        epoch_row = QHBoxLayout()
        self.step_run_btn = QPushButton("RAN step")
        self.step_run_btn.setToolTip("Start an unlimited run paused after epoch 1; click again for the next epoch.")
        self.previous_epoch_btn = QPushButton("<")
        self.previous_epoch_btn.setToolTip("Previous computed epoch")
        self.next_epoch_btn = QPushButton(">")
        self.next_epoch_btn.setToolTip("Next computed epoch")
        self.epoch_spin = QSpinBox()
        self.epoch_spin.setRange(0, 0)
        self.epoch_spin.setKeyboardTracking(False)
        self.epoch_count_lbl = QLabel("/ 0")
        self.latest_epoch_btn = QPushButton("Latest")
        for widget in (self.step_run_btn, self.previous_epoch_btn, QLabel("Epoch:"),
                       self.epoch_spin, self.epoch_count_lbl, self.next_epoch_btn, self.latest_epoch_btn):
            epoch_row.addWidget(widget)
        epoch_row.addStretch()
        self._plot_layout.addLayout(epoch_row)
        plot_options = QHBoxLayout()
        self.grid_cb = QCheckBox("Show grid")
        self.grid_cb.setChecked(True)
        self.grid_spacing_spin = QDoubleSpinBox()
        self.grid_spacing_spin.setDecimals(4)
        self.grid_spacing_spin.setRange(0, 1e9)
        self.grid_spacing_spin.setSpecialValueText("Auto")
        self.grid_spacing_spin.setKeyboardTracking(False)
        self.grid_spacing_spin.setToolTip("Grid and axis tick interval, e.g. 1, 2, 3 or 0.5. Zero restores automatic spacing.")
        self.export_png_btn = QPushButton("Export PNG")
        plot_options.addWidget(self.grid_cb)
        plot_options.addWidget(QLabel("Grid interval:"))
        plot_options.addWidget(self.grid_spacing_spin)
        plot_options.addStretch()
        plot_options.addWidget(self.export_png_btn)
        self._plot_layout.addLayout(plot_options)
        self._plot_layout.addWidget(self._plot_placeholder, 1)

        self._table = QTableWidget()
        self._table.setColumnCount(3 + len(METRIC_TABLE_ORDER))
        self._table.setHorizontalHeaderLabels(
            ["n_gen", "n_eval", "n_nds", *[METRIC_LABELS[key] for key in METRIC_TABLE_ORDER]]
        )
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        for col in (3, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        panel = QSplitter(Qt.Vertical)
        panel.addWidget(self._plot_panel)
        panel.addWidget(self._table)
        panel.setStretchFactor(0, 3)
        panel.setStretchFactor(1, 1)
        return panel

    def _build_problem_controls(self) -> None:
        # Add problem and algorithm selectors with their dynamic parameter forms.
        self.problem_combo = QComboBox()
        for key, entry in PROBLEMS.items():
            self.problem_combo.addItem(entry.get("label", key), userData=key)
        self.problem_form = ParamForm("Problem parameters")

        self.alg_combo = QComboBox()
        for key, entry in ALGORITHMS.items():
            self.alg_combo.addItem(entry.get("label", key), userData=key)
        self.alg_form = ParamForm("Algorithm parameters")

        self._left.addWidget(QLabel("Problem:"))
        self._left.addWidget(self.problem_combo)
        self._left.addWidget(self.problem_form)
        self._left.addWidget(QLabel("Algorithm:"))
        self._left.addWidget(self.alg_combo)
        self._left.addWidget(self.alg_form)

    def _build_hv_controls(self) -> None:
        # Build controls for automatic or manual hypervolume reference points.
        self.hv_ref_group = QGroupBox("HV ref point")
        hv_layout = QVBoxLayout(self.hv_ref_group)
        mode_row = QHBoxLayout()
        self.hv_auto_radio = QRadioButton("Auto ref point")
        self.hv_manual_radio = QRadioButton("Manual ref point")
        self.hv_auto_radio.setChecked(True)
        mode_row.addWidget(self.hv_auto_radio)
        mode_row.addWidget(self.hv_manual_radio)
        hv_layout.addLayout(mode_row)
        self.hv_manual_edit = QLineEdit()
        self.hv_manual_edit.setPlaceholderText("0.6 0.6 0.6 or 0.6,0.6,0.6")
        self.hv_manual_edit.setEnabled(False)
        self.hv_ref_lbl = QLabel("HV ref point (active): -")
        hv_layout.addWidget(self.hv_manual_edit)
        hv_layout.addWidget(self.hv_ref_lbl)
        self._left.addWidget(self.hv_ref_group)

    def _build_run_controls(self) -> None:
        # Build run options, live-plot toggles, command buttons, and status labels.
        self.run_form = ParamForm("Run")
        self.run_form.build_from_specs(RUN_FORM_FIELDS)
        self._left.addWidget(self.run_form)

        self.live_updates = QCheckBox("Update plot during run")
        self.live_updates.setChecked(True)
        self.show_population_cb = QCheckBox("Show population")
        self.show_population_cb.setChecked(True)
        self.hide_pareto_front_cb = QCheckBox("Hide Pareto front")
        self.hide_pareto_front_cb.setChecked(False)
        self.auto_scale_axes = QCheckBox("Auto-scale axes")
        self.auto_scale_axes.setChecked(True)
        self.nd_save_group = QGroupBox("Nondominated solution export")
        nd_save_layout = QFormLayout(self.nd_save_group)
        self.nd_save_mode_combo = QComboBox()
        self.nd_save_mode_combo.addItem("Last epoch", userData=ND_SAVE_LAST_EPOCH)
        self.nd_save_mode_combo.addItem("Every N epochs", userData=ND_SAVE_EVERY_N_EPOCHS)
        self.nd_save_mode_combo.addItem("Cascade", userData=ND_SAVE_CASCADE)
        self.nd_save_step_spin = QSpinBox()
        self.nd_save_step_spin.setRange(1, 10**9)
        self.nd_save_step_spin.setValue(10)
        nd_save_layout.addRow("Mode:", self.nd_save_mode_combo)
        nd_save_layout.addRow("Step:", self.nd_save_step_spin)
        self._left.addWidget(self.live_updates)
        self._left.addWidget(self.show_population_cb)
        self._left.addWidget(self.hide_pareto_front_cb)
        self._left.addWidget(self.auto_scale_axes)
        self._left.addWidget(self.nd_save_group)

        button_row = QHBoxLayout()
        self.run_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.console_btn = QPushButton("Console")
        self.clear_btn = QPushButton("Clear")
        button_row.addWidget(self.run_btn)
        button_row.addWidget(self.stop_btn)
        button_row.addWidget(self.console_btn)
        button_row.addWidget(self.clear_btn)
        self._left.addLayout(button_row)

        self.status_lbl = QLabel("Status: idle")
        self.metrics_lbl = QLabel(self._metrics_label_text({}))
        self._left.addWidget(self.status_lbl)
        self._left.addWidget(self.metrics_lbl)
        self._left.addStretch(1)

    def _build_console(self) -> None:
        # Create the docked runtime console.
        self.text_out = QTextEdit()
        self.text_out.setReadOnly(True)
        self.console_dock = QDockWidget("Console", self)
        self.console_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.console_dock.setWidget(self.text_out)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)
        self.resizeDocks([self.console_dock], [120], Qt.Vertical)

    def _connect_signals(self) -> None:
        # Connect Qt widget signals to their event handlers.
        self.problem_combo.currentIndexChanged.connect(self._rebuild_problem_form)
        self.alg_combo.currentIndexChanged.connect(self._rebuild_alg_form)
        self.hv_auto_radio.toggled.connect(self._on_hv_mode_changed)
        self.hv_manual_radio.toggled.connect(self._on_hv_mode_changed)
        self.hv_manual_edit.textChanged.connect(self._on_hv_manual_changed)
        self.live_updates.toggled.connect(self._on_live_updates_toggled)
        self.show_population_cb.toggled.connect(self._on_show_population_toggled)
        self.hide_pareto_front_cb.toggled.connect(self._on_hide_pareto_front_toggled)
        self.auto_scale_axes.toggled.connect(self._on_auto_scale_toggled)
        self.nd_save_mode_combo.currentIndexChanged.connect(self._on_nd_save_mode_changed)
        self.run_btn.clicked.connect(self.start_run)
        self.step_run_btn.clicked.connect(self._run_next_epoch)
        self.previous_epoch_btn.clicked.connect(lambda: self._move_epoch(-1))
        self.next_epoch_btn.clicked.connect(lambda: self._move_epoch(1))
        self.latest_epoch_btn.clicked.connect(self._show_latest_epoch)
        self.epoch_spin.valueChanged.connect(self._show_epoch)
        self.grid_cb.toggled.connect(self._apply_grid_options)
        self.grid_spacing_spin.valueChanged.connect(self._apply_grid_options)
        self.export_png_btn.clicked.connect(self._export_plot_png)
        self.screenshot_btn.clicked.connect(self._export_window_screenshot)
        self.stop_btn.clicked.connect(self.stop_run)
        self.console_btn.clicked.connect(self._toggle_console_dock)
        self.clear_btn.clicked.connect(self._clear_console_and_visuals)
        self.console_dock.visibilityChanged.connect(self._on_console_visibility_changed)
        self._on_console_visibility_changed(self.console_dock.isVisible())
        self.multi_algorithm_list.itemChanged.connect(self._update_multi_selection_state)
        self.multi_problem_list.itemChanged.connect(self._update_multi_selection_state)
        self.multi_start_btn.clicked.connect(self.start_multi_experiment)
        self.multi_stop_btn.clicked.connect(self.stop_multi_experiment)
        ran_binding = self.run_form.binding("ran")
        if ran_binding is not None and isinstance(ran_binding.widget, QCheckBox):
            ran_binding.widget.toggled.connect(self._on_ran_toggled)
        parallel_binding = self.run_form.binding("parallel_eval")
        if parallel_binding is not None and isinstance(parallel_binding.widget, QCheckBox):
            parallel_binding.widget.toggled.connect(self._on_parallel_eval_toggled)
        self._update_multi_selection_state()

    def _configure_placeholders(self) -> None:
        # Configure initial tooltips, placeholders, and dependent run-form state.
        self.live_updates.setToolTip("Refresh the Pareto plot after each generation.")
        self.show_population_cb.setToolTip("Show or hide the full population in the Pareto plot.")
        self.hide_pareto_front_cb.setToolTip(
            "Hide the Pareto front without removing it from the data used by the metrics."
        )
        self.auto_scale_axes.setToolTip(
            "Fit the axis ranges for the current Pareto view without recomputing them on every generation."
        )
        self.clear_btn.setToolTip("Clear the console, Pareto plot, and metric trajectory charts.")
        self.nd_save_mode_combo.setToolTip("Choose for which epochs the nondominated front should be saved.")
        self.nd_save_step_spin.setToolTip("Positive integer used only in the 'Every N epochs' mode.")
        self._update_nd_save_controls_state()
        self._update_run_form_state()

    def _set_all_multi_items(self, widget: QListWidget, checked: bool) -> None:
        # Set all items in one Multi selection list to the same check state.
        if self._multi_thread and self._multi_thread.isRunning():
            return
        widget.blockSignals(True)
        try:
            state = Qt.Checked if checked else Qt.Unchecked
            for index in range(widget.count()):
                widget.item(index).setCheckState(state)
        finally:
            widget.blockSignals(False)
        self._update_multi_selection_state()

    def _checked_multi_keys(self, widget: QListWidget) -> list[str]:
        # Return registry keys for checked entries in display order.
        keys: list[str] = []
        for index in range(widget.count()):
            item = widget.item(index)
            if item.checkState() == Qt.Checked:
                key = item.data(Qt.UserRole)
                if key is not None:
                    keys.append(str(key))
        return keys

    def _update_multi_selection_state(self, *_args: Any) -> None:
        # Refresh the Cartesian run count and Multi button availability.
        algorithm_count = len(self._checked_multi_keys(self.multi_algorithm_list))
        problem_count = len(self._checked_multi_keys(self.multi_problem_list))
        run_count = algorithm_count * problem_count
        self.multi_selection_lbl.setText(
            f"{algorithm_count} algorithms × {problem_count} problems = {run_count} runs"
        )
        multi_running = bool(self._multi_thread and self._multi_thread.isRunning())
        single_running = bool(self._thread and self._thread.isRunning())
        self.multi_start_btn.setEnabled(run_count > 0 and not multi_running and not single_running)
        self.multi_stop_btn.setEnabled(multi_running)

    def _set_multi_running_state(self, running: bool) -> None:
        # Lock Multi configuration while the finite batch is running.
        self.multi_algorithm_group.setEnabled(not running)
        self.multi_problem_group.setEnabled(not running)
        self.multi_n_gen_spin.setEnabled(not running)
        self.multi_seed_spin.setEnabled(not running)
        self.multi_stop_btn.setEnabled(running)
        self.clear_btn.setEnabled(not running and not (self._thread and self._thread.isRunning()))
        if running:
            self.multi_start_btn.setEnabled(False)
            self.run_btn.setEnabled(False)
            self.step_run_btn.setEnabled(False)
        else:
            self._update_multi_selection_state()
            self._update_run_button_state()

    def _multi_row_key(self, payload: Mapping[str, Any]) -> tuple[str, str]:
        # Return the stable table key for one problem/algorithm combination.
        return str(payload.get("problem_key", "")), str(payload.get("algorithm_key", ""))

    def _set_multi_table_value(self, row: int, column: int, value: Any) -> None:
        # Store one display value in the Multi results table.
        text = "" if value is None else str(value)
        item = QTableWidgetItem(text)
        item.setToolTip(text)
        self.multi_results_table.setItem(row, column, item)

    def _on_multi_run_started(self, payload: Mapping[str, Any]) -> None:
        # Add a running combination to the Multi result table.
        row = self.multi_results_table.rowCount()
        self.multi_results_table.insertRow(row)
        self._multi_result_rows[self._multi_row_key(payload)] = row
        values = [
            payload.get("run_index"),
            payload.get("problem_name"),
            payload.get("algorithm_name"),
            "running",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
        for column, value in enumerate(values):
            self._set_multi_table_value(row, column, value)
        self.multi_log.append(
            f"Run {payload.get('run_index')}/{payload.get('total_runs')} started: "
            f"{payload.get('algorithm_name')} on {payload.get('problem_name')}."
        )

    def _on_multi_run_progress(self, payload: Mapping[str, Any]) -> None:
        # Update generation counters without creating any graphical visualization.
        row = self._multi_result_rows.get(self._multi_row_key(payload))
        if row is not None:
            self._set_multi_table_value(row, 4, payload.get("n_gen"))
            self._set_multi_table_value(row, 5, payload.get("n_eval"))
            self._set_multi_table_value(row, 6, payload.get("n_nds"))
        try:
            run_index = max(1, int(payload.get("run_index", 1)))
            generation = max(0, int(payload.get("n_gen", 0) or 0))
        except (TypeError, ValueError):
            return
        bounded_generation = min(generation, int(self.multi_n_gen_spin.value()))
        self.multi_progress.setValue((run_index - 1) * int(self.multi_n_gen_spin.value()) + bounded_generation)
        self.multi_status_lbl.setText(
            f"Status: run {run_index}/{payload.get('total_runs')}, generation "
            f"{generation}/{self.multi_n_gen_spin.value()}"
        )

    def _on_multi_run_finished(self, payload: Mapping[str, Any]) -> None:
        # Finalize one Multi table row and report its output files.
        row = self._multi_result_rows.get(self._multi_row_key(payload))
        if row is not None:
            values = {
                3: payload.get("status"),
                4: payload.get("n_gen"),
                5: payload.get("n_eval"),
                6: payload.get("n_nds"),
                7: payload.get("metrics_path"),
                8: payload.get("solutions_path"),
                9: payload.get("error"),
            }
            for column, value in values.items():
                self._set_multi_table_value(row, column, value)
        self.multi_log.append(
            f"Run {payload.get('run_index')}/{payload.get('total_runs')} {payload.get('status')}: "
            f"{payload.get('algorithm_name')} on {payload.get('problem_name')}."
        )
        if payload.get("metrics_path"):
            self.multi_log.append(f"Metrics saved: {payload.get('metrics_path')}")
        if payload.get("solutions_path"):
            self.multi_log.append(f"Solutions saved: {payload.get('solutions_path')}")
        if payload.get("error"):
            self.multi_log.append(f"Error: {payload.get('error')}")

    def start_multi_experiment(self) -> None:
        # Validate and start the finite Cartesian Multi experiment.
        if self._multi_thread and self._multi_thread.isRunning():
            self.multi_log.append("Start ignored: a Multi experiment is already running.")
            return
        if self._thread and self._thread.isRunning():
            QMessageBox.warning(self, "Run in progress", "Stop the Main run before starting a Multi experiment.")
            return
        problem_keys = self._checked_multi_keys(self.multi_problem_list)
        algorithm_keys = self._checked_multi_keys(self.multi_algorithm_list)
        if not problem_keys or not algorithm_keys:
            QMessageBox.warning(self, "Missing selection", "Select at least one problem and one algorithm.")
            return
        n_gen = int(self.multi_n_gen_spin.value())
        if n_gen < 1:
            QMessageBox.warning(self, "Invalid generation limit", "Maximum generations must be at least 1.")
            return
        try:
            specs = build_multi_run_specs(problem_keys, algorithm_keys)
        except KeyError as exc:
            QMessageBox.warning(self, "Invalid selection", str(exc))
            return

        seed = int(self.multi_seed_spin.value())
        self.multi_results_table.setRowCount(0)
        self.multi_log.clear()
        self._multi_result_rows = {}
        self.multi_progress.setRange(0, max(1, len(specs) * n_gen))
        self.multi_progress.setValue(0)
        self.multi_status_lbl.setText(f"Status: starting {len(specs)} runs")
        self.multi_log.append(
            f"Multi experiment started: {len(algorithm_keys)} algorithms × {len(problem_keys)} problems = "
            f"{len(specs)} runs, maximum generations={n_gen}, seed={seed}."
        )

        self._multi_thread = MultiExperimentWorker(
            specs,
            n_gen=n_gen,
            seed=seed,
            project_root=results_root(),
            parent=self,
        )
        self._multi_thread.run_started.connect(self._on_multi_run_started)
        self._multi_thread.run_progress.connect(self._on_multi_run_progress)
        self._multi_thread.run_finished.connect(self._on_multi_run_finished)
        self._multi_thread.done.connect(self._on_multi_experiment_done)
        self._multi_thread.cancelled.connect(self._on_multi_experiment_cancelled)
        self._multi_thread.failed.connect(self._on_multi_experiment_failed)
        self._set_multi_running_state(True)
        self._multi_thread.start()

    def stop_multi_experiment(self) -> None:
        # Request cooperative cancellation of the active Multi experiment.
        if not self._multi_thread or not self._multi_thread.isRunning():
            self.multi_log.append("Stop ignored: no Multi experiment is running.")
            return
        self._multi_thread.request_cancel()
        self.multi_stop_btn.setEnabled(False)
        self.multi_status_lbl.setText("Status: stopping")
        self.multi_log.append("Cancellation requested; waiting for the current generation callback.")

    def _finish_multi_experiment(self, status: str, results: Sequence[Mapping[str, Any]]) -> None:
        # Restore controls and summarize terminal Multi experiment state.
        total = len(results)
        failed = sum(1 for result in results if result.get("status") == "failed")
        completed = sum(1 for result in results if result.get("status") == "completed")
        self._multi_thread = None
        self._set_multi_running_state(False)
        if status == "completed":
            self.multi_progress.setValue(self.multi_progress.maximum())
        self.multi_status_lbl.setText(
            f"Status: {status}; completed={completed}, failed={failed}, processed={total}"
        )
        self.multi_log.append(
            f"Multi experiment {status}: completed={completed}, failed={failed}, processed={total}."
        )

    def _on_multi_experiment_done(self, results: Sequence[Mapping[str, Any]]) -> None:
        # Handle normal completion of every selected combination.
        self._finish_multi_experiment("completed", results)

    def _on_multi_experiment_cancelled(self, results: Sequence[Mapping[str, Any]]) -> None:
        # Handle user cancellation while preserving already exported results.
        self._finish_multi_experiment("cancelled", results)

    def _on_multi_experiment_failed(self, error: str) -> None:
        # Handle an unexpected worker-level failure.
        self._multi_thread = None
        self._set_multi_running_state(False)
        self.multi_status_lbl.setText("Status: error")
        self.multi_log.append(f"Multi experiment failed: {error}")
        QMessageBox.warning(self, "Multi experiment error", error)

    def _entry(self, combo: QComboBox, registry: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]:
        # Return the registry entry for the current combo-box selection.
        key = combo.currentData()
        return dict(registry.get(str(key), {})) if key is not None else {}

    def _known_pf_for_problem(self, entry: Mapping[str, Any], problem: Any) -> Optional[np.ndarray]:
        # Resolve and normalize a known Pareto front for preview and metrics.
        known_pf_factory = entry.get("known_pf_factory")
        if callable(known_pf_factory):
            try:
                known_pf = known_pf_factory(problem)
            except Exception as exc:
                self._log(f"Preview known_pf failed: {exc!r}")
                return None
            try:
                data = np.asarray(known_pf, dtype=float)
            except (TypeError, ValueError):
                return None
            if data.ndim == 1:
                data = data.reshape(1, -1)
            if data.ndim != 2 or data.shape[0] == 0:
                return None
            data = data[np.isfinite(data).all(axis=1)]
            return data if data.shape[0] > 0 else None
        return known_pareto_front(problem)

    def _instantiate_selected_problem(
        self,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[Optional[Any], Optional[str]]:
        # Instantiate the selected problem and return an error string instead of raising.
        entry = self._entry(self.problem_combo, PROBLEMS)
        factory = entry.get("factory")
        if not callable(factory):
            return None, "No valid problem factory is available."
        params = dict(params or self.problem_form.values())
        try:
            return factory(**filter_callable_kwargs(factory, params)), None
        except Exception as exc:
            return None, repr(exc)

    def _connect_problem_form_signals(self) -> None:
        # Connect dynamic problem-form widgets to preview refresh handling.
        for binding in self.problem_form.bindings():
            widget = binding.widget
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.valueChanged.connect(self._on_problem_form_changed)
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_problem_form_changed)
            elif isinstance(widget, QCheckBox):
                widget.toggled.connect(self._on_problem_form_changed)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._on_problem_form_changed)

    def _ensure_plot_widget(self) -> UnifiedParetoWidget:
        # Create or reuse a Pareto plot widget matching the current objective count.
        n_obj = int(self._plot_n_obj or 2)
        if self._plot_widget is not None and self._plot_widget_dim != n_obj:
            self._plot_layout.removeWidget(self._plot_widget)
            self._plot_widget.setParent(None)
            self._plot_widget.deleteLater()
            self._plot_widget = None
            self._plot_widget_dim = None
        if self._plot_widget is None:
            front = self._plot_known_pf
            if front is None:
                front = np.empty((0, n_obj))
            self._plot_widget = UnifiedParetoWidget(
                front,
                parent=self._plot_panel,
                objective_names=tuple(f"f{i + 1}" for i in range(n_obj)),
            )
            self._plot_widget_dim = n_obj
            self._plot_layout.addWidget(self._plot_widget, 1)
        self._plot_widget.set_auto_scale(self.auto_scale_axes.isChecked())
        self._plot_widget.set_grid(self.grid_cb.isChecked(), self.grid_spacing_spin.value())
        self.export_png_btn.setEnabled(True)
        return self._plot_widget

    def _reset_plot_axes(self) -> None:
        # Reset cached plot axis limits when the underlying data context changes.
        if self._plot_widget is not None and hasattr(self._plot_widget, "reset_view_limits"):
            self._plot_widget.reset_view_limits()

    def _set_plot_message(self, text: str) -> None:
        # Hide the plot widget and show an explanatory placeholder message.
        self._plot_placeholder.setText(translate_ui_text(text))
        self._plot_placeholder.show()
        self.export_png_btn.setEnabled(False)
        if self._plot_widget is not None:
            self._plot_widget.hide()

    def _reset_plot_run_data(self) -> None:
        # Clear per-run plot data while keeping problem-level reference data.
        self._plot_feasible_nd_F = None
        self._plot_population_F = None
        self._plot_generation = None
        self._epoch_history.clear()
        self._update_epoch_controls()

    def _update_epoch_controls(self) -> None:
        epochs = sorted(self._epoch_history)
        current = self._plot_generation or 0
        self.epoch_spin.blockSignals(True)
        self.epoch_spin.setRange(epochs[0] if epochs else 0, epochs[-1] if epochs else 0)
        self.epoch_spin.setValue(current)
        self.epoch_spin.blockSignals(False)
        self.epoch_spin.setEnabled(bool(epochs))
        self.epoch_count_lbl.setText(f"/ {epochs[-1] if epochs else 0}")
        self.previous_epoch_btn.setEnabled(any(epoch < current for epoch in epochs))
        self.next_epoch_btn.setEnabled(any(epoch > current for epoch in epochs))
        self.latest_epoch_btn.setEnabled(bool(epochs) and current != epochs[-1])

    def _remember_epoch(self, payload: Mapping[str, Any]) -> None:
        epoch = payload.get("n_gen")
        if epoch is None:
            return
        # Keep only plot data and summary values, without decision-variable matrices.
        snapshot = {key: payload.get(key) for key in (*METRIC_DISPLAY_ORDER, "n_gen", "n_eval", "n_nds")}
        for key in ("population_F", "feasible_nd_F"):
            data = payload.get(key)
            snapshot[key] = None if data is None else np.array(data, copy=True)
        snapshot["known_pf"] = payload.get("known_pf")
        self._epoch_history[int(epoch)] = snapshot

    def _show_epoch(self, epoch: int) -> None:
        payload = self._epoch_history.get(epoch)
        if payload is None:
            return
        self._apply_generation_payload(payload)
        self._update_metrics_label(payload)
        self._render_plot()
        self._update_epoch_controls()

    def _move_epoch(self, direction: int) -> None:
        current = self._plot_generation or 0
        epochs = sorted(epoch for epoch in self._epoch_history if (epoch - current) * direction > 0)
        if epochs:
            self._show_epoch(epochs[0] if direction > 0 else epochs[-1])

    def _show_latest_epoch(self) -> None:
        if self._epoch_history:
            self._show_epoch(max(self._epoch_history))

    def _apply_grid_options(self, *_args: Any) -> None:
        self.grid_spacing_spin.setEnabled(self.grid_cb.isChecked())
        if self._plot_widget is not None:
            self._plot_widget.set_grid(self.grid_cb.isChecked(), self.grid_spacing_spin.value())

    def _export_window_screenshot(self) -> None:
        # Capture the current window before opening the save dialog.
        screenshot = self.grab()
        name = f"AGtest_screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save application screenshot", str(results_root() / name), "PNG image (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        if not screenshot.save(path, "PNG"):
            self._warn("Screenshot export failed", f"Could not save PNG: {path}")
            return
        self._log(f"Saved application screenshot: {path}")

    def _export_plot_png(self) -> None:
        if self._plot_widget is None or self._plot_widget.isHidden():
            return
        name = f"pareto_epoch_{self._plot_generation}.png" if self._plot_generation else "pareto.png"
        path, _ = QFileDialog.getSaveFileName(self, "Export Pareto plot", str(results_root() / name), "PNG image (*.png)")
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        try:
            self._plot_widget.export_png(path)
        except Exception as exc:
            self._warn("PNG export failed", str(exc))
            return
        self._log(f"Saved Pareto plot: {path}")

    def _run_next_epoch(self) -> None:
        if self._thread and self._thread.isRunning():
            self._show_latest_epoch()
            if self._thread.request_next_epoch():
                self.step_run_btn.setEnabled(False)
                self.status_lbl.setText("Status: computing next epoch")
            return
        self.start_run(step_mode=True)

    def _reset_run_result_state(self) -> None:
        # Clear metrics history, run plot data, and summary labels.
        self._clear_table()
        self._reset_plot_run_data()
        self._update_metrics_label(None)

    def _update_run_form_state(self) -> None:
        # Enable or disable run-form fields according to RAN and parallel-evaluation toggles.
        ran_binding = self.run_form.binding("ran")
        n_gen_binding = self.run_form.binding("n_gen")
        if ran_binding is not None and n_gen_binding is not None:
            ran_enabled = bool(ran_binding.widget.isChecked())
            n_gen_widget = n_gen_binding.widget
            if isinstance(n_gen_widget, (QSpinBox, QDoubleSpinBox)):
                n_gen_widget.setEnabled(not ran_enabled)
            if isinstance(n_gen_widget, QAbstractSpinBox):
                n_gen_widget.setReadOnly(ran_enabled)
                n_gen_widget.setButtonSymbols(
                    QAbstractSpinBox.NoButtons if ran_enabled else QAbstractSpinBox.UpDownArrows
                )

        parallel_binding = self.run_form.binding("parallel_eval")
        parallel_workers_binding = self.run_form.binding("parallel_workers")
        parallel_backend_binding = self.run_form.binding("parallel_backend")
        if parallel_binding is not None:
            parallel_enabled = bool(parallel_binding.widget.isChecked())
            for binding in (parallel_workers_binding, parallel_backend_binding):
                if binding is not None:
                    binding.widget.setEnabled(parallel_enabled)

    def _current_nd_save_mode(self) -> str:
        # Return the selected nondominated-solution save mode.
        mode = self.nd_save_mode_combo.currentData()
        return str(mode) if mode is not None else ND_SAVE_LAST_EPOCH

    def _update_nd_save_controls_state(self) -> None:
        # Enable the step field only for the "every N epochs" save mode.
        self.nd_save_step_spin.setEnabled(self._current_nd_save_mode() == ND_SAVE_EVERY_N_EPOCHS)

    def _collect_nd_save_args(self) -> Tuple[Optional[dict], Optional[str]]:
        # Validate nondominated-solution export settings selected in the GUI.
        mode = self._current_nd_save_mode()
        if mode not in {ND_SAVE_LAST_EPOCH, "every_epoch", ND_SAVE_EVERY_N_EPOCHS, ND_SAVE_CASCADE}:
            return None, "Invalid nondominated-solution export mode."
        step, error = self._validated_int(self.nd_save_step_spin.value(), "Solution export step", 1)
        if error:
            return None, error
        return {"mode": mode, "step": int(step)}, None

    def _set_run_state(self, status_text: str, running: bool) -> None:
        # Update run status text and Start/Stop button availability.
        self.status_lbl.setText(translate_ui_text(f"Status: {status_text}"))
        multi_running = bool(self._multi_thread and self._multi_thread.isRunning())
        self.run_btn.setEnabled(not running and not multi_running and self._validate_hv_manual_ref_point())
        self.stop_btn.setEnabled(running)
        self.clear_btn.setEnabled(not running and not multi_running)
        self.step_run_btn.setEnabled(not running and not multi_running and self._validate_hv_manual_ref_point())
        self.step_run_btn.setText("RAN step")
        for widget in (self.problem_combo, self.problem_form, self.alg_combo, self.alg_form, self.run_form, self.hv_ref_group):
            widget.setEnabled(not running)
        if running:
            self.multi_start_btn.setEnabled(False)
        else:
            self._update_multi_selection_state()

    def _apply_generation_payload(self, payload: Mapping[str, Any]) -> None:
        # Copy generation payload data into plot-state fields.
        known_pf = payload.get("known_pf")
        if known_pf is not None:
            self._plot_known_pf = known_pf
        self._plot_feasible_nd_F = payload.get("feasible_nd_F")
        self._plot_population_F = payload.get("population_F")
        self._plot_generation = payload.get("n_gen")

    def _apply_problem_preview_state(self, problem: Any) -> None:
        # Refresh problem-level Pareto preview data after problem changes.
        entry = self._entry(self.problem_combo, PROBLEMS)
        self._plot_known_pf = self._known_pf_for_problem(entry, problem)
        try:
            self._plot_n_obj = int(getattr(problem, "n_obj", 0))
        except (TypeError, ValueError):
            self._plot_n_obj = None
        self._render_plot()

    def _refresh_problem_plot(self) -> None:
        # Recreate the selected problem and refresh the Pareto preview.
        problem, error = self._instantiate_selected_problem()
        self._reset_plot_run_data()
        self._reset_plot_axes()
        if problem is None:
            self._plot_known_pf = None
            self._plot_n_obj = None
            self._set_plot_message("Unable to prepare the Pareto preview.")
            if error:
                self._log(f"Preview: {error}")
            return
        self._apply_problem_preview_state(problem)

    def _render_plot(self) -> None:
        # Render the current 2D/3D Pareto data or show a dimensionality message.
        if self._plot_n_obj not in (2, 3):
            label = "?" if self._plot_n_obj is None else str(self._plot_n_obj)
            self._set_plot_message(
                f"Pareto preview is available only for 2 or 3 objectives. The selected problem has {label}."
            )
            return
        widget = self._ensure_plot_widget()
        self._plot_placeholder.hide()
        widget.show()
        n_obj = int(self._plot_n_obj)
        widget.set_show_population(self.show_population_cb.isChecked())
        pop = self._plot_population_F
        ref = np.empty((0, n_obj)) if self.hide_pareto_front_cb.isChecked() else self._plot_known_pf
        widget.update_points(pop, self._plot_feasible_nd_F, ref, self._plot_generation)

    def _rebuild_problem_form(self) -> None:
        # Rebuild problem parameter widgets after the selected problem changes.
        entry = self._entry(self.problem_combo, PROBLEMS)
        self.problem_form.build_for_callable(entry["factory"], entry.get("form_fields"))
        self.problem_form.setToolTip(translate_ui_text(entry.get("form_note") or ""))
        self._connect_problem_form_signals()
        self._connect_problem_param_signals()
        self._refresh_problem_plot()
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _rebuild_alg_form(self) -> None:
        # Rebuild algorithm parameter widgets after the selected algorithm changes.
        entry = self._entry(self.alg_combo, ALGORITHMS)
        self.alg_form.build_for_callable(entry["factory"], entry.get("form_fields"))
        self.alg_form.setToolTip(translate_ui_text(entry.get("form_note") or ""))

    def _connect_problem_param_signals(self) -> None:
        # Track the `n_obj` field because it affects HV validation and plotting.
        binding = self.problem_form.binding("n_obj")
        widget = binding.widget if binding and isinstance(binding.widget, QSpinBox) else None
        if self._n_obj_widget is not None and self._n_obj_widget is not widget:
            try:
                self._n_obj_widget.valueChanged.disconnect(self._on_n_obj_changed)
            except (TypeError, RuntimeError):
                pass
        self._n_obj_widget = widget
        if self._n_obj_widget is not None:
            try:
                self._n_obj_widget.valueChanged.disconnect(self._on_n_obj_changed)
            except (TypeError, RuntimeError):
                pass
            self._n_obj_widget.valueChanged.connect(self._on_n_obj_changed)

    def _on_n_obj_changed(self, _value: int) -> None:
        # Refresh HV validation and run availability after objective-count changes.
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _on_problem_form_changed(self, *_args: Any) -> None:
        # Handle any problem-parameter change by refreshing the preview.
        self._refresh_problem_plot()

    def _on_show_population_toggled(self, checked: bool) -> None:
        # Toggle the full-population layer on the Pareto plot.
        self._log(f"show_population={checked} (full population as a separate layer)")
        self._render_plot()

    def _on_hide_pareto_front_toggled(self, checked: bool) -> None:
        # Toggle display of the known Pareto-front reference layer.
        self._log(f"hide_pareto_front={checked}")
        if checked or self.auto_scale_axes.isChecked():
            self._reset_plot_axes()
        self._render_plot()

    def _on_auto_scale_toggled(self, checked: bool) -> None:
        # Toggle plot auto-scaling and reset cached limits when re-enabled.
        self._log(f"auto_scale={checked}")
        if self._plot_widget is not None:
            self._plot_widget.set_auto_scale(bool(checked))
        if checked:
            self._reset_plot_axes()
            self._render_plot()

    def _on_nd_save_mode_changed(self, _index: int) -> None:
        # React to changes of the nondominated-solution save mode.
        self._update_nd_save_controls_state()

    def _on_ran_toggled(self, checked: bool) -> None:
        # Handle switching the run to or from unbounded RAN mode.
        self._update_run_form_state()
        self._log(f"RAN={checked}")

    def _on_parallel_eval_toggled(self, checked: bool) -> None:
        # Enable or disable fields related to parallel objective evaluation.
        self._update_run_form_state()
        self._log(f"parallel_eval={checked}")

    def _toggle_console_dock(self) -> None:
        # Toggle the visibility of the docked console.
        self.console_dock.setVisible(not self.console_dock.isVisible())

    def _on_console_visibility_changed(self, visible: bool) -> None:
        # Keep the console button label synchronized with dock visibility.
        self.console_btn.setText("Hide console" if visible else "Show console")

    def _log(self, msg: str) -> None:
        # Append a message to the GUI console.
        self.text_out.append(translate_ui_text(msg))
        if self.console_dock.isVisible():
            self.text_out.ensureCursorVisible()

    def _warn(self, title: str, message: str, log_message: Optional[str] = None) -> None:
        # Show a warning dialog and optionally record the same issue in the console.
        if log_message:
            self._log(log_message)
        QMessageBox.warning(self, translate_ui_text(title), translate_ui_text(message))

    def _current_n_obj(self) -> int:
        # Return the current objective count with a safe fallback.
        if self._n_obj_widget is not None:
            value = int(self._n_obj_widget.value())
            if value > 0:
                return value
        raw = self.problem_form.values().get("n_obj")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = 2
        return value if value > 0 else 2

    def _parse_float_token(self, token: str) -> Optional[float]:
        # Parse one numeric token using Polish and C locale conventions.
        token = token.strip()
        if not token:
            return None
        for locale in (QLocale(), QLocale(QLocale.Polish, QLocale.Poland), QLocale.c()):
            value, ok = locale.toDouble(token)
            if ok and math.isfinite(value):
                return value
        normalized = token.replace(" ", "")
        if normalized.count(",") == 1 and "." not in normalized:
            normalized = normalized.replace(",", ".")
        try:
            value = float(normalized)
        except ValueError:
            return None
        return value if math.isfinite(value) else None

    def _parse_ref_point_text(self, text: str) -> Tuple[Optional[list[float]], Optional[str]]:
        # Parse manual HV reference-point text into a list of finite floats.
        cleaned = text.strip().replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ").strip()
        if not cleaned:
            return None, None
        if "." in cleaned:
            tokens = [part for part in re.split(r"[;,\s]+", cleaned) if part]
        elif ";" in cleaned or re.search(r"\s", cleaned):
            tokens = [part.strip().strip(",") for part in re.split(r"[;\s]+", cleaned) if part.strip()]
        elif cleaned.count(",") > 1:
            return None, "For decimal commas, separate dimensions with spaces or ';', e.g. '0,6 0,7'."
        else:
            tokens = [cleaned]
        values = []
        for token in tokens:
            value = self._parse_float_token(token)
            if value is None:
                return None, f"Unable to parse the number '{token}'. Use, for example, '0,6 0,7' or '0.6,0.7'."
            values.append(value)
        return values, None

    def _auto_hv_ref_point(self) -> list[float]:
        # Build the default hypervolume reference point for the current objective count.
        return [1.1 for _ in range(self._current_n_obj())]

    def _hv_ref_point_state(self) -> Tuple[bool, Optional[list[float]], str, Optional[str]]:
        # Return validity, values, mode, and error message for the active HV reference point.
        if not self.hv_manual_radio.isChecked():
            values = self._auto_hv_ref_point()
            return True, values, "AUTO", None
        values, error = self._parse_ref_point_text(self.hv_manual_edit.text())
        if error:
            return False, None, "MANUAL", error
        if values is None:
            return False, None, "MANUAL", "Enter a ref_point or switch to Auto mode."
        expected = self._current_n_obj()
        if len(values) != expected:
            return False, None, "MANUAL", f"ref_point has length {len(values)}; expected M={expected}."
        return True, values, "MANUAL", None

    def _validate_hv_manual_ref_point(self) -> bool:
        # Validate manual HV input and mark the field when invalid.
        if not self.hv_manual_radio.isChecked():
            self.hv_manual_edit.setStyleSheet("")
            self.hv_manual_edit.setToolTip("")
            return True
        valid, _values, _mode, error = self._hv_ref_point_state()
        self.hv_manual_edit.setStyleSheet("" if valid else "border: 1px solid #d33;")
        self.hv_manual_edit.setToolTip("" if valid else error or "")
        return valid

    def _update_hv_ref_point_label(self) -> None:
        # Update the label showing the currently active HV reference point.
        valid, values, mode, error = self._hv_ref_point_state()
        if not valid or values is None:
            self.hv_ref_lbl.setText("HV ref point (active): INVALID")
            self.hv_ref_lbl.setToolTip(error or "")
            return
        self.hv_ref_lbl.setText("HV ref point (active): [" + ",".join(f"{v:.4g}" for v in values) + "]")
        self.hv_ref_lbl.setToolTip(f"mode={mode}")

    def _on_hv_mode_changed(self, _checked: bool) -> None:
        # Handle switching between automatic and manual HV reference-point mode.
        manual = self.hv_manual_radio.isChecked()
        self.hv_manual_edit.setEnabled(manual)
        if manual and not self.hv_manual_edit.text().strip():
            self.hv_manual_edit.setText(" ".join(f"{v:.6g}" for v in self._auto_hv_ref_point()))
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _on_hv_manual_changed(self, _text: str) -> None:
        # Revalidate and refresh the manual HV reference-point display.
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _on_live_updates_toggled(self, checked: bool) -> None:
        # Toggle live plot updates during optimization.
        self._log(f"live_updates={checked}")
        self._render_plot()

    def _update_run_button_state(self) -> None:
        # Enable Start only when no run is active and HV configuration is valid.
        self.run_btn.setEnabled(
            not (self._thread and self._thread.isRunning())
            and not (self._multi_thread and self._multi_thread.isRunning())
            and self._validate_hv_manual_ref_point()
        )
        if not (self._thread and self._thread.isRunning()):
            self.step_run_btn.setEnabled(self.run_btn.isEnabled())

    def _update_plot_status(self, payload: Optional[dict] = None, message: Optional[str] = None) -> None:
        # Refresh the plot or placeholder status after generation updates.
        if self._plot_n_obj in (2, 3):
            self._render_plot()
            return
        if message:
            self._plot_placeholder.setText(translate_ui_text(message))
            return
        if payload:
            self._plot_placeholder.setText(
                f"Pareto preview is unavailable for {self._plot_n_obj or '?'} objectives. "
                f"Gen={self._fmt_int(payload.get('n_gen'))}"
            )
            return
        self._set_plot_message("No plot available. Start an optimization run.")

    def _fmt_int(self, value: Optional[int]) -> str:
        # Format optional integers for labels and table cells.
        try:
            return "-" if value is None else str(int(value))
        except (TypeError, ValueError):
            return "-"

    def _fmt_metric(self, value: Optional[float]) -> str:
        # Format optional metric values with stable precision for the GUI.
        try:
            return "-" if value is None else f"{float(value):.10g}"
        except (TypeError, ValueError):
            return "-"

    def _update_metrics_label(self, payload: Optional[dict]) -> None:
        # Update the compact metrics summary label.
        self.metrics_lbl.setText(self._metrics_label_text(payload or {}))

    def _metrics_label_text(self, payload: Mapping[str, Any]) -> str:
        # Build one-line metric summary text from a payload.
        return " | ".join(
            f"{METRIC_LABELS[key]}: {self._fmt_metric(payload.get(key))}" for key in METRIC_DISPLAY_ORDER
        )

    def _clear_table(self) -> None:
        # Clear the generation-history metrics table.
        self._table.setRowCount(0)
        self._last_gen_appended = None

    def _should_scroll_table(self) -> bool:
        # Return whether the metrics table should remain scrolled to the newest row.
        bar = self._table.verticalScrollBar()
        return self._table.rowCount() == 0 or bar.value() >= bar.maximum() - 2

    def _append_generation_row(self, payload: dict) -> None:
        # Append one generation's counters and metrics to the history table.
        should_scroll = self._should_scroll_table()
        row = self._table.rowCount()
        self._table.insertRow(row)
        values = [
            self._fmt_int(payload.get("n_gen")),
            self._fmt_int(payload.get("n_eval")),
            self._fmt_int(payload.get("n_nds")),
            *[self._fmt_metric(payload.get(key)) for key in METRIC_TABLE_ORDER],
        ]
        for col, text in enumerate(values):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setToolTip(text)
            self._table.setItem(row, col, item)
        try:
            self._last_gen_appended = int(payload.get("n_gen")) if payload.get("n_gen") is not None else None
        except (TypeError, ValueError):
            self._last_gen_appended = None
        if should_scroll:
            self._table.verticalScrollBar().setValue(self._table.verticalScrollBar().maximum())

    def _append_last_payload_once(self, payload: Mapping[str, Any]) -> None:
        # Append the final payload only if it was not already recorded.
        last_gen = payload.get("n_gen")
        if last_gen is not None and last_gen != self._last_gen_appended:
            self._append_generation_row(dict(payload))
        elif self._last_gen_appended is None and payload:
            self._append_generation_row(dict(payload))

    def _metrics_table_data(self) -> Tuple[list[str], list[list[str]]]:
        # Extract headers and rows from the metrics table for export.
        headers: list[str] = []
        for col in range(self._table.columnCount()):
            item = self._table.horizontalHeaderItem(col)
            headers.append(item.text() if item is not None else f"col_{col + 1}")

        rows: list[list[str]] = []
        for row in range(self._table.rowCount()):
            values: list[str] = []
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                values.append(item.text() if item is not None else "")
            rows.append(values)
        return headers, rows

    def _export_metrics_table(self) -> None:
        # Export the current metrics table to an XLSX file when it contains data.
        if self._table.rowCount() <= 0:
            self._log("Metrics export skipped: the history table is empty.")
            return
        headers, rows = self._metrics_table_data()
        project_root = results_root()
        path = self._run_metrics_export_path or metrics_export_path(
            project_root,
            self._run_algorithm_name or self.alg_combo.currentText(),
            self._run_problem_name or self.problem_combo.currentText(),
        )
        try:
            saved_path = write_xlsx_table(path, headers, rows)
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            self._log(f"Metrics export failed: {exc!r}")
            return
        self._log(f"Metrics export saved: {saved_path}")

    def _xlsx_value(self, value: Any) -> object:
        # Normalize values before storing them in a worksheet cell.
        if value is None:
            return ""
        if isinstance(value, np.generic):
            value = value.item()
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return str(value)
        return numeric if math.isfinite(numeric) else ""

    def _solution_table_data(self, payload: Mapping[str, Any]) -> Tuple[list[str], list[list[object]]]:
        # Build spreadsheet headers and rows from the final nondominated front.
        raw_F = payload.get("feasible_nd_F")
        try:
            f_raw = np.asarray(raw_F, dtype=float) if raw_F is not None else np.empty((0, self._current_n_obj()))
        except (TypeError, ValueError):
            f_raw = np.empty((0, self._current_n_obj()))
        if f_raw.ndim == 1:
            f_raw = f_raw.reshape(-1, 1)
        if f_raw.ndim != 2:
            f_raw = np.empty((0, self._current_n_obj()))

        n_obj = int(f_raw.shape[1]) if f_raw.ndim == 2 and f_raw.shape[1] > 0 else self._current_n_obj()
        finite_mask = np.isfinite(f_raw).all(axis=1) if f_raw.shape[0] > 0 else np.empty(0, dtype=bool)
        f_arr = f_raw[finite_mask] if f_raw.shape[0] > 0 else np.empty((0, n_obj))

        headers: list[str] = ["id", *[f"f{i + 1}" for i in range(n_obj)]]
        x_arr: Optional[np.ndarray] = None
        raw_X = payload.get("feasible_nd_X")
        if raw_X is not None and f_raw.shape[0] > 0:
            try:
                x_raw = np.asarray(raw_X, dtype=object)
            except (TypeError, ValueError):
                x_raw = None
            if x_raw is not None:
                if x_raw.ndim == 1 and f_raw.shape[0] == 1:
                    x_raw = x_raw.reshape(1, -1)
                elif x_raw.ndim == 1 and x_raw.shape[0] == f_raw.shape[0]:
                    x_raw = x_raw.reshape(-1, 1)
                if x_raw.ndim == 2 and x_raw.shape[0] == f_raw.shape[0]:
                    x_arr = x_raw[finite_mask]
                    headers.extend(f"x{i + 1}" for i in range(x_arr.shape[1]))

        rows: list[list[object]] = []
        for row_id, f_values in enumerate(f_arr, start=1):
            row: list[object] = [row_id, *[self._xlsx_value(value) for value in f_values]]
            if x_arr is not None:
                row.extend(self._xlsx_value(value) for value in x_arr[row_id - 1])
            rows.append(row)
        return headers, rows

    def _export_solution_table(self, payload: Mapping[str, Any]) -> None:
        # Export final nondominated points to the project solution-table directory.
        project_root = results_root()
        algorithm_name = self._run_algorithm_name or self.alg_combo.currentText()
        problem_name = self._run_problem_name or self.problem_combo.currentText()
        path = self._run_solutions_export_path or solutions_export_path(project_root, algorithm_name, problem_name)
        if self._nd_solution_sheets:
            sheets = [
                (f"Epoch {epoch}", headers, rows)
                for epoch, (headers, rows) in sorted(self._nd_solution_sheets.items())
            ]
        else:
            headers, rows = self._solution_table_data(payload)
            sheets = [("Solutions", headers, rows)]
        try:
            saved_path = write_xlsx_workbook(path, sheets)
            created = saved_path.is_file() and saved_path.stat().st_size > 0
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            self._log(f"Nondominated-point export failed: {exc!r}")
            return
        if not created:
            self._log(f"Nondominated-point export did not create a file: {saved_path}")
            return

        total_rows = sum(len(rows) for _sheet_name, _headers, rows in sheets)
        self._log(f"Created Excel file with nondominated points: {saved_path}")
        self._log(f"Number of saved points: {total_rows}")
        self._log(f"Data source run: {algorithm_name} + {problem_name}")

    def _export_nondominated_solutions_for_epoch(self, payload: Mapping[str, Any]) -> None:
        # Export nondominated solutions for the current epoch when the selected mode requires it.
        epoch = payload.get("n_gen")
        if not should_save_nondominated_solutions_for_epoch(epoch, self._run_nd_save_mode, self._run_nd_save_step):
            return
        try:
            epoch_number = int(epoch)
        except (TypeError, ValueError):
            return
        if epoch_number in self._nd_solution_sheets:
            return
        headers, rows = self._solution_table_data(payload)
        self._nd_solution_sheets[epoch_number] = (list(headers), list(rows))
        try:
            self._export_solution_table(payload)
        except Exception as exc:
            self._log(f"Nondominated-point export for epoch {epoch_number} failed: {exc!r}")
            return
        self._log(f"Saved nondominated points in the worksheet for epoch {epoch_number}.")

    def _export_nondominated_solutions_for_final_epoch(self, payload: Mapping[str, Any]) -> None:
        # Export nondominated solutions for the final epoch when the selected mode requires it.
        epoch = payload.get("n_gen")
        if not should_save_nondominated_solutions_for_epoch(
            epoch,
            self._run_nd_save_mode,
            self._run_nd_save_step,
            is_final=True,
        ):
            return
        try:
            epoch_number = int(epoch)
        except (TypeError, ValueError):
            return
        if epoch_number in self._nd_solution_sheets:
            return
        headers, rows = self._solution_table_data(payload)
        self._nd_solution_sheets[epoch_number] = (list(headers), list(rows))
        try:
            self._export_solution_table(payload)
        except Exception as exc:
            self._log(f"Nondominated-point export for the final epoch {epoch_number} failed: {exc!r}")
            return
        self._log(f"Saved nondominated points for the final epoch {epoch_number}.")

    def _validated_int(self, value: Any, label: str, minimum: int) -> Tuple[Optional[int], Optional[str]]:
        # Validate an integer form value and return an error message instead of raising.
        if value is None or isinstance(value, bool):
            return None, f"{label}: invalid integer value."
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None, f"{label}: invalid integer value."
        if parsed < minimum:
            return None, f"{label}: value must be >= {minimum}."
        return parsed, None

    def _collect_run_args(self) -> Tuple[Optional[dict], Optional[str]]:
        # Collect and validate run-wide settings from the run form.
        run_values = self.run_form.values()
        seed, error = self._validated_int(run_values.get("seed"), "Seed", 0)
        if error:
            return None, error
        ran = bool(run_values.get("ran", False))
        n_gen = None
        if not ran:
            n_gen, error = self._validated_int(run_values.get("n_gen"), "Number of generations", 1)
            if error:
                return None, error
        parallel_workers, error = self._validated_int(run_values.get("parallel_workers"), "Number of workers", 1)
        if error:
            return None, error
        parallel_backend = str(run_values.get("parallel_backend") or "process")
        if parallel_backend not in {"process", "thread"}:
            return None, f"Parallel backend: unsupported value {parallel_backend!r}."
        return {
            "seed": seed,
            "n_gen": n_gen,
            "ran": ran,
            "verbose": bool(run_values.get("verbose", False)),
            "parallel_eval": bool(run_values.get("parallel_eval", False)),
            "parallel_workers": parallel_workers,
            "parallel_backend": parallel_backend,
        }, None

    def _collect_algorithm_args(self) -> Tuple[Optional[dict], Optional[str]]:
        # Collect and lightly validate algorithm-specific form values.
        values = self.alg_form.values()
        if "pop_size" in values:
            pop_size, error = self._validated_int(values.get("pop_size"), "Population size", 1)
            if error:
                return None, error
            values["pop_size"] = pop_size
        return values, None

    def _collect_problem_args(self) -> Tuple[dict, Optional[str]]:
        # Collect current problem form values.
        return self.problem_form.values(), None

    def _prepare_run_visuals(self) -> None:
        # Reset run-specific visual state before starting a new optimization.
        self._reset_run_result_state()
        self.metric_trajectories.reset(
            self._run_algorithm_name,
            self._run_problem_name,
        )
        self._run_metrics_export_path = None
        self._run_solutions_export_path = None
        self._nd_solution_sheets = {}
        if self._plot_known_pf is None:
            self._reset_plot_axes()
        self._render_plot()

    def _finish_run(self, status_text: str, last_payload: Optional[dict]) -> None:
        # Finalize GUI state after completion, cancellation, or early stop.
        self._thread = None
        self._set_run_state(status_text, running=False)
        if isinstance(last_payload, dict) and last_payload:
            self._remember_epoch(last_payload)
            self._append_last_payload_once(last_payload)
            self.metric_trajectories.append_payload(last_payload)
            self._apply_generation_payload(last_payload)
            self._update_epoch_controls()
            self._export_nondominated_solutions_for_final_epoch(last_payload)
            self._update_metrics_label(last_payload)
            self._update_plot_status(last_payload)
            self._export_metrics_table()
            self._export_solution_table(last_payload)
            return
        self._export_metrics_table()
        self._render_plot()

    def _on_generation(self, payload: dict) -> None:
        # Handle a generation payload emitted by the optimization worker.
        if not isinstance(payload, dict):
            return
        for message in payload.get("diagnostics") or ():
            self._log(f"GEN diag: {message}")
        follow_latest = not self._epoch_history or self._plot_generation == max(self._epoch_history)
        self._remember_epoch(payload)
        if follow_latest:
            self._apply_generation_payload(payload)
        self._update_epoch_controls()
        self._append_generation_row(payload)
        self.metric_trajectories.append_payload(payload)
        self._export_nondominated_solutions_for_epoch(payload)
        if follow_latest:
            self._update_metrics_label(payload)
        stepping = bool(self._thread and self._thread.step_mode)
        if (self.live_updates.isChecked() or stepping) and follow_latest:
            self._update_plot_status(payload)
        if stepping and self._thread.waiting_for_step:
            self.step_run_btn.setEnabled(True)
            self.status_lbl.setText(f"Status: paused after epoch {payload.get('n_gen')}")

    def start_run(self, _checked: bool = False, *, step_mode: bool = False) -> None:
        # Validate all forms, create the worker, and start the run.
        if self._thread and self._thread.isRunning():
            self._log("Start: a run is already in progress.")
            return
        if self._multi_thread and self._multi_thread.isRunning():
            self._warn(
                "Run in progress",
                "Stop the Multi experiment before starting a Main run.",
                "Start ignored: a Multi experiment is already running.",
            )
            return
        if not self._validate_hv_manual_ref_point():
            self._warn(
                "Invalid ref point",
                self.hv_manual_edit.toolTip() or "Invalid ref_point.",
                "HV ref_point: start zablokowany.",
            )
            return
        problem_key = self.problem_combo.currentData()
        alg_key = self.alg_combo.currentData()
        if not problem_key or not alg_key:
            self._warn(
                "Missing configuration",
                "Select a problem and an algorithm before starting the run.",
                "Start: brak wybranego problemu lub algorytmu.",
            )
            return
        run_args, error = self._collect_run_args()
        if error:
            self._warn("Invalid input data", error, f"Start: {error}")
            return
        if step_mode:
            run_args.update(ran=True, n_gen=None)
        nd_save_args, error = self._collect_nd_save_args()
        if error:
            self._warn("Invalid export settings", error, f"Start: {error}")
            return
        algorithm_args, error = self._collect_algorithm_args()
        if error:
            self._warn("Invalid algorithm data", error, f"Start: {error}")
            return
        problem_args, error = self._collect_problem_args()
        if error:
            self._warn("Invalid problem data", error, f"Start: {error}")
            return
        _valid_ref_point, ref_point, _mode, _err = self._hv_ref_point_state()
        if ref_point is None:
            ref_point = self._auto_hv_ref_point()
        self._run_algorithm_key = str(alg_key)
        self._run_algorithm_name = self.alg_combo.currentText() or str(alg_key)
        self._run_problem_name = self.problem_combo.currentText() or str(problem_key)
        self._run_nd_save_mode = str(nd_save_args["mode"])
        self._run_nd_save_step = int(nd_save_args["step"])
        self._prepare_run_visuals()
        project_root = results_root()
        self._run_metrics_export_path = next_available_export_path(
            metrics_export_path(project_root, self._run_algorithm_name, self._run_problem_name)
        )
        self._run_solutions_export_path = next_available_export_path(
            solutions_export_path(project_root, self._run_algorithm_name, self._run_problem_name)
        )
        self._set_run_state("running", running=True)
        if step_mode:
            self.step_run_btn.setText("Next epoch")
        termination_desc = "RAN" if run_args["ran"] else f"n_gen={run_args['n_gen']}"
        parallel_desc = (
            f"{run_args['parallel_backend']}:{run_args['parallel_workers']}"
            if run_args["parallel_eval"]
            else "off"
        )
        self._log(
            f"Start | problem={problem_key} alg={alg_key} seed={run_args['seed']} "
            f"termination={termination_desc} "
            f"nd_save_mode={self._run_nd_save_mode} nd_save_step={self._run_nd_save_step} "
            f"metrics_path={self._run_metrics_export_path} "
            f"solutions_path={self._run_solutions_export_path} "
            f"parallel={parallel_desc} "
            f"verbose={run_args['verbose']} "
            f"problem_params={problem_args} algorithm_params={algorithm_args}"
        )
        self._thread = OptimizationWorker(
            str(problem_key),
            str(alg_key),
            problem_args,
            algorithm_args or {},
            int(run_args["n_gen"]) if run_args["n_gen"] is not None else None,
            int(run_args["seed"]),
            bool(run_args["verbose"]),
            ref_point,
            bool(run_args["parallel_eval"]),
            int(run_args["parallel_workers"]),
            str(run_args["parallel_backend"]),
            parent=self,
            step_mode=step_mode,
        )
        self._thread.generation.connect(self._on_generation)
        self._thread.done.connect(self._on_run_done)
        self._thread.cancelled.connect(self._on_run_cancelled)
        self._thread.failed.connect(self._on_run_failed)
        self._thread.start()

    def stop_run(self) -> None:
        # Request cancellation of the active optimization worker.
        if not self._thread or not self._thread.isRunning():
            self._log("Stop: no active run.")
            return
        self._thread.request_cancel()
        self.status_lbl.setText("Status: stopping")
        self.stop_btn.setEnabled(False)
        self.step_run_btn.setEnabled(False)
        self._log("Stop: cancellation requested; waiting for the current generation to finish.")

    def _on_run_done(self, last_payload: dict) -> None:
        # Handle successful completion of the optimization worker.
        self._finish_run("completed", last_payload)

    def _on_run_cancelled(self, last_payload: dict) -> None:
        # Handle user-requested cancellation of the optimization worker.
        self._log("Run stopped by user.")
        self._finish_run("stopped", last_payload)

    def _on_run_failed(self, err: str) -> None:
        # Handle worker failure and restore the idle GUI state.
        self._log(f"Run failed: {err}")
        self._thread = None
        self._set_run_state("error", running=False)
        self._update_metrics_label(None)
        self._render_plot()
        QMessageBox.warning(self, "Optimization error", err)

    def _clear_console_and_visuals(self) -> None:
        # Clear transient console and chart content without deleting exported result files.
        if (self._thread and self._thread.isRunning()) or (
            self._multi_thread and self._multi_thread.isRunning()
        ):
            return
        self.text_out.clear()
        self._plot_known_pf = None
        self._reset_plot_run_data()
        self._reset_plot_axes()
        self._set_plot_message("No plot available. Start an optimization run.")
        self.metric_trajectories.reset()

    def closeEvent(self, event) -> None:
        # Wake paused workers and let their cleanup finish before destroying Qt objects.
        workers = [worker for worker in self.findChildren(QThread) if worker.isRunning()]
        if workers:
            event.ignore()
            for worker in workers:
                if not getattr(worker, "_close_on_finish", False):
                    worker._close_on_finish = True
                    worker.finished.connect(self.close)
                worker.request_cancel()
            return
        super().closeEvent(event)


def main() -> None:
    # Create the Qt application, show the main window, and enter the event loop.
    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationDisplayName(APPLICATION_TITLE)
    app.setApplicationVersion(__version__)
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
