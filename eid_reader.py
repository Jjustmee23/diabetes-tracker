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
        """Selecteer bestand op kaart"""
        apdu = [0x00, 0xA4, 0x08, 0x0C, len(file_id)] + file_id
        return self.send_apdu(apdu)
    
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
                    mf_apdu = [0x00, 0xA4, 0x00, 0x0C, 0x02, 0x3F, 0x00]
                    response = self.send_apdu(mf_apdu)
                    print("✅ Master File geselecteerd")
                    return True
                except Exception as mf_error:
                    print(f"Master File selectie mislukt: {mf_error}")
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
            
            # PIN verificatie indien vereist
            if pin_code:
                self.verify_pin(pin_code)
            
            # Lees identiteitsbestand
            identity_data = {}
            try:
                self.select_file(self.file_ids['identity'])
                raw_data = self.read_binary()
                identity_data = self.parse_eid_tlv_data(raw_data, 'identity')
            except Exception as e:
                print(f"Waarschuwing: Kon identiteitsgegevens niet lezen: {e}")
            
            # Lees adresbestand
            address_data = {}
            try:
                self.select_file(self.file_ids['address'])
                raw_data = self.read_binary()
                address_data = self.parse_eid_tlv_data(raw_data, 'address')
            except Exception as e:
                print(f"Waarschuwing: Kon adresgegevens niet lezen: {e}")
            
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
            "3. 🔢 Voer je PIN code in wanneer gevraagd",
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
        
        self.read_button = ttk.Button(button_frame, text="🔄 Start Uitleen", 
                                     command=self.begin_card_reading)
        self.read_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.demo_button = ttk.Button(button_frame, text="🎭 Demo Mode", 
                                     command=self.simulate_eid_reading)
        self.demo_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Annuleren", 
                  command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def begin_card_reading(self):
        """Begin met kaart uitleen in thread"""
        self.read_button.config(state='disabled')
        self.progress.start()
        
        # Start in thread om UI responsive te houden
        thread = threading.Thread(target=self.read_card_thread)
        thread.daemon = True
        thread.start()
    
    def read_card_thread(self):
        """Lees kaart in background thread"""
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
        """Toon EID uitleen resultaten"""
        if self.dialog:
            self.dialog.destroy()
        
        # Maak resultaten venster
        results_window = tk.Toplevel(self.parent)
        results_window.title("📋 EID Gegevens Uitgelezen")
        results_window.geometry("700x800")
        results_window.transient(self.parent)
        results_window.grab_set()
        
        # Centreren
        results_window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 100,
            self.parent.winfo_rooty() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(results_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="📋 EID Gegevens Succesvol Uitgelezen", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
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
        
        # Toon alle uitgelezen gegevens
        for field, value in eid_data.items():
            if field in self.eid_reader.available_fields:
                field_info = self.eid_reader.available_fields[field]
                if field_info['selected'] and field != 'photo':
                    field_frame = ttk.Frame(scrollable_frame)
                    field_frame.pack(fill=tk.X, pady=5, padx=10)
                    
                    ttk.Label(field_frame, text=f"{field_info['name']}:", 
                             font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
                    ttk.Label(field_frame, text=str(value), 
                             font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_to_patient_profile():
            """Sla gegevens op in patiënten profiel"""
            try:
                if self.patient_management:
                    if self.update_mode and self.patient_id:
                        # Update bestaande patiënt
                        success = self.patient_management.update_existing_patient_from_eid(self.patient_id, eid_data)
                        
                        if success:
                            messagebox.showinfo("Update Succesvol", "Patiënt succesvol bijgewerkt via EID!")
                            results_window.destroy()
                        else:
                            messagebox.showinfo("Update Geannuleerd", "Update geannuleerd door gebruiker.")
                    else:
                        # Voeg nieuwe patiënt toe
                        patient_data = self.map_eid_to_patient_data(eid_data)
                        success = self.patient_management.add_patient_from_eid(patient_data)
                        
                        if success:
                            messagebox.showinfo("Succes", "Patiënt succesvol toegevoegd via EID!")
                            results_window.destroy()
                        else:
                            messagebox.showerror("Fout", "Kon patiënt niet toevoegen.")
                else:
                    messagebox.showerror("Fout", "Patiënten management niet beschikbaar.")
                    
            except Exception as e:
                messagebox.showerror("Fout", f"Kon gegevens niet opslaan: {str(e)}")
        
        def export_to_file():
            """Exporteer gegevens naar bestand"""
            try:
                from tkinter import filedialog
                import json
                
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    title="Export EID Gegevens"
                )
                
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(eid_data, f, indent=2, ensure_ascii=False)
                    
                    messagebox.showinfo("Export", f"Gegevens geëxporteerd naar {filename}")
                    
            except Exception as e:
                messagebox.showerror("Export Fout", f"Kon niet exporteren: {str(e)}")
        
        # Aanpassing knop tekst voor update mode
        save_button_text = "🔄 Bijwerken Patiënt" if self.update_mode else "💾 Opslaan als Patiënt"
        ttk.Button(button_frame, text=save_button_text, 
                  command=save_to_patient_profile).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📤 Exporteren", 
                  command=export_to_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Opnieuw Lezen", 
                  command=lambda: [results_window.destroy(), self.show_field_selection_dialog()]).pack(side=tk.LEFT, padx=(0, 10))
        
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
    """Hoofdfunctie om EID reader dialoog te tonen"""
    try:
        if not SMARTCARD_AVAILABLE:
            show_eid_not_available()
            return
            
        dialog = EIDReaderDialog(parent, patient_management, update_mode, patient_id)
        dialog.show_field_selection_dialog()
        
    except Exception as e:
        messagebox.showerror("EID Reader Fout", f"Kon EID reader niet starten: {str(e)}")

if __name__ == "__main__":
    # Test de EID reader
    root = tk.Tk()
    root.withdraw()
    
    show_eid_reader_dialog(root)
    
    root.mainloop() 