from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QSize, Signal, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView,
                               QFrame)

from qfluentwidgets import (CardWidget, StrongBodyLabel, CaptionLabel, BodyLabel, TransparentToolButton,
                            FluentIcon as FIF, PrimaryPushButton, RoundMenu, Action, IconWidget, InfoBarIcon,
                            ToolTipFilter, ToolTipPosition, SearchLineEdit, ComboBox, CheckBox, MessageBoxBase,
                            SubtitleLabel, FlowLayout, SmoothScrollArea, InfoBar, themeColor, isDarkTheme,
                            ListWidget)

from .. import i18n
from ..i18n import tr
from ..widgets import Page, NetIcon, EmptyHint, TextInputDialog, tinted_icon

ROW_H = 72


class LineupRow(CardWidget):
    moveRequested = Signal(int, int)
    removeRequested = Signal(int)
    renameRequested = Signal(int)

    def __init__(self, state, index: int, aid: int, count: int, parent=None):
        super().__init__(parent)
        self.index, self.aid = index, aid
        cat = state.catalog
        a = cat.by_id.get(aid, {})
        self.setFixedHeight(ROW_H - 6)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 8, 10, 8)
        lay.setSpacing(12)

        grip = IconWidget(FIF.MENU, self)
        grip.setFixedSize(14, 14)
        grip.setToolTip(tr("lineup_hint"))
        lay.addWidget(grip)
        num = BodyLabel(str(index + 1), self)
        num.setFixedWidth(18)
        num.setAlignment(Qt.AlignCenter)
        lay.addWidget(num)
        lay.addWidget(NetIcon(state.icons, cat.icon_rel(aid), 44, round_=True, parent=self,
                              fallback_text=cat.name(aid)))

        col = QVBoxLayout()
        col.setSpacing(0)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(StrongBodyLabel(cat.name(aid), self))
        if not a.get("owned", False):
            warn = IconWidget(InfoBarIcon.WARNING, self)
            warn.setFixedSize(16, 16)
            warn.setToolTip(tr("not_owned"))
            warn.installEventFilter(ToolTipFilter(warn, 200, ToolTipPosition.TOP))
            top.addWidget(warn)
        top.addStretch(1)
        col.addLayout(top)
        col.addWidget(CaptionLabel(cat.subtitle(aid), self))
        lay.addLayout(col, 1)

        for icon, tip, enabled, slot in (
                (FIF.UP, tr("move_up"), index > 0, lambda: self.moveRequested.emit(self.index, -1)),
                (FIF.DOWN, tr("move_down"), index < count - 1, lambda: self.moveRequested.emit(self.index, 1)),
                (FIF.DELETE, tr("remove"), True, lambda: self.removeRequested.emit(self.index))):
            b = TransparentToolButton(icon, self)
            b.setToolTip(tip)
            b.installEventFilter(ToolTipFilter(b, 300, ToolTipPosition.TOP))
            b.setEnabled(enabled)
            b.clicked.connect(slot)
            lay.addWidget(b)

    def contextMenuEvent(self, e):
        m = RoundMenu(parent=self)
        a2 = Action(FIF.EDIT, tr("rename"))
        a2.triggered.connect(lambda: self.renameRequested.emit(self.aid))
        a3 = Action(FIF.DELETE, tr("remove"))
        a3.triggered.connect(lambda: self.removeRequested.emit(self.index))
        m.addAction(a2)
        m.addSeparator()
        m.addAction(a3)
        m.exec(e.globalPos())


