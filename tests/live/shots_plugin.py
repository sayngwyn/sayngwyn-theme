"""Test-only MO2 plugin: screenshots the theme, then closes MO2.

tests/live/run_shots.py copies this into the test MO2's plugins folder,
starts MO2, and removes it afterwards. Never shipped.
"""

import os
from pathlib import Path

import mobase
from PyQt6.QtCore import QTimer, qWarning
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

OUT = Path(os.environ.get("SAYNGWYN_SHOTS", str(Path(__file__).resolve().parents[2] / "shots")))


class Shots(mobase.IPlugin):
    def __init__(self) -> None:
        super().__init__()
        self._window: QMainWindow | None = None
        self._steps: list = []

    def init(self, organizer: mobase.IOrganizer) -> bool:
        organizer.onUserInterfaceInitialized(self._ready)
        return True

    def name(self) -> str:
        return "sayngwyn theme shots"

    def author(self) -> str:
        return "sayngwyn"

    def description(self) -> str:
        return "Test only."

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(0, 1, 0)

    def settings(self) -> list[mobase.PluginSetting]:
        return []

    # ------------------------------------------------------------------

    def _ready(self, window: QMainWindow) -> None:
        try:
            OUT.mkdir(parents=True, exist_ok=True)
            self._window = window
            window.showNormal()
            # logical size; at QT_SCALE_FACTOR=2 the shots come out at twice this in pixels
            w, h = (int(v) for v in os.environ.get("SAYNGWYN_SIZE", "1600x900").split("x"))
            window.resize(w, h)
            # an even split, so the program picker beside Run has room for its name
            from PyQt6.QtWidgets import QSplitter
            split = window.findChild(QSplitter, "splitter")
            if split is not None:
                split.setSizes([w // 2, w - w // 2])
            # MO2's log shows folder paths: keep it out of every shot.
            from PyQt6.QtWidgets import QDockWidget
            log = window.findChild(QDockWidget, "logDock")
            if log is not None:
                log.hide()
            self._steps = [
                lambda: self._grab(window, "main-plugins"),
                lambda: self._select_mod(os.environ.get("SAYNGWYN_SELECT", "Lighting Overhaul"),
                                         "main-selected-conflict"),
                lambda: self._tab("dataTab", "main-data"),
                lambda: self._tab("downloadTab", "main-downloads"),
                lambda: self._tab("espTab", None),
                lambda: self._dialog("actionSettings", "settings", tabs=True),
                lambda: self._dialog("actionModify_Executables", "executables"),
                lambda: self._dialog("actionAdd_Profile", "profiles"),
                self._quit,
            ]
            QTimer.singleShot(3000, self._next)
        except Exception as e:  # noqa: BLE001
            qWarning(f"shots: {e!r}")

    def _next(self) -> None:
        if not self._steps:
            return
        step = self._steps.pop(0)
        try:
            step()
        except Exception as e:  # noqa: BLE001
            qWarning(f"shots step failed: {e!r}")
            QTimer.singleShot(500, self._next)

    def _grab(self, widget: QWidget, name: str) -> None:
        widget.grab().save(str(OUT / f"{name}.png"))
        if name == "main-plugins":
            self._dump_geometry(widget)
        QTimer.singleShot(800, self._next)

    def _dump_geometry(self, window: QWidget) -> None:
        """Record where the Run area's widgets sit, for alignment checks."""
        import json

        out = {}
        for name in ("executablesListBox", "startButton", "linkButton"):
            w = window.findChild(QWidget, name)
            if w is not None:
                top_left = w.mapTo(window, w.rect().topLeft())
                out[name] = {"x": top_left.x(), "y": top_left.y(),
                             "w": w.width(), "h": w.height()}
        (OUT / "geometry.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    def _select_mod(self, mod: str, shot: str) -> None:
        """Select a mod that conflicts, so MO2 highlights the mods it overwrites."""
        from PyQt6.QtCore import QItemSelectionModel, Qt
        from PyQt6.QtWidgets import QTreeView

        assert self._window is not None
        view = self._window.findChild(QTreeView, "modList")
        if view is not None:
            # as if clicked: MO2 colours the overwrite rows for the focused list's selection
            self._window.activateWindow()
            view.setFocus()
            # the real mouse may sit over the window: no hover tint in a shot
            from PyQt6.QtCore import Qt as _Qt
            view.viewport().setAttribute(_Qt.WidgetAttribute.WA_Hover, False)
            model = view.model()
            hits = model.match(model.index(0, 0), Qt.ItemDataRole.DisplayRole, mod, 1,
                               Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive)
            if hits:
                view.expandAll()  # every separator open, so the demo list shows in full
                view.selectionModel().setCurrentIndex(
                    hits[0], QItemSelectionModel.SelectionFlag.ClearAndSelect
                    | QItemSelectionModel.SelectionFlag.Rows)
                view.scrollTo(hits[0], QTreeView.ScrollHint.PositionAtCenter)
                view.horizontalScrollBar().setValue(0)  # scrollTo also scrolls sideways
        # MO2 works out the overwrite highlights after the selection; give it time to repaint
        QTimer.singleShot(2500, lambda: self._grab(self._window, shot))

    def _tab(self, tab_name: str, shot: str | None) -> None:
        assert self._window is not None
        for tabs in self._window.findChildren(QTabWidget):
            page = tabs.findChild(QWidget, tab_name)
            if page is not None and tabs.indexOf(page) >= 0:
                tabs.setCurrentWidget(page)
                break
        if shot:
            QTimer.singleShot(1200, lambda: self._grab(self._window, shot))
        else:
            QTimer.singleShot(300, self._next)

    def _dialog(self, action_name: str, shot: str, tabs: bool = False) -> None:
        """Open a modal dialog; timers are set before it blocks."""
        assert self._window is not None
        from PyQt6.QtGui import QAction

        action = self._window.findChild(QAction, action_name)
        if action is None:
            qWarning(f"shots: no action {action_name}")
            QTimer.singleShot(300, self._next)
            return

        def capture() -> None:
            try:
                dlg = QApplication.activeModalWidget()
                if dlg is None:
                    qWarning(f"shots: no dialog for {action_name}")
                    return
                dlg.grab().save(str(OUT / f"{shot}.png"))
                if tabs:
                    t = dlg.findChild(QTabWidget)
                    if t is not None:
                        for i in range(1, t.count()):
                            t.setCurrentIndex(i)
                            QApplication.processEvents()
                            dlg.grab().save(str(OUT / f"{shot}-{i}.png"))
                dlg.close()
            except Exception as e:  # noqa: BLE001
                qWarning(f"shots capture failed: {e!r}")
            QTimer.singleShot(800, self._next)

        QTimer.singleShot(1500, capture)
        action.trigger()

    def _quit(self) -> None:
        assert self._window is not None
        self._window.close()


def createPlugin() -> mobase.IPlugin:
    return Shots()
