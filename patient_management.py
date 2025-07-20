import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import json
# AI functionaliteiten verwijderd
from tkcalendar import DateEntry
import ttkbootstrap as tb

# EID Reader import (fallback als niet beschikbaar)
try:
    from eid_reader import show_eid_reader_dialog
    EID_READER_AVAILABLE = True
except ImportError:
    EID_READER_AVAILABLE = False
    print("⚠️ EID Reader niet beschikbaar")

class PatientProfile:
    def __init__(self, parent):
        self.parent = parent
        self.patient_window = None
        self.medication_window = None
        self.schedule_window = None
        # AI functionaliteiten verwijderd
        
    def create_patient_window(self):
        """Maak patiënten fiche venster"""
        if self.patient_window:
            self.patient_window.destroy()
            
        self.patient_window = tk.Toplevel(self.parent)
        self.patient_window.title("Patiënten Fiche")
        self.patient_window.geometry("1000x700")
        
        # Database initialisatie
        self.init_patient_database()
        
        # Voeg complete medicatie lijst toe
        self.add_complete_medications()
        
        # GUI maken
        self.create_patient_gui()
        self.load_patients()
        
    def init_patient_database(self):
        """Database voor patiënten en medicatie"""
        self.patient_conn = sqlite3.connect('patient_data.db')
        self.patient_cursor = self.patient_conn.cursor()
        
        # Patiënten tabel (uitgebreid voor EID gegevens)
        self.patient_cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                rijksnummer TEXT UNIQUE,
                blood_group TEXT,
                weight REAL,
                height REAL,
                birth_date TEXT,
                phone TEXT,
                email TEXT,
                emergency_contact TEXT,
                notes TEXT,
                created_date TEXT,
                -- EID specifieke velden
                national_number TEXT,
                nationality TEXT,
                address TEXT,
                postal_code TEXT,
                city TEXT,
                birth_place TEXT,
                gender TEXT,
                card_number TEXT,
                card_validity TEXT,
                eid_read_date TEXT,
                photo_base64 TEXT
            )
        ''')
        
        # Medicatie tabel
        self.patient_cursor.execute('''
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                medication_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                morning BOOLEAN DEFAULT 0,
                afternoon BOOLEAN DEFAULT 0,
                evening BOOLEAN DEFAULT 0,
                night BOOLEAN DEFAULT 0,
                start_date TEXT,
                end_date TEXT,
                active BOOLEAN DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Medicatie fiche tabel
        self.patient_cursor.execute('''
            CREATE TABLE IF NOT EXISTS medication_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_name TEXT UNIQUE,
                description TEXT,
                pros TEXT,
                cons TEXT,
                warnings TEXT,
                pregnancy_warning TEXT,
                side_effects TEXT,
                interactions TEXT,
                dosage_info TEXT
            )
        ''')
        
        # Medicatie schema tabel
        self.patient_cursor.execute('''
            CREATE TABLE IF NOT EXISTS medication_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                medication_id INTEGER,
                scheduled_time TEXT,
                taken BOOLEAN DEFAULT 0,
                missed BOOLEAN DEFAULT 0,
                date TEXT,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (medication_id) REFERENCES medications (id)
            )
        ''')
        
        self.patient_conn.commit()
        
    def add_complete_medications(self):
        """Voeg complete medicatie lijst toe aan de database"""
        complete_medications = [
            # DIABETES MEDICATIE
            {
                'name': 'Metformine 500mg',
                'description': 'Diabetes medicatie - verlaagt bloedsuiker door lever glucose productie te remmen',
                'pros': 'Effectief, goedkoop, weinig bijwerkingen, verlaagt risico op hart- en vaatziekten, kan gewichtsverlies bevorderen',
                'cons': 'Kan maagklachten veroorzaken, niet geschikt bij nierproblemen, kan vitamine B12 tekort veroorzaken',
                'warnings': 'Niet gebruiken bij nierproblemen, overleg bij leverproblemen, stop bij ernstige infecties',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap, veilig in normale dosering',
                'side_effects': 'Maagklachten, diarree, misselijkheid, vitamine B12 tekort, metaalachtige smaak',
                'interactions': 'Kan interactie hebben met alcohol, verminderd effect door corticosteroïden',
                'dosage_info': '500mg 2-3x per dag bij maaltijd, geleidelijk opbouwen'
            },
            {
                'name': 'Insuline (kortwerkend)',
                'description': 'Diabetes medicatie - verlaagt bloedsuiker snel door glucose opname te stimuleren',
                'pros': 'Snel werkend, goed regelbaar, effectief bij hoge bloedsuiker, levensreddend bij diabetes type 1',
                'cons': 'Risico op hypoglykemie, injectie nodig, gewichtstoename mogelijk, kostbaar',
                'warnings': 'Altijd suiker bij de hand hebben, regelmatig bloedsuiker meten, nooit overslaan',
                'pregnancy_warning': 'Veilig tijdens zwangerschap onder begeleiding, dosering kan aangepast worden',
                'side_effects': 'Hypoglykemie, injectieplaats reacties, gewichtstoename, allergische reacties',
                'interactions': 'Veel interacties mogelijk, overleg bij andere medicatie, alcohol vermijden',
                'dosage_info': 'Dosering op basis van bloedsuiker en voeding, voor maaltijd injecteren'
            },
            {
                'name': 'Gliclazide 80mg',
                'description': 'Diabetes medicatie - stimuleert insuline productie in pancreas',
                'pros': 'Effectief, oraal in te nemen, goed verdraagbaar, betaalbaar',
                'cons': 'Kan hypoglykemie veroorzaken, gewichtstoename, niet geschikt bij nierproblemen',
                'warnings': 'Niet gebruiken bij nierproblemen, regelmatig bloedsuiker meten, voorzichtig bij ouderen',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap, overleg met arts',
                'side_effects': 'Hypoglykemie, gewichtstoename, hoofdpijn, duizeligheid, huidreacties',
                'interactions': 'Interactie met alcohol, verminderd effect door corticosteroïden',
                'dosage_info': '80mg 1-2x per dag voor ontbijt, geleidelijk opbouwen'
            },
            {
                'name': 'Sitagliptine 100mg',
                'description': 'Diabetes medicatie - verhoogt GLP-1 hormoon voor betere bloedsuiker controle',
                'pros': 'Weinig hypoglykemie risico, gewichtsneutraal, goed verdraagbaar, eenmaal daags',
                'cons': 'Kostbaar, kan pancreatitis veroorzaken, niet geschikt bij hartfalen',
                'warnings': 'Niet gebruiken bij pancreatitis, voorzichtig bij hartfalen, regelmatig controleren',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Hoofdpijn, duizeligheid, misselijkheid, pancreatitis, gewrichtspijn',
                'interactions': 'Weinig interacties, veilig met andere diabetes medicatie',
                'dosage_info': '100mg 1x per dag, met of zonder voedsel'
            },
            
            # HART- EN VAATZIEKTEN MEDICATIE
            {
                'name': 'Bisoprolol 5mg',
                'description': 'Bètablokker - verlaagt bloeddruk en hartslag',
                'pros': 'Effectief bij hoge bloeddruk, beschermt hart, goed verdraagbaar, betaalbaar',
                'cons': 'Kan vermoeidheid veroorzaken, niet geschikt bij astma, kan koude handen/voeten',
                'warnings': 'Niet plotseling stoppen, voorzichtig bij astma/COPD, regelmatig controleren',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap, mogelijk risico voor foetus',
                'side_effects': 'Vermoeidheid, koude handen/voeten, duizeligheid, slaapproblemen, depressie',
                'interactions': 'Interactie met andere bloeddruk medicatie, voorzichtig met alcohol',
                'dosage_info': '5mg 1x per dag, geleidelijk opbouwen indien nodig'
            },
            {
                'name': 'Metoprolol 50mg',
                'description': 'Bètablokker - verlaagt bloeddruk en hartslag, beschermt hart',
                'pros': 'Effectief bij hoge bloeddruk, beschermt na hartinfarct, goed verdraagbaar',
                'cons': 'Kan vermoeidheid veroorzaken, niet geschikt bij astma, kan erectieproblemen',
                'warnings': 'Niet plotseling stoppen, voorzichtig bij astma/COPD, regelmatig controleren',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Vermoeidheid, duizeligheid, koude extremiteiten, erectieproblemen, depressie',
                'interactions': 'Interactie met andere bloeddruk medicatie, voorzichtig met alcohol',
                'dosage_info': '50mg 1-2x per dag, geleidelijk opbouwen'
            },
            {
                'name': 'Enalapril 10mg',
                'description': 'ACE-remmer - verlaagt bloeddruk door bloedvaten te verwijden',
                'pros': 'Effectief bij hoge bloeddruk, beschermt nieren, goed verdraagbaar',
                'cons': 'Kan droge hoest veroorzaken, niet geschikt bij zwangerschap, kan duizeligheid',
                'warnings': 'Niet gebruiken tijdens zwangerschap, voorzichtig bij nierproblemen, regelmatig controleren',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap - gevaarlijk voor foetus',
                'side_effects': 'Droge hoest, duizeligheid, hoofdpijn, smaakverandering, huiduitslag',
                'interactions': 'Interactie met andere bloeddruk medicatie, voorzichtig met NSAIDs',
                'dosage_info': '10mg 1x per dag, geleidelijk opbouwen indien nodig'
            },
            {
                'name': 'Amlodipine 5mg',
                'description': 'Calciumantagonist - verlaagt bloeddruk door bloedvaten te verwijden',
                'pros': 'Effectief bij hoge bloeddruk, weinig interacties, goed verdraagbaar',
                'cons': 'Kan enkeloedeem veroorzaken, hoofdpijn, niet geschikt bij hartfalen',
                'warnings': 'Voorzichtig bij hartfalen, regelmatig controleren, geleidelijk opbouwen',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Enkeloedeem, hoofdpijn, duizeligheid, blozen, misselijkheid',
                'interactions': 'Weinig interacties, veilig met andere bloeddruk medicatie',
                'dosage_info': '5mg 1x per dag, geleidelijk opbouwen indien nodig'
            },
            {
                'name': 'Simvastatine 40mg',
                'description': 'Statine - verlaagt cholesterol en beschermt tegen hart- en vaatziekten',
                'pros': 'Effectief cholesterol verlagend, beschermt hart en vaten, goed verdraagbaar',
                'cons': 'Kan spierpijn veroorzaken, leverfunctie controleren, niet geschikt bij leverproblemen',
                'warnings': 'Regelmatig leverfunctie controleren, niet gebruiken bij leverproblemen',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap',
                'side_effects': 'Spierpijn, hoofdpijn, misselijkheid, leverfunctie afwijkingen, slapeloosheid',
                'interactions': 'Interactie met grapefruit, voorzichtig met andere cholesterol medicatie',
                'dosage_info': '40mg 1x per dag in de avond, met of zonder voedsel'
            },
            {
                'name': 'Atorvastatine 20mg',
                'description': 'Statine - verlaagt cholesterol en beschermt tegen hart- en vaatziekten',
                'pros': 'Zeer effectief cholesterol verlagend, beschermt hart en vaten, flexibele dosering',
                'cons': 'Kan spierpijn veroorzaken, leverfunctie controleren, kostbaar',
                'warnings': 'Regelmatig leverfunctie controleren, niet gebruiken bij leverproblemen',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap',
                'side_effects': 'Spierpijn, hoofdpijn, misselijkheid, leverfunctie afwijkingen, slapeloosheid',
                'interactions': 'Interactie met grapefruit, voorzichtig met andere cholesterol medicatie',
                'dosage_info': '20mg 1x per dag, met of zonder voedsel'
            },
            
            # DAGELIJKSE MEDICATIE
            {
                'name': 'Ibuprofen 400mg',
                'description': 'Pijnstiller en ontstekingsremmer - verlaagt pijn, koorts en ontstekingen',
                'pros': 'Effectief tegen pijn en ontstekingen, vrij verkrijgbaar, snel werkend',
                'cons': 'Kan maagklachten veroorzaken, niet geschikt bij hartproblemen, kan nierproblemen',
                'warnings': 'Niet gebruiken bij maagzweren, overleg bij hartproblemen, niet langdurig',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap, vooral laatste trimester',
                'side_effects': 'Maagklachten, hoofdpijn, duizeligheid, nierproblemen, verhoogde bloeddruk',
                'interactions': 'Kan interactie hebben met bloedverdunners, voorzichtig met andere pijnstillers',
                'dosage_info': '400mg 3-4x per dag bij maaltijd, niet langer dan 10 dagen'
            },
            {
                'name': 'Paracetamol 500mg',
                'description': 'Pijnstiller en koortsverlager - verlaagt pijn en koorts',
                'pros': 'Veilig, weinig bijwerkingen, goed verdraagbaar, vrij verkrijgbaar',
                'cons': 'Minder effectief bij ontstekingen, levertoxiciteit bij overdosering',
                'warnings': 'Niet meer dan 4g per dag, voorzichtig bij leverproblemen',
                'pregnancy_warning': 'Veilig tijdens zwangerschap in normale dosering',
                'side_effects': 'Zelden bijwerkingen bij normale dosering, levertoxiciteit bij overdosering',
                'interactions': 'Weinig interacties, veilig met andere medicatie',
                'dosage_info': '500-1000mg 4-6x per dag, maximaal 4g per dag'
            },
            {
                'name': 'Omeprazol 20mg',
                'description': 'Maagzuurremmer - vermindert maagzuur productie',
                'pros': 'Effectief bij maagklachten, goed verdraagbaar, beschermt maag',
                'cons': 'Langdurig gebruik kan botontkalking veroorzaken, vitamine B12 tekort',
                'warnings': 'Niet langer dan 8 weken zonder overleg, voorzichtig bij ouderen',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Hoofdpijn, diarree, misselijkheid, botontkalking, vitamine B12 tekort',
                'interactions': 'Kan interactie hebben met andere medicatie, vermindert opname van sommige medicijnen',
                'dosage_info': '20mg 1x per dag voor ontbijt, 30 minuten voor maaltijd'
            },
            {
                'name': 'Cetirizine 10mg',
                'description': 'Antihistaminicum - verlicht allergie symptomen',
                'pros': 'Effectief bij allergie, weinig sedatie, eenmaal daags, goed verdraagbaar',
                'cons': 'Kan slaperigheid veroorzaken, droge mond, niet geschikt bij nierproblemen',
                'warnings': 'Voorzichtig bij nierproblemen, niet combineren met alcohol',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Slaperigheid, droge mond, hoofdpijn, duizeligheid, vermoeidheid',
                'interactions': 'Interactie met alcohol, voorzichtig met andere sedativa',
                'dosage_info': '10mg 1x per dag, met of zonder voedsel'
            },
            {
                'name': 'Salbutamol inhalator',
                'description': 'Luchtwegverwijder - verlicht astma en COPD symptomen',
                'pros': 'Snel werkend, levensreddend bij astma, goed verdraagbaar',
                'cons': 'Kan hartkloppingen veroorzaken, niet voor langdurig gebruik, kan verslaving',
                'warnings': 'Alleen bij kortademigheid gebruiken, niet overdoseren, regelmatig controleren',
                'pregnancy_warning': 'Veilig tijdens zwangerschap onder begeleiding',
                'side_effects': 'Hartkloppingen, trillen, hoofdpijn, duizeligheid, droge mond',
                'interactions': 'Weinig interacties, veilig met andere astma medicatie',
                'dosage_info': '1-2 pufjes bij kortademigheid, maximaal 8 pufjes per dag'
            },
            {
                'name': 'Levothyroxine 50mcg',
                'description': 'Schildklierhormoon - vervangt tekort aan schildklierhormoon',
                'pros': 'Effectief bij schildklierproblemen, levensreddend, goed verdraagbaar',
                'cons': 'Lifetime behandeling nodig, regelmatige controle, interactie met voedsel',
                'warnings': 'Nuchter innemen, regelmatig bloedonderzoek, niet combineren met ijzer',
                'pregnancy_warning': 'Veilig tijdens zwangerschap, dosering kan aangepast worden',
                'side_effects': 'Hartkloppingen, nervositeit, gewichtsverlies, slapeloosheid bij overdosering',
                'interactions': 'Interactie met ijzer, calcium, soja, 4 uur wachten met andere medicatie',
                'dosage_info': '50mcg 1x per dag nuchter, 30 minuten voor ontbijt'
            },
            {
                'name': 'Prednison 5mg',
                'description': 'Corticosteroïd - onderdrukt ontstekingen en immuunsysteem',
                'pros': 'Effectief bij ontstekingen, snel werkend, levensreddend bij ernstige aandoeningen',
                'cons': 'Veel bijwerkingen, gewichtstoename, botontkalking, niet langdurig',
                'warnings': 'Niet plotseling stoppen, regelmatige controle, voorzichtig bij diabetes',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Gewichtstoename, botontkalking, diabetes, hoge bloeddruk, stemmingswisselingen',
                'interactions': 'Veel interacties, voorzichtig met andere medicatie',
                'dosage_info': '5mg 1x per dag bij ontbijt, geleidelijk afbouwen'
            },
            {
                'name': 'Furosemide 40mg',
                'description': 'Plaspil - verwijdert overtollig vocht uit lichaam',
                'pros': 'Effectief bij vochtophoping, verlaagt bloeddruk, snel werkend',
                'cons': 'Kan uitdroging veroorzaken, verlies van kalium, niet geschikt bij nierproblemen',
                'warnings': 'Regelmatig bloedonderzoek, voorzichtig bij uitdroging, niet voor langdurig',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Frequent urineren, uitdroging, kaliumtekort, duizeligheid, spierkrampen',
                'interactions': 'Interactie met andere bloeddruk medicatie, voorzichtig met NSAIDs',
                'dosage_info': '40mg 1x per dag in de ochtend, met veel water'
            },
            {
                'name': 'Acetylsalicylzuur 80mg',
                'description': 'Bloedverdunner - voorkomt bloedstolsels en hart- en vaatziekten',
                'pros': 'Beschermt tegen hartinfarct en beroerte, goedkoop, effectief',
                'cons': 'Kan maagklachten veroorzaken, verhoogd risico op bloedingen',
                'warnings': 'Niet gebruiken bij maagzweren, voorzichtig bij bloedingen, regelmatige controle',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap, vooral laatste trimester',
                'side_effects': 'Maagklachten, verhoogd risico op bloedingen, hoofdpijn, duizeligheid',
                'interactions': 'Interactie met andere bloedverdunners, voorzichtig met NSAIDs',
                'dosage_info': '80mg 1x per dag, levenslang bij hart- en vaatziekten'
            }
        ]
        
        # Voeg toe als ze nog niet bestaan
        for med in complete_medications:
            try:
                self.patient_cursor.execute('''
                    INSERT OR IGNORE INTO medication_info 
                    (medication_name, description, pros, cons, warnings, pregnancy_warning, 
                     side_effects, interactions, dosage_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (med['name'], med['description'], med['pros'], med['cons'], 
                      med['warnings'], med['pregnancy_warning'], med['side_effects'], 
                      med['interactions'], med['dosage_info']))
            except Exception:
                pass
        
        self.patient_conn.commit()
        
    def create_patient_gui(self):
        """GUI voor patiënten fiche"""
        # Notebook voor tabs
        notebook = ttk.Notebook(self.patient_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tab 1: Patiënt Profiel
        profile_frame = ttk.Frame(notebook)
        notebook.add(profile_frame, text="Patiënt Profiel")
        
        # Patiënt informatie
        info_frame = ttk.LabelFrame(profile_frame, text="Persoonlijke Informatie", padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Patiënt gegevens
        patient_data = self.get_patient_data()
        if patient_data:
            # Toon patiënt informatie
            ttk.Label(info_frame, text=f"Naam: {patient_data['first_name']} {patient_data['last_name']}", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Rijksnummer: {patient_data['rijksnummer']}").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Bloedgroep: {patient_data['blood_group']}").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Gewicht: {patient_data['weight']} kg").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Lengte: {patient_data['height']} cm").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Geboortedatum: {patient_data['birth_date']}").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Telefoon: {patient_data['phone']}").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Email: {patient_data['email']}").pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Noodcontact: {patient_data['emergency_contact']}").pack(anchor=tk.W, pady=2)
            
            if patient_data['notes']:
                ttk.Label(info_frame, text=f"Opmerkingen: {patient_data['notes']}").pack(anchor=tk.W, pady=2)
            
            # Bewerken knoppen
            edit_buttons_frame = ttk.Frame(info_frame)
            edit_buttons_frame.pack(pady=20)
            
            ttk.Button(edit_buttons_frame, text="✏️ Bewerken", 
                      command=lambda: self.edit_patient_data(patient_data)).pack(side=tk.LEFT, padx=(0, 15))
            
            # EID bewerken knop (alleen als beschikbaar)
            if EID_READER_AVAILABLE:
                ttk.Button(edit_buttons_frame, text="🆔 Bewerken met EID", 
                          command=lambda: self.update_patient_via_eid(patient_data['id']), 
                          style='info.TButton').pack(side=tk.LEFT)
            else:
                ttk.Button(edit_buttons_frame, text="🆔 EID (Niet Beschikbaar)", 
                          command=self.show_eid_not_available,
                          state='disabled').pack(side=tk.LEFT)
        else:
            # Nieuwe patiënt toevoegen
            ttk.Label(info_frame, text="Nog geen patiënt profiel aangemaakt", 
                     font=('Arial', 12, 'bold')).pack(pady=20)
            
            # Knoppen frame
            buttons_frame = ttk.Frame(info_frame)
            buttons_frame.pack(pady=20)
            
            ttk.Button(buttons_frame, text="Patiënt Toevoegen", 
                      command=self.add_patient).pack(side=tk.LEFT, padx=(0, 15))
            
            # EID knop (alleen als beschikbaar)
            if EID_READER_AVAILABLE:
                ttk.Button(buttons_frame, text="🆔 Toevoegen via EID", 
                          command=self.add_patient_via_eid, 
                          style='info.TButton').pack(side=tk.LEFT)
            else:
                ttk.Button(buttons_frame, text="🆔 EID (Niet Beschikbaar)", 
                          command=self.show_eid_not_available,
                          state='disabled').pack(side=tk.LEFT)
        
        # Tab 2: Medicatie Beheer
        medication_frame = ttk.Frame(notebook)
        notebook.add(medication_frame, text="Medicatie Beheer")
        
        # Medicatie lijst voor deze patiënt
        med_list_frame = ttk.LabelFrame(medication_frame, text="Huidige Medicatie", padding="20")
        med_list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview voor medicatie
        med_columns = ('Medicatie', 'Dosering', 'Frequentie', 'Ochtend', 'Middag', 'Avond', 'Nacht', 'Actief', 'Details')
        self.patient_med_tree = ttk.Treeview(med_list_frame, columns=med_columns, show='headings', height=10)
        
        for col in med_columns[:-1]:
            self.patient_med_tree.heading(col, text=col)
            self.patient_med_tree.column(col, width=110)
        self.patient_med_tree.heading('Details', text='Details')
        self.patient_med_tree.column('Details', width=80)
        self.patient_med_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Dubbelklik binding voor medicatie details
        self.patient_med_tree.bind('<Double-1>', self.open_medication_details_popup)
        
        # Knoppen
        med_buttons = ttk.Frame(med_list_frame)
        med_buttons.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(med_buttons, text="Medicatie Toevoegen", command=self.add_patient_medication_modern, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(med_buttons, text="Bewerken", command=self.edit_patient_medication_modern).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(med_buttons, text="Schema Bekijken", command=self.view_schedule).pack(side=tk.LEFT, padx=(0, 15))
        self.load_patient_medications_modern()
    
    def add_patient_via_eid(self):
        """Voeg patiënt toe via EID kaart"""
        try:
            if not EID_READER_AVAILABLE:
                self.show_eid_not_available()
                return
            
            # Start EID reader dialoog
            show_eid_reader_dialog(self.patient_window, self)
            
        except Exception as e:
            messagebox.showerror("EID Fout", f"Kon EID reader niet starten: {str(e)}")
    
    def show_eid_not_available(self):
        """Toon melding dat EID niet beschikbaar is"""
        messagebox.showinfo(
            "EID Niet Beschikbaar", 
            "EID card reader functionaliteit is niet beschikbaar.\n\n"
            "Om EID kaarten te kunnen uitlezen, moeten de volgende\n"
            "bibliotheken geïnstalleerd worden:\n"
            "• pyscard\n"
            "• smartcard\n"
            "• cryptography\n\n"
            "Installeer deze via: pip install pyscard smartcard cryptography"
        )
    
    def add_patient_from_eid(self, eid_data):
        """Voeg patiënt toe vanuit EID gegevens"""
        try:
            # Maap EID gegevens naar database velden
            patient_data = {
                'first_name': eid_data.get('first_name', ''),
                'last_name': eid_data.get('last_name', ''),
                'rijksnummer': eid_data.get('national_number', ''),
                'birth_date': eid_data.get('birth_date', ''),
                'phone': '',  # Niet beschikbaar op EID
                'email': '',  # Niet beschikbaar op EID
                'emergency_contact': '',  # Niet beschikbaar op EID
                'blood_group': '',  # Niet beschikbaar op EID
                'weight': None,  # Niet beschikbaar op EID
                'height': None,  # Niet beschikbaar op EID
                'notes': f"Toegevoegd via EID op {eid_data.get('eid_read_date', '')}",
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                # EID specifieke velden
                'national_number': eid_data.get('national_number', ''),
                'nationality': eid_data.get('nationality', ''),
                'address': eid_data.get('address', ''),
                'postal_code': eid_data.get('postal_code', ''),
                'city': eid_data.get('city', ''),
                'birth_place': eid_data.get('birth_place', ''),
                'gender': eid_data.get('gender', ''),
                'card_number': eid_data.get('card_number', ''),
                'card_validity': eid_data.get('card_validity', ''),
                'eid_read_date': eid_data.get('eid_read_date', ''),
                'photo_base64': eid_data.get('photo_base64', '')
            }
            
            # Controleer of patiënt al bestaat
            self.patient_cursor.execute('''
                SELECT id FROM patients WHERE rijksnummer = ? OR national_number = ?
            ''', (patient_data['rijksnummer'], patient_data['national_number']))
            
            existing_patient = self.patient_cursor.fetchone()
            
            if existing_patient:
                # Vraag of gebruiker wil updaten
                result = messagebox.askyesno(
                    "Patiënt Bestaat Al", 
                    f"Een patiënt met dit rijksnummer bestaat al.\n\n"
                    f"Wil je de gegevens bijwerken met de EID informatie?"
                )
                
                if result:
                    return self.update_patient_with_eid(existing_patient[0], eid_data)
                else:
                    return False
            
            # Voeg nieuwe patiënt toe
            self.patient_cursor.execute('''
                INSERT INTO patients (
                    first_name, last_name, rijksnummer, birth_date, phone, email, 
                    emergency_contact, blood_group, weight, height, notes, created_date,
                    national_number, nationality, address, postal_code, city, 
                    birth_place, gender, card_number, card_validity, eid_read_date, photo_base64
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_data['first_name'], patient_data['last_name'], patient_data['rijksnummer'],
                patient_data['birth_date'], patient_data['phone'], patient_data['email'],
                patient_data['emergency_contact'], patient_data['blood_group'], patient_data['weight'],
                patient_data['height'], patient_data['notes'], patient_data['created_date'],
                patient_data['national_number'], patient_data['nationality'], patient_data['address'],
                patient_data['postal_code'], patient_data['city'], patient_data['birth_place'],
                patient_data['gender'], patient_data['card_number'], patient_data['card_validity'],
                patient_data['eid_read_date'], patient_data['photo_base64']
            ))
            
            self.patient_conn.commit()
            
            # Refresh de GUI
            if self.patient_window:
                self.patient_window.destroy()
                self.create_patient_window()
            
            messagebox.showinfo("Succes", f"Patiënt {patient_data['first_name']} {patient_data['last_name']} succesvol toegevoegd via EID!")
            
            return True
            
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Fout", f"Patiënt bestaat al of database fout: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("Fout", f"Kon patiënt niet toevoegen: {str(e)}")
            return False
    
    def update_patient_with_eid(self, patient_id, eid_data):
        """Update bestaande patiënt met EID gegevens"""
        try:
            # Update patiënt met EID gegevens
            self.patient_cursor.execute('''
                UPDATE patients SET 
                    national_number = ?, nationality = ?, address = ?, postal_code = ?, 
                    city = ?, birth_place = ?, gender = ?, card_number = ?, 
                    card_validity = ?, eid_read_date = ?, photo_base64 = ?,
                    notes = COALESCE(notes, '') || ? 
                WHERE id = ?
            ''', (
                eid_data.get('national_number', ''),
                eid_data.get('nationality', ''),
                eid_data.get('address', ''),
                eid_data.get('postal_code', ''),
                eid_data.get('city', ''),
                eid_data.get('birth_place', ''),
                eid_data.get('gender', ''),
                eid_data.get('card_number', ''),
                eid_data.get('card_validity', ''),
                eid_data.get('eid_read_date', ''),
                eid_data.get('photo_base64', ''),
                f"\n\nEID bijgewerkt op {eid_data.get('eid_read_date', '')}",
                patient_id
            ))
            
            self.patient_conn.commit()
            
            # Refresh de GUI
            if self.patient_window:
                self.patient_window.destroy()
                self.create_patient_window()
            
            messagebox.showinfo("Succes", "Patiënt gegevens succesvol bijgewerkt met EID informatie!")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Update Fout", f"Kon patiënt niet bijwerken: {str(e)}")
            return False
    
    def update_patient_via_eid(self, patient_id):
        """Update bestaande patiënt via EID kaart"""
        try:
            if not EID_READER_AVAILABLE:
                self.show_eid_not_available()
                return
            
            # Bewaar patient_id voor later gebruik
            self.updating_patient_id = patient_id
            
            # Start EID reader dialoog met update context
            show_eid_reader_dialog(self.patient_window, self, update_mode=True, patient_id=patient_id)
            
        except Exception as e:
            messagebox.showerror("EID Update Fout", f"Kon EID update niet starten: {str(e)}")
    
    def update_existing_patient_from_eid(self, patient_id, eid_data):
        """Update bestaande patiënt met EID gegevens"""
        try:
            # Vraag gebruiker welke velden bijgewerkt moeten worden
            update_fields = self.ask_which_fields_to_update(eid_data)
            
            if not update_fields:
                return False  # Gebruiker heeft geannuleerd
            
            # Bouw update query op basis van geselecteerde velden
            update_parts = []
            values = []
            
            field_mappings = {
                'name': ('first_name', 'last_name'),
                'birth_info': ('birth_date', 'birth_place'),
                'nationality': ('nationality',),
                'gender': ('gender',),
                'address': ('address', 'postal_code', 'city'),
                'eid_card': ('card_number', 'card_validity', 'national_number'),
                'photo': ('photo_base64',),
                'eid_metadata': ('eid_read_date',)
            }
            
            for field_category in update_fields:
                if field_category in field_mappings:
                    for db_field in field_mappings[field_category]:
                        if db_field == 'first_name':
                            first_name = eid_data.get('first_name', '').split()[0] if eid_data.get('first_name') else ''
                            update_parts.append(f"{db_field} = ?")
                            values.append(first_name)
                        elif db_field == 'last_name':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('last_name', ''))
                        elif db_field == 'birth_date':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('birth_date', ''))
                        elif db_field == 'birth_place':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('birth_place', ''))
                        elif db_field == 'nationality':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('nationality', ''))
                        elif db_field == 'gender':
                            gender = 'Man' if eid_data.get('gender') == 'M' else 'Vrouw' if eid_data.get('gender') == 'V' else 'Onbekend'
                            update_parts.append(f"{db_field} = ?")
                            values.append(gender)
                        elif db_field == 'address':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('address', ''))
                        elif db_field == 'postal_code':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('postal_code', ''))
                        elif db_field == 'city':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('city', ''))
                        elif db_field == 'card_number':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('card_number', ''))
                        elif db_field == 'card_validity':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('card_validity', ''))
                        elif db_field == 'national_number':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('national_number', ''))
                        elif db_field == 'photo_base64':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('photo_base64', ''))
                        elif db_field == 'eid_read_date':
                            update_parts.append(f"{db_field} = ?")
                            values.append(eid_data.get('eid_read_date', ''))
            
            # Voeg altijd EID update timestamp toe aan notes
            update_parts.append("notes = COALESCE(notes, '') || ?")
            values.append(f"\n\nEID bijgewerkt op {eid_data.get('eid_read_date', '')} - Velden: {', '.join(update_fields)}")
            
            # Voeg patient_id toe voor WHERE clause
            values.append(patient_id)
            
            if update_parts:
                query = f"UPDATE patients SET {', '.join(update_parts)} WHERE id = ?"
                
                self.patient_cursor.execute(query, values)
                self.patient_conn.commit()
                
                # Refresh de GUI
                if self.patient_window:
                    self.patient_window.destroy()
                    self.create_patient_window()
                
                messagebox.showinfo("Update Succesvol", 
                                  f"Patiënt gegevens succesvol bijgewerkt met EID informatie!\n\n"
                                  f"Bijgewerkte velden: {', '.join(update_fields)}")
                
                return True
            else:
                messagebox.showinfo("Geen Updates", "Geen velden geselecteerd voor update.")
                return False
                
        except Exception as e:
            messagebox.showerror("Update Fout", f"Kon patiënt niet bijwerken: {str(e)}")
            return False
    
    def ask_which_fields_to_update(self, eid_data):
        """Vraag gebruiker welke velden bijgewerkt moeten worden"""
        selection_window = tk.Toplevel(self.patient_window)
        selection_window.title("🔄 Selecteer Velden voor Update")
        selection_window.geometry("600x500")
        selection_window.transient(self.patient_window)
        selection_window.grab_set()
        
        # Centreren
        selection_window.geometry("+%d+%d" % (
            self.patient_window.winfo_rootx() + 100,
            self.patient_window.winfo_rooty() + 100
        ))
        
        # Main frame
        main_frame = ttk.Frame(selection_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="🔄 EID Update - Selecteer Velden", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Selecteer welke gegevens bijgewerkt moeten worden met EID informatie:", 
                 font=('Arial', 11)).pack(pady=(0, 20))
        
        # Checkboxes voor verschillende categorieën
        self.update_field_vars = {}
        
        # Veld categorieën met beschrijvingen
        field_categories = [
            ('name', '👤 Naam Gegevens', f"Voornaam: {eid_data.get('first_name', 'N/A')}\nAchternaam: {eid_data.get('last_name', 'N/A')}"),
            ('birth_info', '📅 Geboorte Informatie', f"Geboortedatum: {eid_data.get('birth_date', 'N/A')}\nGeboorteplaats: {eid_data.get('birth_place', 'N/A')}"),
            ('nationality', '🌍 Nationaliteit', f"Nationaliteit: {eid_data.get('nationality', 'N/A')}"),
            ('gender', '⚥ Geslacht', f"Geslacht: {eid_data.get('gender', 'N/A')}"),
            ('address', '📍 Adres Gegevens', f"Adres: {eid_data.get('address', 'N/A')}\nPostcode: {eid_data.get('postal_code', 'N/A')}\nGemeente: {eid_data.get('city', 'N/A')}"),
            ('eid_card', '🆔 EID Kaart Info', f"Kaartnummer: {eid_data.get('card_number', 'N/A')}\nGeldigheid: {eid_data.get('card_validity', 'N/A')}\nRijksnummer: {eid_data.get('national_number', 'N/A')}"),
            ('photo', '📷 Pasfoto', "Pasfoto van EID kaart"),
            ('eid_metadata', '📋 EID Metadata', f"Uitgelezen op: {eid_data.get('eid_read_date', 'N/A')}")
        ]
        
        # Scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for field_key, field_name, field_preview in field_categories:
            var = tk.BooleanVar(value=True)  # Standaard alles geselecteerd
            self.update_field_vars[field_key] = var
            
            # Frame voor elke categorie
            cat_frame = ttk.LabelFrame(scrollable_frame, text=field_name, padding="10")
            cat_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Checkbox
            ttk.Checkbutton(cat_frame, text="Bijwerken", variable=var).pack(anchor=tk.W)
            
            # Preview van EID gegevens
            ttk.Label(cat_frame, text=field_preview, font=('Arial', 9), 
                     foreground='gray').pack(anchor=tk.W, padx=(20, 0))
        
        canvas.pack(side="left", fill="both", expand=True, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
        
        # Resultaat variabele
        self.update_selection_result = None
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def select_all():
            for var in self.update_field_vars.values():
                var.set(True)
        
        def select_none():
            for var in self.update_field_vars.values():
                var.set(False)
        
        def confirm_selection():
            selected_fields = [field for field, var in self.update_field_vars.items() if var.get()]
            self.update_selection_result = selected_fields
            selection_window.destroy()
        
        def cancel_selection():
            self.update_selection_result = None
            selection_window.destroy()
        
        ttk.Button(button_frame, text="✅ Alles Selecteren", 
                  command=select_all).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Niets Selecteren", 
                  command=select_none).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Bijwerken", 
                  command=confirm_selection).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🚫 Annuleren", 
                  command=cancel_selection).pack(side=tk.LEFT)
        
        # Wacht tot window gesloten is
        selection_window.wait_window()
        
        return self.update_selection_result
        
    def get_patient_data(self):
        """Haal patiënt data op (voor 1 patiënt)"""
        try:
            self.patient_cursor.execute('''
                SELECT * FROM patients ORDER BY id LIMIT 1
            ''')
            patient_data = self.patient_cursor.fetchone()
            
            if patient_data:
                columns = [desc[0] for desc in self.patient_cursor.description]
                return dict(zip(columns, patient_data))
            return None
        except Exception:
            return None
            
    def add_patient(self):
        """Nieuwe patiënt toevoegen (vervangt bestaande)"""
        # Verwijder bestaande patiënten
        self.patient_cursor.execute('DELETE FROM patients')
        self.patient_conn.commit()
        
        self.show_patient_form()
        
    def show_patient_form(self, patient_data=None):
        """Toon patiënt formulier"""
        form_window = tk.Toplevel(self.patient_window)
        form_window.title("Patiënt Toevoegen" if not patient_data else "Patiënt Bewerken")
        form_window.geometry("500x600")
        
        # Bloedgroepen lijst
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        # Formulier velden
        fields = [
            ("Voornaam:", "first_name"),
            ("Achternaam:", "last_name"),
            ("Rijksnummer:", "rijksnummer"),
            ("Bloedgroep:", "blood_group"),
            ("Gewicht (kg):", "weight"),
            ("Lengte (cm):", "height"),
            ("Geboortedatum:", "birth_date"),
            ("Telefoon:", "phone"),
            ("Email:", "email"),
            ("Noodcontact:", "emergency_contact"),
            ("Opmerkingen:", "notes")
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_window, text=label).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            if field == "blood_group":
                entry = ttk.Combobox(form_window, values=blood_groups, width=27, state="readonly")
                entry.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
            elif field == "birth_date":
                entry = ttk.Entry(form_window, width=27)
                entry.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
                entry.insert(0, "dd-mm-jjjj")
                entry.bind('<FocusIn>', lambda e: entry.delete(0, tk.END) if entry.get() == "dd-mm-jjjj" else None)
                entry.bind('<FocusOut>', lambda e: entry.insert(0, "dd-mm-jjjj") if entry.get() == "" else None)
            else:
                entry = ttk.Entry(form_window, width=30)
                entry.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
            entries[field] = entry
            if patient_data and field in patient_data:
                if field == "birth_date" and patient_data[field]:
                    try:
                        d = datetime.strptime(patient_data[field], "%Y-%m-%d")
                        entry.delete(0, tk.END)
                        entry.insert(0, d.strftime("%d-%m-%Y"))
                    except:
                        pass
                else:
                    entry.insert(0, str(patient_data[field]))
        
        def save_patient():
            try:
                data = {}
                for field, entry in entries.items():
                    if field == "birth_date":
                        date_str = entry.get()
                        if date_str and date_str != "dd-mm-jjjj":
                            try:
                                d = datetime.strptime(date_str, "%d-%m-%Y")
                                data[field] = d.strftime("%Y-%m-%d")
                            except:
                                data[field] = date_str
                        else:
                            data[field] = ""
                    else:
                        data[field] = entry.get()
                if patient_data:
                    self.patient_cursor.execute('''
                        UPDATE patients SET 
                        first_name=?, last_name=?, rijksnummer=?, blood_group=?, weight=?, 
                        height=?, birth_date=?, phone=?, email=?, emergency_contact=?, notes=?
                        WHERE id=?
                    ''', (data['first_name'], data['last_name'], data['rijksnummer'], 
                          data['blood_group'], data['weight'], data['height'], data['birth_date'],
                          data['phone'], data['email'], data['emergency_contact'], data['notes'],
                          patient_data['id']))
                else:
                    self.patient_cursor.execute('''
                        INSERT INTO patients (first_name, last_name, rijksnummer, blood_group, 
                        weight, height, birth_date, phone, email, emergency_contact, notes, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (data['first_name'], data['last_name'], data['rijksnummer'], 
                          data['blood_group'], data['weight'], data['height'], data['birth_date'],
                          data['phone'], data['email'], data['emergency_contact'], data['notes'],
                          datetime.now().strftime("%Y-%m-%d")))
                self.patient_conn.commit()
                self.load_patients()
                form_window.destroy()
                messagebox.showinfo("Succes", "Patiënt opgeslagen!")
            except Exception as e:
                messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
        ttk.Button(form_window, text="Opslaan", command=save_patient).grid(row=len(fields), column=0, columnspan=2, pady=20)
        
    def load_patients(self):
        """Laad patiënten in de lijst"""
        # This method is no longer used as patient_tree is removed.
        # Keeping it for now as it might be called elsewhere or for future use.
        pass
            
    def edit_patient(self):
        """Patiënt bewerken"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een patiënt.")
            return
            
        item = self.patient_tree.item(selected[0])
        patient_id = item['values'][0]
        
        self.patient_cursor.execute('''
            SELECT * FROM patients WHERE id = ?
        ''', (patient_id,))
        
        patient_data = self.patient_cursor.fetchone()
        if patient_data:
            columns = [desc[0] for desc in self.patient_cursor.description]
            patient_dict = dict(zip(columns, patient_data))
            self.show_patient_form(patient_dict)
            
    def delete_patient(self):
        """Patiënt verwijderen"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een patiënt.")
            return
            
        if messagebox.askyesno("Bevestiging", "Weet je zeker dat je deze patiënt wilt verwijderen?"):
            item = self.patient_tree.item(selected[0])
            patient_id = item['values'][0]
            
            self.patient_cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
            self.patient_conn.commit()
            self.load_patients()
            messagebox.showinfo("Succes", "Patiënt verwijderd!")
            
    def add_medication_info(self):
        """Nieuwe medicatie fiche toevoegen"""
        self.show_medication_form()
        
    def show_medication_form(self, med_data=None):
        """Toon medicatie formulier"""
        form_window = tk.Toplevel(self.patient_window)
        form_window.title("Medicatie Fiche Toevoegen" if not med_data else "Medicatie Fiche Bewerken")
        form_window.geometry("600x700")
        
        # Formulier velden
        fields = [
            ("Medicatie Naam:", "medication_name"),
            ("Beschrijving:", "description"),
            ("Voordelen:", "pros"),
            ("Nadelen:", "cons"),
            ("Waarschuwingen:", "warnings"),
            ("Zwangerschap Waarschuwing:", "pregnancy_warning"),
            ("Bijwerkingen:", "side_effects"),
            ("Interacties:", "interactions"),
            ("Dosering Info:", "dosage_info")
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_window, text=label).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            
            if field in ['description', 'pros', 'cons', 'warnings', 'pregnancy_warning', 'side_effects', 'interactions', 'dosage_info']:
                # Text widget voor lange velden
                text_widget = tk.Text(form_window, height=4, width=40)
                text_widget.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
                entries[field] = text_widget
            else:
                entry = ttk.Entry(form_window, width=40)
                entry.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
                entries[field] = entry
                
            if med_data and field in med_data:
                if field in ['description', 'pros', 'cons', 'warnings', 'pregnancy_warning', 'side_effects', 'interactions', 'dosage_info']:
                    entries[field].insert('1.0', str(med_data[field]))
                else:
                    entries[field].insert(0, str(med_data[field]))
        
        # Opslaan knop
        def save_medication():
            try:
                data = {}
                for field, widget in entries.items():
                    if isinstance(widget, tk.Text):
                        data[field] = widget.get('1.0', tk.END).strip()
                    else:
                        data[field] = widget.get()
                
                if med_data:  # Update
                    self.patient_cursor.execute('''
                        UPDATE medication_info SET 
                        medication_name=?, description=?, pros=?, cons=?, warnings=?,
                        pregnancy_warning=?, side_effects=?, interactions=?, dosage_info=?
                        WHERE id=?
                    ''', (data['medication_name'], data['description'], data['pros'], 
                          data['cons'], data['warnings'], data['pregnancy_warning'],
                          data['side_effects'], data['interactions'], data['dosage_info'],
                          med_data['id']))
                else:  # Insert
                    self.patient_cursor.execute('''
                        INSERT INTO medication_info (medication_name, description, pros, cons,
                        warnings, pregnancy_warning, side_effects, interactions, dosage_info)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (data['medication_name'], data['description'], data['pros'], 
                          data['cons'], data['warnings'], data['pregnancy_warning'],
                          data['side_effects'], data['interactions'], data['dosage_info']))
                
                self.patient_conn.commit()
                self.load_medication_info()
                form_window.destroy()
                messagebox.showinfo("Succes", "Medicatie fiche opgeslagen!")
                
            except Exception as e:
                messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
        
        ttk.Button(form_window, text="Opslaan", command=save_medication).grid(row=len(fields), column=0, columnspan=2, pady=20)
        
    def load_medication_info(self):
        """Laad medicatie info in de lijst"""
        for item in self.med_tree.get_children():
            self.med_tree.delete(item)
            
        self.patient_cursor.execute('''
            SELECT medication_name, description, pros, cons FROM medication_info ORDER BY medication_name
        ''')
        
        for row in self.patient_cursor.fetchall():
            self.med_tree.insert('', 'end', values=(
                row[0], row[1][:50] + "..." if len(row[1]) > 50 else row[1],
                row[2][:50] + "..." if len(row[2]) > 50 else row[2],
                row[3][:50] + "..." if len(row[3]) > 50 else row[3]
            ))
            
    def edit_medication_info(self):
        """Medicatie fiche bewerken"""
        selected = self.med_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een medicatie.")
            return
            
        item = self.med_tree.item(selected[0])
        med_name = item['values'][0]
        
        self.patient_cursor.execute('''
            SELECT * FROM medication_info WHERE medication_name = ?
        ''', (med_name,))
        
        med_data = self.patient_cursor.fetchone()
        if med_data:
            columns = [desc[0] for desc in self.patient_cursor.description]
            med_dict = dict(zip(columns, med_data))
            self.show_medication_form(med_dict)
            
    def delete_medication_info(self):
        """Medicatie fiche verwijderen"""
        selected = self.med_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een medicatie.")
            return
            
        if messagebox.askyesno("Bevestiging", "Weet je zeker dat je deze medicatie fiche wilt verwijderen?"):
            item = self.med_tree.item(selected[0])
            med_name = item['values'][0]
            
            self.patient_cursor.execute('DELETE FROM medication_info WHERE medication_name = ?', (med_name,))
            self.patient_conn.commit()
            self.load_medication_info()
            messagebox.showinfo("Succes", "Medicatie fiche verwijderd!")
            
    def manage_medication(self):
        """Medicatie beheren voor geselecteerde patiënt"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een patiënt.")
            return
            
        item = self.patient_tree.item(selected[0])
        patient_id = item['values'][0]
        patient_name = f"{item['values'][1]} {item['values'][2]}"
        
        self.show_medication_management(patient_id, patient_name)
        
    def show_medication_management(self, patient_id, patient_name):
        """Toon medicatie beheer voor patiënt"""
        if self.medication_window:
            self.medication_window.destroy()
            
        self.medication_window = tk.Toplevel(self.patient_window)
        self.medication_window.title(f"Medicatie Beheer - {patient_name}")
        self.medication_window.geometry("900x600")
        
        # Medicatie lijst voor deze patiënt
        list_frame = ttk.LabelFrame(self.medication_window, text="Medicatie van Patiënt", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview voor medicatie
        med_columns = ('ID', 'Medicatie', 'Dosering', 'Frequentie', 'Ochtend', 'Middag', 'Avond', 'Nacht', 'Actief')
        self.patient_med_tree = ttk.Treeview(list_frame, columns=med_columns, show='headings', height=10)
        
        for col in med_columns:
            self.patient_med_tree.heading(col, text=col)
            self.patient_med_tree.column(col, width=100)
        
        self.patient_med_tree.pack(fill=tk.BOTH, expand=True)
        
        # Knoppen
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Medicatie Toevoegen", 
                  command=lambda: self.add_patient_medication(patient_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Bewerken", 
                  command=lambda: self.edit_patient_medication(patient_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Verwijderen", 
                  command=lambda: self.delete_patient_medication(patient_id)).pack(side=tk.LEFT)
        
        self.load_patient_medications(patient_id)
        
    def add_patient_medication(self, patient_id):
        """Medicatie toevoegen aan patiënt"""
        self.show_patient_medication_form(patient_id)
        
    def show_patient_medication_form(self, patient_id, med_data=None):
        """Toon medicatie formulier voor patiënt"""
        form_window = tk.Toplevel(self.medication_window)
        form_window.title("Medicatie Toevoegen" if not med_data else "Medicatie Bewerken")
        form_window.geometry("500x400")
        # Suggestielijst voor medicatie
        medicatie_suggesties = [
            "Metformine", "Insuline", "Gliclazide", "Sitagliptine", "Empagliflozine", "Dapagliflozine", "Canagliflozine",
            "Acarbose", "Repaglinide", "Nateglinide", "Pioglitazone", "Ibuprofen", "Paracetamol", "Omeprazol",
            "Bisoprolol", "Metoprolol", "Atenolol", "Enalapril", "Lisinopril", "Perindopril", "Amlodipine", "Simvastatine",
            "Atorvastatine", "Rosuvastatine", "Acetylsalicylzuur", "Clopidogrel", "Apixaban", "Rivaroxaban", "Dabigatran",
            "Furosemide", "Spironolacton", "Hydrochloorthiazide", "Amoxicilline", "Ciprofloxacine", "Doxycycline",
            "Levothyroxine", "Prednison", "Salbutamol", "Budesonide", "Cetirizine", "Loratadine", "Esomeprazol",
            "Pantoprazol", "Losartan", "Valsartan", "Olmesartan", "Hydroxychloroquine", "Methotrexaat", "Allopurinol",
            "Colchicine", "Tramadol", "Oxycodon", "Morfine", "Codeïne", "Diazepam", "Oxazepam", "Temazepam"
        ]
        ttk.Label(form_window, text="Medicatie Naam:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        med_name_entry = ttk.Combobox(form_window, width=30, values=medicatie_suggesties)
        med_name_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(form_window, text="Dosering:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        dosage_entry = ttk.Entry(form_window, width=30)
        dosage_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(form_window, text="Frequentie:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        frequency_entry = ttk.Entry(form_window, width=30)
        frequency_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Tijden checkboxes
        ttk.Label(form_window, text="Tijden:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        
        morning_var = tk.BooleanVar()
        afternoon_var = tk.BooleanVar()
        evening_var = tk.BooleanVar()
        night_var = tk.BooleanVar()
        
        ttk.Checkbutton(form_window, text="Ochtend", variable=morning_var).grid(row=4, column=0, sticky=tk.W, padx=20)
        ttk.Checkbutton(form_window, text="Middag", variable=afternoon_var).grid(row=4, column=1, sticky=tk.W, padx=20)
        ttk.Checkbutton(form_window, text="Avond", variable=evening_var).grid(row=5, column=0, sticky=tk.W, padx=20)
        ttk.Checkbutton(form_window, text="Nacht", variable=night_var).grid(row=5, column=1, sticky=tk.W, padx=20)
        
        ttk.Label(form_window, text="Start Datum (YYYY-MM-DD):").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        start_date_entry = ttk.Entry(form_window, width=30)
        start_date_entry.grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)
        start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(form_window, text="Eind Datum (optioneel):").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        end_date_entry = ttk.Entry(form_window, width=30)
        end_date_entry.grid(row=7, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(form_window, text="Opmerkingen:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
        notes_text = tk.Text(form_window, height=4, width=40)
        notes_text.grid(row=8, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Vul in als bewerken
        if med_data:
            med_name_entry.insert(0, med_data['medication_name'])
            dosage_entry.insert(0, med_data['dosage'])
            frequency_entry.insert(0, med_data['frequency'])
            morning_var.set(med_data['morning'])
            afternoon_var.set(med_data['afternoon'])
            evening_var.set(med_data['evening'])
            night_var.set(med_data['night'])
            start_date_entry.delete(0, tk.END)
            start_date_entry.insert(0, med_data['start_date'])
            if med_data['end_date']:
                end_date_entry.insert(0, med_data['end_date'])
            notes_text.insert('1.0', med_data['notes'])
        
        # Opslaan knop
        def save_medication():
            try:
                medication_name = med_name_entry.get().strip()
                if not medication_name:
                    messagebox.showwarning("Waarschuwing", "Voer een medicatie naam in.")
                    return
                
                # Controleer of medicatie-fiche bestaat, zo niet: maak aan met AI
                self.patient_cursor.execute('''
                    SELECT COUNT(*) FROM medication_info WHERE medication_name = ?
                ''', (medication_name,))
                
                if self.patient_cursor.fetchone()[0] == 0:
                    # Medicatie-fiche bestaat niet, maak aan met AI
                    if messagebox.askyesno("AI Medicatie Fiche", 
                                         f"Medicatie '{medication_name}' heeft nog geen fiche. Wil je deze automatisch laten invullen door AI?"):
                        self.create_medication_fiche_with_ai(medication_name)
                
                # Sla patiënt medicatie op
                self.patient_cursor.execute('''
                    INSERT OR REPLACE INTO medications 
                    (patient_id, medication_name, dosage, frequency, morning, afternoon, evening, night, notes, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id, medication_name, dosage_entry.get(), frequency_entry.get(),
                    morning_var.get(), afternoon_var.get(), evening_var.get(), night_var.get(),
                    notes_text.get('1.0', tk.END).strip(), True
                ))
                
                self.patient_conn.commit()
                self.load_patient_medications(patient_id)
                form_window.destroy()
                messagebox.showinfo("Succes", "Medicatie succesvol opgeslagen!")
                
            except Exception as e:
                messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
        
        # Knoppen
        button_frame = ttk.Frame(form_window)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💾 Opslaan", command=save_medication, 
                  style='success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Annuleren", command=form_window.destroy, 
                  style='danger.TButton').pack(side=tk.LEFT)
    
    def create_medication_fiche(self, medication_name):
        """Maak medicatie-fiche aan"""
        try:
            # Controleer of fiche al bestaat
            self.patient_cursor.execute('''
                SELECT id FROM medication_info WHERE medication_name = ?
            ''', (medication_name,))
            
            if self.patient_cursor.fetchone():
                messagebox.showinfo("Info", f"Medicatie-fiche voor '{medication_name}' bestaat al!")
                return
            
            # Maak eenvoudige fiche aan
            self.patient_cursor.execute('''
                INSERT INTO medication_info 
                (medication_name, description, pros, cons, warnings, pregnancy_warning, 
                 side_effects, interactions, dosage_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                medication_name,
                "Beschrijving wordt toegevoegd", 
                "Voordelen worden toegevoegd", 
                "Nadelen worden toegevoegd", 
                "Waarschuwingen worden toegevoegd", 
                "Zwangerschap waarschuwing wordt toegevoegd", 
                "Bijwerkingen worden toegevoegd", 
                "Interacties worden toegevoegd", 
                "Dosering info wordt toegevoegd"
            ))
            
            self.patient_conn.commit()
            messagebox.showinfo("Succes", f"Medicatie-fiche voor '{medication_name}' succesvol aangemaakt!")
            
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
    
    def edit_patient_medication_modern(self):
        """Bewerk patiënt medicatie"""
        patient_data = self.get_patient_data()
        if not patient_data:
            messagebox.showwarning("Waarschuwing", "Geen patiënt gevonden.")
            return
        selected = self.patient_med_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een medicatie.")
            return
        item = self.patient_med_tree.item(selected[0])
        med_name = item['values'][0]
        self.patient_cursor.execute('''
            SELECT * FROM medications WHERE patient_id = ? AND medication_name = ?
        ''', (patient_data['id'], med_name))
        med_data = self.patient_cursor.fetchone()
        if med_data:
            columns = [desc[0] for desc in self.patient_cursor.description]
            med_dict = dict(zip(columns, med_data))
            self.show_patient_medication_form_with_autocomplete(patient_data['id'], med_dict)

    def delete_patient_medication_modern(self):
        """Verwijder patiënt medicatie"""
        patient_data = self.get_patient_data()
        if not patient_data:
            messagebox.showwarning("Waarschuwing", "Geen patiënt gevonden.")
            return
        selected = self.patient_med_tree.selection()
        if not selected:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een medicatie.")
            return
        if messagebox.askyesno("Bevestiging", "Weet je zeker dat je deze medicatie wilt verwijderen?"):
            item = self.patient_med_tree.item(selected[0])
            med_name = item['values'][0]
            self.patient_cursor.execute('''
                DELETE FROM medications WHERE patient_id = ? AND medication_name = ?
            ''', (patient_data['id'], med_name))
            self.patient_conn.commit()
            self.load_patient_medications_modern()
            messagebox.showinfo("Succes", "Medicatie verwijderd!")

    def open_medication_details_popup(self, event):
        item_id = self.patient_med_tree.identify_row(event.y)
        if not item_id:
            return
        med_name = self.patient_med_tree.item(item_id)['values'][0]
        patient_data = self.get_patient_data()
        self.patient_cursor.execute('''
            SELECT * FROM medications WHERE patient_id = ? AND medication_name = ?
        ''', (patient_data['id'], med_name))
        med_data = self.patient_cursor.fetchone()
        if med_data:
            columns = [desc[0] for desc in self.patient_cursor.description]
            med_dict = dict(zip(columns, med_data))
            self.show_medication_details_popup(med_dict)

    def show_medication_details_popup(self, med_dict):
        popup = tk.Toplevel(self.patient_window)
        popup.title(f"💊 Details: {med_dict['medication_name']}")
        popup.geometry("700x700")
        popup.configure(bg="#f7fafd")
        
        # Hoofdframe
        main_frame = ttk.Frame(popup, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text=f"💊 {med_dict['medication_name']}", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Haal pro/con info op uit medicatie database
        try:
            self.patient_cursor.execute('''
                SELECT pros, cons, warnings, side_effects, interactions, dosage_info 
                FROM medication_info WHERE medication_name = ?
            ''', (med_dict['medication_name'],))
            
            med_info = self.patient_cursor.fetchone()
            if med_info:
                pros, cons, warnings, side_effects, interactions, dosage_info = med_info
            else:
                pros = cons = warnings = side_effects = interactions = dosage_info = "Geen informatie beschikbaar"
        except Exception:
            pros = cons = warnings = side_effects = interactions = dosage_info = "Geen informatie beschikbaar"
        
        # Notebook voor tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Tab 1: Patiënt Medicatie Info
        patient_tab = ttk.Frame(notebook)
        notebook.add(patient_tab, text="Patiënt Medicatie")
        
        patient_info_frame = ttk.LabelFrame(patient_tab, text="📋 Patiënt Specifieke Informatie", padding="15")
        patient_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        patient_fields = [
            ("Dosering", med_dict.get('dosage', '')),
            ("Frequentie", med_dict.get('frequency', '')),
            ("Ochtend", "✅ Ja" if med_dict.get('morning') else "❌ Nee"),
            ("Middag", "✅ Ja" if med_dict.get('afternoon') else "❌ Nee"),
            ("Avond", "✅ Ja" if med_dict.get('evening') else "❌ Nee"),
            ("Nacht", "✅ Ja" if med_dict.get('night') else "❌ Nee"),
            ("Actief", "✅ Ja" if med_dict.get('active') else "❌ Nee"),
            ("Start datum", med_dict.get('start_date', '')),
            ("Eind datum", med_dict.get('end_date', '')),
            ("Opmerkingen", med_dict.get('notes', ''))
        ]
        
        for i, (label, value) in enumerate(patient_fields):
            ttk.Label(patient_info_frame, text=f"{label}:", font=("Arial", 11, "bold")).grid(row=i, column=0, sticky=tk.W, pady=6, padx=(0, 10))
            ttk.Label(patient_info_frame, text=value, font=("Arial", 11)).grid(row=i, column=1, sticky=tk.W, pady=6)
        
        # Tab 2: Medicatie Fiche Info
        fiche_tab = ttk.Frame(notebook)
        notebook.add(fiche_tab, text="Medicatie Fiche")
        
        fiche_info_frame = ttk.LabelFrame(fiche_tab, text="📖 Algemene Medicatie Informatie", padding="15")
        fiche_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable frame voor lange teksten
        canvas = tk.Canvas(fiche_info_frame)
        scrollbar = ttk.Scrollbar(fiche_info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pro/Con sectie
        pros_frame = ttk.LabelFrame(scrollable_frame, text="✅ Voordelen", padding="10")
        pros_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(pros_frame, text=pros, font=("Arial", 11), wraplength=500).pack(anchor=tk.W)
        
        cons_frame = ttk.LabelFrame(scrollable_frame, text="❌ Nadelen", padding="10")
        cons_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(cons_frame, text=cons, font=("Arial", 11), wraplength=500).pack(anchor=tk.W)
        
        warnings_frame = ttk.LabelFrame(scrollable_frame, text="⚠️ Waarschuwingen", padding="10")
        warnings_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(warnings_frame, text=warnings, font=("Arial", 11), wraplength=500).pack(anchor=tk.W)
        
        side_effects_frame = ttk.LabelFrame(scrollable_frame, text="💊 Bijwerkingen", padding="10")
        side_effects_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(side_effects_frame, text=side_effects, font=("Arial", 11), wraplength=500).pack(anchor=tk.W)
        
        interactions_frame = ttk.LabelFrame(scrollable_frame, text="🔗 Interacties", padding="10")
        interactions_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(interactions_frame, text=interactions, font=("Arial", 11), wraplength=500).pack(anchor=tk.W)
        
        dosage_frame = ttk.LabelFrame(scrollable_frame, text="💊 Dosering Info", padding="10")
        dosage_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dosage_frame, text=dosage_info, font=("Arial", 11), wraplength=500).pack(anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="✏️ Bewerken", 
                  command=lambda: [popup.destroy(), self.show_patient_medication_form(med_dict['patient_id'], med_dict)], 
                  style='primary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Sluiten", 
                  command=popup.destroy, 
                  style='secondary.TButton').pack(side=tk.LEFT) 

    def add_patient_medication_modern(self):
        """Voeg medicatie toe aan patiënt"""
        patient_data = self.get_patient_data()
        if not patient_data:
            messagebox.showwarning("Waarschuwing", "Voeg eerst een patiënt toe.")
            return
        
        # Toon medicatie formulier met autocomplete
        self.show_patient_medication_form_with_autocomplete(patient_data['id'])
    
    def show_patient_medication_form_with_autocomplete(self, patient_id, med_data=None):
        """Toon medicatie formulier met autocomplete functionaliteit"""
        form_window = tk.Toplevel(self.patient_window)
        form_window.title("Medicatie Toevoegen" if not med_data else "Medicatie Bewerken")
        form_window.geometry("600x500")
        
        # Haal alle beschikbare medicatie op voor suggesties
        self.patient_cursor.execute('''
            SELECT medication_name FROM medication_info ORDER BY medication_name
        ''')
        available_medications = [row[0] for row in self.patient_cursor.fetchall()]
        
        # Voeg veelvoorkomende medicatie toe als suggesties
        common_medications = [
            "Metformine 500mg", "Insuline (kortwerkend)", "Omeprazol 20mg", "Ibuprofen 400mg",
            "Paracetamol 500mg", "Gliclazide 80mg", "Sitagliptine 100mg", "Bisoprolol 5mg",
            "Metoprolol 50mg", "Enalapril 10mg", "Amlodipine 5mg", "Simvastatine 40mg",
            "Atorvastatine 20mg", "Cetirizine 10mg", "Salbutamol inhalator", "Levothyroxine 50mcg",
            "Prednison 5mg", "Furosemide 40mg", "Acetylsalicylzuur 80mg"
        ]
        
        all_suggestions = list(set(available_medications + common_medications))
        
        # Formulier velden
        ttk.Label(form_window, text="Medicatie Naam:", font=('Arial', 12)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        # Autocomplete combobox voor medicatie naam
        med_name_var = tk.StringVar()
        med_name_combo = ttk.Combobox(form_window, textvariable=med_name_var, 
                                     values=all_suggestions, width=40, font=('Arial', 12))
        med_name_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Autocomplete functionaliteit
        def on_medication_type(event):
            typed = med_name_var.get().lower()
            filtered = [med for med in all_suggestions if typed in med.lower()]
            if filtered:
                med_name_combo['values'] = filtered
            else:
                med_name_combo['values'] = all_suggestions
        
        med_name_combo.bind('<KeyRelease>', on_medication_type)
        
        # Andere velden
        ttk.Label(form_window, text="Dosering:", font=('Arial', 12)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        dosage_entry = ttk.Entry(form_window, width=40, font=('Arial', 12))
        dosage_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(form_window, text="Frequentie:", font=('Arial', 12)).grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        frequency_combo = ttk.Combobox(form_window, values=["1x per dag", "2x per dag", "3x per dag", "4x per dag", "Zo nodig", "Voor maaltijd", "Na maaltijd"], 
                                      width=40, font=('Arial', 12))
        frequency_combo.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Tijdstippen
        ttk.Label(form_window, text="Tijdstippen:", font=('Arial', 12)).grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        time_frame = ttk.Frame(form_window)
        time_frame.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        morning_var = tk.BooleanVar()
        afternoon_var = tk.BooleanVar()
        evening_var = tk.BooleanVar()
        night_var = tk.BooleanVar()
        
        ttk.Checkbutton(time_frame, text="🌅 Ochtend", variable=morning_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(time_frame, text="☀️ Middag", variable=afternoon_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(time_frame, text="🌆 Avond", variable=evening_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(time_frame, text="🌙 Nacht", variable=night_var).pack(side=tk.LEFT)
        
        # Opmerkingen
        ttk.Label(form_window, text="Opmerkingen:", font=('Arial', 12)).grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)
        notes_entry = ttk.Entry(form_window, width=40, font=('Arial', 12))
        notes_entry.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Vul bestaande data in als bewerken
        if med_data:
            med_name_var.set(med_data.get('medication_name', ''))
            dosage_entry.insert(0, med_data.get('dosage', ''))
            frequency_combo.set(med_data.get('frequency', ''))
            morning_var.set(med_data.get('morning', False))
            afternoon_var.set(med_data.get('afternoon', False))
            evening_var.set(med_data.get('evening', False))
            night_var.set(med_data.get('night', False))
            notes_entry.insert(0, med_data.get('notes', ''))
        
        def save_medication():
            try:
                medication_name = med_name_var.get().strip()
                if not medication_name:
                    messagebox.showwarning("Waarschuwing", "Voer een medicatie naam in.")
                    return
                
                # Controleer of medicatie-fiche bestaat, zo niet maak aan
                self.patient_cursor.execute('''
                    SELECT id FROM medication_info WHERE medication_name = ?
                ''', (medication_name,))
                
                if not self.patient_cursor.fetchone():
                    if messagebox.askyesno("Medicatie-fiche", f"Medicatie-fiche voor '{medication_name}' bestaat niet. Wil je deze aanmaken?"):
                        self.create_medication_fiche(medication_name)
                
                if med_data:  # Update
                    self.patient_cursor.execute('''
                        UPDATE medications SET 
                        medication_name=?, dosage=?, frequency=?, morning=?, afternoon=?,
                        evening=?, night=?, notes=?
                        WHERE id=?
                    ''', (medication_name, dosage_entry.get(), frequency_combo.get(),
                          morning_var.get(), afternoon_var.get(), evening_var.get(), night_var.get(),
                          notes_entry.get(), med_data['id']))
                else:  # Insert
                    self.patient_cursor.execute('''
                        INSERT INTO medications (patient_id, medication_name, dosage, frequency,
                        morning, afternoon, evening, night, notes, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        patient_id, medication_name, dosage_entry.get(), frequency_combo.get(),
                        morning_var.get(), afternoon_var.get(), evening_var.get(), night_var.get(),
                        notes_entry.get(), True
                    ))
                
                self.patient_conn.commit()
                self.load_patient_medications_modern()
                form_window.destroy()
                messagebox.showinfo("Succes", "Medicatie succesvol opgeslagen!")
                
            except Exception as e:
                messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
        
        # Knoppen
        button_frame = ttk.Frame(form_window)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💾 Opslaan", command=save_medication, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Annuleren", command=form_window.destroy, 
                  style='secondary.TButton').pack(side=tk.LEFT)
    
    def load_patient_medications_modern(self):
        """Laad patiënt medicatie in moderne interface"""
        patient_data = self.get_patient_data()
        if not patient_data:
            return
        
        for item in self.patient_med_tree.get_children():
            self.patient_med_tree.delete(item)
        
        self.patient_cursor.execute('''
            SELECT id, medication_name, dosage, frequency, morning, afternoon, evening, night, active
            FROM medications WHERE patient_id = ? ORDER BY medication_name
        ''', (patient_data['id'],))
        
        for row in self.patient_cursor.fetchall():
            values = [row[1], row[2], row[3], "Ja" if row[4] else "Nee", "Ja" if row[5] else "Nee", 
                     "Ja" if row[6] else "Nee", "Ja" if row[7] else "Nee", "Ja" if row[8] else "Nee"]
            iid = self.patient_med_tree.insert('', 'end', values=values + ["Details"])
            self.patient_med_tree.set(iid, 'Details', 'Details')
        
        self.patient_med_tree.bind('<Double-1>', self.open_medication_details_popup)
    
    def view_schedule(self):
        """Bekijk medicatie schema"""
        patient_data = self.get_patient_data()
        if not patient_data:
            messagebox.showwarning("Waarschuwing", "Geen patiënt gevonden.")
            return
        
        self.show_medication_schedule(patient_data['id'], f"{patient_data['first_name']} {patient_data['last_name']}")
    
    def show_medication_schedule(self, patient_id, patient_name):
        """Toon medicatie schema"""
        if self.schedule_window:
            self.schedule_window.destroy()
            
        self.schedule_window = tk.Toplevel(self.patient_window)
        self.schedule_window.title(f"Medicatie Schema - {patient_name}")
        self.schedule_window.geometry("1000x700")
        
        # Schema voor vandaag
        today = datetime.now().strftime("%Y-%m-%d")
        
        schedule_frame = ttk.LabelFrame(self.schedule_window, text=f"Schema voor {today}", padding="10")
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Haal medicatie op voor deze patiënt
        self.patient_cursor.execute('''
            SELECT id, medication_name, dosage, morning, afternoon, evening, night
            FROM medications WHERE patient_id = ? AND active = 1
        ''', (patient_id,))
        
        medications = self.patient_cursor.fetchall()
        
        # Maak schema voor vandaag
        times = [
            ("Ochtend (08:00)", "morning", 8),
            ("Middag (12:00)", "afternoon", 12),
            ("Avond (18:00)", "evening", 18),
            ("Nacht (22:00)", "night", 22)
        ]
        
        for i, (time_label, time_field, hour) in enumerate(times):
            time_frame = ttk.LabelFrame(schedule_frame, text=time_label, padding="10")
            time_frame.pack(fill=tk.X, pady=5)
            
            # Zoek medicatie voor deze tijd
            for med in medications:
                if med[3 + i]:  # morning, afternoon, evening, night
                    med_frame = ttk.Frame(time_frame)
                    med_frame.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(med_frame, text=f"{med[1]} - {med[2]}").pack(side=tk.LEFT)
                    
                    taken_var = tk.BooleanVar()
                    missed_var = tk.BooleanVar()
                    
                    ttk.Checkbutton(med_frame, text="Genomen", variable=taken_var).pack(side=tk.LEFT, padx=(20, 5))
                    ttk.Checkbutton(med_frame, text="Vergeten", variable=missed_var).pack(side=tk.LEFT, padx=5)
                    
                    # Opslaan functie
                    def save_status(med_id=med[0], time_field=time_field, hour=hour, taken_var=taken_var, missed_var=missed_var):
                        taken = taken_var.get()
                        missed = missed_var.get()
                        
                        # Verwijder bestaande entry voor vandaag
                        self.patient_cursor.execute('''
                            DELETE FROM medication_schedule 
                            WHERE patient_id = ? AND medication_id = ? AND date = ? AND scheduled_time = ?
                        ''', (patient_id, med_id, today, f"{hour:02d}:00"))
                        
                        # Voeg nieuwe status toe
                        if taken or missed:
                            self.patient_cursor.execute('''
                                INSERT INTO medication_schedule (patient_id, medication_id, scheduled_time, taken, missed, date)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (patient_id, med_id, f"{hour:02d}:00", taken, missed, today))
                            
                            self.patient_conn.commit()
                    
                    ttk.Button(med_frame, text="Opslaan", command=save_status).pack(side=tk.LEFT, padx=(20, 0))
        
        # Toon statistieken
        stats_frame = ttk.LabelFrame(self.schedule_window, text="Statistieken", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Tel medicatie voor vandaag
        total_meds = sum(1 for med in medications for i in range(4) if med[3 + i])
        taken_meds = 0
        missed_meds = 0
        
        self.patient_cursor.execute('''
            SELECT taken, missed FROM medication_schedule 
            WHERE patient_id = ? AND date = ?
        ''', (patient_id, today))
        
        for row in self.patient_cursor.fetchall():
            if row[0]: taken_meds += 1
            if row[1]: missed_meds += 1
        
        compliance_rate = (taken_meds / total_meds * 100) if total_meds > 0 else 0
        
        ttk.Label(stats_frame, text=f"Totaal medicatie vandaag: {total_meds}").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Genomen: {taken_meds}").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Vergeten: {missed_meds}").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Compliance: {compliance_rate:.1f}%").pack(anchor=tk.W)
        
        # Aanbevelingen
        if compliance_rate < 80:
            ttk.Label(stats_frame, text="⚠️ Aanbeveling: Probeer medicatie op tijd in te nemen", 
                     foreground='red').pack(anchor=tk.W, pady=(10, 0))
        elif compliance_rate >= 90:
            ttk.Label(stats_frame, text="✅ Uitstekende compliance!", 
                     foreground='green').pack(anchor=tk.W, pady=(10, 0))
        else:
            ttk.Label(stats_frame, text="👍 Goede compliance, blijf zo doorgaan!", 
                     foreground='blue').pack(anchor=tk.W, pady=(10, 0))
    
    def edit_patient_data(self, patient_data):
        """Bewerk patiënt data"""
        self.show_patient_form(patient_data) 