class DragList(QListWidget):
    reordered = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDropIndicatorShown(False)          # we draw our own accent line
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setSpacing(0)
        self.setResizeMode(QListWidget.Adjust)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("QListWidget{background:transparent;border:none;outline:none;}"
                           "QListWidget::item{background:transparent;border:none;}"
                           "QListWidget::item:selected,QListWidget::item:hover{background:transparent;border:none;}")

    def startDrag(self, actions):
        """Drag a translucent snapshot of the card; the original fades while it moves."""
        from PySide6.QtGui import QDrag, QPixmap
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        it = self.currentItem()
        row = self.itemWidget(it) if it else None
        if row is None:
            return super().startDrag(actions)
        snap = row.grab()
        pm = QPixmap(snap.size())
        pm.setDevicePixelRatio(snap.devicePixelRatio())
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setOpacity(0.85)
        p.drawPixmap(0, 0, snap)
        p.end()
        drag = QDrag(self)
        drag.setMimeData(self.model().mimeData(self.selectedIndexes()))
        drag.setPixmap(pm)
        drag.setHotSpot(row.mapFromGlobal(self.cursor().pos()))
        fx = QGraphicsOpacityEffect(row)
        fx.setOpacity(0.3)
        row.setGraphicsEffect(fx)
        try:
            drag.exec(Qt.MoveAction)
        finally:
            try:
                row.setGraphicsEffect(None)
            except RuntimeError:       # row already rebuilt
                pass

    def paintEvent(self, e):
        super().paintEvent(e)
        # accent line where the card will land
        if self.state() == QAbstractItemView.DraggingState and self._drop_y is not None:
            p = QPainter(self.viewport())
            p.setRenderHint(QPainter.Antialiasing)
            p.setPen(Qt.NoPen)
            p.setBrush(themeColor())
            p.drawRoundedRect(8, self._drop_y - 2, self.viewport().width() - 16, 4, 2, 2)

    _drop_y = None

    def dragMoveEvent(self, e):
        super().dragMoveEvent(e)
        y = e.position().toPoint().y()
        row = min(max(0, round(y / ROW_H)), self.count())
        self._drop_y = min(row * ROW_H, self.count() * ROW_H - 2) if self.count() else None
        self.viewport().update()

    def dragLeaveEvent(self, e):
        self._drop_y = None
        super().dragLeaveEvent(e)
        self.viewport().update()

    def dropEvent(self, e):
        self._drop_y = None
        super().dropEvent(e)
        ids = [self.item(i).data(Qt.UserRole) for i in range(self.count())]
        QTimer.singleShot(0, lambda: self.reordered.emit(ids))


class LineupPage(Page):
    def __init__(self, state, parent=None):
        super().__init__("lineupPage", tr("lineup_title"), parent)
        self.state = state
        self.count = CaptionLabel("")
        self.header.insertWidget(1, self.count, 0, Qt.AlignBottom)
        self.header.insertSpacing(1, 8)
        add = PrimaryPushButton(FIF.ADD, tr("lineup_add"))
        add.clicked.connect(self.open_picker)
        self.header.addWidget(add)
        self.add(CaptionLabel(tr("lineup_hint")))
        self.list = DragList(self.view)
        self.list.reordered.connect(self.on_reordered)
        self.add(self.list)
        self.empty = self.add(EmptyHint(tr("lineup_empty")))
        self.layout_.addStretch(1)
        state.reloaded.connect(self.refresh)
        state.lineupChanged.connect(self.refresh)
        state.namesChanged.connect(self.refresh)
        state.catalogChanged.connect(self.refresh)
        self.refresh()

    def refresh(self):
        L = self.state.lineup
        self.list.clear()
        for i, aid in enumerate(L):
            it = QListWidgetItem()
            it.setData(Qt.UserRole, aid)
            it.setSizeHint(QSize(100, ROW_H))
            self.list.addItem(it)
            row = LineupRow(self.state, i, aid, len(L))
            row.moveRequested.connect(self.move)
            row.removeRequested.connect(self.remove)
            row.renameRequested.connect(self.rename)
            self.list.setItemWidget(it, row)
        self.list.setFixedHeight(max(1, len(L) * ROW_H + 2 * self.list.frameWidth() + 2))
        self.list.setVisible(bool(L))
        self.empty.setVisible(not L)
        self.count.setText(tr("lineup_count", len(L)))

    def commit(self):
        self.state.mark_changed()
        self.refresh()

    def move(self, i, d):
        L = self.state.lineup
        j = i + d
        if 0 <= j < len(L):
            L[i], L[j] = L[j], L[i]
            self.commit()

    def move_to(self, i, j):
        L = self.state.lineup
        L.insert(j, L.pop(i))
        self.commit()

    def remove(self, i):
        self.state.lineup.pop(i)
        self.commit()

    def on_reordered(self, ids):
        if ids != self.state.lineup and sorted(ids) == sorted(self.state.lineup):
            self.state.lineup[:] = ids
            self.state.mark_changed()
        self.refresh()

    def rename(self, aid):
        d = TextInputDialog(tr("rename_title"), self.state.names.value.get(str(aid), ""),
                            f"{self.state.catalog.default_name(aid)} · {tr('rename_hint')}", self.window())
        if d.exec():
            self.state.set_custom_name(aid, d.value())

    def open_picker(self):
        d = PickerDialog(self.state, self.window())
        if d.exec():
            if d.selected:            # 同一角色可以重複加入
                self.state.lineup.extend(d.selected)
                self.commit()


