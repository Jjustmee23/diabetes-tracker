@echo off
echo ========================================
echo Diabetes Tracker - Installer Builder
echo ========================================
echo.

REM Controleer of Python geïnstalleerd is
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is niet geïnstalleerd of niet in PATH
    echo 📦 Installeer Python van https://python.org
    pause
    exit /b 1
)

echo ✅ Python gevonden
echo.

REM Vraag versie
set /p version="Voer versie in (bijv. 1.2.0): "

if "%version%"=="" (
    echo ❌ Geen versie ingevoerd
    pause
    exit /b 1
)

echo.
echo 🎯 Maak installer voor versie %version%
echo.

REM Run installer script
python create_installer.py %version%

echo.
echo ✅ Installer build voltooid!
echo.
pause 