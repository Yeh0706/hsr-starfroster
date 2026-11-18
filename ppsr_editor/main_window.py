from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QFileSystemWatcher, Signal, QObject, QProcess
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QPainter, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication

from qfluentwidgets import (FluentWindow, FluentIcon as FIF, NavigationItemPosition, CardWidget, BodyLabel,
                            PushButton, PrimaryPushButton, InfoBar, InfoBarPosition, MessageBox, CaptionLabel,
                            TransparentPushButton, IconWidget, InfoBarIcon, StateToolTip, MessageBoxBase,
                            SubtitleLabel, isDarkTheme)

from . import ppsr
from .i18n import tr
from .resources import update_characters, update_scenes
from .pages.lineup import LineupPage
from .pages.appearance import AppearancePage
from .pages.maps import MapPage
from .pages.advanced import AdvancedPage
from .pages.settings_page import SettingsPage


class Bridge(QObject):
    """Runs blocking work in a thread and calls back on the GUI thread."""
    done = Signal(object, object, object, object)

    def __init__(self):
        super().__init__()
        self.pool = ThreadPoolExecutor(max_workers=3)
        self.done.connect(lambda ok, err, res, cb: cb(ok, res if ok else err), Qt.QueuedConnection)

    def run(self, fn, callback):
        def job():
            try:
                self.done.emit(True, None, fn(), callback)
            except Exception as e:
                self.done.emit(False, e, None, callback)
        self.pool.submit(job)


class StatusDot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.on = False
        self.setFixedSize(10, 10)

    def set_on(self, on):
        self.on = on
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#3fb950") if self.on else QColor("#8b8b8b"))
        p.drawEllipse(self.rect())


class SaveBar(CardWidget):
    def __init__(self, parent):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 12, 10)
        lay.setSpacing(10)
        ic = IconWidget(InfoBarIcon.WARNING, self)
        ic.setFixedSize(18, 18)
        lay.addWidget(ic)
        lay.addWidget(BodyLabel(tr("unsaved"), self), 1)
        self.discard = PushButton(tr("discard"), self)
        self.save = PrimaryPushButton(FIF.SAVE, tr("save") + "  (Ctrl+S)", self)
        lay.addWidget(self.discard)
        lay.addWidget(self.save)
        self.setFixedSize(520, 58)
        self.setBackgroundColor(QColor(43, 43, 43) if isDarkTheme() else QColor(251, 251, 251))


class CloseDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.choice = None
        self.viewLayout.addWidget(SubtitleLabel(tr("unsaved")))
        self.yesButton.setText(tr("save"))
        self.cancelButton.setText(tr("cancel"))
        self.no = PushButton(tr("discard"))
        self.buttonLayout.insertWidget(1, self.no, 1)
        self.no.clicked.connect(lambda: (setattr(self, "choice", "discard"), self.accept()))
        self.widget.setMinimumWidth(380)

    def exec(self):
        r = super().exec()
        if r and self.choice is None:
            self.choice = "save"
        return self.choice


