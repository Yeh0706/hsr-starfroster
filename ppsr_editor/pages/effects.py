"""专属效果（ppSR 的 global_passive）開關。名稱與說明取自 nanoka.cc（4.7.52）。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel

from qfluentwidgets import CardWidget, StrongBodyLabel, CaptionLabel, BodyLabel, SwitchButton

from .. import i18n
from ..i18n import tr
from ..widgets import Page

ICON_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "effects"

# avatar_id, persistent.json 裡用的被動 ID（取自 ppSR 原本的 persistent.json）, 名稱/標籤/說明
EFFECTS = [
    {"avatar_id": 1407, "id": 140703,
     "name": {"zh": "月茧之庇", "en": "Sanctuary of Mooncocoon"},
     "tag": {"zh": "辅助", "en": "Support"},
     "desc": {"zh": "获取遐蝶后或当前队伍存在遐蝶时获得效果：战斗中，若我方角色受到致命攻击，则本次行动中所有受到致命攻击的我方角色获得【月茧】状态。"
                    "【月茧】状态下的角色会暂时延后陷入无法战斗状态，且可以正常行动。若行动后，下一次回合开始前当前生命值提高或获得护盾，"
                    "则解除【月茧】状态，否则将立即陷入无法战斗状态。该效果单场战斗中最多触发1次。",
              "en": "After obtaining Castorice or when Castorice is in the current team: in battle, when an ally receives a killing "
                    "blow, all allies that received a killing blow in this action enter \"Mooncocoon\". They temporarily delay "
                    "becoming downed and can act normally. If their HP increases or they gain a Shield before the next turn "
                    "starts, \"Mooncocoon\" is removed; otherwise they are downed immediately. Triggers once per battle."}},
    {"avatar_id": 1506, "id": 150602,
     "name": {"zh": "999安全卫士", "en": "McAwolfee 999"},
     "tag": {"zh": "辅助", "en": "Support"},
     "desc": {"zh": "获取「银狼LV.999」后或当前队伍存在「银狼LV.999」时获得效果：战斗中，若敌方目标对我方施加了控制类负面状态，"
                    "则使我方全体获得【防火墙】，持续1回合。【防火墙】状态下，我方目标免疫敌方目标施加的控制类负面状态。该效果每个波次最多触发1次。",
              "en": "After obtaining \"Silver Wolf LV.999\" or when she is in the current team: during combat, if an enemy inflicts "
                    "a Crowd Control debuff on an ally, all allies gain \"Firewall\" for 1 turn, becoming immune to Crowd Control "
                    "debuffs from enemies. Triggers at most once per wave."}},
    {"avatar_id": 1511, "id": 151104,
     "name": {"zh": "阿哈时刻在", "en": "Aha Instant Incoming"},
     "tag": {"zh": "辅助", "en": "Support"},
     "desc": {"zh": "获取星神★阿哈后或当前队伍存在星神★阿哈时获得效果：战斗中，星神★阿哈将亲自领演【阿哈时刻】，并可以快进施放中的欢愉技。"
                    "【阿哈时刻】的基础速度从80提高至星神★阿哈的基础速度。",
              "en": "After obtaining Aeon ★ Aha or when Aeon ★ Aha is in the current team: in combat, Aeon ★ Aha personally leads "
                    "\"Aha Instant\" and can fast-forward the Elation Skill being used. The base SPD of \"Aha Instant\" increases "
                    "from 80 to Aeon ★ Aha's base SPD."}},
]


def _t(d: dict) -> str:
    return d["en"] if i18n.LANG == "en" else i18n.zh_text(d["zh"])


class EffectCard(CardWidget):
    def __init__(self, page, eff: dict, parent=None):
        super().__init__(parent)
        self.page, self.eff = page, eff
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(16)

        icon = QLabel(self)
        icon.setFixedSize(56, 56)
        pm = QPixmap(str(ICON_DIR / f"{eff['avatar_id']}.png"))
        if not pm.isNull():
            dpr = self.devicePixelRatioF()
            s = pm.scaled(int(56 * dpr), int(56 * dpr), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            s.setDevicePixelRatio(dpr)
            icon.setPixmap(s)
        lay.addWidget(icon, 0, Qt.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(4)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(StrongBodyLabel(_t(eff["name"]), self))
        tag = CaptionLabel(_t(eff["tag"]), self)
        tag.setStyleSheet("CaptionLabel{border:1px solid rgba(128,128,128,0.5);border-radius:4px;padding:0 6px;}")
        top.addWidget(tag)
        who = CaptionLabel(page.state.catalog.name(eff["avatar_id"]), self)
        who.setStyleSheet("color:gray")
        top.addWidget(who)
        top.addStretch(1)
        col.addLayout(top)
        desc = BodyLabel(_t(eff["desc"]), self)
        desc.setWordWrap(True)
        desc.setStyleSheet("color:rgba(128,128,128,1);")
        col.addWidget(desc)
        lay.addLayout(col, 1)

        self.switch = SwitchButton(self)
        self.switch.setOnText(tr("on"))
        self.switch.setOffText(tr("off"))
        self.switch.setChecked(page.is_active(eff))
        self.switch.checkedChanged.connect(lambda on: page.set_active(eff, on))
        lay.addWidget(self.switch, 0, Qt.AlignVCenter)


class EffectsPage(Page):
    def __init__(self, state, parent=None):
        super().__init__("effectsPage", tr("effects_title"), parent)
        self.state = state
        self.add(CaptionLabel(tr("effects_hint")))
        self.cards = []
        for eff in EFFECTS:
            c = EffectCard(self, eff, self.view)
            self.cards.append(c)
            self.add(c)
        self.layout_.addStretch(1)
        state.reloaded.connect(self.refresh)
        state.namesChanged.connect(self.refresh)

    # global_passive entries matched by avatar_id; other entries are left untouched
    def _entry(self, eff):
        for g in self.state.avatar.get("global_passive") or []:
            if g.get("avatar_id") == eff["avatar_id"]:
                return g
        return None

    def is_active(self, eff) -> bool:
        g = self._entry(eff)
        return bool(g and g.get("active"))

    def set_active(self, eff, on: bool):
        g = self._entry(eff)
        if g is None:
            if not on:
                return
            g = {"name": eff["name"]["en"] + " Global Passive", "avatar_id": eff["avatar_id"], "id": eff["id"],
                 "active": True}
            self.state.avatar.setdefault("global_passive", []).append(g)
        elif bool(g.get("active")) == on:
            return
        g["active"] = on
        self.state.mark_changed()

    def refresh(self):
        for c in self.cards:
            c.switch.blockSignals(True)
            c.switch.setChecked(self.is_active(c.eff))
            c.switch.blockSignals(False)
