# Metric trajectory charts for the current single experiment.

from __future__ import annotations

import math
from typing import Any, Mapping, Optional

import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QScrollArea, QStackedLayout, QVBoxLayout, QWidget

from ..metrics import METRIC_LABELS, METRIC_TABLE_ORDER


class PlainDecimalAxisItem(pg.AxisItem):
    # Display metric values directly instead of using an SI multiplier or exponent.

    def tickStrings(self, values, scale, spacing):
        effective_spacing = abs(float(spacing) * float(scale))
        if effective_spacing <= 0 or not math.isfinite(effective_spacing):
            decimals = 6
        else:
            decimals = max(0, min(12, int(math.ceil(-math.log10(effective_spacing))) + 1))
        labels = []
        for value in values:
            scaled = float(value) * float(scale)
            text = f"{scaled:.{decimals}f}".rstrip("0").rstrip(".")
            labels.append("0" if text in {"", "-0"} else text)
        return labels


class MetricTrajectoriesWidget(QWidget):
    # Display one generation/value line chart for every supported quality metric.

    _COLORS = (
        (41, 128, 185),
        (192, 57, 43),
        (39, 174, 96),
        (142, 68, 173),
        (243, 156, 18),
        (22, 160, 133),
        (127, 140, 141),
        (211, 84, 0),
    )

    def __init__(self, parent=None) -> None:
        # Build a scrollable two-column grid of metric plots.
        super().__init__(parent)
        self._algorithm_name: Optional[str] = None
        self._problem_name: Optional[str] = None
        self._values: dict[str, dict[int, float]] = {key: {} for key in METRIC_TABLE_ORDER}
        self._plots: dict[str, pg.PlotWidget] = {}
        self._curves: dict[str, Any] = {}
        self._empty_labels: dict[str, QLabel] = {}
        self._chart_containers: dict[str, QWidget] = {}
        self._visible_metrics = set(METRIC_TABLE_ORDER)

        root = QVBoxLayout(self)
        self.context_label = QLabel()
        self.context_label.setWordWrap(True)
        root.addWidget(self.context_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self._grid = QGridLayout(content)
        for index, metric_key in enumerate(METRIC_TABLE_ORDER):
            label = "KKTPM (mean)" if metric_key == "kktpm" else METRIC_LABELS[metric_key]
            chart_container = QWidget()
            self._chart_containers[metric_key] = chart_container
            chart_stack = QStackedLayout(chart_container)
            chart_stack.setStackingMode(QStackedLayout.StackAll)
            chart_stack.setContentsMargins(0, 0, 0, 0)
            axis_items = None
            if metric_key in {"spread", "delta", "kktpm"}:
                decimal_axis = PlainDecimalAxisItem(orientation="left")
                decimal_axis.enableAutoSIPrefix(False)
                axis_items = {"left": decimal_axis}
            plot = pg.PlotWidget(background="w", axisItems=axis_items)
            plot.setMinimumHeight(230)
            plot.setTitle(label, color="#202020", size="11pt")
            plot.setLabel("bottom", "Generation")
            plot.setLabel("left", "Value")
            plot.showGrid(x=True, y=True, alpha=0.25)
            color = self._COLORS[index % len(self._COLORS)]
            self._plots[metric_key] = plot
            self._curves[metric_key] = plot.plot(
                [],
                [],
                pen=pg.mkPen(color=color, width=2),
                symbol="o",
                symbolSize=5,
                symbolBrush=color,
                symbolPen=color,
            )
            empty_label = QLabel("N/A")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            empty_label.setStyleSheet(
                "QLabel { color: #777777; background: transparent; font-size: 18px; font-weight: bold; }"
            )
            empty_label.setToolTip("This metric is not available for the current Main run.")
            self._empty_labels[metric_key] = empty_label
            chart_stack.addWidget(plot)
            chart_stack.addWidget(empty_label)
            chart_stack.setCurrentWidget(empty_label)
            self._grid.addWidget(chart_container, index // 2, index % 2)
        self._grid.setColumnStretch(0, 1)
        self._grid.setColumnStretch(1, 1)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)
        self.reset()

    def reset(
        self,
        algorithm_name: Optional[str] = None,
        problem_name: Optional[str] = None,
    ) -> None:
        # Clear previous values and describe the current Main-run context.
        self._algorithm_name = str(algorithm_name) if algorithm_name else None
        self._problem_name = str(problem_name) if problem_name else None
        for metric_key in METRIC_TABLE_ORDER:
            self._values[metric_key].clear()
            self._curves[metric_key].setData([], [])
            self._empty_labels[metric_key].show()
        if self._algorithm_name and self._problem_name:
            self.context_label.setText(
                f"Current Main run: {self._algorithm_name} on {self._problem_name}. "
                "Charts update after each completed generation."
            )
        else:
            self.context_label.setText(
                "No Main run is active. Start a single experiment on the Main tab to populate these charts."
            )

    def is_metric_visible(self, metric_key: str) -> bool:
        # Report whether a metric chart is enabled for the current run configuration.
        return str(metric_key) in self._visible_metrics

    def append_payload(self, payload: Mapping[str, Any]) -> None:
        # Add or replace finite metric values for one completed generation.
        try:
            generation = int(payload.get("n_gen"))
        except (TypeError, ValueError):
            return
        if generation < 1:
            return
        for metric_key in METRIC_TABLE_ORDER:
            if metric_key not in self._visible_metrics:
                continue
            raw_value = payload.get(metric_key)
            if raw_value is None:
                continue
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                continue
            self._values[metric_key][generation] = value
            self._empty_labels[metric_key].hide()
            points = sorted(self._values[metric_key].items())
            self._curves[metric_key].setData(
                [point_generation for point_generation, _point_value in points],
                [point_value for _point_generation, point_value in points],
            )

    def history(self) -> dict[str, list[tuple[int, float]]]:
        # Return a detached, sorted snapshot used by tests and diagnostics.
        return {metric_key: sorted(values.items()) for metric_key, values in self._values.items()}
