"""Downloads and caches nanoka.cc character data/icons and Escape-penacony scenes.json."""
from __future__ import annotations

import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QPixmap

from . import i18n
from .core import Paths, read_json, write_json

UA = {"User-Agent": "ppsr-persistent-editor/1.0"}
NANOKA_MANIFEST = "https://static.nanoka.cc/manifest.json"
NANOKA_DATA = "https://static.nanoka.cc/hsr/{ver}/character.json"
NANOKA_ASSET = "https://static.nanoka.cc/assets/hsr/{rel}"
SRR_ASSET = "https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{rel}"   # rel prefix "srr:"
ALIOTH_ASSET = "https://transform.alioth.wiki/i/sr/{rel}?w=256&f=auto"              # rel prefix "alioth:"
SCENES_URL = "https://raw.githubusercontent.com/CAtlas0784/Escape-penacony/main/scenes.json"

_TAG_RE = re.compile(r"<[^>]+>")


def fetch(url: str, timeout=20) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_json(url: str):
    return json.loads(fetch(url).decode("utf-8-sig"))


# ---------------------------------------------------------------- data downloads (blocking; run in worker threads)

def update_characters(paths: Paths) -> tuple[str, bool]:
    """Returns (version, changed)."""
    manifest = fetch_json(NANOKA_MANIFEST)
    ver = manifest["hsr"]["latest"]
    meta = read_json(paths.cache / "characters_meta.json", {}) or {}
    if meta.get("version") == ver and (paths.cache / "characters.json").exists():
        return ver, False
    data = fetch_json(NANOKA_DATA.format(ver=ver))
    write_json(paths.cache / "characters.json", data)
    write_json(paths.cache / "characters_meta.json", {"version": ver, "count": len(data)})
    return ver, True


def update_scenes(paths: Paths) -> tuple[str, bool]:
    data = fetch_json(SCENES_URL)
    if not isinstance(data, dict) or "planets" not in data:
        raise ValueError("scenes.json format not recognized")
    old = read_json(paths.cache / "scenes.json", None)
    changed = old != data
    if changed:
        write_json(paths.cache / "scenes.json", data)
    return str(data.get("version", "?")), changed


# ---------------------------------------------------------------- character catalog

