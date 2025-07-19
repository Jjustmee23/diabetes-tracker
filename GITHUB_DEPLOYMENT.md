# 🚀 GitHub Deployment Guide - Diabetes Tracker

## 📋 Overzicht

Deze gids legt uit hoe je de Diabetes Tracker applicatie kunt updaten bij patiënten via GitHub releases.

## 🔧 Setup

### 1. GitHub Repository Configuratie

Pas de repository URL aan in `update_system.py`:

```python
# Regel 28 in update_system.py
self.github_repo = "jouw-username/diabetes-tracker"  # Pas dit aan!
```

### 2. Dependencies Installeren

```bash
pip install requests
```

## 📦 Release Maken

### Automatische Release Package

```bash
# Maak een nieuwe release
python create_github_release.py 1.1.0 "Nieuwe features en bug fixes"

# Of zonder release notes
python create_github_release.py 1.1.0
```

Dit script maakt automatisch:
- `Diabetes_Tracker_Auto_Start_v1.1.0.zip`
- `Diabetes_Tracker_Standalone_v1.1.0.zip`
- `RELEASE_NOTES_v1.1.0.txt`
- `GITHUB_RELEASE_INSTRUCTIONS_v1.1.0.txt`

### Handmatige Release

1. **Maak ZIP bestanden:**
   - `Diabetes_Tracker_Auto_Start/` → `Diabetes_Tracker_Auto_Start_v1.1.0.zip`
   - `Diabetes_Tracker_Standalone/` → `Diabetes_Tracker_Standalone_v1.1.0.zip`

2. **Schrijf release notes:**
   - Nieuwe features
   - Bug fixes
   - Installatie instructies

## 🌐 GitHub Release Publiceren

### Stap 1: Ga naar GitHub
1. Open je repository op GitHub
2. Klik op "Releases" in de rechterkolom
3. Klik op "Create a new release"

### Stap 2: Release Details
- **Tag:** `v1.1.0` (gebruik v prefix)
- **Title:** `Diabetes Tracker v1.1.0`
- **Description:** Kopieer inhoud van `RELEASE_NOTES_v1.1.0.txt`

### Stap 3: Upload Bestanden
Upload de ZIP bestanden:
- `Diabetes_Tracker_Auto_Start_v1.1.0.zip`
- `Diabetes_Tracker_Standalone_v1.1.0.zip`

### Stap 4: Publiceren
Klik op "Publish release"

## 🔄 Update Proces bij Patiënten

### Automatische Updates
1. **Update Check:** Applicatie controleert elke 7 dagen op updates
2. **Melding:** Patiënt krijgt popup met update informatie
3. **Download:** Applicatie downloadt automatisch de nieuwe versie
4. **Backup:** Huidige data wordt automatisch geback-upt
5. **Installatie:** Nieuwe versie wordt geïnstalleerd
6. **Herstart:** Applicatie herstart met nieuwe versie

### Handmatige Updates
1. **Update Check:** Patiënt klikt op "Check for Updates" in menu
2. **Download:** Patiënt downloadt handmatig van GitHub
3. **Extract:** ZIP bestand uitpakken
4. **Vervangen:** Oude versie vervangen door nieuwe
5. **Database:** Database blijft behouden

## 📊 Update Statistieken

### Wat wordt behouden:
- ✅ Patiënt data (diabetes_data.db)
- ✅ Backup bestanden
- ✅ Instellingen
- ✅ Export data

### Wat wordt geüpdatet:
- 🔄 Applicatie code
- 🔄 UI verbeteringen
- 🔄 Nieuwe features
- 🔄 Bug fixes

## 🛠️ Troubleshooting

### Update Check Fails
```python
# Controleer in update_system.py
print(f"GitHub update check error: {e}")
```

**Oplossingen:**
1. Controleer internet verbinding
2. Controleer GitHub repository URL
3. Controleer of release bestaat
4. Controleer of ZIP bestanden geüpload zijn

### Download Fails
```python
# Controleer download URL
download_url = update_info.get('download_url')
if not download_url:
    print("Geen download URL beschikbaar")
```

**Oplossingen:**
1. Controleer of GitHub release gepubliceerd is
2. Controleer of ZIP bestanden geüpload zijn
3. Controleer bestandsgrootte (max 100MB voor GitHub)

### Installatie Fails
```python
# Controleer bestandsrechten
shutil.copy2(src, dst)
```

**Oplossingen:**
1. Sluit applicatie volledig
2. Controleer schrijfrechten
3. Controleer antivirus software
4. Voer uit als administrator

## 📱 Patiënt Instructies

### Voor Patiënten
1. **Automatische Updates:** Klik "Ja" op update melding
2. **Handmatige Updates:** Download van GitHub releases
3. **Database Behoud:** Geen actie nodig - data blijft behouden
4. **Backup:** Automatisch gemaakt in `backups/` map

### Voor Artsen/Therapeuten
1. **Distributie:** Stuur GitHub release link naar patiënten
2. **Ondersteuning:** Help bij handmatige installatie indien nodig
3. **Monitoring:** Controleer of updates succesvol zijn

## 🔒 Beveiliging

### Best Practices
- ✅ Gebruik HTTPS voor downloads
- ✅ Verificeer bestand integriteit
- ✅ Maak altijd backups voor updates
- ✅ Test updates op test systeem eerst

### Veiligheidsmaatregelen
- 🔐 GitHub releases zijn veilig
- 🔐 Downloads via HTTPS
- 🔐 Automatische backup voor updates
- 🔐 Rollback mogelijkheid via backups

## 📈 Monitoring

### Update Statistieken
- Aantal patiënten met update melding
- Aantal succesvolle updates
- Aantal failed updates
- Meest gebruikte versie

### Logs
```python
# Update logs worden opgeslagen in:
# - Console output
# - Application logs
# - Error logs
```

## 🎯 Best Practices

### Release Management
1. **Versioning:** Gebruik semantic versioning (1.1.0)
2. **Testing:** Test altijd op test systeem
3. **Documentation:** Schrijf duidelijke release notes
4. **Rollback:** Zorg voor rollback mogelijkheid

### Communication
1. **Release Notes:** Duidelijke beschrijving van wijzigingen
2. **Breaking Changes:** Markeer breaking changes duidelijk
3. **Installation:** Duidelijke installatie instructies
4. **Support:** Bied ondersteuning voor problemen

## 📞 Support

### Voor Problemen
1. **GitHub Issues:** Maak issue aan in repository
2. **Email:** Contact via email
3. **Documentation:** Check deze guide
4. **Logs:** Check applicatie logs voor details

### Contact Informatie
- **Repository:** [GitHub Repository URL]
- **Email:** [Support Email]
- **Documentation:** Deze guide

---

**🎉 Succesvolle deployment!** Patiënten krijgen nu automatisch updates via GitHub releases. 