# ---------------------------------------------------------------- picker

class PickerTile(CardWidget):
    toggled = Signal(int, bool)

    def __init__(self, state, a: dict, pos: int, parent=None):
        super().__init__(parent)
        self.aid, self.pos, self.checked = a["id"], pos, False
        cat = state.catalog
        self.setFixedSize(116, 160)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 6)
        lay.setSpacing(4)
        icon = NetIcon(state.icons, cat.icon_rel(a["id"], big=True), 100, radius=8, parent=self,
                       fallback_text=cat.name(a["id"]), height=106, top=True)
        icon.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(icon, 0, Qt.AlignHCenter)
        name = CaptionLabel(cat.name(a["id"]), self)
        name.setAlignment(Qt.AlignCenter)
        name.setWordWrap(False)
        f = name.font()
        f.setBold(True)
        name.setFont(f)
        lay.addWidget(name)
        sub = CaptionLabel(tr("in_lineup", pos + 1) if pos >= 0 else f"{a['id']} · {'★' * a['rarity']}", self)
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color:gray;")
        lay.addWidget(sub)
        self.el = QColor(i18n.ELEMENT_COLORS.get(a["element"], "#888"))
        tip = f"{cat.name(a['id'])}\n{cat.subtitle(a['id'])}"
        if not a["owned"]:
            tip += "\n⚠ " + tr("not_owned")
            self.setStyleSheet("PickerTile{opacity:0.6}")
        self.setToolTip(tip)
        self.installEventFilter(ToolTipFilter(self, 500, ToolTipPosition.TOP))
        self.clicked.connect(self.toggle)

    def toggle(self):
        self.checked = not self.checked
        self.update()
        self.toggled.emit(self.aid, self.checked)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self.checked:
            p.setPen(QPen(themeColor(), 2.5))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(self.rect().adjusted(1, 1, -2, -2), 8, 8)
            p.setPen(Qt.NoPen)
            p.setBrush(themeColor())
            p.drawEllipse(self.width() - 30, 8, 22, 22)
            p.setPen(QPen(QColor("white"), 2))
            x, y = self.width() - 30, 8
            p.drawPolyline([QPointF(x + 6, y + 11), QPointF(x + 10, y + 15), QPointF(x + 16, y + 7)])