class Catalog:
    """Merged character info: local Excel (ids, path, element) + nanoka names."""

    def __init__(self, paths: Paths, local: dict[int, dict], owned: set[int], custom_names: dict):
        self.paths = paths
        self.local = local
        self.owned = owned
        self.custom = custom_names
        self.reload_remote()

    def reload_remote(self):
        self.remote = read_json(self.paths.cache / "characters.json", {}) or {}
        self.meta = read_json(self.paths.cache / "characters_meta.json", {}) or {}
        ids = set(self.local) | {int(k) for k in self.remote if k.isdigit()}
        self.items = []
        for i in sorted(ids):
            loc = self.local.get(i, {})
            rem = self.remote.get(str(i), {})
            base = loc.get("path") or rem.get("baseType", "")
            el = loc.get("element") or rem.get("damageType", "")
            rarity = loc.get("rarity") or (5 if str(rem.get("rank", "")).endswith("5") else 4)
            self.items.append({"id": i, "tag": loc.get("tag") or rem.get("icon", ""), "base": base,
                               "path": i18n.BASE_TO_PATH.get(base, base), "element": el, "rarity": rarity,
                               "owned": i in self.owned, "local": i in self.local})
        self.by_id = {a["id"]: a for a in self.items}
        # 開拓者：(命途, 性別) -> 角色 ID，例如 ("Elation", "Female") -> 8010
        self.trailblazers: dict[tuple[str, str], int] = {}
        for a in self.items:
            tag = a["tag"].lower()
            if a["id"] >= 8000 and tag.startswith("player"):
                gender = "Female" if "girl" in tag else "Male"
                self.trailblazers[(a["path"], gender)] = a["id"]
        # 三月七的各命途版本（1001 存護、1224 巡獵…）
        self.march = {a["path"]: a["id"] for a in self.items if a["tag"].lower().startswith("mar7th")}

    def ordered_paths(self, paths) -> list[str]:
        have = set(paths)
        return [p for p in i18n.PATHS if p in have]

    def trailblazer_paths(self) -> list[str]:
        return self.ordered_paths(p for p, _ in self.trailblazers)

    def march_paths(self) -> list[str]:
        return self.ordered_paths(self.march)

    def is_trailblazer(self, aid: int) -> bool:
        return aid in self.trailblazers.values()

    def trailblazer_id(self, path: str, gender: str):
        return self.trailblazers.get((path, gender))

    def is_march(self, aid: int) -> bool:
        return aid in self.march.values()

    def march_id(self, path: str):
        return self.march.get(path)

    def current_variant(self, aid: int, avatar: dict):
        """For Trailblazer/March, the ID matching the current path settings; None otherwise."""
        if self.is_trailblazer(aid):
            return self.trailblazer_id(avatar.get("tb_path"), avatar.get("tb_gender"))
        if self.is_march(aid):
            return self.march_id(avatar.get("march_path"))
        return None

    def default_name(self, aid: int) -> str:
        rem = self.remote.get(str(aid))
        a = self.by_id.get(aid, {})
        if rem:
            name = _TAG_RE.sub("", rem.get(i18n.LANG, "") or rem.get("en", ""))
            if "{NICKNAME}" in name or not name:
                who = ("穹" if aid % 2 else "星") if i18n.LANG == "zh" else ("Caelus" if aid % 2 else "Stelle")
                tb = "开拓者" if i18n.LANG == "zh" else "Trailblazer"
                return f"{tb}·{i18n.path_name(a.get('base', ''))}（{who}）" if i18n.LANG == "zh" \
                    else f"{tb} · {i18n.path_name(a.get('base', ''))} ({who})"
            return name
        return a.get("tag") or str(aid)

    def name(self, aid: int) -> str:
        return self.custom.get(str(aid)) or self.default_name(aid)

    def subtitle(self, aid: int) -> str:
        a = self.by_id.get(aid)
        if not a:
            return str(aid)
        return f"{aid} · {i18n.element_name(a['element'])} · {i18n.path_name(a['base'])} · {'★' * a['rarity']}"

    @staticmethod
    def icon_rel(aid: int, big=False) -> str:
        return f"avatar{'shop' if big else 'round'}icon/{aid}.webp"

    @staticmethod
    def skin_head_rel(skin_id: int) -> str:
        return f"alioth:avataricon/avatarskin/{skin_id}.png"

    @staticmethod
    def element_rel(el: str) -> str:
        return f"element/{el.lower()}.webp"

    @staticmethod
    def path_rel(path_or_base: str) -> str:
        """Simplest monochrome path glyph (StarRailRes icon/path/<Path>Small.png)."""
        p = i18n.BASE_TO_PATH.get(path_or_base, path_or_base)
        return f"srr:icon/path/{p}Small.png"


# ---------------------------------------------------------------- scenes

# 地圖資料（Escape-penacony）裡名稱有誤的地方，在這裡修正；更新地圖資料也不會被蓋掉
SCENE_FIXES = {
    20411: {"name_zh": "「纷争荒墟」悬锋城", "name": "Strife Ruins: Castrum Kremnos"},
}


class Scenes:
    def __init__(self, paths: Paths):
        self.paths = paths
        self.reload()

    def reload(self):
        self.raw = read_json(self.paths.cache / "scenes.json", None)
        self.worlds = (self.raw or {}).get("planets", [])
        for w in self.worlds:
            for s in w.get("scenes", []):
                s.update(SCENE_FIXES.get(s.get("plane_id"), {}))

    @property
    def loaded(self):
        return bool(self.worlds)

    @property
    def version(self):
        return (self.raw or {}).get("version", "?"), (self.raw or {}).get("updated_at", "?")

    @staticmethod
    def name(obj: dict) -> str:
        return (obj.get("name_zh") if i18n.LANG == "zh" else None) or obj.get("name", "?")

    @staticmethod
    def desc(obj: dict) -> str:
        return (obj.get("desc_zh") if i18n.LANG == "zh" else None) or obj.get("desc", "")

    @staticmethod
    def notice(obj: dict) -> str:
        return (obj.get("beta_notice_zh") if i18n.LANG == "zh" else None) or obj.get("beta_notice", "")

    def all(self):
        for w in self.worlds:
            for s in w.get("scenes", []):
                yield w, s

    def locate(self, scene: dict):
        """Find the listed scene matching the current location (same plane, nearest x/z)."""
        if not scene:
            return None
        pid = scene.get("plane_id")
        best, bd = None, None
        for w, s in self.all():
            if s.get("plane_id") != pid:
                continue
            d = abs(s.get("x", 0) - scene.get("x", 0)) + abs(s.get("z", 0) - scene.get("z", 0))
            if bd is None or d < bd:
                best, bd = (w, s, d), d
        return best


