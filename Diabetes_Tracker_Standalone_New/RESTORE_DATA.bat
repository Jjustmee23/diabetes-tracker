@echo off
echo Restoring Diabetes Tracker data from backup...
echo.

set BACKUP_DIR=backups

if not exist "%BACKUP_DIR%" (
    echo Error: No backups directory found
    pause
    exit /b 1
)

echo Available backups:
dir "%BACKUP_DIR%\*.db" /b

echo.
set /p BACKUP_FILE="Enter backup filename (e.g., diabetes_backup_20241215_143022.db): "

if not exist "%BACKUP_DIR%\%BACKUP_FILE%" (
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
copy "%BACKUP_DIR%\%BACKUP_FILE%" "diabetes_data.db"
echo Restore completed!

pause
