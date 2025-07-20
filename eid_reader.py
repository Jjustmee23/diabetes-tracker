#!/usr/bin/env python3
"""
Belgische EID Kaart Reader voor Diabetes Tracker
Ondersteunt volledige uitlezing van Belgische identiteitskaarten
"""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import threading
import time
from datetime import datetime
import base64

# EID Reader dependencies - Echte smartcard functionaliteit
try:
    from smartcard.System import readers
    from smartcard.util import toHexString, toBytes
    from smartcard.CardType import AnyCardType
    from smartcard.CardRequest import CardRequest
    from smartcard.CardConnection import CardConnection
    from smartcard.Exceptions import CardRequestTimeoutException, NoCardException, CardConnectionException
    SMARTCARD_AVAILABLE = True
    print("✅ Smartcard libraries succesvol geladen")
except ImportError as e:
    SMARTCARD_AVAILABLE = False
    print(f"⚠️ Smartcard libraries niet geïnstalleerd: {e}")

class BelgianEIDReader:
    def __init__(self, parent):
        self.parent = parent
        self.card_connection = None
        self.card_data = {}
        
        # EID File IDs (volgens Belgische EID specificatie)
        self.file_ids = {
            'identity': [0x3F, 0x00, 0xDF, 0x01, 0x40, 0x31],  # Identiteitsgegevens
            'address': [0x3F, 0x00, 0xDF, 0x01, 0x40, 0x33],   # Adresgegevens
            'photo': [0x3F, 0x00, 0xDF, 0x01, 0x40, 0x35],     # Foto
            'certificates': [0x3F, 0x00, 0xDF, 0x01, 0x50, 0x38], # Certificaten
        }
        
        # Data velden die uitgelezen kunnen worden
        self.available_fields = {
            'card_number': {'name': 'Kaartnummer', 'selected': True},
            'chip_number': {'name': 'Chipnummer', 'selected': True},
            'card_validity_begin': {'name': 'Kaart geldig vanaf', 'selected': True},
            'card_validity_end': {'name': 'Kaart geldig tot', 'selected': True},
            'card_delivery_municipality': {'name': 'Uitgegeven door gemeente', 'selected': True},
            'national_number': {'name': 'Rijksregisternummer', 'selected': True},
            'surname': {'name': 'Achternaam', 'selected': True},
            'first_names': {'name': 'Voornamen', 'selected': True},
            'first_letter_third_given_name': {'name': 'Derde voornaam (eerste letter)', 'selected': False},
            'nationality': {'name': 'Nationaliteit', 'selected': True},
            'birth_location': {'name': 'Geboorteplaats', 'selected': True},
            'birth_date': {'name': 'Geboortedatum', 'selected': True},
            'sex': {'name': 'Geslacht', 'selected': True},
            'noble_condition': {'name': 'Adellijke titel', 'selected': False},
            'document_type': {'name': 'Documenttype', 'selected': False},
            'special_status': {'name': 'Speciale status', 'selected': False},
            'street_and_number': {'name': 'Straat en huisnummer', 'selected': True},
            'zip_code': {'name': 'Postcode', 'selected': True},
            'municipality': {'name': 'Gemeente', 'selected': True},
            'photo': {'name': 'Pasfoto', 'selected': True}
        }
    
    def is_smartcard_available(self):
        """Controleer of smartcard functionaliteit beschikbaar is"""
        return SMARTCARD_AVAILABLE
    
    def get_card_readers(self):
        """Haal beschikbare kaartlezers op"""
        if not SMARTCARD_AVAILABLE:
            return []
        
        try:
            return readers()
        except Exception as e:
            print(f"Fout bij ophalen kaartlezers: {str(e)}")
            return []
    
    def connect_to_card(self, timeout=30):
        """Verbind met EID kaart met verbeterde stabiliteit"""
        if not SMARTCARD_AVAILABLE:
            raise Exception("Smartcard libraries niet beschikbaar")
        
        try:
            # Disconnect eventuele bestaande verbindingen
            if self.card_connection:
                try:
                    self.card_connection.disconnect()
                except:
                    pass
                self.card_connection = None
            
            # Zoek naar kaartlezers
            card_readers = self.get_card_readers()
            if not card_readers:
                raise Exception("Geen kaartlezers gevonden")
            
            print(f"Gevonden kaartlezers: {[str(reader) for reader in card_readers]}")
            
            # Probeer verbinding per reader
            for reader in card_readers:
                # Skip Windows Hello for Business - dat is geen echte smartcard reader
                if "Windows Hello" in str(reader):
                    continue
                    
                try:
                    print(f"Probeer verbinding met: {reader}")
                    
                    # Maak verbinding met specifieke reader
                    connection = reader.createConnection()
                    connection.connect()
                    
                    # Test of kaart reageert met basic SELECT
                    test_apdu = [0x00, 0xA4, 0x04, 0x00, 0x00]
                    response, sw1, sw2 = connection.transmit(test_apdu)
                    
                    # Als we hier komen is verbinding OK
                    self.card_connection = connection
                    print(f"✅ Verbonden met EID kaart via {reader}")
                    return True
                    
                except Exception as reader_error:
                    print(f"Reader {reader} werkt niet: {reader_error}")
                    continue
            
            # Als we hier komen heeft geen enkele reader gewerkt
            raise Exception("Geen werkende kaartverbinding gevonden. Controleer of EID kaart correct in lezer zit.")
            
        except Exception as e:
            print(f"Fout bij verbinden met kaart: {str(e)}")
            raise
    
    def send_apdu(self, apdu):
        """Stuur APDU commando naar kaart met verbeterde error handling"""
        if not self.card_connection:
            raise Exception("Geen kaartverbinding - roep eerst connect_to_card() aan")
        
        try:
            # Controleer of verbinding nog actief is
            response, sw1, sw2 = self.card_connection.transmit(apdu)
            
            # Controleer status codes
            if sw1 == 0x90 and sw2 == 0x00:
                return response
            elif sw1 == 0x6A and sw2 == 0x82:
                raise Exception("Bestand niet gevonden op EID kaart")
            elif sw1 == 0x69 and sw2 == 0x83:
                raise Exception("PIN geblokkeerd - te veel foute pogingen")
            elif sw1 == 0x63 and (sw2 & 0xF0) == 0xC0:
                remaining = sw2 & 0x0F
                raise Exception(f"Foute PIN - nog {remaining} pogingen over")
            elif sw1 == 0x6A and sw2 == 0x86:
                raise Exception("Verkeerde parameters in APDU commando")
            elif sw1 == 0x6D and sw2 == 0x00:
                raise Exception("Instructie niet ondersteund door kaart")
            else:
                raise Exception(f"APDU fout: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
        except CardConnectionException as e:
            raise Exception(f"Kaartverbinding verloren: {str(e)}")
        except Exception as e:
            if "Card not connected" in str(e) or "connection" in str(e).lower():
                raise Exception("Kaartverbinding verloren - probeer opnieuw")
            print(f"APDU fout: {str(e)}")
            raise
    
    def select_file(self, file_id):
        """Selecteer bestand op kaart met meerdere methoden"""
        # Probeer verschillende SELECT methoden
        methods = [
            [0x00, 0xA4, 0x08, 0x0C, len(file_id)] + file_id,  # Originele methode
            [0x00, 0xA4, 0x02, 0x0C, len(file_id)] + file_id,  # DF selectie
            [0x00, 0xA4, 0x04, 0x0C, len(file_id)] + file_id,  # AID selectie
            [0x00, 0xA4, 0x00, 0x0C, len(file_id)] + file_id,  # MF/EF selectie
        ]
        
        for i, apdu in enumerate(methods):
            try:
                response = self.send_apdu(apdu)
                if i > 0:
                    print(f"✅ File geselecteerd met methode {i+1}")
                return response
            except Exception as e:
                if i == len(methods) - 1:  # Laatste poging
                    raise e
                continue
    
    def read_binary(self, offset=0, length=0):
        """Lees binaire data van kaart"""
        if length == 0:
            # Lees eerst de bestandsgrootte
            apdu = [0x00, 0xB0, (offset >> 8) & 0xFF, offset & 0xFF, 0]
            try:
                data = self.send_apdu(apdu)
                return data
            except:
                return []
        else:
            apdu = [0x00, 0xB0, (offset >> 8) & 0xFF, offset & 0xFF, length]
            return self.send_apdu(apdu)
    
    def get_eid_application_info(self):
        """Selecteer EID applicatie op kaart"""
        try:
            print("🔍 Selecteer EID applicatie...")
            
            # Probeer eerst Belgische EID AID: A000000177504B43532D31
            eid_aid = [0xA0, 0x00, 0x00, 0x01, 0x77, 0x50, 0x4B, 0x43, 0x53, 0x2D, 0x31]
            apdu = [0x00, 0xA4, 0x04, 0x00, len(eid_aid)] + eid_aid
            
            try:
                response = self.send_apdu(apdu)
                print("✅ Belgische EID applicatie geselecteerd")
                return True
            except Exception as aid_error:
                print(f"EID AID selectie mislukt: {aid_error}")
                
                # Probeer alternatieve methode: direct Master File selectie
                try:
                    print("🔄 Probeer Master File selectie...")
                    mf_apdu = [0x00, 0xA4, 0x00, 0x00, 0x02, 0x3F, 0x00]
                    response = self.send_apdu(mf_apdu)
                    print("✅ Master File geselecteerd")
                    return True
                except Exception as mf_error:
                    print(f"Master File selectie mislukt: {mf_error}")
                    
                    # Laatste poging: geen parameters
                    try:
                        print("🔄 Probeer basis file selectie...")
                        basic_apdu = [0x00, 0xA4, 0x00, 0x00]
                        response = self.send_apdu(basic_apdu)
                        print("✅ Basis file geselecteerd")
                        return True
                    except Exception as basic_error:
                        print(f"Basis selectie mislukt: {basic_error}")
                        print("⚠️ Geen EID applicatie gevonden - mogelijk geen Belgische EID kaart")
                        return False
            
        except Exception as e:
            print(f"Fout bij EID applicatie selectie: {str(e)}")
            return False
    
    def read_photo(self):
        """Lees pasfoto van kaart"""
        try:
            self.select_file(self.file_ids['photo'])
            photo_data = self.read_binary()
            
            if photo_data:
                # Converteer naar base64 voor opslag
                return base64.b64encode(bytes(photo_data)).decode('utf-8')
            
            return None
            
        except Exception as e:
            print(f"Fout bij lezen foto: {str(e)}")
            return None
    
    def read_full_eid_data(self, pin_code=None):
        """Lees alle EID gegevens van echte kaart"""
        try:
            if not SMARTCARD_AVAILABLE:
                raise Exception("Smartcard libraries niet beschikbaar")
            
            # Verbind met kaart
            self.connect_to_card()
            
            # Selecteer EID applicatie
            self.get_eid_application_info()
            
            # PIN verificatie is NIET nodig voor standaard identiteitsgegevens
            # Alleen voor beveiligde gegevens zoals certificaten
            # PIN verificatie overslaan voor basis info
            
            # Probeer gegevens te lezen met verschillende methoden
            identity_data = {}
            address_data = {}
            
            # Methode 1: Probeer standaard EID files
            try:
                print("📖 Probeer standaard EID file structuur...")
                identity_data = self.read_eid_identity_file()
                address_data = self.read_eid_address_file()
            except Exception as e:
                print(f"Standaard methode mislukt: {e}")
                
                # Methode 2: Probeer alternatieve file paths
                try:
                    print("🔄 Probeer alternatieve file methoden...")
                    identity_data = self.read_alternative_identity()
                    address_data = self.read_alternative_address()
                except Exception as e2:
                    print(f"Alternatieve methode mislukt: {e2}")
                    
                    # Methode 3: Genereer demo data met kaart info
                    print("🎭 Gebruik generieke kaart informatie...")
                    identity_data, address_data = self.generate_generic_card_data()
            
            # Lees foto indien geselecteerd
            photo_data = None
            if self.available_fields['photo']['selected']:
                try:
                    photo_data = self.read_photo()
                except Exception as e:
                    print(f"Waarschuwing: Kon foto niet lezen: {e}")
            
            # Combineer alle data
            all_data = {**identity_data, **address_data}
            
            if photo_data:
                all_data['photo'] = photo_data
            
            # Voeg metadata toe
            all_data['read_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            all_data['reader_version'] = 'Diabetes Tracker EID Reader v1.3.1'
            
            self.card_data = all_data
            return all_data
            
        except Exception as e:
            print(f"Fout bij lezen EID data: {str(e)}")
            raise
        finally:
            self.disconnect()
    
    def parse_eid_tlv_data(self, raw_data, data_type):
        """Parse EID TLV (Tag-Length-Value) data"""
        if not raw_data:
            return {}
        
        try:
            data = {}
            i = 0
            
            while i < len(raw_data):
                if i + 1 >= len(raw_data):
                    break
                    
                tag = raw_data[i]
                length = raw_data[i + 1] if i + 1 < len(raw_data) else 0
                
                if length == 0 or i + 2 + length > len(raw_data):
                    break
                
                value_bytes = raw_data[i + 2:i + 2 + length]
                
                # Converteer naar string (UTF-8)
                try:
                    value = bytes(value_bytes).decode('utf-8').strip()
                except:
                    value = ''.join([chr(b) for b in value_bytes if 32 <= b <= 126]).strip()
                
                # Map tags naar veld namen
                if data_type == 'identity':
                    field_mapping = {
                        1: 'card_number',
                        2: 'chip_number', 
                        3: 'card_validity_begin',
                        4: 'card_validity_end',
                        5: 'card_delivery_municipality',
                        6: 'national_number',
                        7: 'surname',
                        8: 'first_names',
                        9: 'first_letter_third_given_name',
                        10: 'nationality',
                        11: 'birth_location',
                        12: 'birth_date',
                        13: 'sex',
                        14: 'noble_condition',
                        15: 'document_type',
                        16: 'special_status'
                    }
                elif data_type == 'address':
                    field_mapping = {
                        1: 'street_and_number',
                        2: 'zip_code',
                        3: 'municipality'
                    }
                else:
                    field_mapping = {}
                
                if tag in field_mapping and value:
                    data[field_mapping[tag]] = value
                
                i += 2 + length
            
            return data
            
        except Exception as e:
            print(f"TLV parsing fout voor {data_type}: {str(e)}")
            return {}
    
    def read_eid_identity_file(self):
        """Lees identiteitsgegevens met standaard methode"""
        self.select_file(self.file_ids['identity'])
        raw_data = self.read_binary()
        return self.parse_eid_tlv_data(raw_data, 'identity')
    
    def read_eid_address_file(self):
        """Lees adresgegevens met standaard methode"""
        self.select_file(self.file_ids['address'])
        raw_data = self.read_binary()
        return self.parse_eid_tlv_data(raw_data, 'address')
    
    def read_alternative_identity(self):
        """Probeer alternatieve methode voor identiteit"""
        # Probeer verschillende file IDs
        alt_file_ids = [
            [0x3F, 0x00, 0xDF, 0x01, 0x40, 0x31],  # Standaard
            [0xDF, 0x01, 0x40, 0x31],              # Zonder MF
            [0x40, 0x31],                          # Direct
        ]
        
        for file_id in alt_file_ids:
            try:
                self.select_file(file_id)
                raw_data = self.read_binary()
                if raw_data:
                    return self.parse_eid_tlv_data(raw_data, 'identity')
            except:
                continue
        
        raise Exception("Geen identiteitsfile gevonden")
    
    def read_alternative_address(self):
        """Probeer alternatieve methode voor adres"""
        # Probeer verschillende file IDs
        alt_file_ids = [
            [0x3F, 0x00, 0xDF, 0x01, 0x40, 0x33],  # Standaard
            [0xDF, 0x01, 0x40, 0x33],              # Zonder MF
            [0x40, 0x33],                          # Direct
        ]
        
        for file_id in alt_file_ids:
            try:
                self.select_file(file_id)
                raw_data = self.read_binary()
                if raw_data:
                    return self.parse_eid_tlv_data(raw_data, 'address')
            except:
                continue
        
        raise Exception("Geen adresfile gevonden")
    
    def generate_generic_card_data(self):
        """Lees echte Belgische eID data met officiële methoden"""
        print("🇧🇪 Lees Belgische eID kaart met officiële methoden...")
        
        try:
            # Stap 1: Probeer Belgische eID applicatie te selecteren
            identity_data, address_data = self.read_belgian_eid_official()
            if identity_data and len(identity_data) > 2:
                return identity_data, address_data
                
        except Exception as e:
            print(f"⚠️ Officiële eID methode gefaald: {e}")
        
        try:
            # Stap 2: Probeer via CLI tools (indien beschikbaar)
            identity_data, address_data = self.try_eid_cli_reader()
            if identity_data and len(identity_data) > 2:
                return identity_data, address_data
                
        except Exception as e:
            print(f"⚠️ CLI methode gefaald: {e}")
        
        try:
            # Stap 3: Probeer directe TLV parsing
            identity_data, address_data = self.read_eid_tlv_direct()
            if identity_data and len(identity_data) > 2:
                return identity_data, address_data
                
        except Exception as e:
            print(f"⚠️ Directe TLV methode gefaald: {e}")
        
        # Stap 4: ATR-gebaseerde unieke identifier
        identity_data = self.get_card_atr_info()
        if not identity_data:
            print("⚠️ Geen kaart data gevonden - gebruik handmatige invoer")
            identity_data = {
                'card_number': 'HANDMATIG_INVOEREN',
                'surname': 'NIET_UITGELEZEN',
                'first_names': 'HANDMATIG_INVOEREN', 
                'birth_date': 'DD/MM/YYYY',
                'sex': 'Onbekend',
                'nationality': 'Onbekend',
                'birth_location': 'Onbekend',
                'national_number': 'HANDMATIG_INVOEREN'
            }
            
        address_data = {
            'street_and_number': 'HANDMATIG_INVOEREN',
            'zip_code': '0000',
            'municipality': 'HANDMATIG_INVOEREN'
        }
        
        print("✅ Kaart data extraction voltooid")
        return identity_data, address_data
    
    def read_belgian_eid_official(self):
        """Lees Belgische eID met officiële BELPIC selectie"""
        print("🇧🇪 Probeer officiële Belgische eID BELPIC selectie...")
        
        try:
            # Selecteer BELPIC applicatie (officiële Belgische eID)
            belpic_aid = [0x00, 0xA4, 0x04, 0x00, 0x0C] + [ord(c) for c in "BELPIC"] + [0x20, 0x20, 0x20, 0x20, 0x20]
            response = self.send_apdu(belpic_aid)
            
            if response and len(response) >= 2 and response[-2:] == [0x90, 0x00]:
                print("✅ BELPIC applicatie geselecteerd")
                
                # Lees identiteitsgegevens
                identity_data = self.read_eid_identity_file()
                address_data = {}
                
                # Probeer adres (vereist mogelijk PIN)
                try:
                    address_data = self.read_eid_address_file()
                except:
                    print("ℹ️ Adresgegevens niet leesbaar (PIN vereist)")
                    address_data = {
                        'street_and_number': 'PIN_VEREIST',
                        'zip_code': 'PIN_VEREIST',
                        'municipality': 'PIN_VEREIST'
                    }
                
                return identity_data, address_data
            else:
                raise Exception("BELPIC selectie gefaald")
                
        except Exception as e:
            print(f"⚠️ BELPIC methode gefaald: {e}")
            raise e
    
    def try_eid_cli_reader(self):
        """Probeer eID CLI tools te gebruiken"""
        print("🖥️ Probeer eID CLI tools...")
        
        import subprocess
        import os
        import json
        
        # Mogelijke eID CLI tools locaties
        cli_paths = [
            r"C:\Program Files (x86)\Belgium Identity Card\eID Viewer\eid-viewer-cli.exe",
            r"C:\Program Files\Belgium Identity Card\eID Viewer\eid-viewer-cli.exe",
            "eid-viewer-cli",
            "eid-viewer",
            "beid-tool"
        ]
        
        for cli_path in cli_paths:
            try:
                if os.path.exists(cli_path) or cli_path in ["eid-viewer-cli", "eid-viewer", "beid-tool"]:
                    print(f"🔍 Probeer: {cli_path}")
                    
                    # Voer CLI commando uit
                    result = subprocess.run([cli_path, "-x"], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0 and result.stdout:
                        print("✅ CLI data ontvangen")
                        # Parse XML output
                        identity_data, address_data = self.parse_eid_xml(result.stdout)
                        return identity_data, address_data
                        
            except Exception as e:
                print(f"⚠️ CLI {cli_path} gefaald: {e}")
                continue
        
        raise Exception("Geen werkende CLI tools gevonden")
    
    def read_eid_tlv_direct(self):
        """Probeer directe TLV parsing van eID bestanden"""
        print("📋 Probeer directe TLV parsing...")
        
        try:
            # Selecteer Master File
            mf_select = [0x00, 0xA4, 0x00, 0x0C, 0x02, 0x3F, 0x00]
            response = self.send_apdu(mf_select)
            
            # Selecteer eID Directory File
            df_select = [0x00, 0xA4, 0x00, 0x0C, 0x02, 0xDF, 0x01]
            response = self.send_apdu(df_select)
            
            # Selecteer Identity File
            ef_identity = [0x00, 0xA4, 0x00, 0x0C, 0x02, 0x40, 0x31]
            response = self.send_apdu(ef_identity)
            
            if response and len(response) >= 2 and response[-2:] == [0x90, 0x00]:
                # Lees identity data
                identity_raw = self.read_binary()
                identity_data = self.parse_eid_tlv_identity(identity_raw)
                
                # Probeer adres
                address_data = {}
                try:
                    ef_address = [0x00, 0xA4, 0x00, 0x0C, 0x02, 0x40, 0x33]
                    response = self.send_apdu(ef_address)
                    if response and len(response) >= 2 and response[-2:] == [0x90, 0x00]:
                        address_raw = self.read_binary()
                        address_data = self.parse_eid_tlv_address(address_raw)
                except:
                    address_data = {
                        'street_and_number': 'NIET_LEESBAAR',
                        'zip_code': 'NIET_LEESBAAR', 
                        'municipality': 'NIET_LEESBAAR'
                    }
                
                return identity_data, address_data
            else:
                raise Exception("Kon eID bestanden niet selecteren")
                
        except Exception as e:
            print(f"⚠️ Directe TLV parsing gefaald: {e}")
            raise e
    
    def parse_eid_xml(self, xml_data):
        """Parse XML output van eID CLI tools"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_data)
            
            identity_data = {}
            address_data = {}
            
            # Parse identity fields
            for elem in root.iter():
                if 'surname' in elem.tag.lower():
                    identity_data['surname'] = elem.text or 'ONBEKEND'
                elif 'firstnames' in elem.tag.lower() or 'givenname' in elem.tag.lower():
                    identity_data['first_names'] = elem.text or 'ONBEKEND'
                elif 'nationalnumber' in elem.tag.lower():
                    identity_data['national_number'] = elem.text or 'ONBEKEND'
                elif 'birthdate' in elem.tag.lower():
                    identity_data['birth_date'] = elem.text or 'ONBEKEND'
                elif 'sex' in elem.tag.lower() or 'gender' in elem.tag.lower():
                    identity_data['sex'] = elem.text or 'ONBEKEND'
                elif 'nationality' in elem.tag.lower():
                    identity_data['nationality'] = elem.text or 'ONBEKEND'
                elif 'cardnumber' in elem.tag.lower():
                    identity_data['card_number'] = elem.text or 'ONBEKEND'
                elif 'street' in elem.tag.lower():
                    address_data['street_and_number'] = elem.text or 'ONBEKEND'
                elif 'zip' in elem.tag.lower() or 'postal' in elem.tag.lower():
                    address_data['zip_code'] = elem.text or 'ONBEKEND'
                elif 'municipality' in elem.tag.lower() or 'city' in elem.tag.lower():
                    address_data['municipality'] = elem.text or 'ONBEKEND'
            
            print(f"✅ XML parsing succesvol: {len(identity_data)} velden gevonden")
            return identity_data, address_data
            
        except Exception as e:
            print(f"⚠️ XML parsing gefaald: {e}")
            return {}, {}
    
    def parse_eid_tlv_identity(self, raw_data):
        """Parse TLV gecodeerde identiteitsgegevens"""
        try:
            if not raw_data or len(raw_data) < 10:
                return {}
            
            # Basis TLV parsing voor eID
            identity_data = {}
            i = 0
            
            while i < len(raw_data) - 2:
                try:
                    tag = raw_data[i]
                    length = raw_data[i + 1]
                    
                    if i + 2 + length > len(raw_data):
                        break
                    
                    value_bytes = raw_data[i + 2:i + 2 + length]
                    value = ''.join(chr(b) for b in value_bytes if 32 <= b <= 126).strip()
                    
                    # Map eID tags naar velden
                    if tag == 0x01:  # Card Number
                        identity_data['card_number'] = value
                    elif tag == 0x02:  # Chip Number
                        identity_data['chip_number'] = value
                    elif tag == 0x06:  # National Number
                        identity_data['national_number'] = value
                    elif tag == 0x07:  # Surname
                        identity_data['surname'] = value
                    elif tag == 0x08:  # First Names
                        identity_data['first_names'] = value
                    elif tag == 0x0B:  # Birth Date
                        identity_data['birth_date'] = value
                    elif tag == 0x0C:  # Birth Location
                        identity_data['birth_location'] = value
                    elif tag == 0x0D:  # Sex
                        identity_data['sex'] = value
                    elif tag == 0x0E:  # Nationality
                        identity_data['nationality'] = value
                    
                    i += 2 + length
                    
                except:
                    i += 1
            
            print(f"✅ TLV identity parsing: {len(identity_data)} velden")
            return identity_data
            
        except Exception as e:
            print(f"⚠️ TLV identity parsing gefaald: {e}")
            return {}
    
    def parse_eid_tlv_address(self, raw_data):
        """Parse TLV gecodeerde adresgegevens"""
        try:
            if not raw_data or len(raw_data) < 10:
                return {}
            
            address_data = {}
            i = 0
            
            while i < len(raw_data) - 2:
                try:
                    tag = raw_data[i]
                    length = raw_data[i + 1]
                    
                    if i + 2 + length > len(raw_data):
                        break
                    
                    value_bytes = raw_data[i + 2:i + 2 + length]
                    value = ''.join(chr(b) for b in value_bytes if 32 <= b <= 126).strip()
                    
                    # Map address tags
                    if tag == 0x01:  # Street and Number
                        address_data['street_and_number'] = value
                    elif tag == 0x02:  # Zip Code
                        address_data['zip_code'] = value
                    elif tag == 0x03:  # Municipality
                        address_data['municipality'] = value
                    
                    i += 2 + length
                    
                except:
                    i += 1
            
            print(f"✅ TLV address parsing: {len(address_data)} velden")
            return address_data
            
        except Exception as e:
            print(f"⚠️ TLV address parsing gefaald: {e}")
            return {}

    def parse_card_response(self, response):
        """Parse kaart response naar leesbare data"""
        try:
            # Converteer naar string
            if isinstance(response, list):
                # Filter status bytes (laatste 2)
                data_bytes = response[:-2] if len(response) > 2 else response
                # Probeer als ASCII
                try:
                    return ''.join(chr(b) for b in data_bytes if 32 <= b <= 126)
                except:
                    return ''.join(f'{b:02X}' for b in data_bytes)
            return str(response)
        except:
            return None
    
    def extract_personal_info(self, data_str):
        """Extraheer persoonlijke info uit kaart data string"""
        try:
            import re
            info = {}
            
            # Zoek naar datum patronen (DD/MM/YYYY)
            dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', data_str)
            if dates:
                info['birth_date'] = dates[0]
            
            # Zoek naar nationale nummer patronen
            nat_nums = re.findall(r'\b\d{2}\.\d{2}\.\d{2}-\d{3}\.\d{2}\b', data_str)
            if nat_nums:
                info['national_number'] = nat_nums[0]
            
            # Zoek naar namen (capitalized words)
            names = re.findall(r'\b[A-Z][a-z]+\b', data_str)
            if len(names) >= 2:
                info['surname'] = names[0]
                info['first_names'] = ' '.join(names[1:3])
            
            return info if info else None
        except:
            return None
    
    def get_card_atr_info(self):
        """Krijg basis kaart info van ATR"""
        try:
            if hasattr(self.card_connection, 'connection'):
                atr = str(self.card_connection.connection.getATR())
                print(f"📋 Kaart ATR: {atr}")
                
                # Genereer unieke identifier van ATR
                import hashlib
                card_id = hashlib.md5(atr.encode()).hexdigest()[:8].upper()
                
                return {
                    'card_number': f'KAART-{card_id}',
                    'surname': f'ONBEKEND-{card_id[:4]}',
                    'first_names': 'HANDMATIG_INVOEREN',
                    'birth_date': 'DD/MM/YYYY',
                    'sex': 'Onbekend',
                    'nationality': 'Te_bepalen',
                    'birth_location': 'Onbekend',
                    'national_number': f'ATR-{card_id}'
                }
        except:
            pass
        return {}

    def verify_pin(self, pin_code):
        """Verifieer PIN code op echte EID kaart"""
        try:
            if not pin_code or len(pin_code) != 4 or not pin_code.isdigit():
                raise Exception("PIN code moet exact 4 cijfers bevatten")
            
            print(f"🔐 Verifieer PIN voor EID kaart...")
            
            # Controleer verbinding
            if not self.card_connection:
                raise Exception("Geen kaartverbinding voor PIN verificatie")
            
            # APDU voor PIN verificatie op Belgische EID
            # VERIFY commando voor EID PIN: CLA=00, INS=20, P1=00, P2=01
            pin_bytes = [int(d) for d in pin_code]
            
            # EID PIN format: 4 cijfers + 4x 0xFF padding
            padded_pin = pin_bytes + [0xFF, 0xFF, 0xFF, 0xFF]
            
            apdu = [0x00, 0x20, 0x00, 0x01, 0x08] + padded_pin
            
            print(f"Verstuur PIN verificatie APDU...")
            response = self.send_apdu(apdu)
            print("✅ PIN verificatie succesvol")
            return True
                
        except Exception as e:
            error_msg = str(e)
            print(f"PIN verificatie fout: {error_msg}")
            
            # Specifieke PIN fouten worden al door send_apdu afgehandeld
            # Hier alleen specifieke PIN-gerelateerde messages
            if "geblokkeerd" in error_msg:
                raise Exception("❌ PIN geblokkeerd - contacteer gemeente voor deblokkering")
            elif "pogingen over" in error_msg:
                raise Exception(f"❌ {error_msg}")
            elif "Foute PIN" in error_msg:
                raise Exception(f"❌ {error_msg}")
            elif "PIN code moet" in error_msg:
                raise Exception(f"❌ {error_msg}")
            elif "verbinding" in error_msg.lower():
                raise Exception("❌ Kaartverbinding verloren tijdens PIN verificatie")
            else:
                raise Exception(f"❌ PIN verificatie mislukt: {error_msg}")
    
    def disconnect(self):
        """Verbreek kaartverbinding"""
        if self.card_connection:
            try:
                self.card_connection.disconnect()
                self.card_connection = None
                print("✅ Kaartverbinding verbroken")
            except Exception as e:
                print(f"Fout bij verbreken verbinding: {str(e)}")

class EIDReaderDialog:
    def __init__(self, parent, patient_management=None, update_mode=False, patient_id=None):
        self.parent = parent
        self.patient_management = patient_management
        self.eid_reader = BelgianEIDReader(parent)
        self.dialog = None
        self.pin_attempts = 0
        self.max_pin_attempts = 3
        self.update_mode = update_mode
        self.patient_id = patient_id
    
    def show_eid_not_available(self):
        """Toon melding dat EID functionaliteit niet beschikbaar is"""
        show_eid_not_available()
        
    def show_field_selection_dialog(self):
        """Toon dialoog voor selectie van uit te lezen velden"""
        selection_window = tk.Toplevel(self.parent)
        title = "🔄 EID Update - Velden Selecteren" if self.update_mode else "📋 EID Velden Selecteren"
        selection_window.title(title)
        selection_window.geometry("600x700")
        selection_window.transient(self.parent)
        selection_window.grab_set()
        
        # Centreren
        selection_window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 100,
            self.parent.winfo_rooty() + 100
        ))
        
        # Main frame
        main_frame = ttk.Frame(selection_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_text = "🔄 EID Update - Selecteer Gegevens" if self.update_mode else "📋 Selecteer EID Gegevens"
        ttk.Label(main_frame, text=header_text, 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        instruction_text = "Selecteer welke gegevens bijgewerkt moeten worden:" if self.update_mode else "Selecteer welke gegevens van de EID kaart uitgelezen moeten worden:"
        ttk.Label(main_frame, text=instruction_text, 
                 font=('Arial', 11)).pack(pady=(0, 20))
        
        # Scrollable frame voor checkboxes
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Checkboxes voor elk veld
        self.field_vars = {}
        
        # Groepeer velden per categorie
        categories = {
            '👤 Persoonlijke Gegevens': [
                'national_number', 'surname', 'first_names', 'birth_date', 
                'birth_location', 'sex', 'nationality', 'noble_condition'
            ],
            '📍 Adresgegevens': [
                'street_and_number', 'zip_code', 'municipality'
            ],
            '🆔 Kaartgegevens': [
                'card_number', 'chip_number', 'card_validity_begin', 
                'card_validity_end', 'card_delivery_municipality', 'document_type'
            ],
            '📷 Overige': [
                'photo', 'special_status', 'first_letter_third_given_name'
            ]
        }
        
        for category, fields in categories.items():
            # Categorie header
            cat_frame = ttk.LabelFrame(scrollable_frame, text=category, padding="10")
            cat_frame.pack(fill=tk.X, pady=(10, 5), padx=10)
            
            for field in fields:
                if field in self.eid_reader.available_fields:
                    field_info = self.eid_reader.available_fields[field]
                    var = tk.BooleanVar(value=field_info['selected'])
                    self.field_vars[field] = var
                    
                    cb = ttk.Checkbutton(cat_frame, text=field_info['name'], variable=var)
                    cb.pack(anchor=tk.W, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def select_all():
            for var in self.field_vars.values():
                var.set(True)
        
        def select_none():
            for var in self.field_vars.values():
                var.set(False)
        
        def proceed_with_selection():
            # Update selecties
            for field, var in self.field_vars.items():
                self.eid_reader.available_fields[field]['selected'] = var.get()
            
            selection_window.destroy()
            self.start_eid_reading()
        
        ttk.Button(button_frame, text="✅ Alles Selecteren", 
                  command=select_all).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Niets Selecteren", 
                  command=select_none).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Doorgaan met Lezen", 
                  command=proceed_with_selection).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🚫 Annuleren", 
                  command=selection_window.destroy).pack(side=tk.LEFT)
    
    def start_eid_reading(self):
        """Start EID uitleen proces"""
        # Controleer of smartcard beschikbaar is
        if not self.eid_reader.is_smartcard_available():
            self.show_demo_mode_dialog()
            return
        
        # Toon EID reader dialoog
        self.show_eid_reader_dialog()
    
    def show_demo_mode_dialog(self):
        """Toon demo mode dialoog"""
        result = messagebox.askyesno(
            "🔧 Demo Mode", 
            "EID reader libraries zijn niet geïnstalleerd.\n\n"
            "Wil je doorgaan in demo mode met testgegevens?\n\n"
            "In demo mode worden voorbeeldgegevens gebruikt\n"
            "om de functionaliteit te demonstreren."
        )
        
        if result:
            self.simulate_eid_reading()
    
    def show_eid_reader_dialog(self):
        """Toon EID reader interface"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🆔 Belgische EID Kaart Reader")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centreren
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 200,
            self.parent.winfo_rooty() + 200
        ))
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="🆔 EID Kaart Reader", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, text="Klaar om EID kaart te lezen...", 
                                     font=('Arial', 11))
        self.status_label.pack()
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructies", padding="15")
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions = [
            "1. 🔌 Controleer of je kaartlezer aangesloten is",
            "2. 🆔 Steek je Belgische EID kaart in de lezer", 
            "3. 📖 Standaard gegevens worden gelezen zonder PIN",
            "4. ⏳ Wacht tot de gegevens uitgelezen zijn"
        ]
        
        for instruction in instructions:
            ttk.Label(instructions_frame, text=instruction, font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.read_button = ttk.Button(button_frame, text="📖 Lees EID", 
                                     command=self.begin_card_reading)
        self.read_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Optionele PIN knop voor gevorderde functies  
        self.pin_button = ttk.Button(button_frame, text="🔐 Met PIN (Certificaten)", 
                                    command=self.begin_card_reading_with_pin)
        self.pin_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Annuleren", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def begin_card_reading(self):
        """Begin met kaart uitleen direct zonder dialoog"""
        # Start direct zonder UI dialoog
        thread = threading.Thread(target=self.read_card_thread)
        thread.daemon = True
        thread.start()
    
    def begin_card_reading_with_pin(self):
        """Begin met kaart uitleen met PIN voor certificaten"""
        self.read_button.config(state='disabled')
        self.pin_button.config(state='disabled')
        self.progress.start()
        
        # Start in thread om UI responsive te houden
        thread = threading.Thread(target=self.read_card_with_pin_thread)
        thread.daemon = True
        thread.start()
    
    def read_card_thread(self):
        """Lees kaart direct zonder UI feedback"""
        try:
            # Zoek kaartlezers
            readers = self.eid_reader.get_card_readers()
            if not readers:
                raise Exception("Geen kaartlezers gevonden")
            
            # Probeer verbinding te maken
            connected = False
            for attempt in range(3):
                try:
                    self.eid_reader.connect_to_card(timeout=5)
                    connected = True
                    break
                except Exception as e:
                    if attempt == 2:
                        raise e
                    time.sleep(1)
            
            if not connected:
                raise Exception("Kan niet verbinden met EID kaart")
            
            # Lees gegevens direct
            self.read_public_data_direct()
            
        except Exception as e:
            messagebox.showerror("EID Fout", f"Kon EID niet uitlezen:\n\n{str(e)}")
    
    def read_public_data_direct(self):
        """Lees EID gegevens en toon direct resultaten"""
        try:
            # Selecteer gewenste velden
            selected_fields = {field: info for field, info in self.eid_reader.available_fields.items() 
                             if info['selected']}
            
            # Lees EID data zonder PIN
            eid_data = self.eid_reader.read_full_eid_data(pin_code=None)
            
            # Toon resultaten direct
            self.show_eid_results(eid_data)
            
        except Exception as e:
            messagebox.showerror("EID Fout", f"Kon EID niet uitlezen:\n\n{str(e)}")
    
    def read_card_with_pin_thread(self):
        """Lees kaart met PIN voor certificaten"""
        try:
            # Update status
            self.dialog.after(0, lambda: self.status_label.config(text="🔍 Zoek naar kaartlezers..."))
            time.sleep(1)
            
            # Zoek kaartlezers
            readers = self.eid_reader.get_card_readers()
            if not readers:
                raise Exception("Geen kaartlezers gevonden")
            
            self.dialog.after(0, lambda: self.status_label.config(text="🆔 Wacht op EID kaart..."))
            
            # Probeer verbinding te maken
            connected = False
            for attempt in range(3):
                try:
                    self.eid_reader.connect_to_card(timeout=5)
                    connected = True
                    break
                except Exception as e:
                    if attempt == 2:
                        raise e
                    time.sleep(1)
            
            if not connected:
                raise Exception("Kan niet verbinden met EID kaart")
            
            self.dialog.after(0, lambda: self.status_label.config(text="🔢 PIN code vereist..."))
            
            # Vraag PIN code
            self.dialog.after(0, self.ask_pin_code)
            
        except Exception as e:
            self.dialog.after(0, lambda: self.handle_reading_error(str(e)))
    
    def read_eid_without_pin(self):
        """Lees EID gegevens zonder PIN (alleen openbare gegevens)"""
        try:
            self.progress.start()
            
            # Start lezen in thread
            thread = threading.Thread(target=self.read_public_data_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.handle_reading_error(str(e))
    
    def read_public_data_thread(self):
        """Lees openbare EID gegevens in background thread"""
        try:
            self.dialog.after(0, lambda: self.status_label.config(text="📖 Lees identiteitsgegevens..."))
            
            # Selecteer gewenste velden
            selected_fields = {field: info for field, info in self.eid_reader.available_fields.items() 
                             if info['selected']}
            
            # Lees EID data zonder PIN
            eid_data = self.eid_reader.read_full_eid_data(pin_code=None)
            
            # Update UI en toon resultaten
            self.dialog.after(0, lambda: self.progress.stop())
            self.dialog.after(0, lambda: self.status_label.config(text="✅ EID succesvol uitgelezen"))
            self.dialog.after(0, lambda: self.show_eid_results(eid_data))
            
        except Exception as e:
            self.dialog.after(0, lambda: self.handle_reading_error(str(e)))
    
    def ask_pin_code(self):
        """Vraag PIN code van gebruiker"""
        self.progress.stop()
        
        pin_dialog = simpledialog.askstring(
            "🔢 PIN Code", 
            "Voer je EID PIN code in:",
            show='*'
        )
        
        if pin_dialog:
            self.progress.start()
            # Verifieer PIN in thread
            thread = threading.Thread(target=self.verify_pin_and_read, args=(pin_dialog,))
            thread.daemon = True
            thread.start()
        else:
            self.handle_reading_error("PIN code vereist")
    
    def verify_pin_and_read(self, pin_code):
        """Verifieer PIN en lees gegevens"""
        try:
            self.dialog.after(0, lambda: self.status_label.config(text="🔐 Verifieer PIN code..."))
            
            # Verifieer PIN
            self.eid_reader.verify_pin(pin_code)
            
            self.dialog.after(0, lambda: self.status_label.config(text="📖 Lees EID gegevens..."))
            time.sleep(1)
            
            # Lees alle gegevens
            eid_data = self.eid_reader.read_full_eid_data(pin_code)
            
            self.dialog.after(0, lambda: self.status_label.config(text="✅ Gegevens succesvol uitgelezen!"))
            
            # Toon resultaten
            self.dialog.after(1000, lambda: self.show_eid_results(eid_data))
            
        except Exception as e:
            self.pin_attempts += 1
            if self.pin_attempts < self.max_pin_attempts:
                self.dialog.after(0, lambda: self.status_label.config(text="❌ Fout PIN code, probeer opnieuw..."))
                self.dialog.after(2000, self.ask_pin_code)
            else:
                self.dialog.after(0, lambda: self.handle_reading_error(f"Te veel PIN pogingen: {str(e)}"))
    
    def simulate_eid_reading(self):
        """Simuleer EID uitleen met demo gegevens"""
        self.dialog.destroy() if self.dialog else None
        
        # Genereer demo gegevens
        demo_data = {
            'card_number': '592012345612',
            'chip_number': 'DEMO2024001',
            'card_validity_begin': '15/01/2020',
            'card_validity_end': '15/01/2030',
            'card_delivery_municipality': 'Antwerpen',
            'national_number': '90010112345',
            'surname': 'JANSSEN',
            'first_names': 'JAN KAREL',
            'birth_date': '01/01/1990',
            'birth_location': 'Antwerpen',
            'sex': 'M',
            'nationality': 'Belg',
            'street_and_number': 'Grote Markt 1',
            'zip_code': '2000',
            'municipality': 'Antwerpen',
            'document_type': 'Belgische identiteitskaart',
            'read_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.show_eid_results(demo_data)
    
    def show_eid_results(self, eid_data):
        """Toon EID uitleen resultaten met selecteerbare velden"""
        if self.dialog:
            self.dialog.destroy()
        
        # Maak resultaten venster
        results_window = tk.Toplevel(self.parent)
        results_window.title("📋 EID Gegevens Selecteren")
        results_window.geometry("800x900")
        results_window.transient(self.parent)
        results_window.grab_set()
        
        # Centreren
        results_window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 30
        ))
        
        # Main frame
        main_frame = ttk.Frame(results_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header afhankelijk van mode
        if self.update_mode and self.patient_id:
            ttk.Label(main_frame, text="🔄 EID Update - Selecteer Gegevens om Bij te Werken", 
                     font=('Arial', 16, 'bold')).pack(pady=(0, 10))
            ttk.Label(main_frame, text="Vink aan welke gegevens je wilt bijwerken in het patiëntenprofiel:", 
                     font=('Arial', 11)).pack(pady=(0, 20))
        else:
            ttk.Label(main_frame, text="📋 EID Gegevens - Selecteer te Overzetten Velden", 
                     font=('Arial', 16, 'bold')).pack(pady=(0, 10))
            ttk.Label(main_frame, text="Vink aan welke gegevens je wilt overzetten naar het patiëntenprofiel:", 
                     font=('Arial', 11)).pack(pady=(0, 20))
        
        # Selectie knoppen
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Track selecties
        self.field_selections = {}
        
        def select_all():
            for var in self.field_selections.values():
                var.set(True)
        
        def select_none():
            for var in self.field_selections.values():
                var.set(False)
        
        ttk.Button(selection_frame, text="✅ Alles Selecteren", 
                  command=select_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(selection_frame, text="❌ Niets Selecteren", 
                  command=select_none).pack(side=tk.LEFT)
        
        # Scrollable frame voor gegevens
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Categorieën voor betere organisatie
        categories = {
            'Persoonlijke Gegevens': ['surname', 'first_names', 'birth_date', 'birth_location', 'sex', 'nationality', 'national_number'],
            'Kaart Informatie': ['card_number', 'card_validity_begin', 'card_validity_end'],
            'Adres Gegevens': ['street_and_number', 'zip_code', 'municipality'],
            'Extra Informatie': ['photo', 'read_timestamp']
        }
        
        # Toon gegevens per categorie met checkboxes
        for category_name, field_list in categories.items():
            # Categorie header
            cat_frame = ttk.LabelFrame(scrollable_frame, text=category_name, padding="10")
            cat_frame.pack(fill=tk.X, pady=10, padx=10)
            
            for field in field_list:
                if field in eid_data and eid_data[field]:
                    # Frame voor elk veld
                    field_frame = ttk.Frame(cat_frame)
                    field_frame.pack(fill=tk.X, pady=3)
                    
                    # Checkbox voor selectie
                    var = tk.BooleanVar(value=True)  # Standaard alles geselecteerd
                    self.field_selections[field] = var
                    
                    checkbox = ttk.Checkbutton(field_frame, variable=var)
                    checkbox.pack(side=tk.LEFT)
                    
                    # Veld naam
                    field_name = self.eid_reader.available_fields.get(field, {}).get('name', field.replace('_', ' ').title())
                    ttk.Label(field_frame, text=f"{field_name}:", 
                             font=('Arial', 10, 'bold'), width=20).pack(side=tk.LEFT, padx=(5, 10))
                    
                    # Waarde
                    value_text = str(eid_data[field])
                    if len(value_text) > 50:
                        value_text = value_text[:47] + "..."
                    
                    ttk.Label(field_frame, text=value_text, 
                             font=('Arial', 10), foreground='darkgreen').pack(side=tk.LEFT)
        
        canvas.pack(side="left", fill="both", expand=True, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_to_patient_profile():
            """Sla alleen geselecteerde gegevens op in patiënten profiel"""
            try:
                # Filter alleen geselecteerde velden
                selected_data = {}
                selected_fields = []
                
                for field, var in self.field_selections.items():
                    if var.get() and field in eid_data:
                        selected_data[field] = eid_data[field]
                        selected_fields.append(field)
                
                if not selected_data:
                    messagebox.showwarning("Geen Selectie", "Selecteer ten minste één veld om over te zetten.")
                    return
                
                if self.patient_management:
                    if self.update_mode and self.patient_id:
                        # Update bestaande patiënt - direct zonder melding
                        success = self.patient_management.update_existing_patient_from_eid(self.patient_id, selected_data)
                        
                        # Sluit venster en ga terug naar patiënt management
                        results_window.destroy()
                        
                        if success:
                            # Melding tonen en terug naar patiënt management
                            messagebox.showinfo("Update Succesvol", 
                                              f"Patiënt succesvol bijgewerkt via EID!\n\n"
                                              f"Bijgewerkte velden: {len(selected_fields)}")
                        
                        # Breng patiënt management venster naar voren
                        if hasattr(self.patient_management, 'root') and self.patient_management.root:
                            self.patient_management.root.lift()
                            self.patient_management.root.focus_force()
                    else:
                        # Voeg nieuwe patiënt toe
                        patient_data = self.map_eid_to_patient_data(selected_data)
                        success = self.patient_management.add_patient_from_eid(patient_data)
                        
                        if success:
                            messagebox.showinfo("Succes", 
                                              f"Patiënt succesvol toegevoegd via EID!\n\n"
                                              f"Overgezette velden: {len(selected_fields)}")
                            results_window.destroy()
                        else:
                            messagebox.showerror("Fout", "Kon patiënt niet toevoegen.")
                else:
                    messagebox.showerror("Fout", "Patiënten management niet beschikbaar.")
                    
            except Exception as e:
                messagebox.showerror("Fout", f"Kon gegevens niet opslaan: {str(e)}")
        
        def export_to_file():
            """Exporteer alleen geselecteerde gegevens naar bestand"""
            try:
                from tkinter import filedialog
                import json
                
                # Filter alleen geselecteerde velden
                selected_data = {}
                for field, var in self.field_selections.items():
                    if var.get() and field in eid_data:
                        selected_data[field] = eid_data[field]
                
                if not selected_data:
                    messagebox.showwarning("Geen Selectie", "Selecteer ten minste één veld om te exporteren.")
                    return
                
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                    title="Export Geselecteerde EID Gegevens"
                )
                
                if filename:
                    if filename.endswith('.txt'):
                        # Export als leesbare tekst
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write("BELGISCHE EID GEGEVENS\n")
                            f.write("=" * 30 + "\n\n")
                            
                            for field, value in selected_data.items():
                                field_name = self.eid_reader.available_fields.get(field, {}).get('name', field.replace('_', ' ').title())
                                f.write(f"{field_name}: {value}\n")
                    else:
                        # Export als JSON
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(selected_data, f, indent=2, ensure_ascii=False)
                    
                    messagebox.showinfo("Export Succesvol", 
                                      f"Geselecteerde gegevens geëxporteerd naar {filename}\n\n"
                                      f"Aantal velden: {len(selected_data)}")
                    
            except Exception as e:
                messagebox.showerror("Export Fout", f"Kon niet exporteren: {str(e)}")
        
        # Knoppen afhankelijk van mode
        if self.update_mode and self.patient_id:
            # Update mode - toon bijwerken knop
            ttk.Button(button_frame, text="🔄 Patiënt Bijwerken", 
                      command=save_to_patient_profile,
                      style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        else:
            # Nieuwe patiënt mode - toon opslaan knop
            ttk.Button(button_frame, text="💾 Opslaan als Patiënt", 
                      command=save_to_patient_profile,
                      style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📤 Exporteren", 
                  command=export_to_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Opnieuw Lezen", 
                  command=lambda: [results_window.destroy(), show_eid_reader_dialog(self.parent, self.patient_management, self.update_mode, self.patient_id)]).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Sluiten", 
                  command=results_window.destroy).pack(side=tk.LEFT)
    
    def map_eid_to_patient_data(self, eid_data):
        """Map EID gegevens naar patiënt data structuur"""
        patient_data = {
            'first_name': eid_data.get('first_names', '').split()[0] if eid_data.get('first_names') else '',
            'last_name': eid_data.get('surname', ''),
            'birth_date': eid_data.get('birth_date', ''),
            'gender': 'Man' if eid_data.get('sex') == 'M' else 'Vrouw' if eid_data.get('sex') == 'V' else 'Onbekend',
            'national_number': eid_data.get('national_number', ''),
            'nationality': eid_data.get('nationality', ''),
            'address': eid_data.get('street_and_number', ''),
            'postal_code': eid_data.get('zip_code', ''),
            'city': eid_data.get('municipality', ''),
            'birth_place': eid_data.get('birth_location', ''),
            'card_number': eid_data.get('card_number', ''),
            'card_validity': f"{eid_data.get('card_validity_begin', '')} - {eid_data.get('card_validity_end', '')}",
            'eid_read_date': eid_data.get('read_timestamp', ''),
            'photo_base64': eid_data.get('photo', '')
        }
        
        return patient_data
    
    def handle_reading_error(self, error_message):
        """Behandel EID uitleen fouten"""
        self.progress.stop()
        self.read_button.config(state='normal')
        self.pin_button.config(state='normal')
        self.status_label.config(text=f"❌ Fout: {error_message}")
        
        # Disconnect van kaart
        self.eid_reader.disconnect()
        
        messagebox.showerror("EID Fout", f"Kon EID niet uitlezen:\n\n{error_message}")

def show_eid_not_available():
    """Toon melding dat EID functionaliteit niet beschikbaar is"""
    messagebox.showerror(
        "EID Niet Beschikbaar", 
        "EID functionaliteit is niet beschikbaar.\n\n"
        "Smartcard libraries zijn niet geïnstalleerd.\n"
        "Installeer pyscard om EID functionaliteit te gebruiken:\n\n"
        "pip install pyscard"
    )

def show_eid_reader_dialog(parent, patient_management=None, update_mode=False, patient_id=None):
    """Hoofdfunctie om EID reader dialoog te tonen - direct uitlezen"""
    try:
        if not SMARTCARD_AVAILABLE:
            show_eid_not_available()
            return
            
        dialog = EIDReaderDialog(parent, patient_management, update_mode, patient_id)
        # Skip selectie dialoog en ga direct naar uitlezen
        dialog.begin_card_reading()
        
    except Exception as e:
        messagebox.showerror("EID Reader Fout", f"Kon EID reader niet starten: {str(e)}")

if __name__ == "__main__":
    # Test de EID reader
    root = tk.Tk()
    root.withdraw()
    
    show_eid_reader_dialog(root)
    
    root.mainloop() 