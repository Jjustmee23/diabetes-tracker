# 🆔 Belgische EID Kaart Reader

## Overzicht

De Diabetes Tracker ondersteunt nu volledige uitlezing van Belgische identiteitskaarten (EID) voor automatische patiënt registratie. Deze functionaliteit maakt het mogelijk om patiëntgegevens direct van de EID kaart te lezen en op te slaan in het systeem.

## ✨ Features

### 🔍 Volledige EID Uitlezing
- **Persoonlijke Gegevens**: Naam, voornamen, geboortedatum, geslacht, nationaliteit
- **Adresgegevens**: Straat, huisnummer, postcode, gemeente
- **Kaartgegevens**: Kaartnummer, chipnummer, geldigheidsdata
- **Pasfoto**: Digitale pasfoto van de kaart
- **Veiligheid**: PIN code verificatie vereist

### 📋 Selecteerbare Velden
- **Aanpasbaar**: Kies welke gegevens uitgelezen worden
- **Standaard Selectie**: Alle belangrijke velden voorgeselecteerd
- **Categorieën**: Georganiseerd per type gegevens
- **Privacy**: Alleen gewenste gegevens opslaan

### 🛡️ Veiligheid
- **PIN Verificatie**: EID PIN code vereist voor toegang
- **Beveiligde Verbinding**: Veilige communicatie met kaartlezer
- **Foutafhandeling**: Robuuste error handling
- **Privacy Bewust**: Gegevens alleen lokaal opgeslagen

## 🔧 Vereisten

### Hardware
- **Kaartlezer**: USB of ingebouwde smartcard reader
- **EID Kaart**: Geldige Belgische identiteitskaart
- **Drivers**: Kaartlezer drivers geïnstalleerd

### Software Dependencies
```bash
pip install pyscard smartcard cryptography
```

### Ondersteunde Systemen
- **Windows**: 10/11 met smartcard support
- **Linux**: Met PC/SC Lite
- **macOS**: Met smartcard framework

## 🚀 Gebruik

### 1. Patiënt Toevoegen via EID

1. **Open Patiënten Fiche**: Klik op "👤 Patiënten Fiche"
2. **EID Knop**: Klik op "🆔 Toevoegen via EID"
3. **Velden Selecteren**: Kies welke gegevens uitgelezen worden
4. **Kaart Insteken**: Steek EID kaart in de lezer
5. **PIN Invoeren**: Voer je EID PIN code in
6. **Gegevens Controleren**: Bekijk uitgelezen gegevens
7. **Opslaan**: Bevestig om patiënt toe te voegen

### 2. Veld Selectie

#### 👤 Persoonlijke Gegevens
- ✅ Rijksregisternummer
- ✅ Achternaam
- ✅ Voornamen
- ✅ Geboortedatum
- ✅ Geboorteplaats
- ✅ Geslacht
- ✅ Nationaliteit
- ⚪ Adellijke titel
- ⚪ Derde voornaam (eerste letter)

#### 📍 Adresgegevens
- ✅ Straat en huisnummer
- ✅ Postcode
- ✅ Gemeente

#### 🆔 Kaartgegevens
- ✅ Kaartnummer
- ✅ Chipnummer
- ✅ Kaart geldig vanaf
- ✅ Kaart geldig tot
- ✅ Uitgegeven door gemeente
- ⚪ Documenttype

#### 📷 Overige
- ✅ Pasfoto
- ⚪ Speciale status

### 3. Demo Mode

Als EID libraries niet geïnstalleerd zijn:
- **Demo Mode**: Test functionaliteit met voorbeeldgegevens
- **Volledige Interface**: Alle functies beschikbaar
- **Geen Hardware**: Geen kaartlezer vereist

## 🔒 Privacy & Veiligheid

### Gegevensopslag
- **Lokaal**: Alle gegevens blijven lokaal opgeslagen
- **Gecodeerd**: Pasfoto's in Base64 formaat
- **Backup**: Automatische database backups
- **Geen Cloud**: Geen gegevens naar externe servers

### Toegangscontrole
- **PIN Vereist**: EID PIN code altijd vereist
- **Timeout**: Automatische timeout bij inactiviteit
- **Foutdetectie**: Detectie van manipulatie pogingen
- **Logging**: Audit trail van EID toegang

## 🛠️ Installatie

