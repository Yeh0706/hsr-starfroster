from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame

from qfluentwidgets import (SettingCard, SimpleCardWidget, FluentIcon as FIF, Pivot, SearchLineEdit,
                            StrongBodyLabel, CaptionLabel, BodyLabel, PushButton, PrimaryPushButton,
                            TransparentToolButton, CardWidget, InfoBar, InfoBarPosition, MessageBoxBase,
                            SubtitleLabel, IconWidget, ToolTipFilter, ToolTipPosition, themeColor)

from ..i18n import tr
from ..resources import apply_scene
from ..widgets import Page, EmptyHint, TextInputDialog, clear_layout


def tag(text, color):
    lab = CaptionLabel(text)
    lab.setStyleSheet(f"CaptionLabel{{color:{color};border:1px solid {color};border-radius:4px;padding:0 6px;}}")
    return lab


def coords(s: dict) -> str:
    return f"({s.get('x')}, {s.get('y')}, {s.get('z')})"


class SceneRow(QWidget):
    def __init__(self, page, world, scene, current: bool, parent=None):
        super().__init__(parent)
        sc = page.state.scenes
        lay = QHBoxLayout(self)
        lay.setContentsMargins(56, 10, 16, 10)
        lay.setSpacing(12)
        col = QVBoxLayout()
        col.setSpacing(2)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(StrongBodyLabel(sc.name(scene)))
        if scene.get("calyx_supported"):
            top.addWidget(tag(tr("tag_calyx"), "#3a9d6a"))
        if scene.get("is_beta"):
            top.addWidget(tag(tr("tag_beta"), "#c77d1a"))
        if current:
            ok = IconWidget(FIF.ACCEPT_MEDIUM)
            ok.setFixedSize(14, 14)
            top.addWidget(ok)
        top.addStretch(1)
        col.addLayout(top)
        desc = CaptionLabel(sc.desc(scene))
        desc.setWordWrap(True)
        col.addWidget(desc)
        extra = tr("plane", scene.get("plane_id"))
        if scene.get("is_beta") and sc.notice(scene):
            extra += " · ⚠ " + sc.notice(scene)
        meta = CaptionLabel(extra)
        meta.setWordWrap(True)
        meta.setStyleSheet("color:gray")
        col.addWidget(meta)
        lay.addLayout(col, 1)
        btn = PushButton(FIF.SEND, tr("teleport"))
        btn.clicked.connect(lambda: page.teleport(scene, sc.name(scene)))
        lay.addWidget(btn, 0, Qt.AlignVCenter)


