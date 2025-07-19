# Diabetes Tracker Update Systeem

## Overzicht

Het update systeem maakt het gemakkelijk om je diabetes tracker applicatie up-to-date te houden. Het systeem controleert automatisch voor updates, maakt backups en installeert nieuwe versies veilig.

## Functies

### 🔄 Automatische Update Controle
- Controleert automatisch voor updates bij startup
- Instelbare controle intervallen (dagelijks, wekelijks, maandelijks)
- Achtergrond controle zonder de applicatie te onderbreken

### 📁 Backup Systeem
- Automatische backup voor elke update
- Backup geschiedenis met timestamps
- Mogelijkheid om backups te herstellen

### 🛡️ Veilige Updates
- Controleert integriteit van update bestanden
- Rollback mogelijkheid bij problemen
- Stapsgewijze installatie met progress tracking

### 📊 Update Geschiedenis
- Overzicht van alle updates
- Versie informatie en release notes
- Backup geschiedenis

## Hoe te gebruiken

### 1. Automatische Updates

De applicatie controleert automatisch voor updates bij startup. Je kunt de instellingen aanpassen via:

**Menu → Updates → Update Instellingen**

- **Automatisch controleren**: Aan/uit schakelen
- **Controle interval**: 1, 3, 7, 14 of 30 dagen
- **Update notificaties**: Krijg meldingen bij beschikbare updates

### 2. Handmatige Update Check

**Menu → Updates → Controleer voor Updates**

Of gebruik het standalone update script:

```bash
python update_diabetes_tracker.py
```

Of dubbelklik op `update_app.bat`

### 3. Update Geschiedenis Bekijken

**Menu → Updates → Update Geschiedenis**

Bekijk:
- Laatste update informatie
- Versie geschiedenis
- Backup geschiedenis

## Update Proces

### Stap 1: Backup
- Maakt automatisch een backup van alle belangrijke bestanden
- Backup wordt opgeslagen in `backups/` directory
- Timestamp in backup naam voor identificatie

### Stap 2: Download
- Downloadt update bestanden van de server
- Controleert bestandsintegriteit
- Slaat bestanden op in tijdelijke directory

### Stap 3: Installatie
- Vervangt oude bestanden met nieuwe versies
- Behoudt gebruikersdata en instellingen
- Update versie informatie

### Stap 4: Herstart
- Sluit huidige applicatie
- Start nieuwe versie automatisch
- Toont welkomstbericht met nieuwe features

## Bestanden

### Update Systeem Bestanden
- `update_system.py` - Hoofd update systeem
- `update_diabetes_tracker.py` - Standalone update script
- `update_app.bat` - Windows batch script
- `version.json` - Versie informatie
- `update_schedule.json` - Update instellingen

### Backup Bestanden
- `backups/` - Directory met alle backups
- `backup_YYYYMMDD_HHMMSS/` - Backup directories
- `temp_update/` - Tijdelijke update bestanden

## Troubleshooting

### Update Fout
1. Controleer internetverbinding
2. Zorg dat je schrijfrechten hebt in de applicatie directory
3. Sluit andere programma's die bestanden gebruiken
4. Probeer handmatige update check

### Backup Herstellen
1. Ga naar **Menu → Bestand → Herstel Database**
2. Selecteer backup bestand uit `backups/` directory
3. Bevestig herstel actie
4. Herstart applicatie

### Update Instellingen Resetten
1. Verwijder `update_schedule.json` bestand
2. Herstart applicatie
3. Stel nieuwe instellingen in

## Veiligheid

### Data Bescherming
- Alle gebruikersdata wordt behouden tijdens updates
- Automatische backups voor elke update
- Rollback mogelijkheid bij problemen

### Bestandsintegriteit
- Controleert checksums van update bestanden
- Valideert bestandsstructuur
- Test applicatie functionaliteit na update

### Foutafhandeling
- Automatische rollback bij fouten
- Gedetailleerde foutmeldingen
- Logging van alle update activiteiten

## Configuratie

### Update Instellingen
```json
{
  "last_check": "2024-01-15T10:30:00",
  "check_interval_days": 7,
  "auto_check": true,
  "notifications": true
}
```

### Versie Informatie
```json
{
  "version": "1.1.0",
  "updated_at": "2024-01-15T10:30:00",
  "update_system": true,
  "features": [
    "Verbeterde gebruikersinterface",
    "Nieuwe analytics functies"
  ]
}
```

## Ondersteuning

Voor vragen of problemen met het update systeem:

1. Controleer de update geschiedenis
2. Bekijk de backup bestanden
3. Probeer handmatige update
4. Herstel van backup indien nodig

## Toekomstige Verbeteringen

- [ ] Online update server integratie
- [ ] Delta updates voor kleinere downloads
- [ ] Automatische dependency updates
- [ ] Update notificaties via systeem tray
- [ ] Multi-language ondersteuning
- [ ] Update rollback via GUI 