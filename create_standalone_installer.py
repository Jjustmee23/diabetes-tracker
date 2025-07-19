#!/usr/bin/env python3
"""
Diabetes Tracker - Standalone Executable Generator
Maakt een .exe bestand dat geen Python installatie nodig heeft.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

def create_standalone_executable():
    """Maak een standalone executable van de diabetes tracker"""
    
    print("🚀 Diabetes Tracker - Standalone Executable Generator")
    print("=" * 60)
    
    # Controleer of PyInstaller geïnstalleerd is
    try:
        import PyInstaller
        print("✅ PyInstaller gevonden")
    except ImportError:
        print("❌ PyInstaller niet gevonden")
        print("Installeer PyInstaller met: pip install pyinstaller")
        return False
    
    # Controleer of we in de juiste directory zijn
    if not os.path.exists("diabetes_tracker.py"):
        print("❌ Fout: diabetes_tracker.py niet gevonden!")
        return False
    
    print("🔧 Maak standalone executable...")
    
    # PyInstaller commando
    cmd = [
        "pyinstaller",
        "--onefile",  # Eén executable bestand
        "--windowed",  # Geen console venster
        "--name=Diabetes_Tracker",
        "--add-data=patient_management.py;.",
        "--add-data=ai_analysis.py;.",
        "--add-data=ai_medication_filler.py;.",
        "--add-data=templates;templates",
        "--hidden-import=tkinter",
        "--hidden-import=pandas",
        "--hidden-import=matplotlib",
        "--hidden-import=seaborn",
        "--hidden-import=reportlab",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=numpy",
        "--hidden-import=openpyxl",
        "--hidden-import=sqlite3",
        "diabetes_tracker.py"
    ]
    
    try:
        print("⏳ Compileer applicatie (kan enkele minuten duren)...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable succesvol aangemaakt!")
        else:
            print("❌ Fout bij maken executable:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Fout: {str(e)}")
        return False
    
    # Maak distributie map
    dist_dir = "Diabetes_Tracker_Standalone"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir)
    os.makedirs(os.path.join(dist_dir, "data"))
    os.makedirs(os.path.join(dist_dir, "backups"))
    
    # Kopieer executable
    exe_source = os.path.join("dist", "Diabetes_Tracker.exe")
    exe_dest = os.path.join(dist_dir, "Diabetes_Tracker.exe")
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Kopieer executable: Diabetes_Tracker.exe")
    else:
        print("❌ Executable niet gevonden in dist/")
        return False
    
    # Maak start script
    start_script = os.path.join(dist_dir, "START_DIABETES_TRACKER.bat")
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("echo Diabetes Tracker - Standalone Versie\n")
        f.write("echo ======================================\n")
        f.write("echo.\n")
        f.write("echo Start applicatie...\n")
        f.write("Diabetes_Tracker.exe\n")
        f.write("echo.\n")
        f.write("echo Applicatie afgesloten\n")
        f.write("pause\n")
    
    print(f"✅ Maak start script: START_DIABETES_TRACKER.bat")
    
    # Maak README
    readme_content = """# Diabetes Tracker - Standalone Versie

## 🚀 Hoe te gebruiken:

1. **Kopieer deze map naar je USB stick**
2. **Dubbelklik op `START_DIABETES_TRACKER.bat`**
3. **De applicatie start direct - GEEN Python nodig!**

## ✅ Voordelen:
- **Geen Python installatie nodig**
- **Geen dependencies nodig**
- **Werkt op elke Windows computer**
- **Direct starten**

## 📁 Bestanden:
- `Diabetes_Tracker.exe` - Standalone applicatie
- `START_DIABETES_TRACKER.bat` - Start script
- `data/` - Database bestanden
- `backups/` - Backup bestanden

## 🔧 Troubleshooting:
- Als de applicatie niet start: Controleer Windows Defender
- Als data niet wordt opgeslagen: Controleer schrijfrechten
- Database wordt automatisch aangemaakt

## 📊 Features:
- Bloedwaarden tracking met datum/tijd pickers
- Medicatie compliance monitoring
- AI analytics en inzichten
- Data export naar Excel/PDF
- Responsive UI die zich aanpast aan schermgrootte
- Automatische backups

## 💾 Data:
- Alle data wordt opgeslagen in de `data/` map
- Backups worden opgeslagen in de `backups/` map
- Data reist mee met de USB stick

---
Gemaakt met ❤️ voor diabetes patiënten
"""
    
    with open(os.path.join(dist_dir, "README_STANDALONE.txt"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Maak README: README_STANDALONE.txt")
    
    # Maak ZIP bestand
    zip_filename = "Diabetes_Tracker_Standalone.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Maak ZIP bestand: {zip_filename}")
    
    # Ruim op
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("Diabetes_Tracker.spec"):
        os.remove("Diabetes_Tracker.spec")
    
    print("\n" + "=" * 60)
    print("🎉 Standalone executable succesvol aangemaakt!")
    print("=" * 60)
    print(f"📁 Standalone directory: {dist_dir}")
    print(f"📦 ZIP bestand: {zip_filename}")
    print("\n📋 Volgende stappen:")
    print("1. Kopieer de map naar je USB stick")
    print("2. Op elke computer: dubbelklik START_DIABETES_TRACKER.bat")
    print("3. De applicatie start direct - GEEN Python nodig!")
    print("\n💡 Tip: Test eerst op je eigen computer!")
    
    return True

def install_pyinstaller():
    """Installeer PyInstaller als het niet geïnstalleerd is"""
    print("📦 Installeer PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller geïnstalleerd!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Kon PyInstaller niet installeren")
        return False

if __name__ == "__main__":
    print("Diabetes Tracker - Standalone Executable Generator")
    print("=" * 60)
    
    # Controleer PyInstaller
    try:
        import PyInstaller
        create_standalone_executable()
    except ImportError:
        print("PyInstaller niet gevonden. Installeer automatisch? (j/n)")
        response = input().lower()
        if response in ['j', 'ja', 'y', 'yes']:
            if install_pyinstaller():
                create_standalone_executable()
        else:
            print("Installeer handmatig met: pip install pyinstaller") 