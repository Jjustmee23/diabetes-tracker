#!/usr/bin/env python3
"""
Automatische GitHub release maker
"""

import os
import sys
from github import Github
from datetime import datetime

def create_github_release(version, zip_file_path, token):
    """Maak GitHub release met token authenticatie"""
    
    try:
        # Maak GitHub client
        g = Github(token)
        repo = g.get_repo("Jjustmee23/diabetes-tracker")
        
        print(f"🔍 Controleer bestaande releases...")
        
        # Controleer of release al bestaat
        try:
            existing_release = repo.get_release(f"v{version}")
            print(f"⚠️  Release v{version} bestaat al!")
            return False
        except:
            pass  # Release bestaat niet, ga door
        
        print(f"📦 Maak nieuwe release v{version}...")
        
        # Release beschrijving
        release_body = f"""## 🆕 Nieuwe Features
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
- Start met START_DIABETES_TRACKER.bat
- Geen Python of andere software nodig
- Automatische updates via GitHub Releases

Released: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        # Maak release
        release = repo.create_git_release(
            tag=f"v{version}",
            name=f"Diabetes Tracker v{version}",
            message=release_body,
            draft=False,
            prerelease=False
        )
        
        print(f"✅ Release gemaakt: {release.html_url}")
        
        # Upload asset
        print(f"📤 Upload {os.path.basename(zip_file_path)}...")
        
        with open(zip_file_path, 'rb') as f:
            asset = release.upload_asset(
                path=zip_file_path,
                name=os.path.basename(zip_file_path),
                content_type="application/zip"
            )
        
        print(f"✅ Asset geüpload: {asset.browser_download_url}")
        print(f"🎉 Release succesvol gemaakt!")
        print(f"🔗 Download URL: {release.html_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Gebruik: python auto_github_release.py <version>")
        print("Voorbeeld: python auto_github_release.py 1.2.1")
        return
    
    version = sys.argv[1]
    zip_file = f"Diabetes_Tracker_Installer_v{version}.zip"
    
    if not os.path.exists(zip_file):
        print(f"❌ ZIP file niet gevonden: {zip_file}")
        print("Maak eerst de installer met: python create_installer.py {version}")
        return
    
    print(f"🚀 Maak automatische GitHub release voor versie {version}...")
    
    # GitHub token (moet worden ingevoerd)
    print("🔑 Voer je GitHub Personal Access Token in:")
    token = input("Token: ").strip()
    
    if not token:
        print("❌ Geen token ingevoerd")
        return
    
    # Maak release
    success = create_github_release(version, zip_file, token)
    
    if success:
        print(f"\n🎯 Release succesvol gemaakt!")
        print(f"📋 Patiënten kunnen nu downloaden van GitHub Releases")
        print(f"🔄 De app zal automatisch updaten via GitHub Releases")
    else:
        print(f"\n❌ Release maken mislukt")
        print("Controleer je token en internetverbinding")

if __name__ == "__main__":
    main() 