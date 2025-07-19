@echo off
echo ========================================
echo Diabetes Tracker Standalone Restore
echo ========================================

:: Controleer of nieuwe standalone versie bestaat
if not exist "Diabetes_Tracker_Standalone" (
    echo ERROR: Diabetes_Tracker_Standalone directory niet gevonden!
    echo Zorg ervoor dat de nieuwe versie is geïnstalleerd.
    pause
    exit /b 1
)

:: Toon beschikbare database backups
echo Beschikbare database backups:
dir backup_databases\*.db /B 2>nul
echo.

:: Vraag gebruiker welke backup te gebruiken
set /p BACKUP_CHOICE="Welke backup wil je gebruiken? (bijv. diabetes_data_20250715_143022.db): "

if not exist "backup_databases\%BACKUP_CHOICE%" (
    echo ERROR: Backup bestand niet gevonden: %BACKUP_CHOICE%
    pause
    exit /b 1
)

:: Kopieer database bestanden naar nieuwe versie
echo Kopieer database bestanden naar nieuwe versie...

:: Maak data directory als deze niet bestaat
if not exist "Diabetes_Tracker_Standalone\data" mkdir "Diabetes_Tracker_Standalone\data"

:: Kopieer diabetes data
if exist "backup_databases\%BACKUP_CHOICE%" (
    copy "backup_databases\%BACKUP_CHOICE%" "Diabetes_Tracker_Standalone\data\diabetes_data.db" /Y
    echo Diabetes data gerestaureerd
)

:: Zoek bijbehorende patient data backup
set PATIENT_BACKUP=%BACKUP_CHOICE:diabetes_data=patient_data%
if exist "backup_databases\%PATIENT_BACKUP%" (
    copy "backup_databases\%PATIENT_BACKUP%" "Diabetes_Tracker_Standalone\data\patient_data.db" /Y
    echo Patient data gerestaureerd
)

echo.
echo ========================================
echo Restore voltooid!
echo ========================================
echo Database bestanden zijn gerestaureerd naar de nieuwe versie.
echo Je kunt nu de applicatie starten.
echo.
pause 