from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget

from qfluentwidgets import (SettingCardGroup, SettingCard, ComboBox, FluentIcon as FIF, SegmentedWidget,
                            CardWidget, StrongBodyLabel, CaptionLabel, TransparentToolButton, PushButton,
                            RoundMenu, Action, ToolTipFilter, ToolTipPosition, DropDownPushButton, InfoBar,
                            themeColor)

from .. import i18n
from ..i18n import tr
import re

from ..resources import Catalog
from ..widgets import Page, NetIcon, EmptyHint, TextInputDialog, FitStack, clear_layout, tinted_icon

_MODEL_PREFIX = re.compile(r"^(NPC_)?(Avatar_)?(Maid_|Girl_|Boy_)?")


class ComboCard(SettingCard):
    def __init__(self, icon, title, content, items, value, on_change, parent=None):
        """items: list of (text, data, icon_or_None)."""
        super().__init__(icon, title, content, parent)
        self.combo = ComboBox(self)
        datas = [d for _, d, _ in items]
        for text, data, ic in items:
            if ic is not None:
                self.combo.addItem(text, ic, userData=data)
            else:
                self.combo.addItem(text, userData=data)
        if value not in datas and value not in (None, ""):
            self.combo.addItem(str(value), userData=value)
            datas.append(value)
        if value in datas:
            self.combo.setCurrentIndex(datas.index(value))
        self.combo.setMinimumWidth(170)
        self.hBoxLayout.addWidget(self.combo, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.combo.currentIndexChanged.connect(lambda _: on_change(self.combo.currentData()))


class SkinRow(CardWidget):
    """One line: avatar (shows the chosen skin's head icon) · name · skin combo box · delete."""

    def __init__(self, page, key: str, value, parent=None):
        super().__init__(parent)
        st = page.state
        self.cat = cat = st.catalog
        self.aid = aid = int(key) if key.isdigit() else 0
        self.setFixedHeight(60)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 6, 12, 6)
        lay.setSpacing(12)
        self.avatar = NetIcon(st.icons, self.head_rel(value), 40, round_=True, parent=self,
                              fallback_rel=cat.icon_rel(aid), fallback_text=cat.name(aid))
        lay.addWidget(self.avatar)
        lay.addWidget(StrongBodyLabel(cat.name(aid), self))
        id_lbl = CaptionLabel(key, self)
        id_lbl.setStyleSheet("color:gray")
        lay.addWidget(id_lbl)
        lay.addStretch(1)

        self.combo = ComboBox(self)
        self.combo.setMinimumWidth(240)
        datas = [0]
        self.combo.addItem(tr("default"), userData=0)
        for s in (s for s in st.skins if s["avatar_id"] == aid):
            self.combo.addItem(i18n.skin_name(s["id"], _MODEL_PREFIX.sub("", s["model"])), userData=s["id"])
            datas.append(s["id"])
        if value not in datas:
            self.combo.addItem(tr("skin_value_custom", value), userData=value)
            datas.append(value)
        self.combo.setCurrentIndex(datas.index(value))
        self.combo.currentIndexChanged.connect(lambda _: self.on_pick(page, key))
        lay.addWidget(self.combo)
        b = TransparentToolButton(FIF.DELETE, self)
        b.setToolTip(tr("delete"))
        b.installEventFilter(ToolTipFilter(b, 300, ToolTipPosition.TOP))
        b.clicked.connect(lambda: page.del_skin(key))
        lay.addWidget(b)

    def head_rel(self, skin_id) -> str:
        return self.cat.skin_head_rel(skin_id) if skin_id else self.cat.icon_rel(self.aid)

    def on_pick(self, page, key):
        v = self.combo.currentData()
        page.set_skin(key, v)
        self.avatar.set_rel(self.head_rel(v))


