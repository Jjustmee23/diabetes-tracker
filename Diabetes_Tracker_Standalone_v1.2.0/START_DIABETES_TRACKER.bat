@echo off
echo Starting Diabetes Tracker...
cd /d "%~dp0"
Diabetes_Tracker.exe
if errorlevel 1 (
    echo Error: Could not start Diabetes_Tracker.exe
    echo Please make sure the file exists in this directory.
    pause
)
