#!/usr/bin/env python3
"""
Draagbare Diabetes Tracker - USB Versie
Dit script maakt de diabetes applicatie draagbaar voor USB gebruik.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

def create_portable_version():
    """Maak een draagbare versie van de diabetes tracker"""
    
    print("🚀 Draagbare Diabetes Tracker - USB Versie Generator")
    print("=" * 60)
    
    # Controleer of we in de juiste directory zijn
    if not os.path.exists("diabetes_tracker.py"):
        print("❌ Fout: diabetes_tracker.py niet gevonden!")
        print("Zorg ervoor dat je dit script in dezelfde map uitvoert als diabetes_tracker.py")
        return False
    
    # Maak portable directory
    portable_dir = "Diabetes_Tracker_Portable"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    os.makedirs(os.path.join(portable_dir, "data"))
    os.makedirs(os.path.join(portable_dir, "backups"))
    
    print(f"📁 Maak portable directory: {portable_dir}")
    
    # Kopieer hoofdbestanden
    files_to_copy = [
        "diabetes_tracker.py",
        "patient_management.py",
        "requirements.txt"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir)
            print(f"✅ Kopieer: {file}")
        else:
            print(f"⚠️  Waarschuwing: {file} niet gevonden")
    
    # Maak start script voor Windows
    start_script = os.path.join(portable_dir, "START_DIABETES_TRACKER.bat")
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("echo Diabetes Tracker - Draagbare Versie\n")
        f.write("echo ======================================\n")
        f.write("echo.\n")
        f.write("echo Controleer Python installatie...\n")
        f.write("python --version >nul 2>&1\n")
        f.write("if errorlevel 1 (\n")
        f.write("    echo ❌ Python is niet geïnstalleerd!\n")
        f.write("    echo Download Python van: https://python.org\n")
        f.write("    pause\n")
        f.write("    exit /b 1\n")
        f.write(")\n")
        f.write("echo ✅ Python gevonden\n")
        f.write("echo.\n")
        f.write("echo Installeer dependencies...\n")
        f.write("pip install -r requirements.txt --quiet\n")
        f.write("if errorlevel 1 (\n")
        f.write("    echo ❌ Kon dependencies niet installeren\n")
        f.write("    pause\n")
        f.write("    exit /b 1\n")
        f.write(")\n")
        f.write("echo ✅ Dependencies geïnstalleerd\n")
        f.write("echo.\n")
        f.write("echo Start Diabetes Tracker...\n")
        f.write("python diabetes_tracker.py\n")
        f.write("echo.\n")
        f.write("echo Applicatie afgesloten\n")
        f.write("pause\n")
    
    print(f"✅ Maak start script: START_DIABETES_TRACKER.bat")
    
    # Maak README voor USB
    readme_content = """# Diabetes Tracker - Draagbare Versie

## 🚀 Hoe te gebruiken:

1. **Kopieer deze map naar je USB stick**
2. **Dubbelklik op `START_DIABETES_TRACKER.bat`**
3. **De applicatie start automatisch**

## 📋 Vereisten:
- Python 3.7+ geïnstalleerd op de computer
- Internet verbinding (alleen voor eerste keer installeren dependencies)

## 📁 Bestanden:
- `diabetes_tracker.py` - Hoofdapplicatie
- `patient_management.py` - Patiënten beheer
- `requirements.txt` - Python dependencies
- `START_DIABETES_TRACKER.bat` - Start script
- `data/` - Database bestanden (worden automatisch aangemaakt)
- `backups/` - Backup bestanden

## 🔧 Troubleshooting:
- Als Python niet gevonden wordt: Download van python.org
- Als dependencies niet installeren: Controleer internet verbinding
- Database wordt automatisch aangemaakt bij eerste gebruik

## 📊 Features:
- Bloedwaarden tracking
- Medicatie compliance
- Patiënten beheer
- Statistieken en grafieken
- Export naar Excel/PDF
- Automatische backups

## 💾 Data:
- Alle data wordt opgeslagen in de `data/` map
- Backups worden opgeslagen in de `backups/` map
- Data reist mee met de USB stick

---
Gemaakt met ❤️ voor diabetes patiënten
"""
    
    with open(os.path.join(portable_dir, "README_USB.txt"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Maak README: README_USB.txt")
    
    # Maak requirements.txt als deze niet bestaat
    if not os.path.exists("requirements.txt"):
        requirements_content = """tkinter
pandas
matplotlib
seaborn
reportlab
ttkbootstrap
numpy
openpyxl
"""
        with open(os.path.join(portable_dir, "requirements.txt"), 'w') as f:
            f.write(requirements_content)
        print(f"✅ Maak requirements.txt")
    
    # Maak ZIP bestand
    zip_filename = "Diabetes_Tracker_Portable.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Maak ZIP bestand: {zip_filename}")
    
    print("\n" + "=" * 60)
    print("🎉 Draagbare versie succesvol aangemaakt!")
    print("=" * 60)
    print(f"📁 Portable directory: {portable_dir}")
    print(f"📦 ZIP bestand: {zip_filename}")
    print("\n📋 Volgende stappen:")
    print("1. Kopieer de map naar je USB stick")
    print("2. Op elke computer: dubbelklik START_DIABETES_TRACKER.bat")
    print("3. De applicatie start automatisch")
    print("\n💡 Tip: Test eerst op je eigen computer!")
    
    return True

def test_portable_version():
    """Test de draagbare versie"""
    print("\n🧪 Test draagbare versie...")
    
    portable_dir = "Diabetes_Tracker_Portable"
    if not os.path.exists(portable_dir):
        print("❌ Portable directory niet gevonden!")
        return False
    
    start_script = os.path.join(portable_dir, "START_DIABETES_TRACKER.bat")
    if not os.path.exists(start_script):
        print("❌ Start script niet gevonden!")
        return False
    
    print("✅ Portable versie gevonden")
    print("✅ Start script gevonden")
    print("✅ Klaar voor USB gebruik!")
    
    return True

if __name__ == "__main__":
    print("Diabetes Tracker - Draagbare Versie Generator")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_portable_version()
    else:
        create_portable_version() 