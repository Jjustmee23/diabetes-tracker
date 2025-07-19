# Diabetes Tracker v1.2.5 - Installer

## 🚀 Snelle Start

1. **Dubbelklik op `START_DIABETES_TRACKER.bat`**
2. **Wacht tot Python dependencies geïnstalleerd zijn**
3. **De applicatie start automatisch**

## 📋 Vereisten

- Windows 10/11
- Python 3.8 of hoger
- Internetverbinding (voor eerste installatie)

## 🔧 Handmatige Installatie

Als de automatische installatie niet werkt:

1. **Open Command Prompt als Administrator**
2. **Navigeer naar deze map:**
   ```
   cd "releases/Diabetes_Tracker_Installer_v1.2.5"
   ```
3. **Installeer dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **Start de applicatie:**
   ```
   python diabetes_tracker.py
   ```

## 📁 Mapstructuur

```
Diabetes_Tracker_Installer_v1.2.5/
├── diabetes_tracker.py      # Hoofdapplicatie
├── patient_management.py    # Patiënt beheer
├── update_system.py         # Update systeem
├── requirements.txt         # Python dependencies
├── templates/               # Web templates
├── data/                    # Database bestanden
├── backups/                 # Automatische backups
├── START_DIABETES_TRACKER.bat  # Start script
└── README.md               # Deze handleiding
```

## 🆕 Nieuwe Features v1.2.5

### 📅 Verbeterde Datum & Tijd Invoervelden
- **Grotere datum invoerveld**: 20 karakters breed
- **Grotere tijd invoerveld**: 15 karakters breed
- **100% zichtbare datum formaten**: "2025-07-19" past volledig
- **100% zichtbare tijd formaten**: "15:45" past volledig

### 🎯 Date Picker Verbeteringen
- **Grotere spinboxes**: Dag (12), Maand (12), Jaar (15) karakters
- **Volledige jaartallen**: "2025" is nu 100% zichtbaar
- **Betere gebruikerservaring**: Geen afgekapte tekst meer

### ⏰ Time Picker Verbeteringen  
- **Grotere spinboxes**: Uren (12), Minuten (12) karakters
- **Volledige tijd formaten**: Alle tijd waarden zijn zichtbaar

### 🔧 Technische Verbeteringen
- **Database migratie**: Veilige schema updates zonder data verlies
- **Automatische backups**: Voor elke database wijziging
- **Update systeem**: Verbeterde GitHub API integratie

## 🆘 Problemen Oplossen

### Python niet gevonden
- Download Python van: https://python.org
- Zorg dat "Add Python to PATH" is aangevinkt

### Dependencies fout
- Voer uit: `pip install --upgrade pip`
- Probeer opnieuw: `pip install -r requirements.txt`

### Database fout
- Controleer of de `data/` map bestaat
- Herstart de applicatie

## 📞 Support

Voor vragen of problemen:
- GitHub Issues: https://github.com/Jjustmee23/diabetes-tracker/issues
- Email: [jouw-email@domain.com]

---
*Gemaakt op 2025-07-19 16:55:35*
