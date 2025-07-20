#!/usr/bin/env python3
"""
Diabetes Tracker v1.6.0 Installer Creator
Maakt een Windows installer (.exe) voor de Diabetes Tracker
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_installer():
    """Maak installer voor Diabetes Tracker v1.6.0"""
    
    version = "1.6.0"
    installer_name = f"Diabetes_Tracker_Installer_v{version}.exe"
    
    print(f"🚀 Maak installer voor Diabetes Tracker v{version}")
    
    # Check of de main executable bestaat
    exe_path = "dist/Diabetes_Tracker_v1.6.0.exe"
    if not os.path.exists(exe_path):
        print("❌ Fout: Diabetes_Tracker_v1.6.0.exe niet gevonden in dist/")
        print("   Run eerst: pyinstaller diabetes_tracker.spec")
        return False
    
    # Maak installer directory
    installer_dir = f"installer_v{version}"
    if os.path.exists(installer_dir):
        shutil.rmtree(installer_dir)
    os.makedirs(installer_dir)
    
    print(f"📁 Maak installer directory: {installer_dir}")
    
    # Kopieer alle benodigde bestanden
    files_to_copy = [
        (exe_path, f"{installer_dir}/Diabetes_Tracker.exe"),
        ("templates", f"{installer_dir}/templates"),
        ("README.md", f"{installer_dir}/README.md"),
        ("requirements.txt", f"{installer_dir}/requirements.txt")
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dst)
                print(f"📂 Gekopieerd: {src} -> {dst}")
            else:
                shutil.copy2(src, dst)
                print(f"📄 Gekopieerd: {src} -> {dst}")
        else:
            print(f"⚠️ Overgeslagen (niet gevonden): {src}")
    
    # Maak installer README
    installer_readme = f"""# Diabetes Tracker v{version} - Standalone Installer

## 🩺 Diabetes Bloedwaarden Tracker

Een complete diabetes management applicatie zonder Python installatie vereist.

### ✨ Nieuwe Features v{version}:
- 🔥 **Volledig standalone** - geen Python installatie nodig
- ⚡ **Super snelle opstart** - geoptimaliseerd voor prestaties  
- 🧹 **Clean interface** - geen EID afhankelijkheden meer
- 💾 **Draagbaar** - kan vanaf USB stick draaien
- 🔒 **Veilig** - alle data lokaal opgeslagen

### 🚀 Installatie:

1. **Download** `Diabetes_Tracker.exe`
2. **Dubbelklik** om te starten
3. **Klaar!** - geen verdere installatie nodig

### 📋 Features:

- ✅ Bloedwaarden bijhouden
- ✅ Medicatie beheer  
- ✅ Patiënt profielen
- ✅ Grafieken en analytics
- ✅ Data export (Excel, PDF)
- ✅ Automatische backups
- ✅ Update systeem

### 💡 Systeemvereisten:

- Windows 10/11 (64-bit)
- 150MB vrije schijfruimte
- Geen Python installatie nodig!

### 🔧 Ondersteuning:

Voor vragen of problemen:
- GitHub: https://github.com/Jjustmee23/diabetes-tracker
- Issues: https://github.com/Jjustmee23/diabetes-tracker/issues

---
📅 Build: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🔢 Versie: {version}
"""
    
    with open(f"{installer_dir}/INSTALLER_README.md", "w", encoding="utf-8") as f:
        f.write(installer_readme)
    
    # Maak start script voor installer
    start_script = f"""@echo off
title Diabetes Tracker v{version} - Installer
cls
echo.
echo ==========================================
echo    Diabetes Tracker v{version}
echo    Standalone Installer
echo ==========================================
echo.
echo 🩺 Diabetes Bloedwaarden Tracker
echo.
echo ✅ Geen Python installatie nodig
echo ✅ Volledig standalone programma  
echo ✅ Draait direct vanaf elke locatie
echo.
echo Druk op een toets om te starten...
pause >nul

echo.
echo 🚀 Start Diabetes Tracker...
echo.

REM Start de applicatie
Diabetes_Tracker.exe

echo.
echo 👋 Diabetes Tracker afgesloten
echo.
pause
"""
    
    with open(f"{installer_dir}/START_DIABETES_TRACKER.bat", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    # Maak ZIP installer
    zip_name = f"Diabetes_Tracker_Portable_v{version}.zip"
    print(f"📦 Maak ZIP installer: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(installer_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, installer_dir)
                zipf.write(file_path, arc_name)
                print(f"📁 Toegevoegd aan ZIP: {arc_name}")
    
    # File sizes
    exe_size = os.path.getsize(exe_path) / (1024*1024)  # MB
    zip_size = os.path.getsize(zip_name) / (1024*1024)  # MB
    
    print("\n" + "="*60)
    print(f"✅ Installer succesvol gemaakt!")
    print("="*60)
    print(f"📦 ZIP Installer: {zip_name}")
    print(f"📁 Installer Directory: {installer_dir}/")
    print(f"💾 Executable grootte: {exe_size:.1f} MB")
    print(f"📦 ZIP grootte: {zip_size:.1f} MB")
    print(f"🔢 Versie: {version}")
    print("="*60)
    print("\n🚀 Ready voor GitHub Release!")
    print(f"\n1. Upload {zip_name} naar GitHub Release")
    print("2. Voeg release notes toe")
    print("3. Tag als v" + version)
    print("\n🎯 Installatie instructies:")
    print("- Download en extract ZIP")
    print("- Run START_DIABETES_TRACKER.bat")
    print("- Of direct Diabetes_Tracker.exe")
    
    return True

if __name__ == "__main__":
    create_installer() 