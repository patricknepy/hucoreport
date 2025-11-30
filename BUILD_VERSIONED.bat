@echo off
setlocal enabledelayedexpansion

REM ========================================
REM  BUILD HUCO REPORT - Distribution
REM  Script intelligent avec versioning
REM ========================================

cd /d "%~dp0"

echo.
echo ========================================
echo   BUILD HUCO REPORT v1.0
echo ========================================
echo.

REM Demander le numéro de version
echo Quelle version voulez-vous compiler ?
echo.
echo Versions existantes (Git tags) :
git tag | findstr /R "v[0-9]"
echo.
set /p VERSION="Entrez la version (ex: 1.0.0 ou 1.1.0-beta) : "

if "%VERSION%"=="" (
    echo ERREUR : Aucune version specifiee !
    pause
    exit /b 1
)

echo.
echo Compilation de Huco Report v%VERSION%...
echo.

REM Étape 1 : Nettoyage
echo [1/6] Nettoyage des anciens builds...
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
if exist "HucoReport.spec" del "HucoReport.spec" 2>nul

REM Étape 2 : Activation environnement
echo [2/6] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ERREUR : Impossible d'activer l'environnement virtuel !
    pause
    exit /b 1
)

REM Étape 3 : Mise à jour du numéro de version dans le code
echo [3/6] Mise a jour du numero de version...
powershell -Command "(Get-Content 'src\config\settings.py') -replace 'APP_VERSION = \".*\"', 'APP_VERSION = \"%VERSION%\"' | Set-Content 'src\config\settings.py'"

REM Étape 4 : Build avec PyInstaller
echo [4/6] Construction de l'executable avec PyInstaller...
echo (Cette etape peut prendre 2-3 minutes...)
pyinstaller --noconfirm --onedir --windowed --name="HucoReport" --icon=img/cropped-logo-groupe-huco.webp main.py >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ERREUR : La construction a echoue !
    echo Verifiez que PyInstaller est bien installe : pip install pyinstaller
    pause
    exit /b 1
)

REM Étape 5 : Copie des fichiers
echo [5/6] Copie des fichiers necessaires...
mkdir "dist\HucoReport\config" 2>nul
mkdir "dist\HucoReport\img" 2>nul
mkdir "dist\HucoReport\data" 2>nul
mkdir "dist\HucoReport\import" 2>nul

copy "config\excel_schema.json" "dist\HucoReport\config\" >nul
copy "img\cropped-logo-groupe-huco.webp" "dist\HucoReport\img\" >nul
echo. > "dist\HucoReport\data\.gitkeep"
echo. > "dist\HucoReport\import\.gitkeep"

REM Étape 6 : Renommage avec version
echo [6/6] Renommage du dossier de distribution...
if exist "dist\HucoReport_v%VERSION%" rmdir /s /q "dist\HucoReport_v%VERSION%"
ren "dist\HucoReport" "HucoReport_v%VERSION%"

REM Création du README utilisateur
(
echo ====================================
echo   HUCO REPORT v%VERSION%
echo   Humans Connexion
echo ====================================
echo.
echo ## INSTALLATION
echo.
echo 1. Decompressez ce dossier ou vous voulez
echo 2. Double-cliquez sur HucoReport.exe
echo 3. C'est tout !
echo.
echo ## UTILISATION
echo.
echo 1. Cliquez sur "Choisir un fichier" pour importer votre fichier Excel
echo 2. Validez la simulation
echo 3. Confirmez l'import
echo 4. Le dashboard se met a jour automatiquement
echo.
echo ## DOSSIERS
echo.
echo - HucoReport.exe  : L'application
echo - _internal/      : Dependances (ne pas modifier^)
echo - config/         : Configuration de validation
echo - img/            : Logo de l'application
echo - data/           : Base de donnees SQLite (creee automatiquement^)
echo - import/         : Fichiers Excel importes (avec historique^)
echo.
echo ## SUPPORT
echo.
echo Pour toute question, contactez Patrick ou le service informatique.
echo.
echo ---
echo Version : %VERSION%
echo Date de build : %DATE% %TIME%
echo ^(c^) 2025 Humans Connexion - Tous droits reserves
) > "dist\HucoReport_v%VERSION%\README.txt"

REM Succès
echo.
echo ========================================
echo   BUILD TERMINE !
echo ========================================
echo.
echo Version compilee : v%VERSION%
echo Dossier cree     : dist\HucoReport_v%VERSION%\
echo.
echo PROCHAINES ETAPES :
echo.
echo   [PRE-PROD] Pour tests internes :
echo   1. Zipper le dossier : HucoReport_v%VERSION%-beta.zip
echo   2. Distribuer a 2-3 testeurs
echo   3. Collecter feedback pendant 3-5 jours
echo.
echo   [PRODUCTION] Apres validation :
echo   1. Zipper le dossier : HucoReport_v%VERSION%.zip
echo   2. Distribuer a toute l'equipe
echo   3. Mettre a jour CHANGELOG.md
echo   4. Creer le tag Git : git tag -a v%VERSION% -m "Release %VERSION%"
echo.
echo Taille approximative : 200-250 MB
echo.
pause

