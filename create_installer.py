#!/usr/bin/env python3
"""
Script om de Diabetes Tracker .exe te maken en een installer te genereren
Gebruik: python create_installer.py [version]
"""

import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime

def check_dependencies():
    """Controleer of PyInstaller geïnstalleerd is"""
    try:
        import PyInstaller
        print("✅ PyInstaller is geïnstalleerd")
        return True
    except ImportError:
        print("❌ PyInstaller niet gevonden")
        print("📦 Installeer PyInstaller:")
        print("   pip install pyinstaller")
        return False

def install_pyinstaller():
    """Installeer PyInstaller als het niet aanwezig is"""
    print("📦 Installeer PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller succesvol geïnstalleerd")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fout bij installeren PyInstaller: {e}")
        return False

def create_exe(version):
    """Maak de .exe file met PyInstaller"""
    print(f"🔨 Maak .exe voor versie {version}...")
    
    # PyInstaller commando
    cmd = [
        "pyinstaller",
        "--onefile",                    # Één .exe bestand
        "--windowed",                   # Geen console window
        "--name=Diabetes_Tracker",      # Naam van .exe
        "--add-data=templates;templates", # Templates toevoegen
        "--hidden-import=tkinter",      # Verborgen imports
        "--hidden-import=ttkbootstrap",
        "--hidden-import=matplotlib",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=reportlab",
        "diabetes_tracker.py"           # Hoofdbestand
    ]
    
    # Voeg icon toe als het bestaat
    if os.path.exists("templates/favicon.ico"):
        cmd.insert(3, "--icon=templates/favicon.ico")
    
    try:
        print("🚀 Start PyInstaller build...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ .exe succesvol gemaakt!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fout bij maken .exe: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_standalone_package(version):
    """Maak standalone package met .exe en alle benodigde bestanden"""
    print(f"📦 Maak standalone package voor versie {version}...")
    
    # Maak standalone directory
    standalone_dir = f"Diabetes_Tracker_Standalone_v{version}"
    if os.path.exists(standalone_dir):
        shutil.rmtree(standalone_dir)
    os.makedirs(standalone_dir)
    
    # Kopieer .exe file
    exe_source = "dist/Diabetes_Tracker.exe"
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, standalone_dir)
        print("✅ .exe gekopieerd")
    else:
        print("❌ .exe niet gevonden in dist/")
        return False
    
    # Kopieer templates
    if os.path.exists("templates"):
        shutil.copytree("templates", os.path.join(standalone_dir, "templates"))
        print("✅ Templates gekopieerd")
    
    # Maak data directory
    data_dir = os.path.join(standalone_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Maak backup directory
    backup_dir = os.path.join(standalone_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Maak start script
    start_script = os.path.join(standalone_dir, "START_DIABETES_TRACKER.bat")
    with open(start_script, 'w') as f:
        f.write("@echo off\n")
        f.write("echo Starting Diabetes Tracker...\n")
        f.write("Diabetes_Tracker.exe\n")
        f.write("pause\n")
    print("✅ Start script gemaakt")
    
    # Maak README
    readme_file = os.path.join(standalone_dir, "README.txt")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("Diabetes Tracker - Standalone Versie\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Versie: {version}\n")
        f.write(f"Released: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Installatie:\n")
        f.write("1. Extract alle bestanden naar een map\n")
        f.write("2. Dubbelklik op START_DIABETES_TRACKER.bat\n")
        f.write("3. Of dubbelklik direct op Diabetes_Tracker.exe\n\n")
        f.write("Data wordt opgeslagen in de data/ map\n")
        f.write("Backups worden gemaakt in de backups/ map\n\n")
        f.write("Voor ondersteuning, neem contact op met de ontwikkelaar.\n")
    print("✅ README gemaakt")
    
    return standalone_dir

def create_installer(standalone_dir, version):
    """Maak installer ZIP bestand"""
    print(f"🗜️ Maak installer ZIP...")
    
    installer_zip = f"Diabetes_Tracker_Installer_v{version}.zip"
    
    with zipfile.ZipFile(installer_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(standalone_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, standalone_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Installer gemaakt: {installer_zip}")
    return installer_zip

def cleanup_build_files():
    """Ruim build bestanden op"""
    print("🧹 Ruim build bestanden op...")
    
    # Verwijder build en dist directories
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ {dir_name}/ verwijderd")
    
    # Verwijder .spec bestand
    spec_file = "Diabetes_Tracker.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"✅ {spec_file} verwijderd")

def main():
    if len(sys.argv) < 2:
        print("Gebruik: python create_installer.py [version]")
        print("Voorbeeld: python create_installer.py 1.2.0")
        return
    
    version = sys.argv[1]
    
    print(f"🎯 Maak installer voor Diabetes Tracker v{version}")
    print("=" * 50)
    
    # Controleer dependencies
    if not check_dependencies():
        if not install_pyinstaller():
            return
    
    # Maak .exe
    if not create_exe(version):
        return
    
    # Maak standalone package
    standalone_dir = create_standalone_package(version)
    if not standalone_dir:
        return
    
    # Maak installer
    installer_zip = create_installer(standalone_dir, version)
    
    # Cleanup
    cleanup_build_files()
    
    print("\n🎉 Installer succesvol gemaakt!")
    print(f"📁 Installer: {installer_zip}")
    print(f"📁 Standalone directory: {standalone_dir}")
    print("\n📋 Volgende stappen:")
    print("1. Test de installer op een andere computer")
    print("2. Upload naar GitHub releases")
    print("3. Distributeer naar patiënten")

if __name__ == "__main__":
    main() 