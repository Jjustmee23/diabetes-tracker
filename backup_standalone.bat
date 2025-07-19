@echo off
echo ========================================
echo Diabetes Tracker Standalone Backup
echo ========================================

:: Maak backup directory met timestamp
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=backup_standalone_%TIMESTAMP%

echo Maak backup directory: %BACKUP_DIR%
mkdir %BACKUP_DIR%

:: Kopieer hele standalone directory
echo Kopieer standalone applicatie...
xcopy "Diabetes_Tracker_Standalone" "%BACKUP_DIR%\Diabetes_Tracker_Standalone" /E /I /Y

:: Kopieer database bestanden naar aparte locatie
echo Kopieer database bestanden...
if not exist "backup_databases" mkdir backup_databases
copy "Diabetes_Tracker_Standalone\data\diabetes_data.db" "backup_databases\diabetes_data_%TIMESTAMP%.db" /Y
copy "Diabetes_Tracker_Standalone\data\patient_data.db" "backup_databases\patient_data_%TIMESTAMP%.db" /Y

:: Kopieer andere belangrijke bestanden
if exist "diabetes_data.db" copy "diabetes_data.db" "backup_databases\diabetes_data_main_%TIMESTAMP%.db" /Y
if exist "patient_data.db" copy "patient_data.db" "backup_databases\patient_data_main_%TIMESTAMP%.db" /Y

echo.
echo ========================================
echo Backup voltooid!
echo ========================================
echo Backup directory: %BACKUP_DIR%
echo Database backups: backup_databases\
echo.
echo Je kunt nu veilig de oude versie verwijderen
echo en de nieuwe versie installeren.
echo.
pause 