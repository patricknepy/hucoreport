@echo off
echo.
echo ========================================
echo   BUILD HUCO REPORT - Distribution
echo ========================================
echo.

cd /d "%~dp0"

echo Etape 1/5 : Nettoyage des anciens builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "HucoReport.spec" del "HucoReport.spec"

echo Etape 2/5 : Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo Etape 3/5 : Construction de l'executable avec PyInstaller...
pyinstaller --onedir --windowed --name="HucoReport" --icon=img/cropped-logo-groupe-huco.webp main.py

if %errorlevel% neq 0 (
    echo.
    echo ERREUR : La construction a echoue !
    pause
    exit /b 1
)

echo Etape 4/5 : Copie des fichiers necessaires...
mkdir "dist\HucoReport\config"
mkdir "dist\HucoReport\img"
mkdir "dist\HucoReport\data"
mkdir "dist\HucoReport\import"
mkdir "dist\HucoReport\logs"

copy "config\excel_schema.json" "dist\HucoReport\config\"
copy "img\cropped-logo-groupe-huco.webp" "dist\HucoReport\img\"
echo. > "dist\HucoReport\data\.gitkeep"
echo. > "dist\HucoReport\import\.gitkeep"

echo Etape 5/5 : Creation du README utilisateur...
(
echo # HUCO REPORT - Humans Connexion
echo.
echo ## Installation
echo.
echo 1. Decompressez ce dossier ou vous voulez
echo 2. Double-cliquez sur HucoReport.exe
echo 3. C'est tout !
echo.
echo ## Utilisation
echo.
echo 1. Cliquez sur "Choisir un fichier" pour importer votre fichier Excel
echo 2. Validez la simulation
echo 3. Confirmez l'import
echo 4. Le dashboard se met a jour automatiquement
echo.
echo ## Fichiers importants
echo.
echo - HucoReport.exe : L'application
echo - config/ : Configuration de validation
echo - img/ : Logo de l'application
echo - data/ : Base de donnees SQLite (creee automatiquement^)
echo.
echo ## Securite Windows
echo.
echo Si Windows Defender bloque l'application :
echo 1. Cliquez sur "Plus d'infos" dans l'alerte
echo 2. Cliquez sur "Executer quand meme"
echo C'est normal : l'application n'est pas signee numeriquement.
echo.
echo ## Support
echo.
echo Pour toute question, contactez le service informatique.
echo.
echo ---
echo ^(c^) 2025 Humans Connexion - Tous droits reserves
) > "dist\HucoReport\README.txt"

echo.
echo ========================================
echo   BUILD TERMINE !
echo ========================================
echo.
echo Le dossier "dist\HucoReport" est pret a etre distribue.
echo.
echo Vous pouvez :
echo 1. Le zipper : HucoReport.zip
echo 2. Le copier sur un partage reseau
echo 3. Le distribuer par email
echo.
echo Taille approximative : 150-200 MB
echo.
echo NOTE : Si Windows Defender bloque l'executable :
echo   - C'est normal pour une application non signee
echo   - Les utilisateurs devront cliquer "Executer quand meme"
echo   - Voir le README.txt pour les instructions completes
echo.
pause

