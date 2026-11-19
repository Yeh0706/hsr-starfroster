from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def main():
    from .core import Settings
    from . import i18n

    settings = Settings()
    i18n.set_language(settings["language"])

    try:   # own taskbar entry/icon instead of grouping under python.exe
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Starfroster.Editor")
    except Exception:
        pass

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("Starfroster")
    from pathlib import Path
    from PySide6.QtGui import QIcon
    icon = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    from qfluentwidgets import setTheme, Theme, setThemeColor   # 字型一律用預設的 Segoe UI＋微軟雅黑
    setTheme({"auto": Theme.AUTO, "light": Theme.LIGHT, "dark": Theme.DARK}.get(settings["theme"], Theme.AUTO))
    try:
        from qframelesswindow.utils import getSystemAccentColor
        c = getSystemAccentColor()
        if c.isValid():
            setThemeColor(c)
    except Exception:
        pass

    from .state import AppState
    from .main_window import MainWindow
    state = AppState(settings)
    w = MainWindow(state)
    w.show()
    snap = os.environ.get("PPSR_EDITOR_SNAPSHOT")      # self-test: screenshot then quit
    if snap:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(8000, lambda: (w.grab().save(snap), app.quit()))
    return app.exec()
