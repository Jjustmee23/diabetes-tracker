# 🩸 Diabetes Tracker Applicatie

Een moderne desktop applicatie voor het bijhouden van diabetes gegevens, ontwikkeld in Python met Tkinter.

## 🚀 Features

- **📊 Bloedglucose Tracking** - Dagelijkse metingen bijhouden
- **💊 Medicatie Compliance** - Medicatie inname registreren
- **📈 Analytics** - Grafieken en statistieken
- **📤 Export** - Data exporteren naar Excel en PDF
- **🤖 AI Analytics** - Intelligente data analyse
- **🔄 Auto Updates** - Automatische updates via GitHub
- **💾 Database Backup** - Automatische backups
- **📱 Responsive UI** - Moderne gebruikersinterface

## 🛠️ Installatie

### Voor Ontwikkelaars
```bash
# Clone repository
git clone https://github.com/[username]/diabetes-tracker.git
cd diabetes-tracker

# Installeer dependencies
pip install -r requirements.txt

# Start applicatie
python diabetes_tracker.py
```

### Voor Patiënten
1. Download de laatste release van GitHub
2. Extract het ZIP bestand
3. Dubbelklik op `Diabetes_Tracker.exe` (Auto-Start versie)
4. Of dubbelklik op `START_DIABETES_TRACKER.bat` (Standalone versie)

## 📦 Standalone Versies

### Auto-Start Versie (Aanbevolen)
- `Diabetes_Tracker_Auto_Start/`
- Start direct met dubbelklikken op .exe
- Geen extra stappen nodig

### Klassieke Standalone
- `Diabetes_Tracker_Standalone/`
- Start via batch bestand
- Meer controle over start proces

## 🔄 Update Systeem

De applicatie controleert automatisch op updates via GitHub releases:

1. **Automatische Check** - Elke 7 dagen
2. **Update Melding** - Popup met nieuwe features
3. **Automatische Download** - Van GitHub releases
4. **Database Behoud** - Data blijft altijd behouden
5. **Backup** - Automatische backup voor updates

## 📊 Database

- **SQLite Database** - `diabetes_data.db`
- **Automatische Backups** - In `backups/` map
- **Data Behoud** - Bij updates en herinstallaties

## 🎯 Gebruik

### Patiënt Gegevens
- Voeg nieuwe patiënten toe
- Bewerk patiënt informatie
- Verwijder patiënten (met bevestiging)

### Bloedglucose Metingen
- Dagelijkse metingen invoeren
- Tijd en datum selectie
- Activiteit en opmerkingen
- Automatische berekeningen

### Medicatie Compliance
- Medicatie inname registreren
- Compliance tracking
- Herinneringen

### Analytics & Export
- Grafieken en statistieken
- Export naar Excel (.xlsx)
- Export naar PDF
- AI-gebaseerde analyse

## 🛠️ Ontwikkeling

### Dependencies
```
tkinter
ttkbootstrap
matplotlib
pandas
openpyxl
reportlab
requests
```

### Project Structuur
```
diabetes-tracker/
├── diabetes_tracker.py      # Hoofdapplicatie
├── patient_management.py    # Patiënt management
├── update_system.py         # Update systeem
├── templates/               # HTML templates
├── backups/                 # Database backups
├── requirements.txt         # Python dependencies
└── README.md               # Deze file
```

### Build Scripts
- `create_standalone.py` - Maak standalone versie
- `create_github_release.py` - Maak GitHub release
- `setup_github_repo.py` - Repository setup

## 🔒 Privacy & Beveiliging

- **Lokale Opslag** - Alle data lokaal opgeslagen
- **Geen Cloud** - Geen externe servers
- **Database Encryptie** - SQLite met beveiliging
- **Backup Beveiliging** - Versleutelde backups

## 📞 Support

Voor vragen of problemen:
- **GitHub Issues** - Maak issue aan in repository
- **Documentation** - Check deze README
- **Release Notes** - Bekijk GitHub releases

## 📄 Licentie

Dit project is ontwikkeld voor medisch gebruik. Neem contact op voor licentie informatie.

---

**🩸 Diabetes Tracker v1.1.0** - Ontwikkeld voor betere diabetes management
