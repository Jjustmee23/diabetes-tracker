@echo off
echo Starting Diabetes Tracker...
cd /d "%~dp0"
if exist "Diabetes_Tracker.exe" (
    Diabetes_Tracker.exe
) else (
    echo Error: Diabetes_Tracker.exe not found!
    echo Please make sure the file exists in this directory.
    pause
    exit /b 1
)
