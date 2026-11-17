"""Shared widgets: network icons, page scaffold, small helpers."""
from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QPixmap, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget

from qfluentwidgets import (ScrollArea, TitleLabel, CaptionLabel, BodyLabel, isDarkTheme, LineEdit,
                            MessageBoxBase, SubtitleLabel)

from . import i18n


_SCALED: dict = {}


class NetIcon(QWidget):
    """Draws an icon from the IconCache; repaints when it finishes downloading."""

    def __init__(self, icons, rel: str, size: int, round_=False, radius=6, parent=None, fallback_text="",
                 tint=False, fallback_rel="", height=None, top=False):
        super().__init__(parent)
        self.icons, self.rel, self.round, self.radius = icons, rel, round_, radius
        self.top = top        # crop from the top (keeps heads in tall portraits)
        self.tint = tint      # recolor a (white) monochrome icon to the current text color
        self.fallback = fallback_text
        self.fallback_rel = fallback_rel     # image to use when rel cannot be downloaded
        self.setFixedSize(size, height or size)
        icons.ready.connect(self._ready)
        self._load()

    def _load(self):
        self.pm = self.icons.get(self.rel) if self.rel else None
        if self.pm is None and self.fallback_rel and self.rel in self.icons.failed:
            self.pm = self.icons.get(self.fallback_rel)

    def set_rel(self, rel: str):
        self.rel = rel
        self._load()
        self.update()

    def _ready(self, rel):
        if rel in (self.rel, self.fallback_rel):
            self._load()
            self.update()

    def _scaled(self) -> QPixmap:
        """Smooth-scaled (and tinted) pixmap, cached app-wide so repaints/scrolling stay cheap."""
        dpr = self.devicePixelRatioF()
        key = (self.pm.cacheKey(), self.width(), self.height(), dpr, self.tint, self.tint and isDarkTheme())
        pm = _SCALED.get(key)
        if pm is None:
            pm = self.pm.scaled(self.size() * dpr, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            if self.tint:
                pm = tint_pixmap(pm)
            if len(_SCALED) > 600:
                _SCALED.clear()
            _SCALED[key] = pm
        return pm

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        r = QRectF(self.rect())
        path = QPainterPath()
        if self.round:
            path.addEllipse(r)
        else:
            path.addRoundedRect(r, self.radius, self.radius)
        p.setClipPath(path)
        if self.pm:
            pm = self._scaled()
            x = (self.width() - pm.width() / pm.devicePixelRatio()) / 2
            y = 0 if self.top else (self.height() - pm.height() / pm.devicePixelRatio()) / 2
            p.drawPixmap(int(x), int(y), pm)
        else:
            p.fillPath(path, QColor(255, 255, 255, 18) if isDarkTheme() else QColor(0, 0, 0, 12))
            if self.fallback:
                p.setPen(QColor(160, 160, 160))
                p.drawText(self.rect(), Qt.AlignCenter, self.fallback[:2])


def tint_pixmap(pm: QPixmap, color: QColor | None = None) -> QPixmap:
    """Recolor a monochrome (white) glyph to the theme's text color."""
    color = color or (QColor(230, 230, 230) if isDarkTheme() else QColor(40, 40, 40))
    out = QPixmap(pm.size())
    out.setDevicePixelRatio(pm.devicePixelRatio())
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.drawPixmap(0, 0, pm)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(out.rect(), color)
    p.end()
    return out


def tinted_icon(icons, rel: str):
    """QIcon of a tinted glyph from the cache, or None if it is still downloading."""
    from PySide6.QtGui import QIcon
    pm = icons.get(rel)
    return QIcon(tint_pixmap(pm)) if pm else None


class ElementDot(QWidget):
    def __init__(self, element: str, parent=None):
        super().__init__(parent)
        self.color = QColor(i18n.ELEMENT_COLORS.get(element, "#888888"))
        self.setFixedSize(10, 10)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(self.color)
        p.drawEllipse(self.rect())


class Page(ScrollArea):
    """Scrollable page with a title row, like Windows Settings."""

    def __init__(self, object_name: str, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.view = QWidget()
        self.view.setObjectName("view")
        self.layout_ = QVBoxLayout(self.view)
        self.layout_.setContentsMargins(36, 20, 36, 90)   # bottom room for the save bar
        self.layout_.setSpacing(10)
        self.header = QHBoxLayout()
        self.title = TitleLabel(title)
        self.header.addWidget(self.title)
        self.header.addStretch(1)
        self.layout_.addLayout(self.header)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.enableTransparentBackground()

    def add(self, w):
        self.layout_.addWidget(w)
        return w


def EmptyHint(text, parent=None):
    # (Fluent labels use overloaded __init__, so build instead of subclassing)
    lab = CaptionLabel(text, parent)
    lab.setAlignment(Qt.AlignCenter)
    lab.setMinimumHeight(60)
    return lab


class TextInputDialog(MessageBoxBase):
    def __init__(self, title: str, text: str = "", hint: str = "", parent=None, numeric=False):
        super().__init__(parent)
        self.viewLayout.addWidget(SubtitleLabel(title))
        self.edit = LineEdit()
        self.edit.setText(text)
        self.edit.setClearButtonEnabled(True)
        if numeric:
            from PySide6.QtGui import QIntValidator
            self.edit.setValidator(QIntValidator(0, 2_000_000_000))
        self.viewLayout.addWidget(self.edit)
        if hint:
            self.viewLayout.addWidget(CaptionLabel(hint))
        self.yesButton.setText(i18n.tr("ok"))
        self.cancelButton.setText(i18n.tr("cancel"))
        self.widget.setMinimumWidth(380)
        self.edit.setFocus()

    def value(self) -> str:
        return self.edit.text()


class FitStack(QStackedWidget):
    """QStackedWidget that sizes to the current page instead of the largest one."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentChanged.connect(self._fit)

    def addWidget(self, w):
        i = super().addWidget(w)
        self._fit()
        return i

    def _fit(self, *_):
        from PySide6.QtWidgets import QSizePolicy
        for i in range(self.count()):
            w = self.widget(i)
            if w is self.currentWidget():
                w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            else:
                w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.adjustSize()
        self.updateGeometry()

    def sizeHint(self):
        w = self.currentWidget()
        return w.sizeHint() if w else super().sizeHint()

    def minimumSizeHint(self):
        w = self.currentWidget()
        return w.minimumSizeHint() if w else super().minimumSizeHint()


def clear_layout(layout):
    while layout.count():
        it = layout.takeAt(0)
        w = it.widget()
        if w is not None:
            w.hide()
            w.setParent(None)
            w.deleteLater()
        elif it.layout() is not None:
            clear_layout(it.layout())
