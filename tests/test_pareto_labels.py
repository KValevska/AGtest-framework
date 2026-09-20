from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "pymoo_gui_mpl_cache"))

import numpy as np
from PyQt5.QtWidgets import QApplication

from pymoo_gui.viz.pareto_dialogs import UnifiedParetoWidget


def test_pareto_reference_layer_label_does_not_use_known() -> None:
    app = QApplication.instance() or QApplication([])
    widgets = [UnifiedParetoWidget(np.zeros((1, n_obj))) for n_obj in (1, 2, 3)]

    assert app is not None
    assert all(widget._dialog.ref_label == "Pareto front" for widget in widgets)
    for widget in widgets:
        widget.close()
