#!/usr/bin/env python3
"""
Diabetes Tracker - Auto-Start Standalone Executable Generator
Maakt een .exe bestand dat automatisch start zonder .bat bestand.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

def create_auto_start_executable():
    """Maak een standalone executable die automatisch start"""
    
    print("🚀 Diabetes Tracker - Auto-Start Standalone Generator")
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
    
    print("🔧 Maak auto-start standalone executable...")
    
    # PyInstaller commando met auto-start
    cmd = [
        "pyinstaller",
        "--onefile",  # Eén executable bestand
        "--windowed",  # Geen console venster
        "--name=Diabetes_Tracker_Auto",
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
    dist_dir = "Diabetes_Tracker_Auto_Start"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir)
    os.makedirs(os.path.join(dist_dir, "data"))
    os.makedirs(os.path.join(dist_dir, "backups"))
    
    # Kopieer executable
    exe_source = os.path.join("dist", "Diabetes_Tracker_Auto.exe")
    exe_dest = os.path.join(dist_dir, "Diabetes_Tracker.exe")
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Kopieer executable: Diabetes_Tracker.exe")
    else:
        print("❌ Executable niet gevonden in dist/")
        return False
    
    # Maak auto-start script
    auto_start_script = os.path.join(dist_dir, "START_AUTO.bat")
    with open(auto_start_script, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("echo Diabetes Tracker - Auto Start\n")
        f.write("echo ==============================\n")
        f.write("echo.\n")
        f.write("echo Start applicatie automatisch...\n")
        f.write("start Diabetes_Tracker.exe\n")
        f.write("echo Applicatie gestart!\n")
        f.write("timeout /t 2 >nul\n")
        f.write("exit\n")
    
    print(f"✅ Maak auto-start script: START_AUTO.bat")
    
    # Maak direct start script (geen console)
    direct_start = os.path.join(dist_dir, "START_DIRECT.bat")
    with open(direct_start, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("start Diabetes_Tracker.exe\n")
        f.write("exit\n")
    
    print(f"✅ Maak direct start script: START_DIRECT.bat")
    
    # Maak README
    readme_content = """# Diabetes Tracker - Auto-Start Standalone Versie

## 🚀 Hoe te gebruiken:

### Optie 1: Direct starten (aanbevolen)
1. **Dubbelklik op `Diabetes_Tracker.exe`**
2. **De applicatie start direct!**

### Optie 2: Via start script
1. **Dubbelklik op `START_AUTO.bat`**
2. **De applicatie start automatisch**

### Optie 3: Stil starten
1. **Dubbelklik op `START_DIRECT.bat`**
2. **Geen console venster, direct start**

## ✅ Voordelen:
- **Geen Python installatie nodig**
- **Geen dependencies nodig**
- **Werkt op elke Windows computer**
- **Direct starten - geen extra stappen**

## 📁 Bestanden:
- `Diabetes_Tracker.exe` - Standalone applicatie (direct starten)
- `START_AUTO.bat` - Auto-start script
- `START_DIRECT.bat` - Stil starten (geen console)
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
    
    with open(os.path.join(dist_dir, "README_AUTO_START.txt"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Maak README: README_AUTO_START.txt")
    
    # Maak ZIP bestand
    zip_filename = "Diabetes_Tracker_Auto_Start.zip"
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
    if os.path.exists("Diabetes_Tracker_Auto.spec"):
        os.remove("Diabetes_Tracker_Auto.spec")
    
    print("\n" + "=" * 60)
    print("🎉 Auto-start standalone executable succesvol aangemaakt!")
    print("=" * 60)
    print(f"📁 Standalone directory: {dist_dir}")
    print(f"📦 ZIP bestand: {zip_filename}")
    print("\n📋 Volgende stappen:")
    print("1. Kopieer de map naar je USB stick")
    print("2. Dubbelklik direct op Diabetes_Tracker.exe")
    print("3. De applicatie start automatisch!")
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
    print("Diabetes Tracker - Auto-Start Standalone Generator")
    print("=" * 60)
    
    # Controleer PyInstaller
    try:
        import PyInstaller
        create_auto_start_executable()
    except ImportError:
        print("PyInstaller niet gevonden. Installeer automatisch? (j/n)")
        response = input().lower()
        if response in ['j', 'ja', 'y', 'yes']:
            if install_pyinstaller():
                create_auto_start_executable()
        else:
            print("Installeer handmatig met: pip install pyinstaller") 