@echo off
echo Diabetes Tracker v1.2.5 - Installer
echo ======================================
echo.
echo Installeer Python dependencies...
pip install -r requirements.txt
echo.
echo Start Diabetes Tracker...
python diabetes_tracker.py
pause
