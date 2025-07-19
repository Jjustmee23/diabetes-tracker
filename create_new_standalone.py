#!/usr/bin/env python3
"""
Create a new standalone version of the Diabetes Tracker application.
This script copies all necessary files and creates a self-contained package.
"""

import os
import shutil
import zipfile
from datetime import datetime
import sys

def create_standalone():
    """Create a new standalone version of the diabetes tracker."""
    
    # Define source and destination directories
    source_dir = "."
    standalone_dir = "Diabetes_Tracker_Standalone_New"
    
    # Files to copy
    files_to_copy = [
        "diabetes_tracker.py",
        "patient_management.py", 
        "ai_analysis.py",
        "ai_medication_filler.py",
        "requirements.txt"
    ]
    
    # Directories to copy
    dirs_to_copy = [
        "templates"
    ]
    
    print("Creating new standalone version...")
    
    # Remove existing standalone directory if it exists
    if os.path.exists(standalone_dir):
        shutil.rmtree(standalone_dir)
        print(f"Removed existing {standalone_dir}")
    
    # Create new standalone directory
    os.makedirs(standalone_dir)
    os.makedirs(os.path.join(standalone_dir, "data"))
    os.makedirs(os.path.join(standalone_dir, "backups"))
    
    print(f"Created directory: {standalone_dir}")
    
    # Copy main files
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, standalone_dir)
            print(f"Copied: {file}")
        else:
            print(f"Warning: {file} not found")
    
    # Copy directories
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(standalone_dir, dir_name))
            print(f"Copied directory: {dir_name}")
        else:
            print(f"Warning: {dir_name} directory not found")
    
    # Copy database files if they exist
    db_files = ["diabetes_data.db", "patient_data.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            shutil.copy2(db_file, standalone_dir)
            print(f"Copied database: {db_file}")
    
    # Create start script
    start_script = f"""@echo off
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
"""
    
    with open(os.path.join(standalone_dir, "START_DIABETES_TRACKER.bat"), "w") as f:
        f.write(start_script)
    
    # Create README
    readme_content = f"""DIABETES TRACKER - STANDALONE VERSION
===============================================

This is a standalone version of the Diabetes Tracker application.
Created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FEATURES:
- Blood glucose tracking with date/time pickers
- Medication compliance monitoring
- AI-powered analytics and insights
- Data export to Excel and PDF
- Responsive UI that adapts to screen size
- Automatic data backup system
- No internet connection required

HOW TO USE:
1. Double-click "START_DIABETES_TRACKER.bat" to launch the application
2. The app will automatically install required dependencies if needed
3. Your data is stored locally in the database files
4. Backups are automatically created in the backups/ folder

REQUIREMENTS:
- Python 3.7 or higher
- Windows 10/11 (tested on Windows 10)

FILES:
- diabetes_tracker.py: Main application
- patient_management.py: Patient data management
- ai_analysis.py: AI analytics module
- ai_medication_filler.py: Medication tracking
- requirements.txt: Python dependencies
- templates/: HTML templates for exports
- data/: Application data directory
- backups/: Automatic backup files

TROUBLESHOOTING:
- If the app doesn't start, check that Python is installed
- If you get import errors, run: pip install -r requirements.txt
- Data is automatically backed up, but you can manually copy the .db files

For support or questions, check the main README.md file.
"""
    
    with open(os.path.join(standalone_dir, "README_STANDALONE.txt"), "w") as f:
        f.write(readme_content)
    
    # Create backup script
    backup_script = f"""@echo off
echo Creating backup of Diabetes Tracker data...
echo.

set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Creating backup with timestamp: %TIMESTAMP%

REM Backup database files
if exist "diabetes_data.db" (
    copy "diabetes_data.db" "%BACKUP_DIR%\\diabetes_backup_%TIMESTAMP%.db"
    echo Backed up: diabetes_data.db
)

if exist "patient_data.db" (
    copy "patient_data.db" "%BACKUP_DIR%\\patient_backup_%TIMESTAMP%.db"
    echo Backed up: patient_data.db
)

echo.
echo Backup completed successfully!
echo Backup files are in the %BACKUP_DIR% folder
pause
"""
    
    with open(os.path.join(standalone_dir, "BACKUP_DATA.bat"), "w") as f:
        f.write(backup_script)
    
    # Create restore script
    restore_script = f"""@echo off
echo Restoring Diabetes Tracker data from backup...
echo.

set BACKUP_DIR=backups

if not exist "%BACKUP_DIR%" (
    echo Error: No backups directory found
    pause
    exit /b 1
)

echo Available backups:
dir "%BACKUP_DIR%\\*.db" /b

echo.
set /p BACKUP_FILE="Enter backup filename (e.g., diabetes_backup_20241215_143022.db): "

if not exist "%BACKUP_DIR%\\%BACKUP_FILE%" (
    echo Error: Backup file not found
    pause
    exit /b 1
)

echo.
echo WARNING: This will overwrite current data!
set /p CONFIRM="Are you sure? (y/N): "

if /i not "%CONFIRM%"=="y" (
    echo Restore cancelled
    pause
    exit /b 0
)

echo Restoring from backup...
copy "%BACKUP_DIR%\\%BACKUP_FILE%" "diabetes_data.db"
echo Restore completed!

pause
"""
    
    with open(os.path.join(standalone_dir, "RESTORE_DATA.bat"), "w") as f:
        f.write(restore_script)
    
    print(f"\nStandalone version created successfully in: {standalone_dir}")
    print("\nFiles created:")
    print("- START_DIABETES_TRACKER.bat (launcher)")
    print("- BACKUP_DATA.bat (manual backup)")
    print("- RESTORE_DATA.bat (restore from backup)")
    print("- README_STANDALONE.txt (instructions)")
    
    # Create ZIP file
    zip_filename = f"Diabetes_Tracker_Standalone_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(standalone_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, standalone_dir)
                zipf.write(file_path, arcname)
    
    print(f"\nCreated ZIP archive: {zip_filename}")
    print(f"\nStandalone version is ready!")
    print(f"Location: {os.path.abspath(standalone_dir)}")
    print(f"ZIP file: {os.path.abspath(zip_filename)}")

if __name__ == "__main__":
    create_standalone() 