class AppearancePage(Page):
    def __init__(self, state, parent=None):
        super().__init__("appearancePage", tr("appearance_title"), parent)
        self.state = state
        self.seg = SegmentedWidget(self.view)
        self.stack = FitStack(self.view)
        self.tb_host = QWidget()
        self.tb_lay = QVBoxLayout(self.tb_host)
        self.tb_lay.setContentsMargins(0, 0, 0, 0)
        self.skin_host = QWidget()
        self.skin_lay = QVBoxLayout(self.skin_host)
        self.skin_lay.setContentsMargins(0, 0, 0, 0)
        self.skin_lay.setSpacing(6)
        for key, text, w in (("tb", tr("tab_tb"), self.tb_host), ("skin", tr("tab_skin"), self.skin_host)):
            self.stack.addWidget(w)
            self.seg.addItem(key, text, lambda *_, w=w: self.stack.setCurrentWidget(w))
        self.seg.setCurrentItem("tb")
        hl = QHBoxLayout()
        hl.addWidget(self.seg)
        hl.addStretch(1)
        self.layout_.addLayout(hl)
        self.add(self.stack)
        self.layout_.addStretch(1)
        from PySide6.QtCore import QTimer
        self._tb_timer = QTimer(self, singleShot=True, interval=300, timeout=self.refresh_tb)
        state.icons.ready.connect(lambda rel: rel.startswith("srr:icon/path") and self._tb_timer.start())
        state.reloaded.connect(self.refresh)
        state.namesChanged.connect(self.refresh_skins)
        state.catalogChanged.connect(self.refresh_skins)
        self.refresh()

    # ------------------------------------------------------------ trailblazer
    def refresh(self):
        self.refresh_tb()
        self.refresh_skins()

    def refresh_tb(self):
        clear_layout(self.tb_lay)
        av = self.state.avatar
        icons = self.state.icons

        cat = self.state.catalog

        def path_items(paths):
            # 只列出遊戲資料裡真的有的命途（找不到資料時才列全部）
            return [(f"{i18n.path_name(p)}  ({p})", p, tinted_icon(icons, Catalog.path_rel(p)))
                    for p in (paths or i18n.PATHS)]

        g1 = SettingCardGroup(tr("tb_group"), self.tb_host)
        g1.addSettingCard(ComboCard(FIF.PEOPLE, tr("tb_gender"), tr("tb_gender_desc"),
                                    [(tr("female"), "Female", None), (tr("male"), "Male", None)],
                                    av.get("tb_gender"), lambda v: self.set_av("tb_gender", v)))
        tb_card = ComboCard(FIF.TAG, tr("tb_path"), tr("tb_path_desc"), path_items(cat.trailblazer_paths()),
                            av.get("tb_path"), lambda v: self.set_av("tb_path", v))
        g1.addSettingCard(tb_card)
        g2 = SettingCardGroup(tr("march_group"), self.tb_host)
        march_card = ComboCard(FIF.TAG, tr("march_path"), tr("march_path_desc"), path_items(cat.march_paths()),
                               av.get("march_path"), lambda v: self.set_av("march_path", v))
        g2.addSettingCard(march_card)
        # 頭像隨目前命途（與性別）切換
        self.tb_icon = NetIcon(icons, "", 44, round_=True, parent=tb_card)
        self.march_icon = NetIcon(icons, "", 44, round_=True, parent=march_card)
        for card, ic in ((tb_card, self.tb_icon), (march_card, self.march_icon)):
            card.hBoxLayout.insertWidget(card.hBoxLayout.indexOf(card.combo), ic, 0, Qt.AlignVCenter)
            card.hBoxLayout.insertSpacing(card.hBoxLayout.indexOf(card.combo), 12)
            card.setFixedHeight(76)
        self.update_variant_icons()
        self.tb_lay.addWidget(g1)
        self.tb_lay.addSpacing(12)
        self.tb_lay.addWidget(g2)

    def update_variant_icons(self):
        av, cat = self.state.avatar, self.state.catalog
        for ic, aid in ((getattr(self, "tb_icon", None), cat.trailblazer_id(av.get("tb_path"), av.get("tb_gender"))),
                        (getattr(self, "march_icon", None), cat.march_id(av.get("march_path")))):
            if ic is None:
                continue
            try:
                ic.set_rel(cat.icon_rel(aid) if aid else "")
                ic.setToolTip(f"{cat.name(aid)} · {aid}" if aid else "")
            except RuntimeError:     # widget already rebuilt
                pass

    def set_av(self, key, value):
        av = self.state.avatar
        av[key] = value
        if key in ("tb_path", "tb_gender", "march_path"):
            # 編隊裡的開拓者／三月七跟著換成目前命途（與性別）的版本
            cat = self.state.catalog
            lineup = av.get("lineup") or []
            changed = False
            for i, aid in enumerate(lineup):
                new = cat.current_variant(aid, av)
                if new and new != aid:
                    lineup[i] = new
                    changed = True
            if changed:      # let the lineup page redraw (deferred: we're inside the combo's signal)
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, self.state.lineupChanged.emit)
            self.update_variant_icons()
        self.state.mark_changed()

    # ------------------------------------------------------------ skins
    def refresh_skins(self):
        clear_layout(self.skin_lay)
        skins = self.state.avatar.get("skin") or {}
        top = QHBoxLayout()
        self.add_btn = DropDownPushButton(FIF.ADD, tr("skin_add"))
        menu = RoundMenu(parent=self.add_btn)
        have = set(skins)
        cat = self.state.catalog
        for aid in sorted({s["avatar_id"] for s in self.state.skins}):
            if str(aid) in have:
                continue
            act = Action(f"{aid}  {cat.name(aid)}")
            act.triggered.connect(lambda _=False, a=aid: self.add_skin(str(a)))
            menu.addAction(act)
        menu.addSeparator()
        other = Action(FIF.EDIT, tr("skin_other"))
        other.triggered.connect(self.add_other)
        menu.addAction(other)
        self.add_btn.setMenu(menu)
        top.addWidget(self.add_btn)
        top.addSpacing(12)
        top.addWidget(CaptionLabel(tr("skin_hint")))
        top.addStretch(1)
        self.skin_lay.addLayout(top)
        if not skins:
            self.skin_lay.addWidget(EmptyHint(tr("skin_empty")))
        for k, v in skins.items():
            self.skin_lay.addWidget(SkinRow(self, k, v))

    def set_skin(self, key, value):
        skins = self.state.avatar.setdefault("skin", {})
        if skins.get(key) == int(value):
            return
        skins[key] = int(value)
        self.state.mark_changed()

    def del_skin(self, key):
        self.state.avatar.get("skin", {}).pop(key, None)
        self.state.mark_changed()
        self.refresh_skins()

    def add_skin(self, key):
        self.state.avatar.setdefault("skin", {}).setdefault(key, 0)
        self.state.mark_changed()
        self.refresh_skins()

    def add_other(self):
        d = TextInputDialog(tr("skin_id_title"), "", "", self.window(), numeric=True)
        if d.exec() and d.value().strip():
            self.add_skin(d.value().strip())
