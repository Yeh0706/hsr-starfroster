"""Checks GitHub Releases for a newer Starfroster version (notify only; nothing is downloaded or replaced)."""
from __future__ import annotations

import json
import re
import urllib.request

from . import __version__, REPO_URL

API = REPO_URL.replace("https://github.com/", "https://api.github.com/repos/") + "/releases/latest"


def parse_version(s: str) -> tuple[int, ...]:
    """'v1.2.3' / '1.2' -> (1, 2, 3) / (1, 2, 0)."""
    nums = [int(n) for n in re.findall(r"\d+", s or "")[:3]]
    return tuple(nums + [0] * (3 - len(nums)))


def check_latest(timeout=10) -> dict:
    """Returns {'newer': bool, 'version', 'url', 'notes'}; raises on network errors."""
    req = urllib.request.Request(API, headers={"User-Agent": f"Starfroster/{__version__}",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        rel = json.loads(r.read().decode("utf-8"))
    tag = rel.get("tag_name", "")
    return {
        "newer": parse_version(tag) > parse_version(__version__),
        "version": tag.lstrip("vV") or "?",
        "url": rel.get("html_url") or REPO_URL + "/releases",
        "notes": (rel.get("body") or "").strip(),
    }
