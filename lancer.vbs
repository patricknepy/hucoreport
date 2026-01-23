Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Huco_Report 2"
WshShell.Run """C:\Huco_Report 2\venv\Scripts\pythonw.exe"" ""C:\Huco_Report 2\main.py""", 1, False
