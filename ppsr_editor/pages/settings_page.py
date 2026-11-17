from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog

from qfluentwidgets import (SettingCardGroup, SettingCard, PushSettingCard, FluentIcon as FIF, ComboBox, PushButton,
                            InfoBar, InfoBarPosition, HyperlinkCard, setTheme, Theme)

from .. import REPO_URL
from ..i18n import tr
from ..widgets import Page
from .appearance import ComboCard


def pick_persistent(parent, start: str):
    """Ask for persistent.json; returns its folder (the misc folder) or None."""
    f, _ = QFileDialog.getOpenFileName(parent, tr("pick_persistent_title"), start,
                                       "persistent.json (persistent.json);;JSON (*.json)")
    if not f:
        return None
    if os.path.basename(f).lower() != "persistent.json":
        InfoBar.error(tr("error"), tr("pick_persistent_wrong"), parent=parent, position=InfoBarPosition.TOP)
        return None
    return os.path.dirname(f)


class SettingsPage(Page):
    def __init__(self, state, on_update_maps, on_update_chars, on_misc_changed, parent=None):
        super().__init__("settingsPage", tr("settings_title"), parent)
        self.state = state
        s = state.settings

        g = SettingCardGroup(tr("grp_files"), self.view)
        self.misc = PushSettingCard(tr("choose_file"), FIF.DOCUMENT, tr("persistent_file"), s["misc_path"], g)
        self.misc.clicked.connect(lambda: self.choose_misc(on_misc_changed))
        g.addSettingCard(self.misc)
        sc = SettingCard(FIF.LINK, tr("shortcut"), tr("shortcut_desc"), g)
        for key, text in (("desktop", tr("shortcut_desktop")), ("startmenu", tr("shortcut_startmenu"))):
            b = PushButton(text, sc)
            b.clicked.connect(lambda _=False, k=key: self.make_shortcut(k))
            sc.hBoxLayout.addWidget(b, 0, Qt.AlignRight)
            sc.hBoxLayout.addSpacing(8)
        sc.hBoxLayout.addSpacing(8)
        g.addSettingCard(sc)
        self.add(g)

        g = SettingCardGroup(tr("grp_look"), self.view)
        g.addSettingCard(ComboCard(FIF.BRUSH, tr("theme"), tr("theme_desc"),
                                   [(tr("theme_auto"), "auto", None), (tr("theme_light"), "light", None),
                                    (tr("theme_dark"), "dark", None)], s["theme"], self.set_theme, g))
        g.addSettingCard(ComboCard(FIF.LANGUAGE, tr("language"), tr("language_desc"),
                                   [("简体中文", "zh", None), ("English", "en", None)], s["language"],
                                   self.set_lang, g))
        self.add(g)

        g = SettingCardGroup(tr("grp_data"), self.view)
        self.maps_card = PushSettingCard(tr("check_update"), FIF.GLOBE, tr("map_data"), "", g)
        self.maps_card.clicked.connect(on_update_maps)
        self.chars_card = PushSettingCard(tr("check_update"), FIF.PEOPLE, tr("char_data"), "", g)
        self.chars_card.clicked.connect(on_update_chars)
        self.icons_card = PushSettingCard(tr("clear"), FIF.PHOTO, tr("icon_cache"), "", g)
        self.icons_card.clicked.connect(self.clear_icons)
        for c in (self.maps_card, self.chars_card, self.icons_card):
            g.addSettingCard(c)
        self.add(g)

        g = SettingCardGroup(tr("grp_about"), self.view)
        self.about = PushSettingCard(tr("open_data_folder"), FIF.INFO, tr("about"), "", g)
        self.about.clicked.connect(self.open_data)
        g.addSettingCard(self.about)
        g.addSettingCard(HyperlinkCard(REPO_URL, "GitHub", FIF.GITHUB, "Starfroster", tr("repo_desc"), g))
        g.addSettingCard(HyperlinkCard("https://hsr.nanoka.cc", "nanoka.cc", FIF.LINK, "nanoka.cc",
                                       "Character names & icons", g))
        g.addSettingCard(HyperlinkCard("https://github.com/CAtlas0784/Escape-penacony", "GitHub", FIF.GITHUB,
                                       "Escape-penacony", "Map data (scenes.json)", g))
        self.add(g)
        self.layout_.addStretch(1)

        state.scenesChanged.connect(self.refresh)
        state.catalogChanged.connect(self.refresh)
        self.refresh()

    def refresh(self):
        st = self.state
        self.misc.setContent(str(st.paths.persistent))
        if st.scenes.loaded:
            v, d = st.scenes.version
            self.maps_card.setContent(tr("map_data_desc", v, d))
        else:
            self.maps_card.setContent(tr("map_data_none"))
        meta = st.catalog.meta
        self.chars_card.setContent(tr("char_data_desc", meta.get("version"), meta.get("count"))
                                   if meta else tr("char_data_none"))
        self.icons_card.setContent(str(st.paths.icons))
        from .. import __version__
        self.about.setContent(tr("about_desc", st.paths.data, __version__))

    def choose_misc(self, on_changed):
        d = pick_persistent(self.window(), str(self.state.paths.misc))
        if not d:
            return
        self.state.settings["configured"] = True
        self.state.settings["misc_path"] = d
        on_changed()

    def make_shortcut(self, where):
        from .. import shortcuts
        try:
            lnk = shortcuts.create(where)
        except Exception as e:
            InfoBar.error(tr("shortcut_failed"), str(e), duration=-1, parent=self.window(),
                          position=InfoBarPosition.TOP)
            return
        InfoBar.success(tr("shortcut_done"), lnk, duration=4000, parent=self.window(),
                        position=InfoBarPosition.TOP)

    def set_theme(self, v):
        self.state.settings["theme"] = v
        setTheme({"auto": Theme.AUTO, "light": Theme.LIGHT, "dark": Theme.DARK}[v], lazy=True)

    def set_lang(self, v):
        if v != self.state.settings["language"]:
            self.state.settings["language"] = v
            InfoBar.info(tr("language"), tr("language_restart"), duration=4000, parent=self.window(),
                         position=InfoBarPosition.TOP)

    def clear_icons(self):
        self.state.icons.clear()
        InfoBar.success(tr("done"), tr("clear_icons"), duration=2000, parent=self.window(),
                        position=InfoBarPosition.TOP)

    def open_data(self):
        self.state.paths.data.mkdir(parents=True, exist_ok=True)
        os.startfile(str(self.state.paths.data))
