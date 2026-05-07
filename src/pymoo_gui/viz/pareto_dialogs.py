"""
EN:
Qt widgets and dialogs for visualizing Pareto fronts in one, two or three objective dimensions.

PL:
Zawiera widgety i okna wykresow Pareto, ktore pokazuja postep optymalizacji w GUI.
"""

# ------------------------------------------------------------------------------------
# File: pareto_dialogs.py
# Contents: PyQtGraph, Matplotlib and wrapper widgets for 1D, 2D and 3D Pareto-front visualization.
# What happens here: objective arrays are reduced, cached and rendered as live Pareto plots in Qt widgets.
# Role in the framework: displays optimization progress and Pareto approximations in dissertation experiments.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget


def _compute_stable_limits(
    ref_arr: Optional[np.ndarray],
    front_arr: Optional[np.ndarray],
    pop_arr: Optional[np.ndarray],
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    EN:
    Compute stable axis limits from reference, front and population arrays.

    PL:
    Wyznacza stabilne zakresy osi, aby wykres nie przeskakiwal przy kazdej generacji.
    """
    use_pf = ref_arr is not None and ref_arr.ndim == 2 and ref_arr.shape[0] >= 2
    if use_pf:
        data = ref_arr
    else:
        candidates = []
        for arr in (front_arr, pop_arr, ref_arr):
            if arr is not None and arr.ndim == 2 and arr.shape[0] > 0:
                candidates.append(arr)
        if not candidates:
            return None
        try:
            data = np.vstack(candidates)
        except Exception:
            return None

    if data.shape[0] < 20 and not use_pf:
        mins = data.min(axis=0)
        maxs = data.max(axis=0)
    elif use_pf:
        mins = data.min(axis=0)
        maxs = data.max(axis=0)
    else:
        mins = np.percentile(data, 1, axis=0)
        maxs = np.percentile(data, 99, axis=0)

    span = maxs - mins
    pads = np.where(span > 0, span * 0.03, np.maximum(np.abs(mins) * 0.05, 1e-6))
    return mins - pads, maxs + pads


class PyQtGraphParetoDialog(QDialog):
    """
    EN:
    Fast 2D Pareto plot implemented with pyqtgraph.

    PL:
    Szybki wykres 2D do odswiezania wynikow podczas dzialania algorytmu.

    Szybki live-plot 2D na pyqtgraph.
    """

    def __init__(
        self,
        ideal_front: np.ndarray,
        parent=None,
        axis_labels: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
        point_label: str = "Populacja",
        front_label: str = "Rozwiązania niezdominowane",
        ref_label: str = "Reference PF",
    ):
        """
        EN:
        Initialize a 2D plot with reference, nondominated and population layers.

        PL:
        Tworzy wykres 2D z warstwa znanego frontu, rozwiazan niezdominowanych i populacji.
        """
        super().__init__(parent)
        self.setWindowTitle("Live Pareto (2D)")
        self.resize(640, 640)

        self.axis_labels = tuple(axis_labels) if axis_labels else ("f1", "f2")
        self.base_title = title or "Front Pareto (2D)"
        self.point_label = point_label
        self.front_label = front_label
        self.ref_label = ref_label

        self._auto_scale = True
        self._limits_initialized = False
        self._fixed_limits: Optional[Tuple[float, float, float, float]] = None
        self._reference_signature: Optional[Tuple[int, float, float, float, float]] = None

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.white)
        self.setPalette(palette)

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.view = pg.GraphicsLayoutWidget()
        self.view.setBackground("w")
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

        self.plot = self.view.addPlot()
        self.plot.getViewBox().setBackgroundColor((255, 255, 255, 255))
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.addLegend(offset=(10, 10))

        front = np.asarray(ideal_front) if ideal_front is not None else np.empty((0, 2))
        if front.ndim == 2 and front.shape[1] >= 2:
            self.ref_front = front[:, :2]
        else:
            self.ref_front = np.empty((0, 2))

        self._fr_min_x = 0.0
        self._fr_max_x = 1.0
        self._fr_min_y = 0.0
        self._fr_max_y = 1.0

        self.scatter_ref = pg.ScatterPlotItem(size=6, pen=None, brush=pg.mkBrush(0, 102, 204, 200))
        self.plot.addItem(self.scatter_ref)
        if self.plot.legend is not None:
            self.plot.legend.addItem(self.scatter_ref, self.ref_label)

        if self.ref_front.size > 0:
            self.scatter_ref.setData(x=self.ref_front[:, 0], y=self.ref_front[:, 1])
            self._fr_min_x = float(self.ref_front[:, 0].min())
            self._fr_max_x = float(self.ref_front[:, 0].max())
            self._fr_min_y = float(self.ref_front[:, 1].min())
            self._fr_max_y = float(self.ref_front[:, 1].max())

        self.scatter_front = pg.ScatterPlotItem(size=8, pen=None, brush=pg.mkBrush(220, 20, 60, 210))
        self.plot.addItem(self.scatter_front)
        if self.plot.legend is not None:
            self.plot.legend.addItem(self.scatter_front, self.front_label)

        self.scatter_pop = pg.ScatterPlotItem(size=6, pen=None, brush=pg.mkBrush(120, 120, 120, 140))
        self.plot.addItem(self.scatter_pop)
        if self.plot.legend is not None:
            self.plot.legend.addItem(self.scatter_pop, self.point_label)

        self.plot.setLabel("bottom", self.axis_labels[0])
        self.plot.setLabel("left", self.axis_labels[1])
        self.plot.setTitle(self.base_title)
        self.plot.enableAutoRange(False)

    def set_auto_scale(self, enabled: bool) -> None:
        """
        EN:
        Enable or disable automatic axis-limit initialization.

        PL:
        Wlacza albo wylacza automatyczne dopasowanie osi.
        """
        self._auto_scale = bool(enabled)

    def reset_view_limits(self) -> None:
        """
        EN:
        Clear cached fixed limits so the next update can recompute them.

        PL:
        Czyści zapamietane zakresy osi, aby nastepne dane ustawily widok od nowa.
        """
        self._limits_initialized = False
        self._fixed_limits = None
        self._reference_signature = None

    def _reference_limits_signature(self, ref_arr: Optional[np.ndarray]) -> Optional[Tuple[int, float, float, float, float]]:
        """
        EN:
        Build a compact signature for detecting reference-front changes.

        PL:
        Tworzy krotki podpis frontu odniesienia, aby wykryc jego zmiane.
        """
        if ref_arr is None or ref_arr.ndim != 2 or ref_arr.shape[0] == 0:
            return None
        return (
            int(ref_arr.shape[0]),
            float(ref_arr[:, 0].min()),
            float(ref_arr[:, 0].max()),
            float(ref_arr[:, 1].min()),
            float(ref_arr[:, 1].max()),
        )

    def _set_fixed_limits(self, mins: np.ndarray, maxs: np.ndarray) -> None:
        """
        EN:
        Apply fixed x/y ranges to the pyqtgraph plot.

        PL:
        Ustawia stale zakresy osi X i Y na wykresie.
        """
        xmin, xmax = float(mins[0]), float(maxs[0])
        ymin, ymax = float(mins[1]), float(maxs[1])
        self.plot.setXRange(xmin, xmax, padding=0)
        self.plot.setYRange(ymin, ymax, padding=0)
        self._fixed_limits = (xmin, xmax, ymin, ymax)
        self._limits_initialized = True

    def _apply_fixed_limits(
        self,
        ref_arr: Optional[np.ndarray],
        front_arr: Optional[np.ndarray],
        pop_arr: Optional[np.ndarray],
    ) -> None:
        """
        EN:
        Apply stable limits once per reference context or first data update.

        PL:
        Ustawia stabilne osie po zmianie frontu odniesienia albo przy pierwszych danych.
        """
        reference_signature = self._reference_limits_signature(ref_arr)
        if reference_signature is not None and reference_signature != self._reference_signature:
            limits = _compute_stable_limits(ref_arr, None, None)
            if limits is not None:
                mins, maxs = limits
                self._set_fixed_limits(mins, maxs)
                self._reference_signature = reference_signature
            return

        if self._limits_initialized:
            return
        limits = _compute_stable_limits(ref_arr, front_arr, pop_arr)
        if limits is None:
            return
        mins, maxs = limits
        self._set_fixed_limits(mins, maxs)
        self._reference_signature = reference_signature

    def get_axis_limits(self) -> Optional[Tuple[float, float, float, float]]:
        """
        EN:
        Return current 2D axis limits when available.

        PL:
        Zwraca aktualne zakresy osi wykresu 2D.
        """
        if self._fixed_limits is not None:
            return self._fixed_limits
        try:
            x_range, y_range = self.plot.viewRange()
            return (float(x_range[0]), float(x_range[1]), float(y_range[0]), float(y_range[1]))
        except Exception:
            return None

    def update_points(
        self,
        pop_F: Optional[np.ndarray],
        front_F: Optional[np.ndarray],
        ref_F: Optional[np.ndarray],
        gen: Optional[int] = None,
    ) -> None:
        """
        EN:
        Update plotted 2D population, nondominated front and reference-front points.

        PL:
        Odswieza punkty populacji, frontu niezdominowanego i frontu odniesienia na wykresie.
        """
        def _finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Remove rows with non-finite values before plotting.

            PL:
            Usuwa wiersze z blednymi wartosciami przed rysowaniem.
            """
            if data is None:
                return None
            mask = np.isfinite(data).all(axis=1)
            return data[mask]

        def _as_2d(arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Reduce an array to finite two-objective plotting coordinates.

            PL:
            Zamienia dane na dwa wymiary potrzebne do wykresu 2D.
            """
            if arr is None:
                return None
            data = np.asarray(arr)
            if data.ndim != 2 or data.shape[1] < 2:
                return None
            data = data[:, :2]
            return _finite_rows(data)

        pop = _as_2d(pop_F)
        front = _as_2d(front_F) if front_F is not None else None
        ref = _as_2d(ref_F) if ref_F is not None else None

        if ref is not None:
            self.scatter_ref.setData(x=ref[:, 0], y=ref[:, 1])
        else:
            self.scatter_ref.setData(x=[], y=[])
        if front is not None:
            self.scatter_front.setData(x=front[:, 0], y=front[:, 1])
        else:
            self.scatter_front.setData(x=[], y=[])
        if pop is not None:
            self.scatter_pop.setData(x=pop[:, 0], y=pop[:, 1])
        else:
            self.scatter_pop.setData(x=[], y=[])
        self._apply_fixed_limits(ref, front, pop)

        if gen is not None:
            try:
                gen_val = int(gen)
            except Exception:
                gen_val = None
            if gen_val is not None:
                self.plot.setTitle(f"{self.base_title} | iter={gen_val}")


class MatplotlibParetoDialog(QDialog):
    """
    EN:
    Matplotlib-based Pareto plot supporting 2D and 3D displays.

    PL:
    Wykres Pareto oparty na Matplotlib, uzywany zwlaszcza dla widoku 3D.

    Live-plot 2D/3D na matplotlib (bardziej uniwersalny, wolniejszy).
    """

    def __init__(
        self,
        ideal_front: np.ndarray,
        parent=None,
        equal_aspect: bool = False,
        axis_labels: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
        point_label: str = "Populacja",
        front_label: str = "Rozwiązania niezdominowane",
        ref_label: str = "Reference PF",
    ):
        """
        EN:
        Initialize a Matplotlib plot and choose 2D or 3D mode from the reference front.

        PL:
        Tworzy wykres Matplotlib i wybiera tryb 2D albo 3D na podstawie danych.
        """
        super().__init__(parent)
        self.setWindowTitle("Live Pareto (Matplotlib)")
        self.resize(820, 820)

        front = np.asarray(ideal_front) if ideal_front is not None else np.empty((0, 0))
        if front.ndim != 2:
            front = np.empty((0, 0))

        self.dim = 3 if front.shape[1] >= 3 else 2
        if self.dim == 3 and front.shape[1] >= 3:
            front = front[:, :3]
        elif self.dim == 2 and front.shape[1] >= 2:
            front = front[:, :2]
        else:
            front = np.empty((0, self.dim))

        default_labels = ("f1", "f2", "f3") if self.dim == 3 else ("f1", "f2")
        self.axis_labels = tuple(axis_labels) if axis_labels else default_labels
        self.base_title = title or ("Front Pareto (3D)" if self.dim == 3 else "Front Pareto (2D)")
        self.point_label = point_label
        self.front_label = front_label
        self.ref_label = ref_label
        self.equal_aspect = equal_aspect

        self._auto_scale = True
        self._limits_initialized = False

        self.fig = plt.figure(figsize=(8, 8))
        if self.dim == 3:
            self.ax = self.fig.add_subplot(111, projection="3d")
        else:
            self.ax = self.fig.add_subplot(111)

        self.ax.set_title(self.base_title, fontsize=14)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        ref_color = "#0066cc"
        front_color = "#dc143c"
        pop_color = "#808080"

        if self.dim == 3:
            self.scatter_ref = self.ax.scatter([], [], [], s=12, alpha=0.45, label=self.ref_label, color=ref_color)
            self.scatter_front = self.ax.scatter([], [], [], s=20, alpha=0.55, label=self.front_label, color=front_color)
            self.scatter_pop = self.ax.scatter([], [], [], s=25, label=self.point_label, color=pop_color)
        else:
            self.scatter_ref = self.ax.scatter([], [], s=12, alpha=0.45, label=self.ref_label, color=ref_color)
            self.scatter_front = self.ax.scatter([], [], s=20, alpha=0.55, label=self.front_label, color=front_color)
            self.scatter_pop = self.ax.scatter([], [], s=25, label=self.point_label, color=pop_color)

        if front.size > 0:
            if self.dim == 3:
                self.scatter_ref._offsets3d = (front[:, 0], front[:, 1], front[:, 2])
            else:
                self.scatter_ref.set_offsets(front[:, :2])

        self.ax.set_xlabel(self.axis_labels[0])
        self.ax.set_ylabel(self.axis_labels[1])
        if self.dim == 3:
            self.ax.set_zlabel(self.axis_labels[2])

        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")

        if self.equal_aspect:
            self._apply_equal_aspect()

        if self.dim == 3:
            self.ax.view_init(elev=25, azim=135)

        self.fig.tight_layout()

    def _apply_equal_aspect(self) -> None:
        """
        EN:
        Apply equal axis aspect for comparable visual scale.

        PL:
        Ustawia rowne proporcje osi, aby odleglosci byly porownywalne wizualnie.
        """
        if self.dim == 2:
            self.ax.set_aspect("equal", adjustable="box")
        else:
            self.ax.set_box_aspect((1.0, 1.0, 1.0))

    def reset_view_limits(self) -> None:
        """
        EN:
        Mark axis limits for recomputation on the next update.

        PL:
        Oznacza zakresy osi do ponownego wyznaczenia przy nastepnym odswiezeniu.
        """
        self._limits_initialized = False

    def update_points(
        self,
        pop_F: Optional[np.ndarray],
        front_F: Optional[np.ndarray],
        ref_F: Optional[np.ndarray],
        gen: Optional[int] = None,
    ) -> None:
        """
        EN:
        Update Matplotlib scatter layers and refresh the canvas.

        PL:
        Odswieza warstwy punktow na wykresie Matplotlib i przerysowuje plotno.
        """
        def _finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Keep only finite rows for plotting.

            PL:
            Zostawia tylko wiersze z poprawnymi liczbami.
            """
            if data is None:
                return None
            mask = np.isfinite(data).all(axis=1)
            return data[mask]

        def _as_dim(arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Reduce an objective matrix to the plot dimensionality.

            PL:
            Ogranicza dane do liczby wymiarow pokazywanych na wykresie.
            """
            if arr is None:
                return None
            data = np.asarray(arr)
            if data.ndim != 2 or data.shape[1] < self.dim:
                return None
            data = data[:, : self.dim]
            return _finite_rows(data)

        pop = _as_dim(pop_F)
        front = _as_dim(front_F) if front_F is not None else None
        ref = _as_dim(ref_F) if ref_F is not None else None

        if ref is not None:
            if self.dim == 3:
                xs, ys, zs = ref[:, 0], ref[:, 1], ref[:, 2]
                self.scatter_ref._offsets3d = (xs, ys, zs)
            else:
                self.scatter_ref.set_offsets(np.column_stack((ref[:, 0], ref[:, 1])))
        elif self.dim == 3:
            self.scatter_ref._offsets3d = ([], [], [])
        else:
            self.scatter_ref.set_offsets(np.empty((0, 2)))

        if front is not None:
            if self.dim == 3:
                xs, ys, zs = front[:, 0], front[:, 1], front[:, 2]
                self.scatter_front._offsets3d = (xs, ys, zs)
            else:
                self.scatter_front.set_offsets(np.column_stack((front[:, 0], front[:, 1])))
        elif self.dim == 3:
            self.scatter_front._offsets3d = ([], [], [])
        else:
            self.scatter_front.set_offsets(np.empty((0, 2)))

        if pop is not None:
            if self.dim == 3:
                xs, ys, zs = pop[:, 0], pop[:, 1], pop[:, 2]
                self.scatter_pop._offsets3d = (xs, ys, zs)
            else:
                self.scatter_pop.set_offsets(np.column_stack((pop[:, 0], pop[:, 1])))
        elif self.dim == 3:
            self.scatter_pop._offsets3d = ([], [], [])
        else:
            self.scatter_pop.set_offsets(np.empty((0, 2)))

        if self._auto_scale or not self._limits_initialized:
            use_pf = ref is not None and ref.shape[0] >= 2
            if use_pf:
                data = ref
            else:
                candidates = []
                if front is not None and front.size > 0:
                    candidates.append(front)
                if pop is not None and pop.size > 0:
                    candidates.append(pop)
                if ref is not None and ref.size > 0:
                    candidates.append(ref)
                if candidates:
                    try:
                        data = np.vstack(candidates)
                    except Exception:
                        data = None
                else:
                    data = None

            if data is not None:
                if data.shape[0] < 20 and not use_pf:
                    mins = data.min(axis=0)
                    maxs = data.max(axis=0)
                else:
                    if use_pf:
                        mins = data.min(axis=0)
                        maxs = data.max(axis=0)
                    else:
                        mins = np.percentile(data, 1, axis=0)
                        maxs = np.percentile(data, 99, axis=0)
                spans = maxs - mins
                pads = np.where(spans > 0, spans * 0.03, np.maximum(np.abs(mins) * 0.05, 1e-6))
                mins = mins - pads
                maxs = maxs + pads

                self.ax.set_xlim(float(mins[0]), float(maxs[0]))
                self.ax.set_ylim(float(mins[1]), float(maxs[1]))
                if self.dim == 3:
                    self.ax.set_zlim(float(mins[2]), float(maxs[2]))
                self._limits_initialized = True

        if self.equal_aspect:
            self._apply_equal_aspect()

        if gen is not None:
            try:
                gen_val = int(gen)
            except Exception:
                gen_val = None
            if gen_val is not None:
                self.ax.set_title(f"{self.base_title} | iter={gen_val}", fontsize=14)
        self.canvas.draw_idle()

    def set_auto_scale(self, enabled: bool) -> None:
        """
        EN:
        Enable or disable automatic axis scaling.

        PL:
        Wlacza albo wylacza automatyczne skalowanie osi.
        """
        self._auto_scale = bool(enabled)

    def get_axis_limits(self) -> Optional[Tuple[float, ...]]:
        """
        EN:
        Return current Matplotlib axis limits.

        PL:
        Zwraca aktualne zakresy osi wykresu Matplotlib.
        """
        try:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            if self.dim == 3:
                zlim = self.ax.get_zlim()
                return (float(xlim[0]), float(xlim[1]), float(ylim[0]), float(ylim[1]), float(zlim[0]), float(zlim[1]))
            return (float(xlim[0]), float(xlim[1]), float(ylim[0]), float(ylim[1]))
        except Exception:
            return None


class OneDParetoDialog(QDialog):
    """
    EN:
    One-objective Pareto plot using point index on the x-axis and objective value on y.

    PL:
    Wykres dla jednego celu, gdzie os X to numer punktu, a os Y to wartosc celu.

    Prosty wykres 1D: x = indeks punktu, y = f1.
    """

    def __init__(
        self,
        ideal_front: np.ndarray,
        parent=None,
        axis_labels: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
        point_label: str = "Populacja",
        front_label: str = "Rozwiązania niezdominowane",
        ref_label: str = "Reference PF",
    ):
        """
        EN:
        Initialize a one-dimensional Matplotlib plot.

        PL:
        Tworzy prosty wykres dla problemu z jedna funkcja celu.
        """
        super().__init__(parent)
        self.setWindowTitle("Live Pareto (1D)")
        self.resize(820, 600)

        front = np.asarray(ideal_front) if ideal_front is not None else np.empty((0, 1))
        if front.ndim == 1:
            front = front.reshape(-1, 1)
        if front.ndim != 2 or front.shape[1] < 1:
            front = np.empty((0, 1))

        self.axis_label = axis_labels[0] if axis_labels else "f1"
        self.base_title = title or "Front Pareto (1D)"
        self.point_label = point_label
        self.front_label = front_label
        self.ref_label = ref_label

        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(self.base_title, fontsize=14)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        ref_color = "#0066cc"
        front_color = "#dc143c"
        pop_color = "#808080"

        self.scatter_ref = self.ax.scatter([], [], s=18, alpha=0.6, label=self.ref_label, color=ref_color)
        self.scatter_front = self.ax.scatter([], [], s=20, alpha=0.6, label=self.front_label, color=front_color)
        self.scatter_pop = self.ax.scatter([], [], s=25, label=self.point_label, color=pop_color)

        if front.size > 0:
            xs = np.arange(front.shape[0])
            ys = front[:, 0]
            self.scatter_ref.set_offsets(np.column_stack((xs, ys)))
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel(self.axis_label)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")
        self.fig.tight_layout()

    def set_auto_scale(self, enabled: bool) -> None:
        """
        EN:
        Enable or disable y-axis autoscaling.

        PL:
        Wlacza albo wylacza automatyczne dopasowanie osi Y.
        """
        self._auto_scale = bool(enabled)

    def reset_view_limits(self) -> None:
        """
        EN:
        Mark one-dimensional plot limits for recomputation.

        PL:
        Czyści zapamietane zakresy osi dla wykresu 1D.
        """
        self._limits_initialized = False

    def get_axis_limits(self) -> Optional[Tuple[float, float, float, float]]:
        """
        EN:
        Return current 1D plot axis limits.

        PL:
        Zwraca aktualne zakresy osi wykresu 1D.
        """
        try:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            return (float(xlim[0]), float(xlim[1]), float(ylim[0]), float(ylim[1]))
        except Exception:
            return None

    def update_points(
        self,
        pop_F: Optional[np.ndarray],
        front_F: Optional[np.ndarray],
        ref_F: Optional[np.ndarray],
        gen: Optional[int] = None,
    ) -> None:
        """
        EN:
        Update one-dimensional population, front and reference scatter layers.

        PL:
        Odswieza punkty populacji, frontu i odniesienia na wykresie 1D.
        """
        def _finite_rows(data: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Keep finite rows before plotting.

            PL:
            Usuwa wiersze z niepoprawnymi wartosciami.
            """
            if data is None:
                return None
            mask = np.isfinite(data).all(axis=1)
            return data[mask]

        def _as_1d(arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Reduce an array to one objective column.

            PL:
            Zamienia dane na jedna kolumne celu.
            """
            if arr is None:
                return None
            data = np.asarray(arr)
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            if data.ndim != 2 or data.shape[1] < 1:
                return None
            data = data[:, :1]
            return _finite_rows(data)

        pop = _as_1d(pop_F)
        front = _as_1d(front_F) if front_F is not None else None
        ref = _as_1d(ref_F) if ref_F is not None else None

        if ref is not None:
            ys = ref[:, 0]
            xs = np.arange(len(ys))
            self.scatter_ref.set_offsets(np.column_stack((xs, ys)))
        else:
            self.scatter_ref.set_offsets(np.empty((0, 2)))

        if front is not None:
            ys = front[:, 0]
            xs = np.arange(len(ys))
            self.scatter_front.set_offsets(np.column_stack((xs, ys)))
        else:
            self.scatter_front.set_offsets(np.empty((0, 2)))

        if pop is not None:
            ys = pop[:, 0]
            xs = np.arange(len(ys))
            self.scatter_pop.set_offsets(np.column_stack((xs, ys)))
        else:
            self.scatter_pop.set_offsets(np.empty((0, 2)))

        if self._auto_scale or not self._limits_initialized:
            use_pf = ref is not None and ref.shape[0] >= 2
            if use_pf:
                data = ref
            else:
                candidates = []
                if front is not None and front.size > 0:
                    candidates.append(front)
                if pop is not None and pop.size > 0:
                    candidates.append(pop)
                if ref is not None and ref.size > 0:
                    candidates.append(ref)
                if candidates:
                    try:
                        data = np.vstack(candidates)
                    except Exception:
                        data = None
                else:
                    data = None

            if data is not None:
                if data.shape[0] < 20 and not use_pf:
                    mins = data.min(axis=0)
                    maxs = data.max(axis=0)
                else:
                    if use_pf:
                        mins = data.min(axis=0)
                        maxs = data.max(axis=0)
                    else:
                        mins = np.percentile(data, 1, axis=0)
                        maxs = np.percentile(data, 99, axis=0)
                span = float(maxs[0] - mins[0])
                pad = 0.03 * span if span > 0 else max(abs(float(mins[0])) * 0.05, 1e-6)
                ymin = float(mins[0] - pad)
                ymax = float(maxs[0] + pad)
                if use_pf:
                    max_len = int(ref.shape[0]) if ref is not None else 1
                else:
                    max_len = 1
                    for arr in (front, pop, ref):
                        if arr is not None and arr.size > 0:
                            max_len = max(max_len, int(arr.shape[0]))
                xmax = max_len - 1 if max_len > 1 else 1
                self.ax.set_xlim(0, float(xmax))
                self.ax.set_ylim(ymin, ymax)
                self._limits_initialized = True

        if gen is not None:
            try:
                gen_val = int(gen)
            except Exception:
                gen_val = None
            if gen_val is not None:
                self.ax.set_title(f"{self.base_title} | iter={gen_val}", fontsize=14)
        self.canvas.draw_idle()


class UnifiedParetoDialog(QDialog):
    """
    EN:
    Dialog wrapper that chooses 1D, 2D or 3D Pareto visualization automatically.

    PL:
    Okno, ktore samo wybiera odpowiedni typ wykresu Pareto dla liczby celow.
    """

    """
    Dla 1 celu: 1D. Dla 2 celów: 2D. Dla >=3 celów: 3D (pierwsze trzy cele).
    """

    def __init__(
        self,
        ideal_front: np.ndarray,
        parent=None,
        equal_aspect: bool = False,
        objective_names: Optional[Sequence[str]] = None,
    ):
        """
        EN:
        Create the concrete plot dialog matching the objective dimensionality.

        PL:
        Tworzy konkretny wykres dopasowany do liczby funkcji celu.
        """
        super().__init__(parent)

        arr = np.asarray(ideal_front) if ideal_front is not None else np.empty((0, 0))
        if arr.ndim != 2:
            arr = np.empty((0, 0))

        self.original_dim = arr.shape[1]
        if self.original_dim < 1:
            self.original_dim = len(objective_names) if objective_names else 2

        if objective_names:
            self.objective_names = list(objective_names)
        else:
            self.objective_names = []
        if len(self.objective_names) < self.original_dim:
            missing = self.original_dim - len(self.objective_names)
            start = len(self.objective_names)
            self.objective_names.extend(f"f{i + 1}" for i in range(start, start + missing))

        if self.original_dim <= 1:
            self.display_indices = (0,)
            axis_labels = (self.objective_names[0],)
            display_front = arr[:, :1] if arr.shape[1] >= 1 else np.empty((0, 1))
            self._dialog = OneDParetoDialog(
                display_front,
                parent=parent,
                axis_labels=axis_labels,
                title="Front Pareto (1D)",
                front_label="Rozwiązania niezdominowane",
                ref_label="Znany front Pareto",
            )
        elif self.original_dim == 2:
            self.display_indices = (0, 1)
            axis_labels = tuple(self.objective_names[i] for i in self.display_indices)
            display_front = arr[:, self.display_indices] if arr.shape[1] >= 2 else np.empty((0, 2))
            self._dialog = PyQtGraphParetoDialog(
                display_front,
                parent=parent,
                axis_labels=axis_labels,
                title="Front Pareto (2D)",
                front_label="Rozwiązania niezdominowane",
                ref_label="Znany front Pareto",
            )
        else:
            self.display_indices = (0, 1, 2)
            axis_labels = tuple(self.objective_names[i] for i in self.display_indices)
            display_front = arr[:, self.display_indices] if arr.shape[1] >= 3 else np.empty((0, 3))
            title_suffix = "" if self.original_dim <= 3 else f" (cele 1..3 z {self.original_dim})"
            self._dialog = MatplotlibParetoDialog(
                display_front,
                parent=parent,
                equal_aspect=equal_aspect,
                axis_labels=axis_labels,
                title="Front Pareto (3D)" + title_suffix,
                front_label="Rozwiązania niezdominowane",
                ref_label="Znany front Pareto",
            )

    def show(self) -> None:
        """
        EN:
        Show the delegated concrete dialog.

        PL:
        Pokazuje wewnetrzne okno z wykresem.
        """
        self._dialog.show()

    def set_auto_scale(self, enabled: bool) -> None:
        """
        EN:
        Forward auto-scale changes to the concrete plot.

        PL:
        Przekazuje ustawienie autoskali do wlasciwego wykresu.
        """
        if hasattr(self._dialog, "set_auto_scale"):
            self._dialog.set_auto_scale(enabled)

    def get_axis_limits(self) -> Optional[Tuple[float, ...]]:
        """
        EN:
        Return axis limits from the concrete plot when supported.

        PL:
        Zwraca zakresy osi z aktualnego typu wykresu.
        """
        if hasattr(self._dialog, "get_axis_limits"):
            return self._dialog.get_axis_limits()
        return None

    def update_points(
        self,
        pop_F: Optional[np.ndarray],
        front_F: Optional[np.ndarray],
        ref_F: Optional[np.ndarray],
        gen: Optional[int] = None,
    ) -> None:
        """
        EN:
        Reduce objective arrays to displayed dimensions and update the concrete plot.

        PL:
        Wybiera pokazywane wymiary celow i odswieza wlasciwy wykres.
        """
        def _reduce(arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
            """
            EN:
            Select only the objective columns displayed by this wrapper.

            PL:
            Wybiera tylko te kolumny celow, ktore sa widoczne na wykresie.
            """
            if arr is None:
                return None
            data = np.asarray(arr)
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            if data.ndim != 2 or data.shape[1] < len(self.display_indices):
                return None
            return data[:, self.display_indices]

        pop = _reduce(pop_F)
        front = _reduce(front_F) if front_F is not None else None
        ref = _reduce(ref_F) if ref_F is not None else None
        self._dialog.update_points(pop, front, ref, gen)

    def __getattr__(self, name):
        """
        EN:
        Delegate missing attributes to the concrete dialog.

        PL:
        Przekazuje brakujace atrybuty do wewnetrznego okna wykresu.
        """
        return getattr(self._dialog, name)


class PyQtGraphParetoWidget(PyQtGraphParetoDialog):
    """
    EN:
    Embedded QWidget variant of the pyqtgraph 2D Pareto dialog.

    PL:
    Wersja widgetu 2D, ktora mozna wstawic bezposrednio do glownego okna.
    """

    def __init__(self, *args, **kwargs):
        """
        EN:
        Initialize the 2D widget and force widget window flags.

        PL:
        Tworzy widget 2D i ustawia go jako element osadzony w oknie.
        """
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.Widget)


class MatplotlibParetoWidget(MatplotlibParetoDialog):
    """
    EN:
    Embedded QWidget variant of the Matplotlib Pareto dialog.

    PL:
    Wersja widgetu Matplotlib osadzana w glownym oknie.
    """

    def __init__(self, *args, **kwargs):
        """
        EN:
        Initialize the Matplotlib widget and force widget window flags.

        PL:
        Tworzy widget Matplotlib jako element osadzony.
        """
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.Widget)


class OneDParetoWidget(OneDParetoDialog):
    """
    EN:
    Embedded QWidget variant of the one-dimensional Pareto dialog.

    PL:
    Wersja widgetu 1D osadzana w glownym oknie.
    """

    def __init__(self, *args, **kwargs):
        """
        EN:
        Initialize the 1D widget and force widget window flags.

        PL:
        Tworzy widget 1D jako element osadzony.
        """
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.Widget)


class UnifiedParetoWidget(QWidget):
    """
    EN:
    Widget wrapper for embedded Pareto plots (1D/2D/3D).

    PL:
    Osadzony wrapper wykresu Pareto, ktory sam wybiera widok 1D, 2D albo 3D.

    Widget wrapper for embedded Pareto plots (1D/2D/3D).
    """

    def __init__(
        self,
        ideal_front: np.ndarray,
        parent=None,
        equal_aspect: bool = False,
        objective_names: Optional[Sequence[str]] = None,
    ):
        """
        EN:
        Create the embedded concrete plot widget matching the objective dimensionality.

        PL:
        Tworzy osadzony wykres dopasowany do liczby celow.
        """
        super().__init__(parent)

        arr = np.asarray(ideal_front) if ideal_front is not None else np.empty((0, 0))
        if arr.ndim != 2:
            arr = np.empty((0, 0))

        self.original_dim = arr.shape[1]
        if self.original_dim < 1:
            self.original_dim = len(objective_names) if objective_names else 2

        if objective_names:
            self.objective_names = list(objective_names)
        else:
            self.objective_names = []
        if len(self.objective_names) < self.original_dim:
            missing = self.original_dim - len(self.objective_names)
            start = len(self.objective_names)
            self.objective_names.extend(f"f{i + 1}" for i in range(start, start + missing))

        if self.original_dim <= 1:
            self.display_indices = (0,)
            axis_labels = (self.objective_names[0],)
            display_front = arr[:, :1] if arr.shape[1] >= 1 else np.empty((0, 1))
            self._dialog = OneDParetoWidget(
                display_front,
                parent=self,
                axis_labels=axis_labels,
                title="Front Pareto (1D)",
                front_label="Rozwiązania niezdominowane",
                ref_label="Znany front Pareto",
            )
        elif self.original_dim == 2:
            self.display_indices = (0, 1)
            axis_labels = tuple(self.objective_names[i] for i in self.display_indices)
            display_front = arr[:, self.display_indices] if arr.shape[1] >= 2 else np.empty((0, 2))
            self._dialog = PyQtGraphParetoWidget(
                display_front,
                parent=self,
                axis_labels=axis_labels,
                title="Front Pareto (2D)",
                front_label="Rozwiązania niezdominowane",
                ref_label="Znany front Pareto",
            )
        else:
            self.display_indices = (0, 1, 2)
            axis_labels = tuple(self.objective_names[i] for i in self.display_indices)
            display_front = arr[:, self.display_indices] if arr.shape[1] >= 3 else np.empty((0, 3))
            title_suffix = "" if self.original_dim <= 3 else f" (cele 1..3 z {self.original_dim})"
            self._dialog = MatplotlibParetoWidget(
                display_front,
                parent=self,
                equal_aspect=equal_aspect,
                axis_labels=axis_labels,
                title="Front Pareto (3D)" + title_suffix,
                front_label="Rozwiązania niezdominowane",
                ref_label="Znany front Pareto",
            )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._dialog)

        self._show_population = False
        self._last_pop_F: Optional[np.ndarray] = None
        self._last_front_F: Optional[np.ndarray] = None
        self._last_ref_F: Optional[np.ndarray] = None
        self._last_gen: Optional[int] = None
        self._last_rendered_gen: Optional[int] = None
        self._last_rendered_shapes: Tuple[Optional[Tuple[int, ...]], Optional[Tuple[int, ...]], Optional[Tuple[int, ...]]] = (
            None,
            None,
            None,
        )

    def set_auto_scale(self, enabled: bool) -> None:
        """
        EN:
        Forward auto-scale changes to the embedded plot widget.

        PL:
        Przekazuje ustawienie autoskali do osadzonego wykresu.
        """
        if hasattr(self._dialog, "set_auto_scale"):
            self._dialog.set_auto_scale(enabled)

    def set_show_population(self, enabled: bool) -> None:
        """
        EN:
        Toggle whether the full population layer is rendered.

        PL:
        Wlacza albo ukrywa warstwe calej populacji na wykresie.
        """
        enabled = bool(enabled)
        if self._show_population == enabled:
            return
        self._show_population = enabled
        self._render_points()

    def get_axis_limits(self) -> Optional[Tuple[float, ...]]:
        """
        EN:
        Return current axis limits from the embedded plot.

        PL:
        Zwraca aktualne zakresy osi z osadzonego wykresu.
        """
        if hasattr(self._dialog, "get_axis_limits"):
            return self._dialog.get_axis_limits()
        return None

    def _reduce_points(self, arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """
        EN:
        Reduce objective data to the columns displayed by the widget.

        PL:
        Wybiera tylko te kolumny celow, ktore sa pokazywane.
        """
        if arr is None:
            return None
        data = np.asarray(arr)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        if data.ndim != 2 or data.shape[1] < len(self.display_indices):
            return None
        return data[:, self.display_indices]

    def _snapshot_points(self, arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """
        EN:
        Copy plot input data to protect cached state from later mutation.

        PL:
        Kopiuje dane wykresu, aby pozniejsze zmiany tablic nie psuly widoku.
        """
        if arr is None:
            return None
        try:
            data = np.array(arr, dtype=float, copy=True)
        except (TypeError, ValueError):
            return None
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        return data if data.ndim == 2 else None

    def _shape_of(self, arr: Optional[np.ndarray]) -> Optional[Tuple[int, ...]]:
        """
        EN:
        Return an array shape tuple for diagnostics.

        PL:
        Zwraca rozmiar tablicy do diagnostyki.
        """
        return tuple(arr.shape) if arr is not None else None

    def _render_points(self) -> None:
        """
        EN:
        Render cached population, nondominated and reference points in the embedded plot.

        PL:
        Rysuje zapamietane punkty populacji, frontu i odniesienia.
        """
        pop = self._reduce_points(self._last_pop_F) if self._show_population else None
        if not self._show_population:
            pop = np.empty((0, len(self.display_indices)))
        front = self._reduce_points(self._last_front_F) if self._last_front_F is not None else None
        ref = self._reduce_points(self._last_ref_F) if self._last_ref_F is not None else None
        self._dialog.update_points(pop, front, ref, self._last_gen)
        # Diagnostic invariant: rendered series should describe one cached generation.
        self._last_rendered_gen = self._last_gen
        self._last_rendered_shapes = (self._shape_of(pop), self._shape_of(front), self._shape_of(ref))

    def render_snapshot(self) -> dict:
        """
        EN:
        Return diagnostic information about the last rendered plot state.

        PL:
        Zwraca informacje diagnostyczne o ostatnio narysowanym stanie wykresu.
        """
        return {
            "gen": self._last_rendered_gen,
            "pop_shape": self._last_rendered_shapes[0],
            "front_shape": self._last_rendered_shapes[1],
            "ref_shape": self._last_rendered_shapes[2],
            "backend": type(self._dialog).__name__,
        }

    def update_points(
        self,
        pop_F: Optional[np.ndarray],
        front_F: Optional[np.ndarray],
        ref_F: Optional[np.ndarray],
        gen: Optional[int] = None,
    ) -> None:
        """
        EN:
        Cache new plot data and render it through the selected embedded widget.

        PL:
        Zapamietuje nowe dane i odswieza odpowiedni wykres.
        """
        self._last_pop_F = self._snapshot_points(pop_F)
        self._last_front_F = self._snapshot_points(front_F)
        self._last_ref_F = self._snapshot_points(ref_F)
        self._last_gen = gen
        self._render_points()

    def __getattr__(self, name):
        """
        EN:
        Delegate missing attributes to the embedded concrete plot.

        PL:
        Przekazuje brakujace atrybuty do osadzonego wykresu.
        """
        return getattr(self._dialog, name)