class WorldHeader(CardWidget):
    def __init__(self, title, count, expanded, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(16)
        ic = IconWidget(FIF.GLOBE, self)
        ic.setFixedSize(18, 18)
        lay.addWidget(ic)
        col = QVBoxLayout()
        col.setSpacing(0)
        col.addStretch(1)
        col.addWidget(BodyLabel(title, self))
        col.addWidget(CaptionLabel(count, self))
        col.addStretch(1)
        lay.addLayout(col, 1)
        self.chev = IconWidget(self)
        self.chev.setFixedSize(12, 12)
        lay.addWidget(self.chev)
        self.set_expanded(expanded)

    def set_expanded(self, on):
        self.chev.setIcon(FIF.CHEVRON_DOWN_MED if on else FIF.CHEVRON_RIGHT_MED)


class WorldGroup(QWidget):
    """Collapsible world group (no animation, so the layout never leaves gaps)."""

    def __init__(self, title, count, make_rows, expanded, on_toggle, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        self.header = WorldHeader(title, count, expanded, self)
        lay.addWidget(self.header)
        self.make_rows = make_rows          # rows are built lazily on first expand
        self.body = None
        self.on_toggle = on_toggle
        self.header.clicked.connect(self.toggle)
        if expanded:
            self._build()

    def _build(self):
        self.body = SimpleCardWidget(self)
        bl = QVBoxLayout(self.body)
        bl.setContentsMargins(0, 2, 0, 2)
        bl.setSpacing(0)
        for i, r in enumerate(self.make_rows()):
            if i:
                line = QFrame(self.body)
                line.setFixedHeight(1)
                line.setStyleSheet("background:rgba(128,128,128,0.18);")
                bl.addWidget(line)
            bl.addWidget(r)
        self.layout().addWidget(self.body)

    def toggle(self):
        if self.body is None:
            self._build()
            on = True
        else:
            on = not self.body.isVisible()
        self.body.setVisible(on)
        self.header.set_expanded(on)
        self.on_toggle(on)


class FavRow(CardWidget):
    def __init__(self, page, idx: int, fav: dict, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 10, 12, 10)
        lay.setSpacing(12)
        ic = IconWidget(FIF.HEART)
        ic.setFixedSize(18, 18)
        lay.addWidget(ic)
        col = QVBoxLayout()
        col.setSpacing(0)
        col.addWidget(StrongBodyLabel(fav.get("name", "?")))
        s = fav.get("scene", {})
        col.addWidget(CaptionLabel(f"{tr('plane', s.get('plane_id'))} · {coords(s)}"))
        lay.addLayout(col, 1)
        b = PushButton(FIF.SEND, tr("teleport"))
        b.clicked.connect(lambda: page.teleport_fav(fav))
        lay.addWidget(b)
        for icon, tip, slot in ((FIF.EDIT, tr("rename"), lambda: page.rename_fav(idx)),
                                (FIF.DELETE, tr("delete"), lambda: page.delete_fav(idx))):
            t = TransparentToolButton(icon)
            t.setToolTip(tip)
            t.installEventFilter(ToolTipFilter(t, 300, ToolTipPosition.TOP))
            t.clicked.connect(slot)
            lay.addWidget(t)


class FavFirstDialog(MessageBoxBase):
    """Three choices: save favorite then teleport / teleport anyway / cancel."""

    def __init__(self, plane, parent=None):
        super().__init__(parent)
        self.choice = None
        self.viewLayout.addWidget(SubtitleLabel(tr("fav_before_title")))
        body = BodyLabel(tr("fav_before_body", plane))
        body.setWordWrap(True)
        self.viewLayout.addWidget(body)
        self.yesButton.setText(tr("fav_and_teleport"))
        self.cancelButton.setText(tr("cancel"))
        self.anyway = PushButton(tr("teleport_anyway"))
        self.buttonLayout.insertWidget(1, self.anyway, 1)
        self.anyway.clicked.connect(self._anyway)
        self.widget.setMinimumWidth(460)

    def _anyway(self):
        self.choice = "anyway"
        self.accept()

    def exec(self):
        r = super().exec()
        if r and self.choice is None:
            self.choice = "fav"
        return self.choice


class MapPage(Page):
    TABS = ("combat", "explore", "beta", "fav")

    def __init__(self, state, on_restart, on_download, parent=None):
        super().__init__("mapPage", tr("map_title"), parent)
        self.state, self.on_restart, self.on_download = state, on_restart, on_download
        self.tab = "combat"
        self.expanded: dict[tuple, bool] = {}     # (tab, world id) -> open?

        self.current = SettingCard(FIF.GLOBE, tr("map_current"), "", self.view)
        self.fav_btn = PushButton(FIF.HEART, tr("map_add_fav"), self.current)
        self.fav_btn.clicked.connect(self.fav_current)
        self.current.hBoxLayout.addWidget(self.fav_btn, 0, Qt.AlignRight)
        self.current.hBoxLayout.addSpacing(16)
        self.current.setMinimumHeight(76)
        self.add(self.current)

        # search sits in the title row, tabs get their own row
        self.search = SearchLineEdit(self.view)
        self.search.setPlaceholderText(tr("map_search"))
        self.search.setFixedWidth(260)
        from PySide6.QtCore import QTimer
        self._search_timer = QTimer(self, singleShot=True, interval=250, timeout=self.refresh_list)
        self.search.textChanged.connect(lambda _: self._search_timer.start())
        self.header.addWidget(self.search, 0, Qt.AlignVCenter)

        self.layout_.addSpacing(10)
        row = QHBoxLayout()
        self.seg = Pivot(self.view)            # 純文字＋底線的分頁（Win11 設定 App 樣式）
        for key in self.TABS:
            self.seg.addItem(key, tr("tab_" + key), lambda *_, k=key: self.set_tab(k))
        self.seg.setItemFontSize(15)
        self.seg.setCurrentItem(self.tab)
        row.addWidget(self.seg)
        row.addStretch(1)
        self.layout_.addLayout(row)
        self.layout_.addSpacing(4)

        self.host = QWidget(self.view)
        self.host_lay = QVBoxLayout(self.host)
        self.host_lay.setContentsMargins(0, 0, 0, 0)
        self.host_lay.setSpacing(6)
        self.add(self.host)
        self.layout_.addStretch(1)

        state.reloaded.connect(self.refresh)
        state.scenesChanged.connect(self.refresh)
        state.favoritesChanged.connect(self.refresh)
        state.changed.connect(self.refresh_current)
        self.refresh()

    def set_tab(self, k):
        self.tab = k
        self.refresh_list()

    # ------------------------------------------------------------ current
    def refresh_current(self):
        scene = self.state.data.get("scene") or {}
        sc = self.state.scenes
        found = sc.locate(scene)
        if found:
            w, s, d = found
            exact = d == 0 and s.get("y") == scene.get("y")
            title = f"{tr('map_current')}：{sc.name(w)} · {sc.name(s)}" + ("" if exact else " ≈")
        else:
            title = f"{tr('map_current')}：{tr('map_unknown_place')}"
        self.current.setTitle(title)
        self.current.setContent(f"{tr('plane', scene.get('plane_id', '?'))} · {coords(scene)}"
                                f" · map_layer {scene.get('map_layer', '?')}")
        self.fav_btn.setVisible(bool(scene) and not self.state.is_favorite(scene))

    def current_is_safe(self) -> bool:
        """True if the current location can be found again (listed exactly or favorited)."""
        scene = self.state.data.get("scene") or {}
        if not scene or self.state.is_favorite(scene):
            return True
        found = self.state.scenes.locate(scene)
        if not found:
            return False
        _, s, d = found
        keys = ("calyx_x", "calyx_y", "calyx_z", "calyx_group_id", "calyx_inst_id")
        return d == 0 and s.get("y") == scene.get("y") and all(s.get(k) == scene.get(k) for k in keys)

    # ------------------------------------------------------------ list
    def refresh(self):
        self.refresh_current()
        self.refresh_list()

    def refresh_list(self, *_):
        clear_layout(self.host_lay)
        sc = self.state.scenes
        if self.tab == "fav":
            favs = self.state.favorites.value
            q = self.search.text().strip().lower()
            shown = [(i, f) for i, f in enumerate(favs) if not q or q in f.get("name", "").lower()
                     or q in str(f.get("scene", {}).get("plane_id"))]
            if not shown:
                self.host_lay.addWidget(EmptyHint(tr("fav_empty")))
            for i, f in shown:
                self.host_lay.addWidget(FavRow(self, i, f))
            return
        if not sc.loaded:
            self.host_lay.addWidget(EmptyHint(tr("map_no_data")))
            b = PrimaryPushButton(FIF.DOWNLOAD, tr("map_download"))
            b.clicked.connect(self.on_download)
            self.host_lay.addWidget(b, 0, Qt.AlignHCenter)
            return
        q = self.search.text().strip().lower()
        cur = self.state.data.get("scene") or {}
        for w in sc.worlds:
            items = []
            for s in w.get("scenes", []):
                beta, calyx = s.get("is_beta"), s.get("calyx_supported")
                cat = "beta" if beta else ("combat" if calyx else "explore")
                if cat != self.tab:
                    continue
                if q and not any(q in str(v).lower() for v in (s.get("name"), s.get("name_zh"), s.get("plane_id"),
                                                               s.get("desc"), s.get("desc_zh"))):
                    continue
                items.append(s)
            if not items:
                continue
            def make_rows(w=w, items=items):
                return [SceneRow(self, w, s, s.get("plane_id") == cur.get("plane_id") and s.get("x") == cur.get("x")
                                 and s.get("z") == cur.get("z")) for s in items]
            key = (self.tab, w.get("id"))
            # 預設全部收起；搜尋時全部展開
            expanded = True if q else self.expanded.get(key, False)
            group = WorldGroup(sc.name(w), tr("map_count", len(items)), make_rows, expanded,
                               lambda on, k=key: self.expanded.__setitem__(k, on), self.host)
            self.host_lay.addWidget(group)
        if not self.host_lay.count():
            self.host_lay.addWidget(EmptyHint("—"))

    # ------------------------------------------------------------ actions
    def teleport(self, record: dict, name: str):
        if not self.current_is_safe():
            choice = FavFirstDialog((self.state.data.get("scene") or {}).get("plane_id"), self.window()).exec()
            if not choice:
                return
            if choice == "fav" and not self.fav_current():
                return
        self.state.data["scene"] = apply_scene(self.state.data.get("scene"), record)
        self.state.mark_changed()
        self.refresh_list()
        bar = InfoBar.success(tr("done"), tr("teleported", name), duration=8000, parent=self.window(),
                              position=InfoBarPosition.TOP)
        b = PrimaryPushButton(tr("restart_now"))
        b.clicked.connect(lambda: (bar.close(), self.on_restart()))
        bar.addWidget(b)

    def teleport_fav(self, fav: dict):
        rec = dict(fav.get("scene", {}))
        self.teleport(rec, fav.get("name", "?"))

    def fav_current(self) -> bool:
        scene = self.state.data.get("scene") or {}
        if not scene:
            return False
        sc = self.state.scenes
        found = sc.locate(scene)
        default = f"{sc.name(found[1])} ({scene.get('plane_id')})" if found else \
            tr("fav_default_name", scene.get("plane_id"))
        d = TextInputDialog(tr("fav_name_title"), default, "", self.window())
        if not d.exec():
            return False
        self.state.add_favorite(d.value().strip() or default, scene)
        InfoBar.success(tr("fav_added"), d.value().strip() or default, duration=2500, parent=self.window(),
                        position=InfoBarPosition.TOP)
        return True

    def rename_fav(self, idx):
        f = self.state.favorites.value[idx]
        d = TextInputDialog(tr("fav_name_title"), f.get("name", ""), "", self.window())
        if d.exec() and d.value().strip():
            f["name"] = d.value().strip()
            self.state.save_favorites()

    def delete_fav(self, idx):
        self.state.favorites.value.pop(idx)
        self.state.save_favorites()
