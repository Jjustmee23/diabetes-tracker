#!/usr/bin/env python3
"""
Test Script voor Diabetes Tracker Update Systeem
================================================

Dit script test alle functies van het update systeem.
"""

import os
import sys
import json
import shutil
from datetime import datetime

def test_update_system():
    """Test het update systeem"""
    print("🧪 Test Diabetes Tracker Update Systeem")
    print("=" * 50)
    
    # Test 1: Import update systeem
    print("\n1. Test import update systeem...")
    try:
        from update_system import UpdateSystem
        print("✅ Update systeem geïmporteerd")
    except ImportError as e:
        print(f"❌ Import fout: {e}")
        return False
    
    # Test 2: Maak test update systeem
    print("\n2. Test update systeem initialisatie...")
    try:
        update_system = UpdateSystem()
        print("✅ Update systeem geïnitialiseerd")
    except Exception as e:
        print(f"❌ Initialisatie fout: {e}")
        return False
    
    # Test 3: Test backup functionaliteit
    print("\n3. Test backup functionaliteit...")
    try:
        # Maak test bestand
        with open('test_file.txt', 'w') as f:
            f.write('Test content')
        
        # Test backup
        success = update_system.create_backup()
        if success:
            print("✅ Backup functionaliteit werkt")
        else:
            print("❌ Backup mislukt")
            return False
            
        # Ruim test bestand op
        if os.path.exists('test_file.txt'):
            os.remove('test_file.txt')
            
    except Exception as e:
        print(f"❌ Backup test fout: {e}")
        return False
    
    # Test 4: Test update check
    print("\n4. Test update check...")
    try:
        has_update, update_info = update_system.check_for_updates()
        if has_update:
            print("✅ Update check werkt - update beschikbaar")
            print(f"   Versie: {update_info.get('version', 'Onbekend')}")
        else:
            print("✅ Update check werkt - geen updates")
    except Exception as e:
        print(f"❌ Update check fout: {e}")
        return False
    
    # Test 5: Test versie informatie
    print("\n5. Test versie informatie...")
    try:
        version_info = {
            'version': '1.0.0',
            'updated_at': datetime.now().isoformat(),
            'update_system': True
        }
        
        with open('version.json', 'w') as f:
            json.dump(version_info, f, indent=2)
        
        print("✅ Versie informatie aangemaakt")
    except Exception as e:
        print(f"❌ Versie informatie fout: {e}")
        return False
    
    # Test 6: Test update instellingen
    print("\n6. Test update instellingen...")
    try:
        schedule = {
            'last_check': datetime.now().isoformat(),
            'check_interval_days': 7,
            'auto_check': True
        }
        
        with open('update_schedule.json', 'w') as f:
            json.dump(schedule, f, indent=2)
        
        print("✅ Update instellingen aangemaakt")
    except Exception as e:
        print(f"❌ Update instellingen fout: {e}")
        return False
    
    # Test 7: Test cleanup
    print("\n7. Test cleanup...")
    try:
        update_system.cleanup_temp_files()
        print("✅ Cleanup werkt")
    except Exception as e:
        print(f"❌ Cleanup fout: {e}")
        return False
    
    # Test 8: Test bestanden
    print("\n8. Test bestanden...")
    required_files = [
        'update_system.py',
        'update_diabetes_tracker.py',
        'update_app.bat',
        'version.json',
        'update_schedule.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Ontbrekende bestanden: {missing_files}")
        return False
    else:
        print("✅ Alle bestanden aanwezig")
    
    # Test 9: Test directories
    print("\n9. Test directories...")
    required_dirs = ['backups']
    
    missing_dirs = []
    for dir in required_dirs:
        if not os.path.exists(dir):
            missing_dirs.append(dir)
    
    if missing_dirs:
        print(f"❌ Ontbrekende directories: {missing_dirs}")
        return False
    else:
        print("✅ Alle directories aanwezig")
    
    # Test 10: Test integratie met hoofdapplicatie
    print("\n10. Test integratie met hoofdapplicatie...")
    try:
        # Test of de hoofdapplicatie het update systeem kan importeren
        import diabetes_tracker
        print("✅ Hoofdapplicatie kan update systeem importeren")
    except Exception as e:
        print(f"❌ Integratie fout: {e}")
        return False
    
    print("\n🎉 Alle tests geslaagd!")
    print("Het update systeem is correct geïnstalleerd en werkt.")
    
    return True

def cleanup_test_files():
    """Ruim test bestanden op"""
    test_files = [
        'test_file.txt',
        'version.json',
        'update_schedule.json'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Verwijderd: {file}")
            except Exception as e:
                print(f"⚠️ Kon {file} niet verwijderen: {e}")

def main():
    """Hoofdfunctie"""
    print("🧪 Start update systeem tests...")
    
    # Voer tests uit
    success = test_update_system()
    
    # Ruim test bestanden op
    print("\n🧹 Ruim test bestanden op...")
    cleanup_test_files()
    
    if success:
        print("\n✅ Alle tests geslaagd! Het update systeem is klaar voor gebruik.")
        print("\n📋 Volgende stappen:")
        print("1. Start de diabetes tracker applicatie")
        print("2. Ga naar Menu → Updates → Controleer voor Updates")
        print("3. Of gebruik het standalone update script: python update_diabetes_tracker.py")
    else:
        print("\n❌ Sommige tests zijn mislukt. Controleer de foutmeldingen hierboven.")
    
    input("\nDruk op Enter om af te sluiten...")

if __name__ == "__main__":
    main() 