class PickerDialog(MessageBoxBase):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.selected: list[int] = []
        self.viewLayout.addWidget(SubtitleLabel(tr("picker_title")))

        row = QHBoxLayout()
        self.search = SearchLineEdit()
        self.search.setPlaceholderText(tr("picker_search"))
        self._search_timer = QTimer(self, singleShot=True, interval=250, timeout=self.rebuild)
        self.search.textChanged.connect(lambda _: self._search_timer.start())
        row.addWidget(self.search, 2)
        self.fel = ComboBox()
        self.fel.addItem(tr("all_elements"), userData="")
        for el in i18n.ELEMENTS:
            self.fel.addItem(i18n.element_name(el), userData=el)
        self.fpath = ComboBox()
        self.fpath.addItem(tr("all_paths"), userData="")
        for p in i18n.PATHS:
            ic = tinted_icon(state.icons, state.catalog.path_rel(p))
            if ic is not None:
                self.fpath.addItem(i18n.path_name(p), ic, userData=p)
            else:
                self.fpath.addItem(i18n.path_name(p), userData=p)
        self.frar = ComboBox()
        for t, v in ((tr("all_rarity"), 0), ("★★★★★", 5), ("★★★★", 4)):
            self.frar.addItem(t, userData=v)
        for c in (self.fel, self.fpath, self.frar):
            c.currentIndexChanged.connect(self.rebuild)
            row.addWidget(c)
        self.viewLayout.addLayout(row)

        self.grid_scroll = sa = SmoothScrollArea()
        sa.setWidgetResizable(True)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setStyleSheet("QScrollArea{background:transparent;border:none}")
        self.grid_host = QWidget()
        self.grid_host.setStyleSheet("background:transparent")
        self.flow = FlowLayout(self.grid_host, needAni=False)
        self.flow.setContentsMargins(2, 2, 2, 2)
        self.flow.setHorizontalSpacing(self.GAP)
        self.flow.setVerticalSpacing(self.GAP)
        sa.setWidget(self.grid_host)
        sa.setMinimumHeight(470)
        sa.viewport().installEventFilter(self)
        self.viewLayout.addWidget(sa, 1)
        self.info = CaptionLabel("")
        self.viewLayout.addWidget(self.info)

        self.yesButton.setText(tr("picker_add"))
        self.cancelButton.setText(tr("cancel"))
        self.widget.setMinimumWidth(860)
        self.rebuild()
        self.update_info()

    def rebuild(self, *_):
        q = self.search.text().strip().lower()
        fe, fp, fr = self.fel.currentData(), self.fpath.currentData(), self.frar.currentData()
        own = False
        cat = self.state.catalog
        self.flow.takeAllWidgets()   # removes and deletes
        av = self.state.avatar
        for a in cat.items:
            # 開拓者／三月七只顯示目前選的命途（與性別）那一位
            now = cat.current_variant(a["id"], av)
            if now and a["id"] != now:
                continue
            if fe and a["element"] != fe or fp and a["path"] != fp or fr and a["rarity"] != fr or own and not a["owned"]:
                continue
            if q and not (q in str(a["id"]) or q in a["tag"].lower() or q in cat.name(a["id"]).lower()
                          or q in cat.default_name(a["id"]).lower()):
                continue
            pos = self.state.lineup.index(a["id"]) if a["id"] in self.state.lineup else -1
            t = PickerTile(self.state, a, pos, self.grid_host)
            if a["id"] in self.selected:
                t.checked = True
            t.toggled.connect(self.on_toggle)
            self.flow.addWidget(t)
        self.grid_host.adjustSize()

    TILE_W, GAP = 116, 8

    def eventFilter(self, obj, e):
        from PySide6.QtCore import QEvent
        sa = self.__dict__.get("grid_scroll")
        if sa is not None and obj is sa.viewport() and e.type() == QEvent.Resize:
            self.center_grid(e.size().width())
        return super().eventFilter(obj, e)

    def center_grid(self, avail):
        """Equal margins left and right so the tile grid sits in the middle."""
        slack = 4                       # FlowLayout wraps on an exact fit, keep a few px spare
        cols = max(1, (avail - slack + self.GAP) // (self.TILE_W + self.GAP))
        used = cols * self.TILE_W + (cols - 1) * self.GAP
        m = max(0, (avail - used - slack) // 2)
        self.flow.setContentsMargins(m, 2, m, 2)

    def on_toggle(self, aid, on):
        if on and aid not in self.selected:
            self.selected.append(aid)
        elif not on and aid in self.selected:
            self.selected.remove(aid)
        self.update_info()

    def update_info(self):
        self.info.setText(tr("picker_selected", len(self.selected)))
        self.yesButton.setEnabled(bool(self.selected))
