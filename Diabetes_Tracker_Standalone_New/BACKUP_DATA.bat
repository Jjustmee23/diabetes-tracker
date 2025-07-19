@echo off
echo Creating backup of Diabetes Tracker data...
echo.

set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Creating backup with timestamp: %TIMESTAMP%

REM Backup database files
if exist "diabetes_data.db" (
    copy "diabetes_data.db" "%BACKUP_DIR%\diabetes_backup_%TIMESTAMP%.db"
    echo Backed up: diabetes_data.db
)

if exist "patient_data.db" (
    copy "patient_data.db" "%BACKUP_DIR%\patient_backup_%TIMESTAMP%.db"
    echo Backed up: patient_data.db
)

echo.
echo Backup completed successfully!
echo Backup files are in the %BACKUP_DIR% folder
pause
