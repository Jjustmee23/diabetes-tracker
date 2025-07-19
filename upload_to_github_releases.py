#!/usr/bin/env python3
"""
Script om je te helpen met het uploaden naar GitHub Releases
"""

import os
import sys
import webbrowser
from datetime import datetime

def create_release_instructions(version):
    """Maak instructies voor GitHub release upload"""
    
    zip_file = f"Diabetes_Tracker_Installer_v{version}.zip"
    
    if not os.path.exists(zip_file):
        print(f"❌ ZIP file niet gevonden: {zip_file}")
        print("Maak eerst de installer met: python create_installer.py {version}")
        return False
    
    # Maak release notes bestand
    release_notes_file = f"RELEASE_NOTES_v{version}.txt"
    
    release_notes = f"""## 🆕 Nieuwe Features
- Verbeterde modals en popups (groter en gecentreerd)
- Betere date/time pickers
- Auto-update systeem via GitHub Releases
- Standalone .exe versie

## 📦 Installatie
1. Download `Diabetes_Tracker_Installer_v{version}.zip`
2. Extract het bestand
3. Dubbelklik op `START_DIABETES_TRACKER.bat`
4. Klaar! Geen Python nodig

## 🔄 Auto-Update
De app controleert automatisch op updates via GitHub Releases.

## 📋 Changelog
- Verbeterde UI/UX
- Grotere en gecentreerde modals
- Betere date/time pickers
- Auto-update functionaliteit
- Standalone .exe distributie

## 🎯 Voor Patiënten
- Download de ZIP file
- Extract naar gewenste locatie
- Start met START_DIABES_TRACKER.bat
- Geen Python of andere software nodig
- Automatische updates via GitHub Releases

Released: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    with open(release_notes_file, 'w', encoding='utf-8') as f:
        f.write(release_notes)
    
    print(f"✅ Release notes gemaakt: {release_notes_file}")
    
    # Toon instructies
    print(f"\n🎯 GitHub Release Upload Instructies:")
    print(f"=" * 50)
    print(f"1. Ga naar: https://github.com/Jjustmee23/diabetes-tracker/releases")
    print(f"2. Klik op 'Create a new release' (groene knop)")
    print(f"3. Vul in:")
    print(f"   - Tag version: v{version}")
    print(f"   - Release title: Diabetes Tracker v{version}")
    print(f"   - Description: Kopieer de inhoud van {release_notes_file}")
    print(f"4. Upload bestand: {zip_file}")
    print(f"5. Klik 'Publish release'")
    print(f"\n📁 Bestanden klaar:")
    print(f"   - {zip_file}")
    print(f"   - {release_notes_file}")
    
    # Open GitHub releases pagina
    print(f"\n🌐 Open GitHub Releases pagina...")
    webbrowser.open(f"https://github.com/Jjustmee23/diabetes-tracker/releases")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Gebruik: python upload_to_github_releases.py <version>")
        print("Voorbeeld: python upload_to_github_releases.py 1.2.1")
        return
    
    version = sys.argv[1]
    print(f"🚀 Bereid GitHub release voor versie {version}...")
    
    success = create_release_instructions(version)
    
    if success:
        print(f"\n✅ Klaar! Volg de instructies hierboven om de release te uploaden.")
        print(f"📋 De release notes staan in: RELEASE_NOTES_v{version}.txt")
        print(f"📦 Upload bestand: Diabetes_Tracker_Installer_v{version}.zip")
    else:
        print(f"\n❌ Voorbereiding mislukt")

if __name__ == "__main__":
    main() 