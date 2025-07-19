#!/usr/bin/env python3
"""
Script om GitHub releases te maken voor de Diabetes Tracker
Gebruik: python create_github_release.py [version] [release_notes]
"""

import os
import sys
import zipfile
import shutil
from datetime import datetime

def create_release_package(version, release_notes=""):
    """Maak een release package voor GitHub"""
    
    print(f"🎯 Maak release package voor versie {version}")
    
    # Maak release directory
    release_dir = f"release_v{version}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Kopieer standalone versies
    standalone_dirs = [
        "Diabetes_Tracker_Standalone",
        "Diabetes_Tracker_Auto_Start"
    ]
    
    for dir_name in standalone_dirs:
        if os.path.exists(dir_name):
            print(f"📦 Kopieer {dir_name}...")
            shutil.copytree(dir_name, os.path.join(release_dir, dir_name))
    
    # Maak ZIP bestanden voor GitHub releases
    print("🗜️ Maak ZIP bestanden...")
    
    # Auto-start versie ZIP
    auto_start_zip = f"Diabetes_Tracker_Auto_Start_v{version}.zip"
    if os.path.exists(os.path.join(release_dir, "Diabetes_Tracker_Auto_Start")):
        with zipfile.ZipFile(auto_start_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(os.path.join(release_dir, "Diabetes_Tracker_Auto_Start")):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, release_dir)
                    zipf.write(file_path, arcname)
        print(f"✅ {auto_start_zip} gemaakt")
    
    # Klassieke standalone ZIP
    standalone_zip = f"Diabetes_Tracker_Standalone_v{version}.zip"
    if os.path.exists(os.path.join(release_dir, "Diabetes_Tracker_Standalone")):
        with zipfile.ZipFile(standalone_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(os.path.join(release_dir, "Diabetes_Tracker_Standalone")):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, release_dir)
                    zipf.write(file_path, arcname)
        print(f"✅ {standalone_zip} gemaakt")
    
    # Maak release notes bestand
    release_notes_file = f"RELEASE_NOTES_v{version}.txt"
    with open(release_notes_file, 'w', encoding='utf-8') as f:
        f.write(f"Diabetes Tracker v{version}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Released: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if release_notes:
            f.write("Release Notes:\n")
            f.write("-" * 20 + "\n")
            f.write(release_notes)
            f.write("\n\n")
        
        f.write("Installatie Instructies:\n")
        f.write("-" * 25 + "\n")
        f.write("1. Download de gewenste versie:\n")
        f.write("   - Diabetes_Tracker_Auto_Start_v{version}.zip (Aanbevolen)\n")
        f.write("   - Diabetes_Tracker_Standalone_v{version}.zip\n\n")
        f.write("2. Extract het ZIP bestand\n")
        f.write("3. Start de applicatie:\n")
        f.write("   - Auto-Start: Dubbelklik op Diabetes_Tracker.exe\n")
        f.write("   - Standalone: Dubbelklik op START_DIABETES_TRACKER.bat\n\n")
        f.write("Database behoud:\n")
        f.write("- De database wordt automatisch behouden tijdens updates\n")
        f.write("- Backup bestanden worden gemaakt in de backups/ map\n\n")
        f.write("Ondersteuning:\n")
        f.write("- Voor vragen of problemen, neem contact op met de ontwikkelaar\n")
    
    print(f"✅ {release_notes_file} gemaakt")
    
    # Maak GitHub release instructies
    github_instructions = f"GITHUB_RELEASE_INSTRUCTIONS_v{version}.txt"
    with open(github_instructions, 'w', encoding='utf-8') as f:
        f.write("GitHub Release Instructies\n")
        f.write("=" * 30 + "\n\n")
        f.write(f"1. Ga naar je GitHub repository\n")
        f.write("2. Klik op 'Releases' in de rechterkolom\n")
        f.write("3. Klik op 'Create a new release'\n")
        f.write(f"4. Tag: v{version}\n")
        f.write(f"5. Title: Diabetes Tracker v{version}\n")
        f.write("6. Beschrijving:\n")
        f.write("   Kopieer de inhoud van RELEASE_NOTES_v{version}.txt\n\n")
        f.write("7. Upload bestanden:\n")
        if os.path.exists(auto_start_zip):
            f.write(f"   - {auto_start_zip}\n")
        if os.path.exists(standalone_zip):
            f.write(f"   - {standalone_zip}\n")
        f.write("\n8. Klik 'Publish release'\n\n")
        f.write("Update Systeem:\n")
        f.write("- Patienten krijgen automatisch een melding van nieuwe updates\n")
        f.write("- Updates worden gedownload en geïnstalleerd met behoud van data\n")
    
    print(f"✅ {github_instructions} gemaakt")
    
    # Cleanup release directory
    shutil.rmtree(release_dir)
    
    print(f"\n🎉 Release package voor v{version} succesvol gemaakt!")
    print(f"📁 Bestanden gemaakt:")
    if os.path.exists(auto_start_zip):
        print(f"   - {auto_start_zip}")
    if os.path.exists(standalone_zip):
        print(f"   - {standalone_zip}")
    print(f"   - {release_notes_file}")
    print(f"   - {github_instructions}")
    print(f"\n📋 Volg de instructies in {github_instructions} om de release te publiceren")

def main():
    if len(sys.argv) < 2:
        print("Gebruik: python create_github_release.py [version] [release_notes]")
        print("Voorbeeld: python create_github_release.py 1.1.0 'Nieuwe features en bug fixes'")
        return
    
    version = sys.argv[1]
    release_notes = sys.argv[2] if len(sys.argv) > 2 else ""
    
    create_release_package(version, release_notes)

if __name__ == "__main__":
    main() 