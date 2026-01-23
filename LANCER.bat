@echo off
echo.
echo ========================================
echo   HUCO REPORT - Humans Connexion
echo ========================================
echo.
echo Demarrage de l'application...
echo.

cd /d "%~dp0"

REM Lancer le .exe portable (fonctionne sur tous les PC)
if exist "dist\HucoReport\HucoReport.exe" (
    start "" "dist\HucoReport\HucoReport.exe"
    exit
)

REM Fallback: environnement virtuel local (pour developpement)
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
    pause
    exit
)

REM Fallback: Python systeme
python main.py
pause

