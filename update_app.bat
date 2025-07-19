@echo off
echo Diabetes Tracker Updater
echo =======================
echo.

echo Controleer Python installatie...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is niet geïnstalleerd
    echo Installeer Python van https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python gevonden! Start updater...
python update_diabetes_tracker.py

if errorlevel 1 (
    echo ERROR: Er is een fout opgetreden bij het updaten
    pause
) else (
    echo Update proces voltooid!
    pause
) 