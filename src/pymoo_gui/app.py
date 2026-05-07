"""
EN: PyQt5 desktop application for configuring, running, visualizing and exporting multiobjective optimization experiments.
"""

# ------------------------------------------------------------------------------------
# File: app.py
# Contents: PyQt5 main window, dynamic parameter forms, optimization worker, plotting and metrics UI logic.
# What happens here: user-selected problems and algorithms are configured, executed in a thread, visualized and exported.
# Role in the framework: provides the interactive desktop interface for dissertation optimization experiments.
# Author: mgr inż. Kristina Valevska
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
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import numpy as np
from PyQt5.QtCore import QLocale, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
try:
    from pymoo.core.termination import NoTermination
except Exception:
    class NoTermination:  # type: ignore[override]
        """
        EN:
        Compatibility fallback for pymoo versions without `NoTermination`.

        PL:
        Zastepcza klasa uzywana wtedy, gdy dana wersja pymoo nie ma trybu bez
        limitu generacji.
        """

        def __init__(self):
            """
            EN:
            Initialize the fallback termination state.

            PL:
            Ustawia poczatkowy stan sztucznego warunku stopu.
            """
            # Ten fallback udaje brak warunku stopu, gdy pymoo nie dostarcza klasy.
            self.force_termination = False
            self.perc = 0.0

        def update(self, algorithm):
            """
            EN:
            Update fallback progress from the forced-termination flag.

            PL:
            Aktualizuje postep na podstawie informacji, czy wymuszono zatrzymanie.
            """
            # Zwraca postep tylko na potrzeby zgodnosci z interfejsem termination.
            self.perc = 1.0 if self.force_termination else 0.0
            return self.perc

        def has_terminated(self):
            """
            EN:
            Report whether the fallback termination has completed.

            PL:
            Informuje, czy algorytm ma juz zakonczyc prace.
            """
            # Informuje algorytm, czy praca ma byc zakonczona.
            return self.perc >= 1.0

        def do_continue(self):
            """
            EN:
            Return whether optimization should continue.

            PL:
            Zwraca informacje, czy algorytm ma dalej dzialac.
            """
            # Odwrotnosc `has_terminated`, potrzebna w niektorych wersjach API.
            return not self.has_terminated()

# Pozwala odpalic ten plik bez `python -m`, np. bezposrednio z IDE.
if __package__ in (None, ""):
    _src_root = Path(__file__).resolve().parents[1]
    if str(_src_root) not in sys.path:
        sys.path.insert(0, str(_src_root))
    __package__ = "pymoo_gui"

from .algoritms import ALGORITHMS, known_pareto_front, make_generation_callback, minimize
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
from .parallel import make_parallel_problem
from .problems import PROBLEMS
from .viz.pareto_dialogs import UnifiedParetoWidget

DEBUG = False
EMPTY = inspect.Signature.empty
ND_SAVE_EVERY_EPOCH = "every_epoch"
ND_SAVE_EVERY_N_EPOCHS = "every_n_epochs"
ND_SAVE_CASCADE = "cascade"
# GUI pokazuje bardziej czytelne etykiety.
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
    "neighborhood_size": "Rozmiar sasiedztwa",
    "epsilons": "Epsilony",
    "ref_points": "Punkty odniesienia",
    "pop_per_ref_point": "Populacja na punkt odniesienia",
    "mu": "Parametr mu",
    "references": "Liczba probek HV",
    "n_samples": "Liczba probek MC",
    "reference_point": "Punkt referencyjny",
    "reference_set": "Zbior referencyjny",
    "mutation_rate": "Wspolczynnik mutacji",
    "eta": "Parametr eta",
    "alpha": "Parametr alpha",
    "adapt_freq": "Czestotliwosc adaptacji",
    "parallel_eval": "Ewaluacja rownolegla",
    "parallel_workers": "Liczba workerow",
    "parallel_backend": "Backend rownolegly",
}
DEFAULT_PARALLEL_WORKERS = max(1, min(4, os.cpu_count() or 1))
RUN_FORM_FIELDS = {
    "seed": {"default": 1, "kind": "int", "minimum": 0},
    "n_gen": {"default": 10, "kind": "int", "minimum": 1},
    "ran": {"default": False, "kind": "bool", "tooltip": "Brak limitu generacji z GUI. Przebieg zatrzymasz przyciskiem Stop."},
    "verbose": {"default": True, "kind": "bool"},
    "parallel_eval": {
        "default": False,
        "kind": "bool",
        "tooltip": "Rownolegla ewaluacja osobnikow na CPU. Najbardziej przydatna dla drogich funkcji celu.",
    },
    "parallel_workers": {
        "default": DEFAULT_PARALLEL_WORKERS,
        "kind": "int",
        "minimum": 1,
        "tooltip": "Liczba procesow albo watkow uzywanych do ewaluacji funkcji celu.",
    },
    "parallel_backend": {
        "default": "process",
        "kind": "choice",
        "choices": ("process", "thread"),
        "tooltip": "process = multiprocessing; thread = ThreadPool z mniejszym narzutem.",
    },
}


def pl_param_label(name: str) -> str:
    """
    EN:
    Return a Polish GUI label for a technical parameter name.

    PL:
    Zamienia techniczna nazwe parametru na zrozumiala etykiete w formularzu.
    """
    # Zamienia techniczna nazwe parametru na tekst czytelny w formularzu.
    return PARAM_PL.get(name) or f"{name.replace('_', ' ').capitalize()} ({name})"


def callable_signature(obj: Any) -> inspect.Signature:
    """
    EN:
    Return the callable signature used to build dynamic parameter forms.

    PL:
    Pobiera liste parametrow funkcji lub konstruktora, aby zbudowac formularz.
    """
    # Pobiera sygnature callable, aby dynamicznie zbudowac pola GUI.
    return inspect.signature(obj)


def filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> Dict[str, Any]:
    """
    EN:
    Keep only keyword arguments accepted by a callable's signature.

    PL:
    Przepuszcza tylko te ustawienia, ktore dana funkcja naprawde przyjmuje.
    """
    # Przepuszcza tylko te argumenty, ktore dana funkcja naprawde przyjmuje.
    sig = callable_signature(fn)
    accepted = {}
    for param in sig.parameters.values():
        if param.name == "self" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.name in params:
            accepted[param.name] = params[param.name]
    return accepted


def _literal_or_str(value: str) -> Any:
    """
    EN:
    Parse GUI text as a Python literal when possible, otherwise keep it as text.

    PL:
    Odczytuje tekst z formularza jako liczbe, liste lub `None`, a gdy sie nie da,
    zostawia zwykly tekst.
    """
    # Probuje odczytac wpis jako litarl Pythona, a przy niepowodzeniu zostawia zwykly tekst.
    text = value.strip()
    if not text:
        return None
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return text


def should_save_nondominated_solutions_for_epoch(epoch: Any, mode: str, step: int = 1) -> bool:
    """
    EN:
    Decide whether nondominated solutions should be exported for a given epoch.

    PL:
    Okresla, czy dla danej epoki nalezy zapisac front niezdominowany.
    """
    try:
        epoch_number = int(epoch)
    except (TypeError, ValueError):
        return False
    if epoch_number < 1:
        return False
    if mode == ND_SAVE_EVERY_EPOCH:
        return True
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
    """
    EN:
    Declarative description of one dynamic form field.

    PL:
    Opis jednego pola formularza: nazwy, typu, wartosci domyslnej i ograniczen.
    """

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
    """
    EN:
    Binding between a form field specification and the created Qt widget.

    PL:
    Laczy opis pola z konkretnym widgetem w oknie.
    """

    name: str
    widget: Any
    kind: str
    spec: FieldSpec


