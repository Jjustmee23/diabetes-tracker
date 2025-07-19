@echo off
echo Diabetes Bloedwaarden Tracker
echo =============================
echo.
echo Controleer of Python is geïnstalleerd...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is niet geïnstalleerd of niet gevonden in PATH
    echo Installeer Python van https://www.python.org/downloads/
    echo Zorg ervoor dat "Add Python to PATH" is aangevinkt tijdens installatie
    pause
    exit /b 1
)

echo Python gevonden! Controleer dependencies...
python -c "import pandas, openpyxl, reportlab, matplotlib, seaborn" >nul 2>&1
if errorlevel 1 (
    echo Installeer dependencies...
    pip install pandas openpyxl reportlab matplotlib seaborn
    if errorlevel 1 (
        echo ERROR: Kon dependencies niet installeren
        pause
        exit /b 1
    )
)

echo Start applicatie...
python diabetes_tracker.py
if errorlevel 1 (
    echo ERROR: Er is een fout opgetreden bij het starten van de applicatie
    pause
) 