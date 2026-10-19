import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ICON_PATH = PROJECT_ROOT / "assets" / "icons" / "anjiru_angel_gabriel.ico"
VBS_PATH = PROJECT_ROOT / "Launch-Anjiru-AI.vbs"

ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$StartMenuPath = [Environment]::GetFolderPath("Programs")
$IconLocation = "{str(ICON_PATH)},0"
$VbsTarget = "{str(VBS_PATH)}"
$WscriptExe = "$env:SystemRoot\\System32\\wscript.exe"
$WorkingDir = "{str(PROJECT_ROOT)}"

$ShortcutPaths = @(
    (Join-Path $DesktopPath "Anjiru AI.lnk"),
    (Join-Path $StartMenuPath "Anjiru AI.lnk")
)

foreach ($scPath in $ShortcutPaths) {{
    if (Test-Path $scPath) {{
        Remove-Item $scPath -Force
    }}
    $Shortcut = $WshShell.CreateShortcut($scPath)
    $Shortcut.TargetPath = $WscriptExe
    $Shortcut.Arguments = "//B //Nologo `"$VbsTarget`""
    $Shortcut.WorkingDirectory = $WorkingDir
    $Shortcut.IconLocation = $IconLocation
    $Shortcut.Description = "Anjiru AI - Sovereign African Foundation Intelligence"
    $Shortcut.WindowStyle = 7
    $Shortcut.Save()
    Write-Host "Created shortcut: $scPath"
}}

# Flush icon cache
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class ShellNotifier {{
    [DllImport("shell32.dll")]
    public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);
}}
"@
[ShellNotifier]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
Write-Host "Icon cache refreshed."
'''

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
print(res.stdout.strip())
if res.stderr.strip():
    print("Stderr:", res.stderr.strip())

desktop_lnk = os.path.expanduser(r"~\Desktop\Anjiru AI.lnk")
print("Verified Desktop shortcut exists:", os.path.exists(desktop_lnk))