def _specs(raw_specs: Optional[Any]) -> list[FieldSpec]:
    """
    EN:
    Normalize registry form-field definitions into `FieldSpec` objects.

    PL:
    Zamienia rozne formaty opisow pol na jedna wspolna postac uzywana przez GUI.
    """
    # Rozne moduly moga opisac pola na kilka sposobow, wiec tutaj ujednolicamy wejscie.
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
    """
    EN:
    Dynamic Qt form that builds parameter widgets from callable signatures or field specs.

    PL:
    Formularz, ktory sam tworzy pola ustawien dla problemu, algorytmu albo uruchomienia.
    """

    def __init__(self, title: str, parent=None):
        """
        EN:
        Initialize an empty parameter form.

        PL:
        Tworzy pusty formularz, ktory pozniej zostanie wypelniony polami.
        """
        # Tworzy pusty formularz, ktory potem wypelniamy polami z opisu problemu lub algorytmu.
        super().__init__(title, parent)
        self.form = QFormLayout(self)
        self.form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.form.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self._bindings: Dict[str, WidgetBinding] = {}

    def clear(self) -> None:
        """
        EN:
        Remove all rows and widget bindings from the form.

        PL:
        Czyści formularz przed zbudowaniem nowej listy pol.
        """
        # Usuwa wszystkie wiersze i powiazania przed zbudowaniem nowej wersji formularza.
        while self.form.rowCount():
            self.form.removeRow(0)
        self._bindings.clear()

    def binding(self, name: str) -> Optional[WidgetBinding]:
        """
        EN:
        Return the binding for one field name.

        PL:
        Zwraca widget przypisany do podanej nazwy pola.
        """
        # Zwraca pojedyncze powiazanie nazwy pola z widgetem.
        return self._bindings.get(name)

    def bindings(self) -> Sequence[WidgetBinding]:
        """
        EN:
        Return all field-to-widget bindings.

        PL:
        Zwraca wszystkie pola formularza wraz z ich widgetami.
        """
        # Zwraca wszystkie powiazania, aby latwo podpinac sygnaly.
        return tuple(self._bindings.values())

    def build_for_callable(self, fn: Any, extra_fields: Optional[Any] = None) -> None:
        """
        EN:
        Build form fields from a callable signature and optional explicit field specs.

        PL:
        Tworzy pola formularza na podstawie parametrow funkcji oraz dodatkowych opisow.
        """
        # Buduje formularz na podstawie sygnatury funkcji lub konstruktora.
        self.build_for_signature(callable_signature(fn), extra_fields)

    def build_for_signature(self, sig: inspect.Signature, extra_fields: Optional[Any] = None) -> None:
        """
        EN:
        Build form fields from an inspected signature.

        PL:
        Buduje formularz z gotowej sygnatury parametrow.
        """
        # Laczy pola wymuszone recznie z tymi odczytanymi z podpisu callable.
        self.clear()
        added_names = set()
        # Pola przekazane recznie maja pierwszenstwo przed tymi odczytanymi z sygnatury.
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
        """
        EN:
        Build form fields directly from registry field specifications.

        PL:
        Tworzy formularz wprost z opisow pol zapisanych w rejestrze.
        """
        # Buduje formularz wprost z listy lub slownika opisow pol.
        self.clear()
        for spec in _specs(raw_specs):
            self._add_field(spec)

    def _kind(self, annotation: Any, default: Any) -> str:
        """
        EN:
        Infer the widget kind from type annotation or default value.

        PL:
        Dobiera typ pola formularza na podstawie typu albo wartosci domyslnej.
        """
        # Zgaduje typ widgetu na podstawie adnotacji lub wartosci domyslnej.
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
        """
        EN:
        Determine numeric widget bounds from a field specification.

        PL:
        Ustala minimalna i maksymalna wartosc dla pola liczbowego.
        """
        # Ustala sensowne granice dla spinboxow, gdy spec ich nie podal.
        minimum = spec.minimum
        maximum = spec.maximum
        if spec.kind == "int":
            if minimum is None:
                minimum = 1 if spec.name in {"n_gen", "pop_size", "n_var", "n_obj"} else 0 if spec.name == "seed" else -10**9
            if maximum is None:
                maximum = 10**9
        else:
            minimum = -1e12 if minimum is None else minimum
            maximum = 1e12 if maximum is None else maximum
        return float(minimum), float(maximum)

    def _apply_read_only(self, widget: Any, spec: FieldSpec) -> None:
        """
        EN:
        Apply a read-only state to a widget according to the field spec.

        PL:
        Ustawia pole jako tylko do odczytu, gdy opis pola tego wymaga.
        """
        # Ustawia widget w trybie tylko do odczytu.
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
        """
        EN:
        Create one Qt widget for a field specification and add it to the form.

        PL:
        Tworzy jedno pole w formularzu i zapamietuje jego powiazanie z nazwa.
        """
        label = QLabel(pl_param_label(spec.name))
        if spec.tooltip:
            label.setToolTip(spec.tooltip)
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
            widget.setToolTip(spec.tooltip)
        self._apply_read_only(widget, spec)
        self.form.addRow(label, widget)
        self._bindings[spec.name] = WidgetBinding(spec.name, widget, kind, spec)

    def values(self) -> Dict[str, Any]:
        """
        EN:
        Read all form widget values and convert them to Python objects.

        PL:
        Pobiera wartosci z formularza i zamienia je na dane gotowe do przekazania funkcjom.
        """
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
    """
    EN:
    Internal control-flow exception raised when a running optimization is cancelled.

    PL:
    Wewnetrzny sygnal przerwania obliczen po kliknieciu Stop.
    """

    pass


