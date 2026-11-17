"""Checks whether ppsr.exe is running and restarts it."""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_CONSOLE = 0x00000010


def is_running(name="ppsr.exe") -> bool:
    try:
        out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH", "/FO", "CSV"],
                             capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=10).stdout
    except Exception:
        return False
    return f'"{name.lower()}"' in out.lower()


def restart(exe: Path):
    """Kill every ppsr.exe, then start exe in its own folder with its own console window."""
    if not exe.exists():
        raise FileNotFoundError(str(exe))
    subprocess.run(["taskkill", "/IM", exe.name, "/F"], capture_output=True, creationflags=CREATE_NO_WINDOW,
                   timeout=15)
    for _ in range(30):                     # wait up to ~3 s for the process to go away
        if not is_running(exe.name):
            break
        time.sleep(0.1)
    subprocess.Popen([str(exe)], cwd=str(exe.parent), creationflags=CREATE_NEW_CONSOLE)
