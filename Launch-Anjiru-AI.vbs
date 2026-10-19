' Launch-Anjiru-AI.vbs
' Zero console window / silent desktop launcher for Anjiru AI
Option Explicit

Dim WshShell, fso, scriptDir, pythonwExe, desktopPy

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
desktopPy = scriptDir & "\run_desktop.py"

pythonwExe = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe"
If Not fso.FileExists(pythonwExe) Then
    pythonwExe = "pythonw.exe"
End If

WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & pythonwExe & """ """ & desktopPy & """", 0, False

WScript.Quit 0
