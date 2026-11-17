"""Create Windows shortcuts (.lnk) to Starfroster on the Desktop / Start menu.

Uses PowerShell + WScript.Shell: works the same from source and from the packaged exe,
and PowerShell is allowed to write into the Desktop even with Controlled Folder Access on.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000
NAME = "Starfroster"


def _target() -> tuple[str, str, str]:
    """(target exe, arguments, working dir) for the shortcut."""
    if getattr(sys, "frozen", False):                    # packaged: Starfroster.exe
        exe = Path(sys.executable)
        return str(exe), "", str(exe.parent)
    root = Path(__file__).resolve().parent.parent        # source: pythonw "<script>.pyw"
    script = next(root.glob("*.pyw"))
    pyw = Path(sys.executable).with_name("pythonw.exe")
    return str(pyw if pyw.exists() else sys.executable), f'"{script}"', str(root)


def _icon() -> str:
    if getattr(sys, "frozen", False):                    # the exe has the icon embedded
        return sys.executable
    ico = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
    if ico.exists():
        return str(ico)
    return _target()[0]


def _ps_quote(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def create(where: str, folder_override: str | None = None) -> str:
    """where: 'desktop' or 'startmenu'. Returns the .lnk path; raises on failure."""
    folder = {"desktop": "[Environment]::GetFolderPath('Desktop')",
              "startmenu": "[Environment]::GetFolderPath('Programs')"}[where]
    if folder_override:                                  # tests
        folder = _ps_quote(folder_override)
    target, args, workdir = _target()
    script = f"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = {folder}
$lnk = Join-Path $dir {_ps_quote(NAME + '.lnk')}
$s = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$s.TargetPath = {_ps_quote(target)}
$s.Arguments = {_ps_quote(args)}
$s.WorkingDirectory = {_ps_quote(workdir)}
$s.IconLocation = {_ps_quote(_icon() + ',0')}
$s.Description = {_ps_quote('ppSR persistent.json editor')}
$s.Save()
Write-Output $lnk
"""
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                        "-Command", script],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       creationflags=CREATE_NO_WINDOW, timeout=30)
    out = (r.stdout or "").strip().splitlines()
    if r.returncode != 0 or not out or not Path(out[-1]).exists():
        raise RuntimeError((r.stderr or r.stdout or "unknown error").strip()[:300])
    return out[-1]
