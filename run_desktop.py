"""
run_desktop.py - Standalone Desktop Launcher for Anjiru AI Sovereign Workbench
Launches Anjiru AI in a dedicated, native application window without browser URL bars, tabs, or bookmarks.
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def is_server_ready(port: int = 7860) -> bool:
    """Verifies that the server is not only bound to port, but actively serving HTTP 200 responses."""
    import urllib.request
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/", headers={"User-Agent": "AnjiruLauncher/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_server_background():
    if not is_server_ready():
        server_script = PROJECT_ROOT / "app.py"
        py_exe = sys.executable
        if os.name == "nt":
            import shutil
            pw = shutil.which("pythonw")
            if pw:
                py_exe = pw
            else:
                pythonw = Path(sys.exec_prefix) / "pythonw.exe"
                if pythonw.exists():
                    py_exe = str(pythonw)

        startupinfo = None
        flags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            flags = subprocess.CREATE_NO_WINDOW | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
                flags |= subprocess.CREATE_NEW_PROCESS_GROUP

        subprocess.Popen(
            [py_exe, str(server_script)],
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=flags
        )

        # Wait until server is fully initialized and responding with HTTP 200 (up to 15s)
        for _ in range(30):
            if is_server_ready():
                break
            time.sleep(0.5)

def find_browser_app_executable():
    """Locate Chrome, Edge, or Brave on Windows for native standalone app mode."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def launch_desktop_window():
    start_server_background()
    url = "http://127.0.0.1:7860"
    browser_exe = find_browser_app_executable()

    if browser_exe:
        app_profile_dir = Path(os.environ.get("LOCALAPPDATA", PROJECT_ROOT)) / "AnjiruAI" / "AppProfile"
        app_profile_dir.mkdir(parents=True, exist_ok=True)

        args = [
            browser_exe,
            f"--app={url}",
            f"--user-data-dir={str(app_profile_dir)}",
            "--window-size=1440,900",
            "--window-name=Anjiru AI",
            "--app-id=AnjiruAI",
            "--class=AnjiruAI",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
        subprocess.Popen(args, startupinfo=startupinfo)
    else:
        import webbrowser
        webbrowser.open(url)

if __name__ == "__main__":
    launch_desktop_window()
