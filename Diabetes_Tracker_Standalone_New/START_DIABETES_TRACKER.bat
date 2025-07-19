@echo off
echo Starting Diabetes Tracker Standalone...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter, ttkbootstrap, pandas, matplotlib, seaborn" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting application...
python diabetes_tracker.py

if errorlevel 1 (
    echo.
    echo Application crashed or encountered an error
    pause
)
