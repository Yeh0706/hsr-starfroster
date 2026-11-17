"""Paths, settings, persistent.json I/O, favorites, custom names."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

DEFAULT_MISC = Path(r"C:\StarRail Beta\ppSR_REL_4.7.5X\misc")
MAX_BACKUPS = 30

# 設定檔放在 %APPDATA%（不受「受控資料夾存取」影響），可用環境變數覆寫（測試用）
SETTINGS_FILE = Path(os.environ.get("PPSR_EDITOR_SETTINGS")
                     or Path(os.environ.get("APPDATA", Path.home())) / "ppSR-persistent-editor" / "settings.json")


def read_json(path: Path, default=None):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data, indent=2):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    tmp.replace(path)


class Settings:
    DEFAULTS = {"misc_path": str(DEFAULT_MISC), "theme": "dark", "language": "zh", "configured": False}

    def __init__(self):
        self.data = dict(self.DEFAULTS)
        self.data.update(read_json(SETTINGS_FILE, {}) or {})
        env_misc = os.environ.get("PPSR_EDITOR_MISC")
        if env_misc:
            self.data["misc_path"] = env_misc

    def __getitem__(self, k):
        return self.data.get(k, self.DEFAULTS.get(k))

    def __setitem__(self, k, v):
        self.data[k] = v
        write_json(SETTINGS_FILE, self.data)


class Paths:
    def __init__(self, misc: str | Path):
        self.misc = Path(misc)
        self.persistent = self.misc / "persistent.json"
        self.freesr = self.misc / "freesr-data.json"
        self.excel = self.misc / "resources" / "Excel"
        self.root = self.misc.parent                     # ppsr.exe 所在
        self.ppsr_exe = self.root / "ppsr.exe"
        self.data = self.root / "persistent編輯器資料"     # 「文件」資料夾可能被擋寫入，放遊戲旁
        self.names = self.data / "角色名稱.json"
        self.favorites = self.data / "收藏地圖.json"
        self.cache = self.data / "資源"
        self.icons = self.cache / "icons"

    def valid(self) -> bool:
        return self.persistent.exists()


# ---------------------------------------------------------------- persistent.json

class PersistentFile:
    """Loads/saves persistent.json while keeping key order, line endings and the trailing newline."""

    def __init__(self, paths: Paths):
        self.paths = paths
        self.data: dict = {}
        self.saved: dict = {}
        self.eol = "\r\n"
        self.tail = ""
        self.digest = ""
        self.notices: list[str] = []

    @property
    def path(self) -> Path:
        return self.paths.persistent

    def load(self):
        raw = self.path.read_bytes()
        self.eol = "\r\n" if b"\r\n" in raw else "\n"
        self.tail = self.eol if raw.endswith(b"\n") else ""
        self.digest = hashlib.sha1(raw).hexdigest()
        self.data = json.loads(raw.decode("utf-8-sig"))
        self.saved = copy.deepcopy(self.data)
        self.notices = []
        self._normalize()

    def _normalize(self):
        av = self.data.setdefault("avatar", {})
        av.setdefault("lineup", [])
        clamp_leader(av)

    @property
    def dirty(self) -> bool:
        return self.data != self.saved

    def render(self, data=None) -> bytes:
        text = json.dumps(self.data if data is None else data, ensure_ascii=False, indent=4)
        return (text.replace("\n", self.eol) + self.tail).encode("utf-8")

    def changed_on_disk(self) -> bool:
        try:
            return hashlib.sha1(self.path.read_bytes()).hexdigest() != self.digest
        except FileNotFoundError:
            return False

    def save(self):
        out = self.render()
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_bytes(out)
        tmp.replace(self.path)
        self.digest = hashlib.sha1(out).hexdigest()
        self.saved = copy.deepcopy(self.data)

    def revert(self):
        self.data = copy.deepcopy(self.saved)


def clamp_leader(av: dict):
    """The editor doesn't manage the leader; only keep `leader` a valid index into lineup."""
    leader = av.get("leader")
    n = len(av.get("lineup") or [])
    if isinstance(leader, int) and n and not 0 <= leader < n:
        av["leader"] = n - 1 if leader >= n else 0


# ---------------------------------------------------------------- small stores

class JsonStore:
    def __init__(self, path: Path, default):
        self.path = path
        self.value = read_json(path, None)
        if self.value is None:
            self.value = copy.deepcopy(default)

    def save(self):
        write_json(self.path, self.value)


def load_freesr_owned(paths: Paths) -> set[int]:
    fd = read_json(paths.freesr, {}) or {}
    out = set()
    for k in (fd.get("avatars") or {}):
        try:
            out.add(int(k))
        except ValueError:
            pass
    return out


def load_local_avatars(paths: Paths) -> dict[int, dict]:
    out = {}
    for fn in ("AvatarConfig.json", "AvatarConfigLD.json"):
        for a in read_json(paths.excel / fn, []) or []:
            out[a["AvatarID"]] = {
                "id": a["AvatarID"],
                "tag": a.get("AvatarVOTag", ""),
                "path": a.get("AvatarBaseType", ""),
                "element": a.get("DamageType", ""),
                "rarity": 5 if str(a.get("Rarity", "")).endswith("5") else 4,
            }
    return out


def load_local_skins(paths: Paths) -> list[dict]:
    return [{"id": s["ID"], "avatar_id": s["AvatarID"], "type": s.get("Type", ""),
             "model": s.get("FreeStyleCharacterID", "")}
            for s in read_json(paths.excel / "AvatarSkin.json", []) or []]
