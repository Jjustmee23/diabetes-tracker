DIABETES TRACKER - STANDALONE VERSION
===============================================

This is a standalone version of the Diabetes Tracker application.
Created on: 2025-07-15 17:53:18

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
