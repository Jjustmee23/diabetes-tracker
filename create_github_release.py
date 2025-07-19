#!/usr/bin/env python3
"""
Script om GitHub release te maken en installer te uploaden
"""

import os
import sys
import requests
import json
from pathlib import Path

def create_github_release(version, zip_file_path):
    """Maak GitHub release en upload installer"""
    
    # GitHub API configuratie
    repo_owner = "Jjustmee23"
    repo_name = "diabetes-tracker"
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    # Controleer of zip file bestaat
    if not os.path.exists(zip_file_path):
        print(f"❌ ZIP file niet gevonden: {zip_file_path}")
        return False
    
    print(f"🔍 Zoek naar bestaande release voor v{version}...")
    
    # Controleer of release al bestaat
    releases_url = f"{api_url}/releases"
    response = requests.get(releases_url)
    
    if response.status_code == 200:
        releases = response.json()
        for release in releases:
            if release['tag_name'] == f"v{version}":
                print(f"⚠️  Release v{version} bestaat al!")
                return False
    
    # Maak nieuwe release
    print(f"📦 Maak nieuwe release v{version}...")
    
    release_data = {
        "tag_name": f"v{version}",
        "name": f"Diabetes Tracker v{version}",
        "body": f"""## 🆕 Nieuwe Features
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
- Standalone .exe distributie""",
        "draft": False,
        "prerelease": False
    }
    
    # Maak release (zonder assets eerst)
    response = requests.post(
        f"{api_url}/releases",
        headers={"Accept": "application/vnd.github.v3+json"},
        data=json.dumps(release_data)
    )
    
    if response.status_code != 201:
        print(f"❌ Fout bij maken release: {response.status_code}")
        print(response.text)
        return False
    
    release_info = response.json()
    print(f"✅ Release gemaakt: {release_info['html_url']}")
    
    # Upload asset
    print(f"📤 Upload {os.path.basename(zip_file_path)}...")
    
    upload_url = release_info['upload_url'].replace('{?name,label}', f'?name={os.path.basename(zip_file_path)}')
    
    with open(zip_file_path, 'rb') as f:
        response = requests.post(
            upload_url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/zip"
            },
            data=f
        )
    
    if response.status_code == 201:
        print(f"✅ Asset geüpload: {response.json()['browser_download_url']}")
        print(f"🎉 Release succesvol gemaakt!")
        print(f"🔗 Download URL: {release_info['html_url']}")
        return True
    else:
        print(f"❌ Fout bij uploaden asset: {response.status_code}")
        print(response.text)
        return False

def main():
    if len(sys.argv) != 2:
        print("Gebruik: python create_github_release.py <version>")
        print("Voorbeeld: python create_github_release.py 1.2.1")
        return
    
    version = sys.argv[1]
    zip_file = f"Diabetes_Tracker_Installer_v{version}.zip"
    
    if not os.path.exists(zip_file):
        print(f"❌ ZIP file niet gevonden: {zip_file}")
        print("Maak eerst de installer met: python create_installer.py {version}")
        return
    
    print(f"🚀 Maak GitHub release voor versie {version}...")
    success = create_github_release(version, zip_file)
    
    if success:
        print("\n🎯 Volgende stappen:")
        print("1. Test de download van de release")
        print("2. Distributeer de release URL naar patiënten")
        print("3. De app zal automatisch updaten via GitHub Releases")
    else:
        print("\n❌ Release maken mislukt")
        print("Controleer je internetverbinding en GitHub toegang")

if __name__ == "__main__":
    main() 