class MainWindow(FluentWindow):
    ppsrStatus = Signal(bool)

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.bridge = Bridge()
        self.setWindowTitle(tr("app_title"))
        icon = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
        self.setWindowIcon(QIcon(str(icon)) if icon.exists() else FIF.GAME.icon())
        self.resize(1180, 800)
        self.setMinimumSize(900, 600)

        self.lineup = LineupPage(state, self)
        self.appearance = AppearancePage(state, self)
        self.maps = MapPage(state, self.restart_ppsr, lambda: self.update_maps(manual=True), self)
        self.advanced = AdvancedPage(state, self)
        self.settings = SettingsPage(state, lambda: self.update_maps(manual=True),
                                     lambda: self.update_chars(manual=True), self.relaunch, self)
        self.addSubInterface(self.lineup, FIF.PEOPLE, tr("nav_lineup"))
        self.addSubInterface(self.appearance, FIF.PALETTE, tr("nav_appearance"))
        self.addSubInterface(self.maps, FIF.GLOBE, tr("nav_map"))
        self.addSubInterface(self.advanced, FIF.DEVELOPER_TOOLS, tr("nav_advanced"))
        self.addSubInterface(self.settings, FIF.SETTING, tr("nav_settings"), NavigationItemPosition.BOTTOM)
        self.navigationInterface.setExpandWidth(220)

        # title bar: ppsr status + restart
        tb = QWidget(self.titleBar)
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(0, 0, 12, 0)
        tl.setSpacing(8)
        self.dot = StatusDot(tb)
        self.status_lbl = CaptionLabel(tr("ppsr_stopped"), tb)
        self.restart_btn = TransparentPushButton(FIF.SYNC, tr("ppsr_restart"), tb)
        self.restart_btn.clicked.connect(self.restart_ppsr)
        tl.addWidget(self.dot)
        tl.addWidget(self.status_lbl)
        tl.addWidget(self.restart_btn)
        lay = self.titleBar.hBoxLayout
        idx = lay.indexOf(self.titleBar.minBtn)
        lay.insertWidget(idx if idx >= 0 else lay.count() - 1, tb, 0, Qt.AlignVCenter)

        # save bar
        self.savebar = SaveBar(self)
        self.savebar.save.clicked.connect(self.save)
        self.savebar.discard.clicked.connect(self.discard)
        self.savebar.hide()
        QShortcut(QKeySequence.Save, self, activated=self.save)

        state.changed.connect(self.on_changed)

        # file watching
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(lambda _: self.watch_timer.start())
        self.watch_timer = QTimer(self, singleShot=True, interval=400, timeout=self.check_external)
        self.rewatch()

        # ppsr status polling
        self.ppsrStatus.connect(self.set_ppsr_status)
        self.poll = QTimer(self, interval=3000, timeout=self.poll_ppsr)
        self.poll.start()
        self.poll_ppsr()

        QTimer.singleShot(300, self.startup)

    # ------------------------------------------------------------ startup / data updates
    def startup(self):
        from .i18n import PATHS
        for p in PATHS:                       # prefetch the small path glyphs used in combo boxes
            self.state.icons.get(self.state.catalog.path_rel(p))
        s = self.state.settings
        if not s["configured"] and not os.environ.get("PPSR_EDITOR_MISC"):
            if self.first_run():
                return
        if self.state.load_error:
            InfoBar.error(tr("error"), tr("missing_persistent") if self.state.load_error == "missing"
                          else self.state.load_error, duration=-1, parent=self, position=InfoBarPosition.TOP)
            self.switchTo(self.settings)
        if not self.state.catalog.meta:
            self.update_chars(manual=False)
        if not self.state.scenes.loaded:
            self.update_maps(manual=False)
        if not os.environ.get("PPSR_EDITOR_NO_UPDATE_CHECK"):
            QTimer.singleShot(1500, lambda: self.check_app_update(manual=False))

    # ------------------------------------------------------------ app update (notify only)
    def check_app_update(self, manual=True):
        from . import updater

        def done(ok, res):
            if not ok:
                if manual:
                    InfoBar.error(tr("app_update_failed"), str(res), duration=5000, parent=self,
                                  position=InfoBarPosition.TOP)
                return
            if not res["newer"]:
                if manual:
                    InfoBar.success(tr("up_to_date"), tr("app_version_now", updater.__version__), duration=3000,
                                    parent=self, position=InfoBarPosition.TOP)
                return
            notes = res["notes"]
            if len(notes) > 600:
                notes = notes[:600].rstrip() + "…"
            box = MessageBox(tr("app_update_title", res["version"]),
                             tr("app_update_body", updater.__version__, res["version"]) + ("\n\n" + notes if notes else ""),
                             self)
            box.yesButton.setText(tr("app_update_download"))
            box.cancelButton.setText(tr("later"))
            if box.exec():
                from PySide6.QtCore import QUrl
                from PySide6.QtGui import QDesktopServices
                QDesktopServices.openUrl(QUrl(res["url"]))
        self.bridge.run(updater.check_latest, done)

    def first_run(self) -> bool:
        """First launch: ask for persistent.json. Returns True if the editor is relaunching."""
        from .pages.settings_page import pick_persistent
        box = MessageBox(tr("first_run_title"), tr("first_run_body"), self)
        box.yesButton.setText(tr("choose_file"))
        box.cancelButton.setText(tr("cancel"))
        if not box.exec():
            return False
        d = pick_persistent(self, str(self.state.paths.misc))
        if not d:
            return False
        s = self.state.settings
        s["configured"] = True
        if os.path.normcase(os.path.abspath(d)) == os.path.normcase(os.path.abspath(str(self.state.paths.misc))) \
                and not self.state.load_error:
            return False                       # same file already loaded
        s["misc_path"] = d
        self.relaunch()
        return True

    def _tip(self, title):
        tip = StateToolTip(title, tr("downloading"), self)
        tip.move(self.width() - tip.width() - 24, 56)
        tip.show()
        return tip

    def update_chars(self, manual=True):
        tip = self._tip(tr("char_data"))

        def done(ok, res):
            if ok:
                ver, changed = res
                self.state.catalog.reload_remote()
                self.state.catalogChanged.emit()
                tip.setContent(tr("updated") if changed else tr("up_to_date"))
            else:
                tip.setContent(f"{tr('download_failed')}: {res}")
            tip.setState(True)
        self.bridge.run(lambda: update_characters(self.state.paths), done)

    def update_maps(self, manual=True):
        tip = self._tip(tr("map_data"))

        def done(ok, res):
            if ok:
                ver, changed = res
                self.state.scenes.reload()
                self.state.scenesChanged.emit()
                tip.setContent(tr("updated") if changed else tr("up_to_date"))
            else:
                tip.setContent(f"{tr('download_failed')}: {res}")
            tip.setState(True)
        self.bridge.run(lambda: update_scenes(self.state.paths), done)

    # ------------------------------------------------------------ save / dirty
    def on_changed(self):
        dirty = self.state.dirty
        self.savebar.setVisible(dirty)
        self.place_savebar()
        self.setWindowTitle(("● " if dirty else "") + tr("app_title"))

    def place_savebar(self):
        bar = getattr(self, "savebar", None)
        if bar is not None and bar.isVisible():
            x0 = self.navigationInterface.width()
            w = self.width() - x0
            self.savebar.move(x0 + (w - self.savebar.width()) // 2, self.height() - self.savebar.height() - 18)
            self.savebar.raise_()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.place_savebar()

    def save(self) -> bool:
        if not self.state.dirty or self.state.load_error:
            return True
        try:
            self.watcher.removePaths(self.watcher.files())
            self.state.save()
        except Exception as e:
            InfoBar.error(tr("save_failed"), str(e), duration=-1, parent=self, position=InfoBarPosition.TOP)
            return False
        finally:
            self.rewatch()
        InfoBar.success(tr("saved"), str(self.state.paths.persistent), duration=2500, parent=self,
                        position=InfoBarPosition.TOP)
        return True

    def discard(self):
        self.state.revert()

    # ------------------------------------------------------------ external changes
    def rewatch(self):
        p = str(self.state.paths.persistent)
        if self.state.paths.persistent.exists() and p not in self.watcher.files():
            self.watcher.addPath(p)

    def check_external(self):
        self.rewatch()
        if not self.state.pf.changed_on_disk():
            return
        if not self.state.dirty:
            self.state.load()
            InfoBar.info(tr("file_changed_title"), tr("file_reloaded"), duration=4000, parent=self,
                         position=InfoBarPosition.TOP)
            return
        box = MessageBox(tr("file_changed_title"), tr("file_changed_body"), self)
        box.yesButton.setText(tr("reload"))
        box.cancelButton.setText(tr("keep_mine"))
        if box.exec():
            self.state.load()
        else:
            # keep editing; next save overwrites the external change
            self.state.pf.digest = __import__("hashlib").sha1(self.state.paths.persistent.read_bytes()).hexdigest()

    # ------------------------------------------------------------ ppsr
    def poll_ppsr(self):
        self.bridge.pool.submit(lambda: self.ppsrStatus.emit(ppsr.is_running()))

    def set_ppsr_status(self, on):
        self.dot.set_on(on)
        self.status_lbl.setText(tr("ppsr_running") if on else tr("ppsr_stopped"))

    def restart_ppsr(self):
        exe = self.state.paths.ppsr_exe
        if not exe.exists():
            InfoBar.error(tr("ppsr_restart_failed"), tr("ppsr_not_found", exe), duration=6000, parent=self,
                          position=InfoBarPosition.TOP)
            return
        if self.state.dirty:
            box = MessageBox(tr("ppsr_unsaved_title"), tr("ppsr_unsaved_body"), self)
            box.yesButton.setText(tr("save_and_restart"))
            box.cancelButton.setText(tr("cancel"))
            if not box.exec() or not self.save():
                return
        else:
            box = MessageBox(tr("ppsr_restart_title"), tr("ppsr_restart_body"), self)
            box.yesButton.setText(tr("ppsr_restart"))
            box.cancelButton.setText(tr("cancel"))
            if not box.exec():
                return
        self.restart_btn.setEnabled(False)

        def done(ok, res):
            self.restart_btn.setEnabled(True)
            self.poll_ppsr()
            if ok:
                InfoBar.success(tr("done"), tr("ppsr_restarted"), duration=5000, parent=self,
                                position=InfoBarPosition.TOP)
            else:
                InfoBar.error(tr("ppsr_restart_failed"), str(res), duration=-1, parent=self,
                              position=InfoBarPosition.TOP)
        self.bridge.run(lambda: ppsr.restart(exe), done)

    # ------------------------------------------------------------ misc
    def relaunch(self):
        if self.confirm_close():
            if getattr(sys, "frozen", False):      # packaged exe: just start it again
                QProcess.startDetached(sys.executable, sys.argv[1:])
            else:                                  # python <script>.pyw ...
                QProcess.startDetached(sys.executable, sys.argv)
            self._force_close = True
            QApplication.quit()

    def confirm_close(self) -> bool:
        if not self.state.dirty or getattr(self, "_force_close", False):
            return True
        c = CloseDialog(self).exec()
        if c == "save":
            return self.save()
        return c == "discard"

    def closeEvent(self, e):
        if self.confirm_close():
            self.bridge.pool.shutdown(wait=False, cancel_futures=True)
            self.state.icons.pool.shutdown(wait=False, cancel_futures=True)
            e.accept()
        else:
            e.ignore()