### 1. Dependencies Installeren
```bash
# Installeer vereiste packages
pip install pyscard smartcard cryptography requests

# Voor Windows (aanvullend):
# Download en installeer PC/SC drivers
```

### 2. Kaartlezer Setup
```bash
# Windows: Installeer kaartlezer drivers
# Linux: Installeer pcsc-lite
sudo apt-get install pcscd pcsc-tools

# Test kaartlezer
pcsc_scan
```

### 3. Applicatie Starten
```bash
# Start Diabetes Tracker
python diabetes_tracker.py

# EID functionaliteit wordt automatisch gedetecteerd
```

## 🐛 Troubleshooting

### Veelvoorkomende Problemen

#### "Geen kaartlezers gevonden"
- **Oorzaak**: Kaartlezer niet aangesloten of drivers ontbreken
- **Oplossing**: Controleer USB verbinding en installeer drivers

#### "Kan niet verbinden met EID kaart"
- **Oorzaak**: Kaart niet goed ingestoken of defect
- **Oplossing**: Steek kaart opnieuw in, controleer op beschadigingen

#### "PIN verificatie mislukt"
- **Oorzaak**: Verkeerde PIN code ingevoerd
- **Oplossing**: Controleer PIN code, max 3 pogingen

#### "EID libraries niet beschikbaar"
- **Oorzaak**: pyscard/smartcard niet geïnstalleerd
- **Oplossing**: `pip install pyscard smartcard cryptography`

### Debug Mode

Voeg debug output toe:
```python
# In eid_reader.py, wijzig:
DEBUG_MODE = True  # Voor uitgebreide logging
```

## 📊 Ondersteunde EID Gegevens

### Identiteitsbestand (40 31)
| Veld | Beschrijving | Type |
|------|-------------|------|
| 01 | Kaartnummer | Numeriek |
| 02 | Chipnummer | Alphanumeriek |
| 03 | Kaart geldig vanaf | Datum |
| 04 | Kaart geldig tot | Datum |
| 05 | Uitgegeven door | Gemeente |
| 06 | Rijksregisternummer | Numeriek |
| 07 | Naam | Tekst |
| 08 | Voornamen | Tekst |
| 09 | Nationaliteit | Tekst |
| 10 | Geboorteplaats | Tekst |
| 11 | Geboortedatum | Datum |
| 12 | Geslacht | M/V |

### Adresbestand (40 33)
| Veld | Beschrijving | Type |
|------|-------------|------|
| 01 | Straat en nummer | Tekst |
| 02 | Postcode | Numeriek |
| 03 | Gemeente | Tekst |

### Fotobestand (40 35)
| Veld | Beschrijving | Type |
|------|-------------|------|
| 01 | Pasfoto | JPEG Binary |

## 🔄 Updates

### Automatische Updates
- **Versie Check**: Automatische controle op nieuwe EID features
- **Library Updates**: Melding bij nieuwe smartcard libraries
- **Compatibility**: Backward compatibility gegarandeerd

### Handmatige Updates
```bash
# Update EID dependencies
pip install --upgrade pyscard smartcard cryptography

# Check for library updates
pip list --outdated | grep -E "(pyscard|smartcard|cryptography)"
```

## 📞 Support

### Technische Support
- **GitHub Issues**: Rapporteer bugs en feature requests
- **Documentation**: Uitgebreide documentatie beschikbaar
- **Community**: Community support via GitHub

### EID Specifieke Support
- **Kaartlezer Issues**: Contacteer kaartlezer fabrikant
- **EID Problemen**: Contacteer gemeente voor nieuwe kaart
- **PIN Vergeten**: Ga naar gemeente voor PIN reset

## 📈 Roadmap

### Geplande Features
- **🔄 v1.3.1**: Bulk EID import
- **🔄 v1.3.2**: EID foto weergave in interface
- **🔄 v1.3.3**: EID certificaat validatie
- **🔄 v1.3.4**: Multi-taal ondersteuning
- **🔄 v1.3.5**: Export naar EHIC formaat

### Long-term
- **🔮 v1.4.0**: EU EID support (andere landen)
- **🔮 v1.5.0**: NFC EID ondersteuning
- **🔮 v1.6.0**: Mobile EID apps integratie

---

*Voor meer informatie, zie de volledige documentatie of neem contact op via GitHub.* 