def scene_fields(record: dict) -> dict:
    """Fields Escape-penacony writes for a scene record (with its calyx defaults)."""
    x, y, z = int(record["x"]), int(record["y"]), int(record["z"])
    out = {
        "plane_id": int(record["plane_id"]), "x": x, "y": y, "z": z,
        "calyx_x": int(record.get("calyx_x", x)), "calyx_y": int(record.get("calyx_y", y)),
        "calyx_z": int(record.get("calyx_z", z + 1800)),
        "map_layer": int(record.get("map_layer", 1)),
        "calyx_group_id": int(record.get("calyx_group_id", 186)),
        "calyx_inst_id": int(record.get("calyx_inst_id", 300001)),
        "calyx_entity_id": int(record.get("calyx_entity_id", 1337)),
        "calyx_prop_id": int(record.get("calyx_prop_id", 808)),
    }
    for k in ("entry_id", "floor_id", "saved_values"):
        if k in record:
            out[k] = record[k]
    return out


def apply_scene(current: dict | None, record: dict) -> dict:
    """New scene dict: keeps existing key order, drops optional keys the record lacks."""
    new = dict(current or {})
    for k in ("entry_id", "floor_id", "saved_values"):
        new.pop(k, None)
    new.update(scene_fields(record))
    return new


# ---------------------------------------------------------------- icon cache

class IconCache(QObject):
    ready = Signal(str)

    def __init__(self, folder: Path):
        super().__init__()
        self.folder = folder
        self.mem: dict[str, QPixmap] = {}
        self.pending: set[str] = set()
        self.failed: set[str] = set()
        self.pool = ThreadPoolExecutor(max_workers=6)
        self._done.connect(self._on_done, Qt.QueuedConnection)

    _done = Signal(str, bool)

    def file(self, rel: str) -> Path:
        return self.folder / rel.replace("/", "_").replace(":", "_")

    @staticmethod
    def url(rel: str) -> str:
        if rel.startswith("srr:"):
            return SRR_ASSET.format(rel=rel[4:])
        if rel.startswith("alioth:"):
            return ALIOTH_ASSET.format(rel=rel[7:])
        return NANOKA_ASSET.format(rel=rel)

    def get(self, rel: str) -> QPixmap | None:
        if rel in self.mem:
            return self.mem[rel]
        f = self.file(rel)
        if f.exists():
            pm = QPixmap(str(f))
            if not pm.isNull():
                self.mem[rel] = pm
                return pm
        if rel not in self.pending and rel not in self.failed:
            try:
                self.pool.submit(self._download, rel)
                self.pending.add(rel)
            except RuntimeError:          # app is shutting down
                pass
        return None

    def _download(self, rel: str):
        try:
            data = fetch(self.url(rel))
            f = self.file(rel)
            f.parent.mkdir(parents=True, exist_ok=True)
            tmp = f.with_name(f.name + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(f)
            self._done.emit(rel, True)
        except Exception:
            self._done.emit(rel, False)

    def _on_done(self, rel: str, ok: bool):
        self.pending.discard(rel)
        if not ok:
            self.failed.add(rel)
            self.ready.emit(rel)          # listeners switch to their fallback
            return
        self.mem.pop(rel, None)
        if self.get(rel) is not None:
            self.ready.emit(rel)

    def clear(self):
        self.mem.clear()
        self.failed.clear()
        if self.folder.exists():
            for f in self.folder.iterdir():
                f.unlink(missing_ok=True)
