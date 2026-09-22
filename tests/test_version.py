from PyQt5.QtWidgets import QApplication

from pymoo_gui import __version__
from pymoo_gui.app import APPLICATION_NAME, APPLICATION_TITLE, MainWindow


def test_public_version_and_window_title() -> None:
    app = QApplication.instance() or QApplication([])
    assert __version__ == "0.1"
    assert APPLICATION_NAME == "AGtest-framework"
    assert APPLICATION_TITLE == "AGtest-framework v0.1"

    window = MainWindow()
    try:
        assert window.windowTitle() == APPLICATION_TITLE
    finally:
        window.close()
    assert app is QApplication.instance()