class OptimizationWorker(QThread):
    """
    EN:
    Background worker that builds the selected problem and algorithm, runs optimization, and emits GUI updates.

    PL:
    Watek roboczy, ktory wykonuje obliczenia w tle i wysyla do okna postep oraz wynik.
    """

    # Obliczenia ida w osobnym watku, zeby GUI pozostalo dostepne podczas optymalizacji.
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
    ):
        """
        EN:
        Store all configuration needed for one optimization run.

        PL:
        Zapamietuje ustawienia jednego przebiegu: problem, algorytm, seed, limit
        generacji, HV i rownolegla ewaluacje.
        """
        # Zapamietuje konfiguracje jednego uruchomienia, ktore wykona w tle.
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

    def request_cancel(self) -> None:
        """
        EN:
        Request cooperative cancellation of the running optimization.

        PL:
        Prosi dzialajacy algorytm o zatrzymanie przy najblizszej bezpiecznej okazji.
        """
        # Ustawia flage stopu i prosi Qt o przerwanie pracy watku.
        self._cancel_requested.set()
        self.requestInterruption()

    def _cancel_pending(self) -> bool:
        """
        EN:
        Check whether the worker has received a cancellation request.

        PL:
        Sprawdza, czy uzytkownik poprosil o zatrzymanie obliczen.
        """
        # Sprawdza  mechanizm stopu, zeby szybciej wyjsc z obliczen.
        return self._cancel_requested.is_set() or self.isInterruptionRequested()

    def _emit_generation(self, payload: dict) -> None:
        """
        EN:
        Emit one generation payload unless cancellation is pending.

        PL:
        Wysyla dane jednej generacji do GUI albo przerywa, jesli poproszono o Stop.

        Raises:
            OptimizationCancelled: EN: If cancellation is pending before or after emission.
                                   PL: Gdy uzytkownik zatrzymuje obliczenia.
        """
        # Przekazuje do GUI dane z kolejnej generacji albo przerywa, jesli przyszlo zadanie stop.
        if self._cancel_pending():
            raise OptimizationCancelled()
        # Trzymamy ostatni znany stan, aby po stopie lub bledzie pokazac ostatnie dane w UI.
        self._last_payload = payload or {}
        self.generation.emit(self._last_payload)
        if self._cancel_pending():
            raise OptimizationCancelled()

    def run(self) -> None:
        """
        EN:
        Build runtime objects, execute optimization and emit done/cancelled/failed signals.

        PL:
        Tworzy problem i algorytm, uruchamia optymalizacje oraz informuje GUI o
        zakonczeniu, zatrzymaniu albo bledzie.
        """
        # Tworzy problem, algorytm i odpala minimalizacje w osobnym watku.
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
            # Callback zbiera dane po generacjach i odsylka je z powrotem do okna.
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
    """
    EN:
    Main PyQt window coordinating forms, plotting, run control, metrics and export.

    PL:
    Glowne okno aplikacji, ktore laczy formularze, wykres, tabele metryk i
    sterowanie optymalizacja.
    """

    def __init__(self):
        """
        EN:
        Initialize widgets, runtime state and initial previews.

        PL:
        Tworzy okno, ustawia poczatkowy stan paneli i przygotowuje pierwszy podglad.
        """
        # Inicjalizuje glowne okno i ustawia stan startowy wszystkich paneli.
        super().__init__()
        self.setWindowTitle("pymoo GUI framework (zdt1/nsga2)")
        self.resize(1500, 920)
        self._thread: Optional[OptimizationWorker] = None
        self._n_obj_widget: Optional[QSpinBox] = None
        self._last_gen_appended: Optional[int] = None
        self._plot_widget: Optional[UnifiedParetoWidget] = None
        self._plot_widget_dim: Optional[int] = None
        self._plot_known_pf: Optional[np.ndarray] = None
        self._plot_feasible_nd_F: Optional[np.ndarray] = None
        self._plot_population_F: Optional[np.ndarray] = None
        self._plot_generation: Optional[int] = None
        self._plot_n_obj: Optional[int] = None
        self._run_algorithm_name: Optional[str] = None
        self._run_problem_name: Optional[str] = None
        self._run_nd_save_mode = ND_SAVE_EVERY_EPOCH
        self._run_nd_save_step = 1
        self._run_metrics_export_path: Optional[Path] = None
        self._run_solutions_export_path: Optional[Path] = None
        self._nd_solution_sheets: dict[int, tuple[list[str], list[list[object]]]] = {}
        self._build_ui()
        self._connect_signals()
        self._configure_placeholders()
        self._rebuild_problem_form()
        self._rebuild_alg_form()
        self._update_hv_ref_point_label()
        self._update_plot_status()
        self._update_run_button_state()

    def _build_ui(self) -> None:
        """
        EN:
        Build the main horizontal splitter with controls and results panels.

        PL:
        Tworzy glowny podzial okna na panel ustawien oraz panel wynikow.
        """
        # Lewa strona sluzy do konfiguracji, prawa do wykresu i tabeli z metrykami.
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)
        controls_panel = self._build_controls_panel()
        results_panel = self._build_results_panel()
        splitter.addWidget(controls_panel)
        splitter.addWidget(results_panel)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([440, 1060])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _build_controls_panel(self) -> QWidget:
        """
        EN:
        Build the left-side controls panel.

        PL:
        Tworzy lewy panel z wyborem problemu, algorytmu i ustawieniami uruchomienia.
        """
        # Sklada lewy panel z formularzami, ustawieniami przebiegu i konsola.
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
        """
        EN:
        Build the right-side plot and metrics-history panel.

        PL:
        Tworzy prawy panel z wykresem Pareto i tabela metryk.
        """
        # Tworzy prawa czesc okna z wykresem Pareto i tabela metryk.
        self._plot_panel = QWidget()
        self._plot_layout = QVBoxLayout(self._plot_panel)
        self._plot_placeholder = QLabel("Brak wykresu - uruchom optymalizację")
        self._plot_placeholder.setAlignment(Qt.AlignCenter)
        self._plot_placeholder.setWordWrap(True)
        self._plot_layout.setContentsMargins(0, 0, 0, 0)
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
        """
        EN:
        Add problem and algorithm selectors with their dynamic parameter forms.

        PL:
        Dodaje wybor problemu i algorytmu oraz formularze ich parametrow.
        """
        # Dodaje wybieranie problemu i algorytmu wraz z ich dynamicznymi formularzami.
        self.problem_combo = QComboBox()
        for key, entry in PROBLEMS.items():
            self.problem_combo.addItem(entry.get("label", key), userData=key)
        self.problem_form = ParamForm("Parametry problemu")

        self.alg_combo = QComboBox()
        for key, entry in ALGORITHMS.items():
            self.alg_combo.addItem(entry.get("label", key), userData=key)
        self.alg_form = ParamForm("Parametry algorytmu")

        self._left.addWidget(QLabel("Problem:"))
        self._left.addWidget(self.problem_combo)
        self._left.addWidget(self.problem_form)
        self._left.addWidget(QLabel("Algorytm:"))
        self._left.addWidget(self.alg_combo)
        self._left.addWidget(self.alg_form)

    def _build_hv_controls(self) -> None:
        """
        EN:
        Build controls for automatic or manual hypervolume reference points.

        PL:
        Tworzy sekcje ustawiania punktu odniesienia dla metryki HV.
        """
        # Buduje sekcje ustawiania punktu odniesienia dla metryki HV.
        self.hv_ref_group = QGroupBox("HV ref point")
        hv_layout = QVBoxLayout(self.hv_ref_group)
        mode_row = QHBoxLayout()
        self.hv_auto_radio = QRadioButton("Auto ref point")
        self.hv_manual_radio = QRadioButton("Ręczny ref point")
        self.hv_auto_radio.setChecked(True)
        mode_row.addWidget(self.hv_auto_radio)
        mode_row.addWidget(self.hv_manual_radio)
        hv_layout.addLayout(mode_row)
        self.hv_manual_edit = QLineEdit()
        self.hv_manual_edit.setPlaceholderText("0,6 0,6 0,6 albo 0.6,0.6,0.6")
        self.hv_manual_edit.setEnabled(False)
        self.hv_ref_lbl = QLabel("HV ref point (aktywny): -")
        hv_layout.addWidget(self.hv_manual_edit)
        hv_layout.addWidget(self.hv_ref_lbl)
        self._left.addWidget(self.hv_ref_group)

    def _build_run_controls(self) -> None:
        """
        EN:
        Build run options, live-plot toggles, command buttons and status labels.

        PL:
        Tworzy opcje startu, przelaczniki wykresu, przyciski i etykiety statusu.
        """
        # Dodaje opcje uruchomienia oraz przyciski start i stop.
        self.run_form = ParamForm("Uruchomienie")
        self.run_form.build_from_specs(RUN_FORM_FIELDS)
        self._left.addWidget(self.run_form)

        self.live_updates = QCheckBox("Aktualizuj wykres w trakcie")
        self.live_updates.setChecked(True)
        self.show_population_cb = QCheckBox("Pokaż populację")
        self.show_population_cb.setChecked(True)
        self.hide_pareto_front_cb = QCheckBox("Ukryj front Pareto")
        self.hide_pareto_front_cb.setChecked(False)
        self.auto_scale_axes = QCheckBox("Auto-skala osi")
        self.auto_scale_axes.setChecked(True)
        self.nd_save_group = QGroupBox("Zapis rozwiązań niezdominowanych")
        nd_save_layout = QFormLayout(self.nd_save_group)
        self.nd_save_mode_combo = QComboBox()
        self.nd_save_mode_combo.addItem("Każda epoka", userData=ND_SAVE_EVERY_EPOCH)
        self.nd_save_mode_combo.addItem("Co N epok", userData=ND_SAVE_EVERY_N_EPOCHS)
        self.nd_save_mode_combo.addItem("Kaskada", userData=ND_SAVE_CASCADE)
        self.nd_save_step_spin = QSpinBox()
        self.nd_save_step_spin.setRange(1, 10**9)
        self.nd_save_step_spin.setValue(10)
        nd_save_layout.addRow("Tryb:", self.nd_save_mode_combo)
        nd_save_layout.addRow("Krok:", self.nd_save_step_spin)
        self._left.addWidget(self.live_updates)
        self._left.addWidget(self.show_population_cb)
        self._left.addWidget(self.hide_pareto_front_cb)
        self._left.addWidget(self.auto_scale_axes)
        self._left.addWidget(self.nd_save_group)

        button_row = QHBoxLayout()
        self.run_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.console_btn = QPushButton("Konsola")
        button_row.addWidget(self.run_btn)
        button_row.addWidget(self.stop_btn)
        button_row.addWidget(self.console_btn)
        self._left.addLayout(button_row)

        self.status_lbl = QLabel("Status: bezczynny")
        self.metrics_lbl = QLabel(self._metrics_label_text({}))
        self._left.addWidget(self.status_lbl)
        self._left.addWidget(self.metrics_lbl)
        self._left.addStretch(1)

    def _build_console(self) -> None:
        """
        EN:
        Create the docked runtime console.

        PL:
        Tworzy dolny panel konsoli z logami aplikacji.
        """
        # Tworzy dolny dock z logiem dzialania aplikacji.
        self.text_out = QTextEdit()
        self.text_out.setReadOnly(True)
        self.console_dock = QDockWidget("Konsola", self)
        self.console_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.console_dock.setWidget(self.text_out)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)
        self.resizeDocks([self.console_dock], [int(self.height() * 0.3)], Qt.Vertical)

    def _connect_signals(self) -> None:
        """
        EN:
        Connect Qt widget signals to their event handlers.

        PL:
        Podpina klikniecia i zmiany pol do metod obslugujacych reakcje GUI.
        """
        # Spina widgety z handlerami, aby UI reagowalo na zmiany i klikniecia.
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
        self.stop_btn.clicked.connect(self.stop_run)
        self.console_btn.clicked.connect(self._toggle_console_dock)
        self.console_dock.visibilityChanged.connect(self._on_console_visibility_changed)
        self._on_console_visibility_changed(self.console_dock.isVisible())
        ran_binding = self.run_form.binding("ran")
        if ran_binding is not None and isinstance(ran_binding.widget, QCheckBox):
            ran_binding.widget.toggled.connect(self._on_ran_toggled)
        parallel_binding = self.run_form.binding("parallel_eval")
        if parallel_binding is not None and isinstance(parallel_binding.widget, QCheckBox):
            parallel_binding.widget.toggled.connect(self._on_parallel_eval_toggled)

    def _configure_placeholders(self) -> None:
        """
        EN:
        Configure initial tooltips, placeholders and dependent run-form state.

        PL:
        Ustawia podpowiedzi oraz poczatkowy stan pol zaleznch od innych opcji.
        """
        # Ustawia podpowiedzi i dopasowuje stan formularza run po starcie okna.
        self.live_updates.setToolTip("Włącza odświeżanie wykresu Pareto w trakcie kolejnych generacji.")
        self.show_population_cb.setToolTip("Pokazuje lub ukrywa pełną populację na wykresie Pareto.")
        self.hide_pareto_front_cb.setToolTip("Ukrywa znany front Pareto, ale nie usuwa go z danych używanych przez metryki.")
        self.auto_scale_axes.setToolTip("Jednorazowo dopasowuje zakres osi dla aktualnego widoku Pareto, bez przeliczania przy każdej generacji.")
        self.nd_save_mode_combo.setToolTip("Wybiera, dla których epok zapisywać front niezdominowany.")
        self.nd_save_step_spin.setToolTip("Dodatnia liczba całkowita używana tylko w trybie 'Co N epok'.")
        self._update_nd_save_controls_state()
        self._update_run_form_state()

    def _entry(self, combo: QComboBox, registry: Mapping[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        EN:
        Return the registry entry for the current combo-box selection.

        PL:
        Pobiera opis aktualnie wybranego problemu albo algorytmu.
        """
        # Pobiera pelny opis aktualnie wybranej pozycji z rejestru.
        key = combo.currentData()
        return dict(registry.get(str(key), {})) if key is not None else {}

    def _known_pf_for_problem(self, entry: Mapping[str, Any], problem: Any) -> Optional[np.ndarray]:
        """
        EN:
        Resolve and normalize a known Pareto front for preview and metrics.

        PL:
        Przygotowuje znany front Pareto, ktory jest pokazywany na wykresie i
        uzywany do metryk.
        """
        # Przygotowanie znanego frontu Pareto dla podgladu i metryk.
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

    def _instantiate_selected_problem(self, params: Optional[Mapping[str, Any]] = None) -> Tuple[Optional[Any], Optional[str]]:
        """
        EN:
        Instantiate the currently selected problem and return an error string instead of raising.

        PL:
        Tworzy wybrany problem; gdy cos jest niepoprawne, zwraca opis bledu dla GUI.
        """
        # Tworzy instancje aktualnie wybranego problemu i zwraca blad zamiast wyjatku.
        entry = self._entry(self.problem_combo, PROBLEMS)
        factory = entry.get("factory")
        if not callable(factory):
            return None, "Brak poprawnego factory problemu."
        params = dict(params or self.problem_form.values())
        try:
            return factory(**filter_callable_kwargs(factory, params)), None
        except Exception as exc:
            return None, repr(exc)

    def _connect_problem_form_signals(self) -> None:
        """
        EN:
        Connect dynamic problem-form widgets to preview refresh handling.

        PL:
        Podpina pola problemu tak, aby zmiana parametru odswiezala podglad.
        """
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
        """
        EN:
        Create or reuse a Pareto plot widget matching the current objective count.

        PL:
        Tworzy albo odtwarza widget wykresu pasujacy do liczby funkcji celu.
        """
        # Tworzy widget wykresu dla aktualnej liczby celow.
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
        return self._plot_widget

    def _reset_plot_axes(self) -> None:
        """
        EN:
        Reset cached plot axis limits when the underlying data context changes.

        PL:
        Przywraca automatyczny zakres osi po zmianie danych albo ustawien.
        """
        # Przywraca domyslny widok osi, jesli widget wykresu juz istnieje.
        if self._plot_widget is not None and hasattr(self._plot_widget, "reset_view_limits"):
            self._plot_widget.reset_view_limits()

    def _set_plot_message(self, text: str) -> None:
        """
        EN:
        Hide the plot widget and show an explanatory placeholder message.

        PL:
        Ukrywa wykres i pokazuje uzytkownikowi komunikat tekstowy.
        """
        # Ukrywa wykres i pokazuje uzytkownikowi tekstowy komunikat.
        self._plot_placeholder.setText(text)
        self._plot_placeholder.show()
        if self._plot_widget is not None:
            self._plot_widget.hide()

    def _reset_plot_run_data(self) -> None:
        """
        EN:
        Clear per-run plot data while keeping problem-level reference data.

        PL:
        Czyści dane poprzedniego przebiegu z wykresu, ale zostawia znany front problemu.
        """
        self._plot_feasible_nd_F = None
        self._plot_population_F = None
        self._plot_generation = None

    def _reset_run_result_state(self) -> None:
        """
        EN:
        Clear metrics history, run plot data and summary labels.

        PL:
        Czyści wyniki poprzedniego uruchomienia przed nowym startem.
        """
        self._clear_table()
        self._reset_plot_run_data()
        self._update_metrics_label(None)

    def _update_run_form_state(self) -> None:
        """
        EN:
        Enable or disable run-form fields according to RAN and parallel-evaluation toggles.

        PL:
        Wlacza i wylacza pola formularza zalezne od trybu RAN oraz rownoleglosci.
        """
        # Przelacza pole `n_gen` zaleznnie od tego, czy wybrano tryb RAN.
        ran_binding = self.run_form.binding("ran")
        n_gen_binding = self.run_form.binding("n_gen")
        if ran_binding is not None and n_gen_binding is not None:
            ran_enabled = bool(ran_binding.widget.isChecked())
            n_gen_widget = n_gen_binding.widget
            if isinstance(n_gen_widget, (QSpinBox, QDoubleSpinBox)):
                n_gen_widget.setEnabled(not ran_enabled)
            if isinstance(n_gen_widget, QAbstractSpinBox):
                n_gen_widget.setReadOnly(ran_enabled)
                n_gen_widget.setButtonSymbols(QAbstractSpinBox.NoButtons if ran_enabled else QAbstractSpinBox.UpDownArrows)

        parallel_binding = self.run_form.binding("parallel_eval")
        parallel_workers_binding = self.run_form.binding("parallel_workers")
        parallel_backend_binding = self.run_form.binding("parallel_backend")
        if parallel_binding is not None:
            parallel_enabled = bool(parallel_binding.widget.isChecked())
            for binding in (parallel_workers_binding, parallel_backend_binding):
                if binding is not None:
                    binding.widget.setEnabled(parallel_enabled)

    def _current_nd_save_mode(self) -> str:
        """
        EN:
        Return the currently selected nondominated-solution save mode.

        PL:
        Zwraca aktualnie wybrany tryb zapisu frontu niezdominowanego.
        """
        mode = self.nd_save_mode_combo.currentData()
        return str(mode) if mode is not None else ND_SAVE_EVERY_EPOCH

    def _update_nd_save_controls_state(self) -> None:
        """
        EN:
        Enable the step field only for the "every N epochs" nondominated-save mode.

        PL:
        Wlacza pole kroku tylko dla trybu "co N epok".
        """
        self.nd_save_step_spin.setEnabled(self._current_nd_save_mode() == ND_SAVE_EVERY_N_EPOCHS)

    def _collect_nd_save_args(self) -> Tuple[Optional[dict], Optional[str]]:
        """
        EN:
        Validate nondominated-solution export settings selected in the GUI.

        PL:
        Pobiera i sprawdza ustawienia zapisu frontu niezdominowanego.
        """
        mode = self._current_nd_save_mode()
        if mode not in {ND_SAVE_EVERY_EPOCH, ND_SAVE_EVERY_N_EPOCHS, ND_SAVE_CASCADE}:
            return None, "Tryb zapisu rozwiązań niezdominowanych jest niepoprawny."
        step, error = self._validated_int(self.nd_save_step_spin.value(), "Krok zapisu rozwiązań", 1)
        if error:
            return None, error
        return {"mode": mode, "step": int(step)}, None

    def _set_run_state(self, status_text: str, running: bool) -> None:
        """
        EN:
        Update run status text and Start/Stop button availability.

        PL:
        Aktualizuje status oraz dostepnosc przyciskow Start i Stop.
        """
        # Ustawia status uruchomienia i blokuje lub odblokowuje przyciski.
        self.status_lbl.setText(f"Status: {status_text}")
        self.run_btn.setEnabled(not running and self._validate_hv_manual_ref_point())
        self.stop_btn.setEnabled(running)

    def _apply_generation_payload(self, payload: Mapping[str, Any]) -> None:
        """
        EN:
        Copy generation payload data into plot-state fields.

        PL:
        Przenosi dane jednej generacji do pamieci wykresu i etykiet.
        """
        # Kopiuje dane z callbacku do pol uzywanych przez wykres i metryki.
        known_pf = payload.get("known_pf")
        if known_pf is not None:
            self._plot_known_pf = known_pf
        self._plot_feasible_nd_F = payload.get("feasible_nd_F")
        self._plot_population_F = payload.get("population_F")
        self._plot_generation = payload.get("n_gen")
        if DEBUG:
            self._log(
                "PLOT store overwrite "
                f"source=worker_payload gen={self._fmt_int(self._plot_generation)} "
                f"pop={self._shape_text(self._plot_population_F)} "
                f"front={self._shape_text(self._plot_feasible_nd_F)} "
                f"known_pf={self._shape_text(self._plot_known_pf)}"
            )

    def _apply_problem_preview_state(self, problem: Any) -> None:
        """
        EN:
        Refresh problem-level Pareto preview data after problem changes.

        PL:
        Odswieza podglad frontu Pareto po zmianie problemu lub jego parametrow.
        """
        # Odswieza dane podgladu po zmianie problemu lub jego parametrow.
        entry = self._entry(self.problem_combo, PROBLEMS)
        self._plot_known_pf = self._known_pf_for_problem(entry, problem)
        try:
            self._plot_n_obj = int(getattr(problem, "n_obj", 0))
        except (TypeError, ValueError):
            self._plot_n_obj = None
        self._render_plot()

    def _refresh_problem_plot(self) -> None:
        """
        EN:
        Recreate the selected problem and refresh the Pareto preview.

        PL:
        Buduje problem od nowa i aktualizuje podglad, pokazujac blad przy zlych parametrach.
        """
        # Buduje podglad problemu od zera i pokazuje blad, jesli parametry sa niepoprawne.
        problem, error = self._instantiate_selected_problem()
        self._reset_plot_run_data()
        self._reset_plot_axes()
        if problem is None:
            self._plot_known_pf = None
            self._plot_n_obj = None
            self._set_plot_message("Nie można przygotować podglądu Pareto.")
            if error:
                self._log(f"Preview: {error}")
            return
        self._apply_problem_preview_state(problem)

    def _render_plot(self) -> None:
        """
        EN:
        Render the current 2D/3D Pareto data or show a dimensionality message.

        PL:
        Rysuje aktualny wykres Pareto albo pokazuje komunikat, gdy liczba celow jest za duza.
        """
        # Renderuje wykres 2D/3D albo pokazuje komunikat dla wiekszej liczby celow.
        if self._plot_n_obj not in (2, 3):
            label = "?" if self._plot_n_obj is None else str(self._plot_n_obj)
            self._set_plot_message(f"Podgląd Pareto jest dostępny tylko dla 2 lub 3 celów. Wybrany problem ma {label}.")
            return
        widget = self._ensure_plot_widget()
        self._plot_placeholder.hide()
        widget.show()
        n_obj = int(self._plot_n_obj)
        widget.set_show_population(self.show_population_cb.isChecked())
        pop = self._plot_population_F
        ref = np.empty((0, n_obj)) if self.hide_pareto_front_cb.isChecked() else self._plot_known_pf
        widget.update_points(pop, self._plot_feasible_nd_F, ref, self._plot_generation)
        if DEBUG:
            snapshot = widget.render_snapshot() if hasattr(widget, "render_snapshot") else {}
            self._log(
                "PLOT render "
                f"source=main_window_cache dim={n_obj} gen={self._fmt_int(self._plot_generation)} "
                f"backend={snapshot.get('backend', '?')} pop={snapshot.get('pop_shape')} "
                f"front={snapshot.get('front_shape')} ref={snapshot.get('ref_shape')}"
            )
            if snapshot.get("gen") != self._plot_generation:
                self._log(f"PLOT generation mismatch ui={self._plot_generation} rendered={snapshot.get('gen')}")

    def _rebuild_problem_form(self) -> None:
        """
        EN:
        Rebuild problem parameter widgets after the selected problem changes.

        PL:
        Przebudowuje formularz problemu po zmianie wyboru w comboboxie.
        """
        # Przebudowuje formularz problemu po zmianie wyboru w comboboxie.
        entry = self._entry(self.problem_combo, PROBLEMS)
        try:
            self.problem_form.build_for_callable(entry.get("factory"), entry.get("form_fields"))
            note = entry.get("form_note")
        except (TypeError, ValueError, AttributeError):
            self.problem_form.build_from_specs(entry.get("form_fields"))
            note = "Formularz problemu korzysta z bezpiecznego fallbacku; pełna konfiguracja dynamiczna nie jest jeszcze gotowa."
        self.problem_form.setToolTip(note or "")
        self._connect_problem_form_signals()
        self._connect_problem_param_signals()
        self._refresh_problem_plot()
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _rebuild_alg_form(self) -> None:
        """
        EN:
        Rebuild algorithm parameter widgets after the selected algorithm changes.

        PL:
        Przebudowuje formularz algorytmu po zmianie wyboru.
        """
        # Przebudowuje formularz algorytmu na podstawie aktualnego wpisu w rejestrze.
        entry = self._entry(self.alg_combo, ALGORITHMS)
        try:
            self.alg_form.build_for_callable(entry.get("factory"), entry.get("form_fields"))
            note = entry.get("form_note")
        except (TypeError, ValueError, AttributeError):
            self.alg_form.build_from_specs(entry.get("form_fields"))
            note = "Formularz algorytmu korzysta z bezpiecznego fallbacku; pełna konfiguracja dynamiczna nie jest jeszcze gotowa."
        self.alg_form.setToolTip(note or "")

    def _connect_problem_param_signals(self) -> None:
        """
        EN:
        Track the `n_obj` field because it affects HV validation and plotting.

        PL:
        Pilnuje pola liczby celow, od ktorego zalezy HV i stan przycisku Start.
        """
        # Pilnuje sygnalu od `n_obj`, bo od niego zalezy HV i stan przycisku start.
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
        """
        EN:
        Refresh HV validation and run availability after objective-count changes.

        PL:
        Odswieza punkt odniesienia HV i przycisk Start po zmianie liczby celow.
        """
        # Po zmianie liczby celow odswieza zalezne pola i walidacje.
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _on_problem_form_changed(self, *_args: Any) -> None:
        """
        EN:
        Handle any problem-parameter change by refreshing the preview.

        PL:
        Reaguje na zmiane parametrow problemu i odswieza podglad.
        """
        # Kazda zmiana parametrow problemu od razu odswieza podglad.
        self._refresh_problem_plot()

    def _on_show_population_toggled(self, checked: bool) -> None:
        """
        EN:
        Toggle the full-population layer on the Pareto plot.

        PL:
        Wlacza albo ukrywa warstwe z cala populacja na wykresie.
        """
        # Wlacza lub ukrywa warstwe z cala populacja na wykresie.
        self._log(f"show_population={checked} (pelna populacja jako osobna warstwa)")
        self._render_plot()

    def _on_hide_pareto_front_toggled(self, checked: bool) -> None:
        """
        EN:
        Toggle display of the known Pareto-front reference layer.

        PL:
        Ukrywa albo pokazuje znany front Pareto bez usuwania go z danych metryk.
        """
        # Ukrywa albo pokazuje znany front Pareto bez kasowania danych.
        self._log(f"hide_pareto_front={checked}")
        if checked or self.auto_scale_axes.isChecked():
            self._reset_plot_axes()
        self._render_plot()

    def _on_auto_scale_toggled(self, checked: bool) -> None:
        """
        EN:
        Toggle plot auto-scaling and reset cached limits when re-enabled.

        PL:
        Wlacza automatyczna skale osi i resetuje widok, gdy jest ponownie aktywna.
        """
        # Steruje automatycznym dopasowaniem osi i ewentualnie resetuje widok.
        self._log(f"auto_scale={checked}")
        if self._plot_widget is not None:
            self._plot_widget.set_auto_scale(bool(checked))
        if checked:
            self._reset_plot_axes()
            self._render_plot()

    def _on_nd_save_mode_changed(self, _index: int) -> None:
        """
        EN:
        React to changes of the nondominated-solution save mode.

        PL:
        Reaguje na zmiane trybu zapisu frontu niezdominowanego.
        """
        self._update_nd_save_controls_state()

    def _on_ran_toggled(self, checked: bool) -> None:
        """
        EN:
        Handle switching the run to or from unbounded RAN mode.

        PL:
        Reaguje na wlaczenie albo wylaczenie trybu bez limitu generacji.
        """
        # Reaguje na przelaczenie trybu bez limitu generacji.
        self._update_run_form_state()
        self._log(f"RAN={checked}")

    def _on_parallel_eval_toggled(self, checked: bool) -> None:
        """
        EN:
        Enable or disable fields related to parallel objective evaluation.

        PL:
        Reaguje na wlaczenie rownoleglego liczenia funkcji celu.
        """
        # Reaguje na wlaczenie rownoleglej ewaluacji funkcji celu.
        self._update_run_form_state()
        self._log(f"parallel_eval={checked}")

    def _toggle_console_dock(self) -> None:
        """
        EN:
        Toggle the visibility of the docked console.

        PL:
        Pokazuje albo ukrywa panel konsoli.
        """
        # Pokazuje albo ukrywa dolny panel z logiem.
        self.console_dock.setVisible(not self.console_dock.isVisible())

    def _on_console_visibility_changed(self, visible: bool) -> None:
        """
        EN:
        Keep the console button label synchronized with dock visibility.

        PL:
        Dopasowuje tekst przycisku do tego, czy konsola jest widoczna.
        """
        # Aktualizuje tekst przycisku zgodnie z widocznoscia konsoli.
        self.console_btn.setText("Ukryj konsole" if visible else "Pokaz konsole")

    def _log(self, msg: str) -> None:
        """
        EN:
        Append a message to the GUI console.

        PL:
        Dopisuje komunikat do konsoli aplikacji.
        """
        # Dopisuje wpis do konsoli i przewija log do konca, gdy panel jest otwarty.
        self.text_out.append(msg)
        if self.console_dock.isVisible():
            self.text_out.ensureCursorVisible()

    def _warn(self, title: str, message: str, log_message: Optional[str] = None) -> None:
        """
        EN:
        Show a warning dialog and optionally record the same issue in the console.

        PL:
        Pokazuje ostrzezenie w oknie i opcjonalnie zapisuje je w logu.
        """
        # Pokazuje ostrzezenie w GUI i opcjonalnie zapisuje ten sam problem do logu.
        if log_message:
            self._log(log_message)
        QMessageBox.warning(self, title, message)

    def _current_n_obj(self) -> int:
        """
        EN:
        Return the current objective count with a safe fallback.

        PL:
        Zwraca aktualna liczbe funkcji celu, a gdy formularz jest niegotowy, uzywa 2.
        """
        # Zwraca aktualna liczbe celow, nawet gdy formularz jest w trakcie przebudowy.
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
        """
        EN:
        Parse one numeric token using Polish and C locale conventions.

        PL:
        Odczytuje jedna liczbe zapisana z przecinkiem albo kropka.
        """
        # Odczytuje jedna liczbe z roznych zapisow tekstowych.
        token = token.strip()
        if not token:
            return None
        # Akceptujemy zapis lokalny i klasyczny zapis z kropka, bo uzytkownik moze wpisac oba.
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
        """
        EN:
        Parse manual HV reference-point text into a list of finite floats.

        PL:
        Zamienia tekst punktu odniesienia HV na liste liczb albo komunikat bledu.
        """
        # Zamienia tekst z pola ref point na liste liczb albo zwraca komunikat bledu.
        # Uzytkownik moze podac liczby z przecinkami, kropkami albo w nawiasach.
        cleaned = text.strip().replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ").strip()
        if not cleaned:
            return None, None
        if "." in cleaned:
            tokens = [part for part in re.split(r"[;,\s]+", cleaned) if part]
        elif ";" in cleaned or re.search(r"\s", cleaned):
            tokens = [part.strip().strip(",") for part in re.split(r"[;\s]+", cleaned) if part.strip()]
        elif cleaned.count(",") > 1:
            return None, "Dla liczb z przecinkiem oddziel wymiary spacją lub ';', np. '0,6 0,7'."
        else:
            tokens = [cleaned]
        values = []
        for token in tokens:
            value = self._parse_float_token(token)
            if value is None:
                return None, f"Nie można odczytać liczby '{token}'. Użyj np. '0,6 0,7' albo '0.6,0.7'."
            values.append(value)
        return values, None

    def _auto_hv_ref_point(self) -> list[float]:
        """
        EN:
        Build the default hypervolume reference point for the current objective count.

        PL:
        Tworzy automatyczny punkt odniesienia HV dopasowany do liczby celow.
        """
        # Tworzy prosty automatyczny ref point dopasowany do liczby celow.
        return [1.1 for _ in range(self._current_n_obj())]

    def _hv_ref_point_state(self) -> Tuple[bool, Optional[list[float]], str, Optional[str]]:
        """
        EN:
        Return validity, values, mode and error message for the active HV reference point.

        PL:
        Zwraca, czy punkt HV jest poprawny, jakie ma wartosci, w jakim trybie
        dziala i jaki blad pokazac uzytkownikowi.
        """
        # Zwraca kompletny stan ref pointu: czy jest poprawny, jaka ma wartosc i w jakim trybie pracuje.
        if not self.hv_manual_radio.isChecked():
            values = self._auto_hv_ref_point()
            return True, values, "AUTO", None
        values, error = self._parse_ref_point_text(self.hv_manual_edit.text())
        if error:
            return False, None, "MANUAL", error
        if values is None:
            return False, None, "MANUAL", "Podaj ref_point albo wybierz tryb Auto."
        expected = self._current_n_obj()
        if len(values) != expected:
            return False, None, "MANUAL", f"ref_point ma długość {len(values)}, oczekiwano M={expected}."
        return True, values, "MANUAL", None

    def _validate_hv_manual_ref_point(self) -> bool:
        """
        EN:
        Validate manual HV input and mark the field when invalid.

        PL:
        Sprawdza reczny punkt HV i oznacza pole na czerwono przy bledzie.
        """
        # Waliduje reczny ref point i oznacza pole na czerwono przy bledzie.
        if not self.hv_manual_radio.isChecked():
            self.hv_manual_edit.setStyleSheet("")
            self.hv_manual_edit.setToolTip("")
            return True
        valid, _values, _mode, error = self._hv_ref_point_state()
        self.hv_manual_edit.setStyleSheet("" if valid else "border: 1px solid #d33;")
        self.hv_manual_edit.setToolTip("" if valid else error or "")
        return valid

    def _update_hv_ref_point_label(self) -> None:
        """
        EN:
        Update the label showing the currently active HV reference point.

        PL:
        Aktualizuje etykiete informujaca, jaki punkt HV jest obecnie aktywny.
        """
        # Pokazuje uzytkownikowi, jaki ref point jest teraz aktywny.
        valid, values, mode, error = self._hv_ref_point_state()
        if not valid or values is None:
            self.hv_ref_lbl.setText("HV ref point (aktywny): INVALID")
            self.hv_ref_lbl.setToolTip(error or "")
            return
        self.hv_ref_lbl.setText("HV ref point (aktywny): [" + ",".join(f"{v:.4g}" for v in values) + "]")
        self.hv_ref_lbl.setToolTip(f"mode={mode}")

    def _on_hv_mode_changed(self, _checked: bool) -> None:
        """
        EN:
        Handle switching between automatic and manual HV reference-point mode.

        PL:
        Reaguje na przelaczenie miedzy automatycznym i recznym punktem HV.
        """
        # Przelacza miedzy automatycznym i recznym trybem ref pointu.
        manual = self.hv_manual_radio.isChecked()
        self.hv_manual_edit.setEnabled(manual)
        if manual and not self.hv_manual_edit.text().strip():
            self.hv_manual_edit.setText(" ".join(f"{v:.6g}" for v in self._auto_hv_ref_point()))
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _on_hv_manual_changed(self, _text: str) -> None:
        """
        EN:
        Revalidate manual HV text after each edit.

        PL:
        Odswieza walidacje recznego punktu HV po kazdej zmianie tekstu.
        """
        # Odswieza walidacje i etykiete po kazdej zmianie tekstu ref pointu.
        self._update_hv_ref_point_label()
        self._update_run_button_state()

    def _on_live_updates_toggled(self, checked: bool) -> None:
        """
        EN:
        Toggle live plot updates during optimization.

        PL:
        Wlacza albo wylacza odswiezanie wykresu w trakcie obliczen.
        """
        # Wlacza lub wylacza odswiezanie wykresu po kazdej generacji.
        self._log(f"live_updates={checked}")
        self._render_plot()

    def _update_run_button_state(self) -> None:
        """
        EN:
        Enable Start only when no run is active and HV configuration is valid.

        PL:
        Wlacza Start tylko wtedy, gdy nic nie dziala i punkt HV jest poprawny.
        """
        # Blokuje start, gdy cos juz dziala albo ref point jest niepoprawny.
        self.run_btn.setEnabled(not (self._thread and self._thread.isRunning()) and self._validate_hv_manual_ref_point())

    def _update_plot_status(self, payload: Optional[dict] = None, message: Optional[str] = None) -> None:
        """
        EN:
        Refresh the plot or placeholder status after generation updates.

        PL:
        Odswieza wykres albo komunikat zastepczy po zmianie danych.
        """
        # Aktualizuje obszar wykresu albo komunikat zastepczy dla problemow > 3D.
        if self._plot_n_obj in (2, 3):
            self._render_plot()
            return
        if message:
            self._plot_placeholder.setText(message)
            return
        if payload:
            self._plot_placeholder.setText(
                f"Podgląd Pareto niedostępny dla {self._plot_n_obj or '?'} celów. "
                f"Gen={self._fmt_int(payload.get('n_gen'))}"
            )
            return
        self._set_plot_message("Brak wykresu - uruchom optymalizację")

    def _fmt_int(self, value: Optional[int]) -> str:
        """
        EN:
        Format optional integers for labels and table cells.

        PL:
        Formatuje liczby calkowite do wyswietlenia, a braki pokazuje jako `-`.
        """
        # Formatuje liczby calkowite do tabeli i etykiet, zachowujac `-` dla brakow.
        try:
            return "-" if value is None else str(int(value))
        except (TypeError, ValueError):
            return "-"

    def _shape_text(self, value: Optional[Any]) -> str:
        """
        EN:
        Return a compact textual representation of an array-like object's shape.

        PL:
        Zwraca krotki tekst opisujacy rozmiar danych.
        """
        if value is None:
            return "None"
        shape = getattr(value, "shape", None)
        return "x".join(str(part) for part in shape) if shape is not None else type(value).__name__

    def _fmt_metric(self, value: Optional[float]) -> str:
        """
        EN:
        Format optional metric values with stable precision for the GUI.

        PL:
        Formatuje metryke jako krotki tekst, a brak wartosci pokazuje jako `-`.
        """
        # Formatuje metryki zmiennoprzecinkowe w stabilny, krotki sposob.
        try:
            return "-" if value is None else f"{float(value):.10g}"
        except (TypeError, ValueError):
            return "-"

    def _update_metrics_label(self, payload: Optional[dict]) -> None:
        """
        EN:
        Update the compact metrics summary label.

        PL:
        Odswieza krotkie podsumowanie metryk pod przyciskami.
        """
        # Odswieza pasek z metrykami zarejestrowanymi w module metrics.
        self.metrics_lbl.setText(self._metrics_label_text(payload or {}))

    def _metrics_label_text(self, payload: Mapping[str, Any]) -> str:
        """
        EN:
        Build one-line metric summary text from a payload.

        PL:
        Tworzy tekst z najwazniejszymi metrykami dla aktualnej generacji.
        """
        return " | ".join(
            f"{METRIC_LABELS[key]}: {self._fmt_metric(payload.get(key))}" for key in METRIC_DISPLAY_ORDER
        )

    def _clear_table(self) -> None:
        """
        EN:
        Clear the generation-history metrics table.

        PL:
        Czyści tabele historii generacji.
        """
        # Czysci cala tabele historii generacji.
        self._table.setRowCount(0)
        self._last_gen_appended = None

    def _should_scroll_table(self) -> bool:
        """
        EN:
        Decide whether the metrics table should remain scrolled to the newest row.

        PL:
        Sprawdza, czy po dodaniu wiersza tabela ma przewinac sie na dol.
        """
        # Sprawdza, czy po dopisaniu wiersza tabela powinna zostac przewinieta na dol.
        bar = self._table.verticalScrollBar()
        return self._table.rowCount() == 0 or bar.value() >= bar.maximum() - 2

    def _append_generation_row(self, payload: dict) -> None:
        """
        EN:
        Append one generation's counters and metrics to the history table.

        PL:
        Dodaje do tabeli jeden wiersz z licznikami i metrykami generacji.
        """
        # Dopisuje jeden wiersz z danymi generacji do tabeli wynikow.
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
        """
        EN:
        Append the final payload only if it was not already recorded.

        PL:
        Dopisuje ostatnia generacje tylko wtedy, gdy nie ma jej jeszcze w tabeli.
        """
        # Dopisuje finalny payload tylko wtedy, gdy nie trafil juz do tabeli.
        last_gen = payload.get("n_gen")
        if last_gen is not None and last_gen != self._last_gen_appended:
            self._append_generation_row(dict(payload))
        elif self._last_gen_appended is None and payload:
            self._append_generation_row(dict(payload))

    def _metrics_table_data(self) -> Tuple[list[str], list[list[str]]]:
        """
        EN:
        Extract headers and rows from the metrics table for export.

        PL:
        Pobiera naglowki i dane z tabeli metryk do zapisania w pliku.
        """
        # Pobiera aktualne naglowki i wiersze z tabeli metryk.
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
        """
        EN:
        Export the current metrics table to an XLSX file when it contains data.

        PL:
        Zapisuje tabele metryk do pliku Excel, jesli sa w niej jakiekolwiek wyniki.
        """
        # Zapisuje historie metryk po zakonczeniu przebiegu.
        if self._table.rowCount() <= 0:
            self._log("Eksport metryk pominięty: tabela historii jest pusta.")
            return
        headers, rows = self._metrics_table_data()
        project_root = Path(__file__).resolve().parents[2]
        # Nazwa pliku dostaje algorytm, problem i aktualny czas.
        path = self._run_metrics_export_path or metrics_export_path(
            project_root,
            self._run_algorithm_name or self.alg_combo.currentText(),
            self._run_problem_name or self.problem_combo.currentText(),
        )
        try:
            saved_path = write_xlsx_table(path, headers, rows)
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            self._log(f"Eksport metryk nie powiódł się: {exc!r}")
            return
        self._log(f"Eksport metryk zapisany: {saved_path}")

    def _xlsx_value(self, value: Any) -> object:
        """
        EN:
        Normalize values before storing them in a worksheet cell.

        PL:
        Przygotowuje wartosc do zapisu w komorce arkusza.
        """
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
        """
        EN:
        Build spreadsheet headers and rows from the final nondominated front.

        PL:
        Buduje naglowki i wiersze arkusza z finalnego frontu niezdominowanego.
        """
        # Kolumny f1..fM wynikaja z rzeczywistej liczby funkcji celu w danych.
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
        """
        EN:
        Export final nondominated points to the project solution-table directory.

        PL:
        Zapisuje finalne punkty niezdominowane do katalogu tabel rozwiazan.
        """
        project_root = Path(__file__).resolve().parents[2]
        algorithm_name = self._run_algorithm_name or self.alg_combo.currentText()
        problem_name = self._run_problem_name or self.problem_combo.currentText()
        path = self._run_solutions_export_path or solutions_export_path(project_root, algorithm_name, problem_name)
        if self._nd_solution_sheets:
            sheets = [
                (f"Epoka {epoch}", headers, rows)
                for epoch, (headers, rows) in sorted(self._nd_solution_sheets.items())
            ]
        else:
            headers, rows = self._solution_table_data(payload)
            sheets = [("Rozwiazania", headers, rows)]
        try:
            saved_path = write_xlsx_workbook(path, sheets)
            created = saved_path.is_file() and saved_path.stat().st_size > 0
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            self._log(f"Eksport punktów niezdominowanych nie powiódł się: {exc!r}")
            return
        if not created:
            self._log(f"Eksport punktów niezdominowanych nie utworzył pliku: {saved_path}")
            return

        total_rows = sum(len(rows) for _sheet_name, _headers, rows in sheets)
        self._log(f"Utworzony plik Excel z punktami niezdominowanymi: {saved_path}")
        self._log(f"Liczba zapisanych punktów: {total_rows}")
        self._log(f"Dane pochodzą z uruchomienia: {algorithm_name} + {problem_name}")

    def _export_nondominated_solutions_for_epoch(self, payload: Mapping[str, Any]) -> None:
        """
        EN:
        Export nondominated solutions for the current epoch when the selected mode requires it.

        PL:
        Zapisuje front niezdominowany dla biezacej epoki, jesli wymaga tego wybrany tryb.
        """
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
            self._log(f"Eksport punktów niezdominowanych dla epoki {epoch_number} nie powiódł się: {exc!r}")
            return
        self._log(f"Zapisano punkty niezdominowane w arkuszu dla epoki {epoch_number}.")

    def _validated_int(self, value: Any, label: str, minimum: int) -> Tuple[Optional[int], Optional[str]]:
        """
        EN:
        Validate an integer form value and return an error message instead of raising.

        PL:
        Sprawdza liczbe calkowita z formularza i zwraca opis bledu dla uzytkownika.
        """
        # Sprawdza, czy wartosc daje sie odczytac jako liczba calkowita nie mniejsza od minimum.
        if value is None or isinstance(value, bool):
            return None, f"{label}: brak poprawnej liczby całkowitej."
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None, f"{label}: brak poprawnej liczby całkowitej."
        if parsed < minimum:
            return None, f"{label}: wartość musi być >= {minimum}."
        return parsed, None

    def _collect_run_args(self) -> Tuple[Optional[dict], Optional[str]]:
        """
        EN:
        Collect and validate run-wide settings from the run form.

        PL:
        Pobiera i sprawdza ustawienia calego uruchomienia, np. seed i liczbe generacji.
        """
        # Zbiera i waliduje parametry wspolne dla calego uruchomienia.
        run_values = self.run_form.values()
        seed, error = self._validated_int(run_values.get("seed"), "Seed", 0)
        if error:
            return None, error
        ran = bool(run_values.get("ran", False))
        n_gen = None
        if not ran:
            n_gen, error = self._validated_int(run_values.get("n_gen"), "Liczba generacji", 1)
            if error:
                return None, error
        parallel_workers, error = self._validated_int(run_values.get("parallel_workers"), "Liczba workerow", 1)
        if error:
            return None, error
        parallel_backend = str(run_values.get("parallel_backend") or "process")
        if parallel_backend not in {"process", "thread"}:
            return None, f"Backend rownolegly: nieobslugiwana wartosc {parallel_backend!r}."
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
        """
        EN:
        Collect and lightly validate algorithm-specific form values.

        PL:
        Pobiera ustawienia algorytmu z formularza i sprawdza podstawowe warunki.
        """
        # Zbiera i lokalnie waliduje parametry algorytmu z formularza.
        values = self.alg_form.values()
        if "pop_size" in values:
            pop_size, error = self._validated_int(values.get("pop_size"), "Rozmiar populacji", 1)
            if error:
                return None, error
            values["pop_size"] = pop_size
        return values, None

    def _collect_problem_args(self) -> Tuple[dict, Optional[str]]:
        """
        EN:
        Collect current problem form values.

        PL:
        Pobiera aktualne parametry problemu z formularza.
        """
        # Zwraca aktualne parametry problemu w postaci gotowej do przekazania factory.
        return self.problem_form.values(), None

    def _prepare_run_visuals(self) -> None:
        """
        EN:
        Reset run-specific visual state before starting a new optimization.

        PL:
        Czyści widok poprzedniego przebiegu przed nowym uruchomieniem.
        """
        # Czysci widok przed nowym przebiegiem i zostawia podglad problemu, jesli juz istnieje.
        # Nowy start czysci dane z poprzedniego przebiegu, ale nie kasuje znanej fronty problemu.
        self._reset_run_result_state()
        self._run_metrics_export_path = None
        self._run_solutions_export_path = None
        self._nd_solution_sheets = {}
        if self._plot_known_pf is None:
            self._reset_plot_axes()
        self._render_plot()

    def _finish_run(self, status_text: str, last_payload: Optional[dict]) -> None:
        """
        EN:
        Finalize GUI state after completion, cancellation or failure-like early stop.

        PL:
        Domyka stan GUI po zakonczeniu albo zatrzymaniu obliczen.
        """
        # Domyka stan GUI po zakonczeniu, stopie lub normalnym dojsciu do konca.
        self._thread = None
        self._set_run_state(status_text, running=False)
        # Jesli worker zakonczyl sie miedzy emisjami sygnalow, dopinamy ostatni payload tylko raz.
        if isinstance(last_payload, dict) and last_payload:
            self._append_last_payload_once(last_payload)
            self._apply_generation_payload(last_payload)
            self._export_nondominated_solutions_for_epoch(last_payload)
            self._update_metrics_label(last_payload)
            self._update_plot_status(last_payload)
            self._export_metrics_table()
            self._export_solution_table(last_payload)
            return
        self._export_metrics_table()
        self._render_plot()

    def _on_generation(self, payload: dict) -> None:
        """
        EN:
        Handle a generation payload emitted by the optimization worker.

        PL:
        Odbiera dane generacji z watku roboczego i aktualizuje wykres, tabele i metryki.
        """
        # Odbiera dane z worker-a i aktualizuje wykres, tabele oraz metryki.
        if not isinstance(payload, dict):
            return
        if DEBUG:
            self._log(f"GEN payload={list(payload.keys())}")
        for message in payload.get("diagnostics") or ():
            self._log(f"GEN diag: {message}")
        self._apply_generation_payload(payload)
        self._append_generation_row(payload)
        self._export_nondominated_solutions_for_epoch(payload)
        self._update_metrics_label(payload)
        if self.live_updates.isChecked():
            self._update_plot_status(payload)

    def start_run(self) -> None:
        """
        EN:
        Validate all forms, create the optimization worker and start the run.

        PL:
        Sprawdza formularze, tworzy watek roboczy i rozpoczyna optymalizacje.
        """
        # Waliduje formularze, tworzy worker i uruchamia optymalizacje.
        if self._thread and self._thread.isRunning():
            self._log("Start: uruchomienie już trwa.")
            return
        # Najpierw walidujemy wszystko lokalnie, zeby nie uruchamiac watku z bledna konfiguracja.
        if not self._validate_hv_manual_ref_point():
            self._warn("Błędny ref point", self.hv_manual_edit.toolTip() or "Niepoprawny ref_point.", "HV ref_point: start zablokowany.")
            return
        problem_key = self.problem_combo.currentData()
        alg_key = self.alg_combo.currentData()
        if not problem_key or not alg_key:
            self._warn("Brak konfiguracji", "Wybierz problem i algorytm przed uruchomieniem.", "Start: brak wybranego problemu lub algorytmu.")
            return
        run_args, error = self._collect_run_args()
        if error:
            self._warn("Błędne dane wejściowe", error, f"Start: {error}")
            return
        nd_save_args, error = self._collect_nd_save_args()
        if error:
            self._warn("Błędne ustawienia zapisu", error, f"Start: {error}")
            return
        algorithm_args, error = self._collect_algorithm_args()
        if error:
            self._warn("Błędne dane algorytmu", error, f"Start: {error}")
            return
        problem_args, error = self._collect_problem_args()
        if error:
            self._warn("Błędne dane problemu", error, f"Start: {error}")
            return
        _valid_ref_point, ref_point, _mode, _err = self._hv_ref_point_state()
        if ref_point is None:
            ref_point = self._auto_hv_ref_point()
        self._run_algorithm_name = self.alg_combo.currentText() or str(alg_key)
        self._run_problem_name = self.problem_combo.currentText() or str(problem_key)
        self._run_nd_save_mode = str(nd_save_args["mode"])
        self._run_nd_save_step = int(nd_save_args["step"])
        self._prepare_run_visuals()
        project_root = Path(__file__).resolve().parents[2]
        self._run_metrics_export_path = next_available_export_path(
            metrics_export_path(project_root, self._run_algorithm_name, self._run_problem_name)
        )
        self._run_solutions_export_path = next_available_export_path(
            solutions_export_path(project_root, self._run_algorithm_name, self._run_problem_name)
        )
        self._set_run_state("działa", running=True)
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
        )
        # Sygaly worker-a rozdzielaja aktualizacje na zywo, normalne zakonczenie, stop i blad.
        self._thread.generation.connect(self._on_generation)
        self._thread.done.connect(self._on_run_done)
        self._thread.cancelled.connect(self._on_run_cancelled)
        self._thread.failed.connect(self._on_run_failed)
        self._thread.start()

    def stop_run(self) -> None:
        """
        EN:
        Request cancellation of the active optimization worker.

        PL:
        Wysyla prosbe o zatrzymanie aktualnych obliczen.
        """
        # Prosi aktywny worker o zatrzymanie po zakonczeniu biezacego kroku.
        if not self._thread or not self._thread.isRunning():
            self._log("Stop: brak aktywnego uruchomienia.")
            return
        self._thread.request_cancel()
        self.status_lbl.setText("Status: zatrzymywanie")
        self.stop_btn.setEnabled(False)
        self._log("Stop: wyslano zadanie zatrzymania; oczekiwanie na zakonczenie biezacej generacji.")

    def _on_run_done(self, last_payload: dict) -> None:
        """
        EN:
        Handle normal worker completion.

        PL:
        Obsluguje normalne zakonczenie optymalizacji.
        """
        # Obsluguje normalne zakonczenie optymalizacji.
        self._finish_run("zakończono", last_payload)

    def _on_run_cancelled(self, last_payload: dict) -> None:
        """
        EN:
        Handle user-requested optimization cancellation.

        PL:
        Obsluguje zakonczenie po kliknieciu Stop.
        """
        # Obsluguje zakonczenie po recznym zatrzymaniu przez uzytkownika.
        self._log("Run stopped by user.")
        self._finish_run("zatrzymano", last_payload)

    def _on_run_failed(self, err: str) -> None:
        """
        EN:
        Handle worker failure and restore the idle GUI state.

        PL:
        Obsluguje blad optymalizacji i przywraca okno do stanu spoczynku.
        """
        # Obsluguje blad worker-a i przywraca GUI do stanu spoczynkowego.
        self._log(f"Run failed: {err}")
        self._thread = None
        self._set_run_state("błąd", running=False)
        self._update_metrics_label(None)
        self._render_plot()
        QMessageBox.warning(self, "Błąd optymalizacji", err)


def main() -> None:
    """
    EN:
    Create the Qt application, show the main window and enter the event loop.

    PL:
    Tworzy aplikacje Qt, pokazuje glowne okno i uruchamia petle zdarzen.
    """
    # Tworzy aplikacje Qt, pokazuje glowne okno i oddaje sterowanie petli zdarzen.
    app = QApplication(sys.argv)
    QLocale.setDefault(QLocale(QLocale.Polish, QLocale.Poland))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
