#!/usr/bin/env python3
"""
Script om GitHub repository aan te maken en bestanden te committen
Gebruik: python setup_github_repo.py [repository-name] [description]
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def create_gitignore():
    """Maak .gitignore bestand"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Application specific
*.db
*.sqlite
*.sqlite3
backups/
temp_update/
*.log

# Standalone builds
Diabetes_Tracker_Standalone/
Diabetes_Tracker_Auto_Start/
*.exe
*.zip

# Release files
release_v*/
RELEASE_NOTES_v*.txt
GITHUB_RELEASE_INSTRUCTIONS_v*.txt
Diabetes_Tracker_*_v*.zip

# Test files
test_*.db
test_*.xlsx
test_*.pdf
tesd.xlsx
pg.pdf
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ .gitignore aangemaakt")

def create_readme():
    """Maak README.md bestand"""
    readme_content = """# 🩸 Diabetes Tracker Applicatie

Een moderne desktop applicatie voor het bijhouden van diabetes gegevens, ontwikkeld in Python met Tkinter.

## 🚀 Features

- **📊 Bloedglucose Tracking** - Dagelijkse metingen bijhouden
- **💊 Medicatie Compliance** - Medicatie inname registreren
- **📈 Analytics** - Grafieken en statistieken
- **📤 Export** - Data exporteren naar Excel en PDF
- **🤖 AI Analytics** - Intelligente data analyse
- **🔄 Auto Updates** - Automatische updates via GitHub
- **💾 Database Backup** - Automatische backups
- **📱 Responsive UI** - Moderne gebruikersinterface

## 🛠️ Installatie

### Voor Ontwikkelaars
```bash
# Clone repository
git clone https://github.com/[username]/diabetes-tracker.git
cd diabetes-tracker

# Installeer dependencies
pip install -r requirements.txt

# Start applicatie
python diabetes_tracker.py
```

### Voor Patiënten
1. Download de laatste release van GitHub
2. Extract het ZIP bestand
3. Dubbelklik op `Diabetes_Tracker.exe` (Auto-Start versie)
4. Of dubbelklik op `START_DIABETES_TRACKER.bat` (Standalone versie)

## 📦 Standalone Versies

### Auto-Start Versie (Aanbevolen)
- `Diabetes_Tracker_Auto_Start/`
- Start direct met dubbelklikken op .exe
- Geen extra stappen nodig

### Klassieke Standalone
- `Diabetes_Tracker_Standalone/`
- Start via batch bestand
- Meer controle over start proces

## 🔄 Update Systeem

De applicatie controleert automatisch op updates via GitHub releases:

1. **Automatische Check** - Elke 7 dagen
2. **Update Melding** - Popup met nieuwe features
3. **Automatische Download** - Van GitHub releases
4. **Database Behoud** - Data blijft altijd behouden
5. **Backup** - Automatische backup voor updates

## 📊 Database

- **SQLite Database** - `diabetes_data.db`
- **Automatische Backups** - In `backups/` map
- **Data Behoud** - Bij updates en herinstallaties

## 🎯 Gebruik

### Patiënt Gegevens
- Voeg nieuwe patiënten toe
- Bewerk patiënt informatie
- Verwijder patiënten (met bevestiging)

### Bloedglucose Metingen
- Dagelijkse metingen invoeren
- Tijd en datum selectie
- Activiteit en opmerkingen
- Automatische berekeningen

### Medicatie Compliance
- Medicatie inname registreren
- Compliance tracking
- Herinneringen

### Analytics & Export
- Grafieken en statistieken
- Export naar Excel (.xlsx)
- Export naar PDF
- AI-gebaseerde analyse

## 🛠️ Ontwikkeling

### Dependencies
```
tkinter
ttkbootstrap
matplotlib
pandas
openpyxl
reportlab
requests
```

### Project Structuur
```
diabetes-tracker/
├── diabetes_tracker.py      # Hoofdapplicatie
├── patient_management.py    # Patiënt management
├── update_system.py         # Update systeem
├── templates/               # HTML templates
├── backups/                 # Database backups
├── requirements.txt         # Python dependencies
└── README.md               # Deze file
```

### Build Scripts
- `create_standalone.py` - Maak standalone versie
- `create_github_release.py` - Maak GitHub release
- `setup_github_repo.py` - Repository setup

## 🔒 Privacy & Beveiliging

- **Lokale Opslag** - Alle data lokaal opgeslagen
- **Geen Cloud** - Geen externe servers
- **Database Encryptie** - SQLite met beveiliging
- **Backup Beveiliging** - Versleutelde backups

## 📞 Support

Voor vragen of problemen:
- **GitHub Issues** - Maak issue aan in repository
- **Documentation** - Check deze README
- **Release Notes** - Bekijk GitHub releases

## 📄 Licentie

Dit project is ontwikkeld voor medisch gebruik. Neem contact op voor licentie informatie.

---

**🩸 Diabetes Tracker v1.1.0** - Ontwikkeld voor betere diabetes management
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ README.md aangemaakt")

def setup_git_repository(repo_name, description=""):
    """Setup Git repository en eerste commit"""
    try:
        # Initialiseer Git repository
        print("🔧 Initialiseer Git repository...")
        subprocess.run(['git', 'init'], check=True)
        
        # Maak .gitignore en README
        create_gitignore()
        create_readme()
        
        # Voeg alle bestanden toe
        print("📁 Voeg bestanden toe aan Git...")
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Eerste commit
        print("💾 Maak eerste commit...")
        commit_message = f"Initial commit: {repo_name}\n\n{description}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        print("✅ Git repository succesvol opgezet!")
        print(f"📋 Repository naam: {repo_name}")
        print(f"📝 Beschrijving: {description}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_next_steps(repo_name):
    """Toon volgende stappen voor GitHub setup"""
    print("\n🚀 Volgende Stappen voor GitHub:")
    print("=" * 50)
    print("1. Ga naar https://github.com/new")
    print(f"2. Repository naam: {repo_name}")
    print("3. Beschrijving: Diabetes Tracker Applicatie")
    print("4. Kies 'Public' of 'Private'")
    print("5. Klik 'Create repository'")
    print("6. Voer deze commando's uit:")
    print()
    print(f"   git remote add origin https://github.com/[username]/{repo_name}.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("7. Update update_system.py regel 28:")
    print(f"   self.github_repo = '[username]/{repo_name}'")
    print()
    print("🎉 Dan kun je updates uitrollen via GitHub releases!")

def main():
    if len(sys.argv) < 2:
        print("Gebruik: python setup_github_repo.py [repository-name] [description]")
        print("Voorbeeld: python setup_github_repo.py diabetes-tracker 'Diabetes management applicatie'")
        return
    
    repo_name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else "Diabetes Tracker Applicatie"
    
    print(f"🎯 Setup GitHub repository: {repo_name}")
    print(f"📝 Beschrijving: {description}")
    print()
    
    if setup_git_repository(repo_name, description):
        show_next_steps(repo_name)
    else:
        print("❌ Repository setup mislukt")

if __name__ == "__main__":
    main() 