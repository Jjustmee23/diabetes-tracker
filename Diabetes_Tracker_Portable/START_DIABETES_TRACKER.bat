@echo off
echo Diabetes Tracker - Draagbare Versie
echo ======================================
echo.
echo Controleer Python installatie...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is niet geïnstalleerd!
    echo Download Python van: https://python.org
    pause
    exit /b 1
)
echo ✅ Python gevonden
echo.
echo Installeer dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Kon dependencies niet installeren
    pause
    exit /b 1
)
echo ✅ Dependencies geïnstalleerd
echo.
echo Start Diabetes Tracker...
python diabetes_tracker.py
echo.
echo Applicatie afgesloten
pause
