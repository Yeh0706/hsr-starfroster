from __future__ import annotations

import json
import re

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtWidgets import QHBoxLayout

from qfluentwidgets import (PlainTextEdit, PushButton, PrimaryPushButton, CaptionLabel, FluentIcon as FIF,
                            InfoBar, InfoBarPosition, IconWidget, InfoBarIcon, isDarkTheme, qconfig)

from ..i18n import tr
from ..widgets import Page


class JsonHighlighter(QSyntaxHighlighter):
    """Keys / strings / numbers / true-false-null in VS Code-like colors (dark & light)."""
    TOKEN = re.compile(r'"(?:\\.|[^"\\])*"(\s*:)?|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\btrue\b|\bfalse\b|\bnull\b|[{}\[\]]')

    def __init__(self, doc):
        super().__init__(doc)
        self.update_colors()

    def update_colors(self):
        dark = isDarkTheme()

        def fmt(color, bold=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(QFont.DemiBold)
            return f
        self.f_key = fmt("#9CDCFE" if dark else "#0451A5")
        self.f_str = fmt("#CE9178" if dark else "#A31515")
        self.f_num = fmt("#B5CEA8" if dark else "#098658")
        self.f_kw = fmt("#569CD6" if dark else "#0000FF", True)
        self.f_brace = fmt("#FFD700" if dark else "#7A5C00")
        self.rehighlight()

    def highlightBlock(self, text):
        for m in self.TOKEN.finditer(text):
            tok = m.group(0)
            if tok.startswith('"'):
                end = m.start() + len(tok.rstrip().rstrip(":").rstrip())
                self.setFormat(m.start(), end - m.start(), self.f_key if m.group(1) else self.f_str)
            elif tok in ("true", "false", "null"):
                self.setFormat(m.start(), len(tok), self.f_kw)
            elif tok in "{}[]":
                self.setFormat(m.start(), 1, self.f_brace)
            else:
                self.setFormat(m.start(), len(tok), self.f_num)


class AdvancedPage(Page):
    """Raw persistent.json editor with syntax colors and validation."""

    def __init__(self, state, parent=None):
        super().__init__("advancedPage", tr("advanced_title"), parent)
        self.state = state
        self.add(CaptionLabel(tr("json_hint")))
        self.edit = PlainTextEdit()
        f = QFont("Cascadia Mono")
        f.setStyleHint(QFont.Monospace)
        f.setPointSize(10)
        self.edit.setFont(f)
        self.edit.setMinimumHeight(520)
        self.edit.setLineWrapMode(PlainTextEdit.NoWrap)
        self.highlighter = JsonHighlighter(self.edit.document())
        qconfig.themeChanged.connect(lambda *_: self.highlighter.update_colors())
        self.add(self.edit)

        row = QHBoxLayout()
        self.apply_btn = PrimaryPushButton(FIF.ACCEPT, tr("json_apply"))
        self.apply_btn.clicked.connect(self.apply_json)
        ref = PushButton(FIF.SYNC, tr("json_refresh"))
        ref.clicked.connect(self.refresh_json)
        self.status_icon = IconWidget(InfoBarIcon.SUCCESS)
        self.status_icon.setFixedSize(16, 16)
        self.status = CaptionLabel("")
        row.addWidget(self.apply_btn)
        row.addWidget(ref)
        row.addSpacing(12)
        row.addWidget(self.status_icon)
        row.addWidget(self.status, 1)
        self.layout_.addLayout(row)
        self.layout_.addStretch(1)

        self.timer = QTimer(self, singleShot=True, interval=300, timeout=self.validate)
        self.edit.textChanged.connect(self.timer.start)
        state.reloaded.connect(self.refresh_json)
        self.refresh_json()

    def showEvent(self, e):
        super().showEvent(e)
        if not self.edit.hasFocus():
            self.refresh_json()

    def refresh_json(self):
        self.edit.setPlainText(json.dumps(self.state.data, ensure_ascii=False, indent=4))
        self.validate()

    def parse(self):
        try:
            obj = json.loads(self.edit.toPlainText())
        except json.JSONDecodeError as e:
            return None, tr("json_error", e.lineno, e.colno, e.msg)
        if not isinstance(obj, dict):
            return None, tr("json_not_object")
        return obj, None

    def validate(self):
        obj, err = self.parse()
        self.status_icon.setIcon(InfoBarIcon.ERROR if err else InfoBarIcon.SUCCESS)
        self.status.setText(err or tr("json_ok"))
        self.apply_btn.setEnabled(err is None and obj != self.state.data)

    def apply_json(self):
        obj, err = self.parse()
        if err:
            return
        self.state.replace_data(obj)
        InfoBar.success(tr("done"), tr("json_applied"), duration=3000, parent=self.window(),
                        position=InfoBarPosition.TOP)
