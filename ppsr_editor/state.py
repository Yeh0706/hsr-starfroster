"""Shared application state passed to every page."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from .core import (Paths, PersistentFile, Settings, JsonStore, load_freesr_owned, load_local_avatars,
                   load_local_skins, clamp_leader)
from .resources import Catalog, Scenes, IconCache


class AppState(QObject):
    changed = Signal()       # persistent data edited in memory (dirty state may have changed)
    reloaded = Signal()      # persistent data replaced (load / revert / raw JSON apply)
    namesChanged = Signal()
    lineupChanged = Signal()  # lineup edited from another page
    catalogChanged = Signal()
    scenesChanged = Signal()
    favoritesChanged = Signal()

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.paths = Paths(settings["misc_path"])
        self.paths.migrate_legacy()      # 舊版資料夾 → AppData（只複製，不刪舊的）
        self.pf = PersistentFile(self.paths)
        self.names = JsonStore(self.paths.names, {})
        self.favorites = JsonStore(self.paths.favorites, [])
        self.icons = IconCache(self.paths.icons)
        self.skins = load_local_skins(self.paths)
        self.catalog = Catalog(self.paths, load_local_avatars(self.paths), load_freesr_owned(self.paths),
                               self.names.value)
        self.scenes = Scenes(self.paths)
        self.load_error = None
        self.load()

    # ------------------------------------------------------------ persistent
    @property
    def data(self) -> dict:
        return self.pf.data

    @property
    def avatar(self) -> dict:
        return self.pf.data.setdefault("avatar", {})

    @property
    def lineup(self) -> list:
        return self.avatar.setdefault("lineup", [])

    def load(self):
        self.load_error = None
        if not self.paths.valid():
            self.pf.data, self.pf.saved = {}, {}
            self.load_error = "missing"
        else:
            try:
                self.pf.load()
            except Exception as e:  # malformed JSON etc.
                self.pf.data, self.pf.saved = {}, {}
                self.load_error = str(e)
        self.reloaded.emit()
        self.changed.emit()

    def save(self):
        self.pf.save()
        self.changed.emit()

    def revert(self):
        self.pf.revert()
        self.reloaded.emit()
        self.changed.emit()

    def replace_data(self, data: dict):
        self.pf.data = data
        self.pf._normalize()
        self.reloaded.emit()
        self.changed.emit()

    def mark_changed(self):
        av = self.avatar
        clamp_leader(av)                 # 不管隊長，只避免 leader 超出編隊範圍
        self.changed.emit()

    @property
    def dirty(self) -> bool:
        return self.pf.dirty

    # ------------------------------------------------------------ misc
    def set_custom_name(self, aid: int, name: str):
        name = name.strip()
        if name:
            self.names.value[str(aid)] = name
        else:
            self.names.value.pop(str(aid), None)
        self.names.save()
        self.namesChanged.emit()

    def add_favorite(self, name: str, scene: dict):
        self.favorites.value.append({"name": name, "scene": dict(scene)})
        self.favorites.save()
        self.favoritesChanged.emit()

    def save_favorites(self):
        self.favorites.save()
        self.favoritesChanged.emit()

    def is_favorite(self, scene: dict) -> bool:
        keys = ("plane_id", "x", "y", "z")
        return any(all(f["scene"].get(k) == scene.get(k) for k in keys) for f in self.favorites.value)
