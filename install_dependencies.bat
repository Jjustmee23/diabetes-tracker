@echo off
echo Diabetes Bloedwaarden Tracker - Dependencies Installatie
echo ======================================================
echo.
echo Dit script installeert alle benodigde Python packages.
echo.
echo Controleer of Python is geïnstalleerd...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is niet geïnstalleerd of niet gevonden in PATH
    echo.
    echo Installeer Python van https://www.python.org/downloads/
    echo Zorg ervoor dat "Add Python to PATH" is aangevinkt tijdens installatie
    echo.
    pause
    exit /b 1
)

echo Python gevonden! Installeer dependencies...
echo.
pip install pandas openpyxl reportlab matplotlib seaborn
if errorlevel 1 (
    echo.
    echo ERROR: Kon dependencies niet installeren
    echo Controleer je internetverbinding en probeer opnieuw
    pause
    exit /b 1
)

echo.
echo Dependencies succesvol geïnstalleerd!
echo Je kunt nu de applicatie starten met: python diabetes_tracker.py
echo of door te dubbelklikken op start_app.bat
echo.
pause 