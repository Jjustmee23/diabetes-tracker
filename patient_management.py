import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import json
from tkcalendar import DateEntry
import ttkbootstrap as tb

# EID functionaliteit volledig verwijderd in v1.6.0

class PatientProfile:
    def __init__(self, parent):
        self.parent = parent
        self.patient_window = None
        self.medication_window = None
        self.schedule_window = None
        
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
        """Initialiseer patiënten database"""
        try:
            self.patient_conn = sqlite3.connect('patient_data.db')
            self.patient_cursor = self.patient_conn.cursor()
            
            # Patiënten tabel (vereenvoudigd - zonder EID velden)
            self.patient_cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    rijksnummer TEXT UNIQUE,
                    birth_date TEXT,
                    phone TEXT,
                    email TEXT,
                    emergency_contact TEXT,
                    blood_group TEXT,
                    weight INTEGER,
                    height INTEGER,
                    notes TEXT,
                    created_date TEXT
                )
            ''')
            
            # Medicatie informatie tabel
            self.patient_cursor.execute('''
                CREATE TABLE IF NOT EXISTS medication_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medication_name TEXT UNIQUE NOT NULL,
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
            
            # Patiënt medicatie tabel
            self.patient_cursor.execute('''
                CREATE TABLE IF NOT EXISTS medications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    medication_name TEXT,
                    dosage TEXT,
                    frequency TEXT,
                    morning BOOLEAN DEFAULT 0,
                    afternoon BOOLEAN DEFAULT 0,
                    evening BOOLEAN DEFAULT 0,
                    night BOOLEAN DEFAULT 0,
                    start_date TEXT,
                    end_date TEXT,
                    notes TEXT,
                    active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
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
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (medication_id) REFERENCES medications (id)
                )
            ''')
            
            self.patient_conn.commit()
            
        except Exception as e:
            messagebox.showerror("Database Fout", f"Kon patiënten database niet initialiseren: {str(e)}")

    def add_complete_medications(self):
        """Voeg complete medicatie lijst toe"""
        complete_medications = [
            {
                'name': 'Metformine 500mg',
                'description': 'Antidiabeticum - verlaagt bloedsuikerspiegel bij diabetes type 2',
                'pros': 'Effectief, weinig risico op hypoglykemie, gewichtsneutraal, beschermt hart en nieren',
                'cons': 'Maagklachten, diarree, vitamine B12 tekort bij langdurig gebruik',
                'warnings': 'Niet gebruiken bij nierproblemen, tijdelijk stoppen bij operaties',
                'pregnancy_warning': 'Veilig tijdens zwangerschap onder begeleiding, dosering kan aangepast worden',
                'side_effects': 'Maagklachten, diarree, misselijkheid, vitamine B12 tekort, metaalachtige smaak',
                'interactions': 'Interactie met contrast vloeistoffen, alcohol kan lactaatacidose veroorzaken',
                'dosage_info': '500mg 2-3x per dag bij maaltijd, geleidelijk opbouwen'
            },
            {
                'name': 'Gliclazide 80mg',
                'description': 'Antidiabeticum - stimuleert insulineproductie bij diabetes type 2',
                'pros': 'Effectief, langwerkend, beschermt beta-cellen, vermindert diabetische complicaties',
                'cons': 'Risico op hypoglykemie, gewichtstoename mogelijk, niet effectief zonder eigen insuline',
                'warnings': 'Voorzichtig bij ouderen, regelmatige bloedsuiker controle, niet bij type 1 diabetes',
                'pregnancy_warning': 'Veilig tijdens zwangerschap onder begeleiding, dosering kan aangepast worden',
                'side_effects': 'Hypoglykemie, gewichtstoename, hoofdpijn, duizeligheid, huidreacties',
                'interactions': 'Versterkt effect van alcohol, aspirine en sulfonamiden',
                'dosage_info': '80mg 1-2x per dag voor ontbijt, geleidelijk opbouwen'
            },
            {
                'name': 'Sitagliptine 100mg',
                'description': 'DPP-4 remmer - verbetert insulinewerking en verlaagt glucagon bij diabetes type 2',
                'pros': 'Geen hypoglykemie, gewichtsneutraal, eenmaal daags, goed verdraagbaar',
                'cons': 'Duur, mogelijk verhoogd risico op pancreatitis, niet voor monotherapie',
                'warnings': 'Voorzichtig bij nierproblemen, stop bij pancreatitis symptomen',
                'pregnancy_warning': 'Gebruik tijdens zwangerschap alleen als noodzakelijk',
                'side_effects': 'Hoofdpijn, duizeligheid, misselijkheid, pancreatitis, gewrichtspijn',
                'interactions': 'Weinig interacties, voorzichtig met andere diabetesmedicatie',
                'dosage_info': '100mg 1x per dag, met of zonder voedsel'
            },
            {
                'name': 'Bisoprolol 5mg',
                'description': 'Bètablokker - verlaagt bloeddruk en hartslag, beschermt hart',
                'pros': 'Effectief bij hoge bloeddruk, beschermt na hartinfarct, vermindert hartritme',
                'cons': 'Kan vermoeidheid veroorzaken, niet geschikt bij astma, kan koude handen/voeten',
                'warnings': 'Niet plotseling stoppen, voorzichtig bij diabetes, regelmatige controle',
                'pregnancy_warning': 'Alleen gebruiken als voordelen opwegen tegen risicos',
                'side_effects': 'Vermoeidheid, koude handen/voeten, duizeligheid, slaapproblemen, depressie',
                'interactions': 'Interactie met andere bloeddruk medicatie, voorzichtig met insuline',
                'dosage_info': '5mg 1x per dag, geleidelijk opbouwen indien nodig'
            },
            {
                'name': 'Metoprolol 50mg',
                'description': 'Bètablokker - verlaagt bloeddruk en hartslag, voorkomt hartritmestoornissen',
                'pros': 'Effectief bij hoge bloeddruk, beschermt hart, voorkomt migraine',
                'cons': 'Kan vermoeidheid veroorzaken, niet geschikt bij astma, kan erectieproblemen',
                'warnings': 'Niet plotseling stoppen, voorzichtig bij diabetes en COPD',
                'pregnancy_warning': 'Gebruik tijdens zwangerschap alleen onder strikte begeleiding',
                'side_effects': 'Vermoeidheid, duizeligheid, koude extremiteiten, erectieproblemen, depressie',
                'interactions': 'Interactie met andere cardiovasculaire medicatie',
                'dosage_info': '50mg 1-2x per dag, geleidelijk opbouwen'
            },
            {
                'name': 'Enalapril 10mg',
                'description': 'ACE-remmer - verlaagt bloeddruk en beschermt hart en nieren',
                'pros': 'Effectief, beschermt nieren, goed bij hartfalen, verbetert overleving',
                'cons': 'Kan droge hoest veroorzaken, niet geschikt bij zwangerschap, kan duizeligheid',
                'warnings': 'Regelmatige nierfunctie controle, voorzichtig bij uitdroging',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap - kan foetus schaden',
                'side_effects': 'Droge hoest, duizeligheid, hoofdpijn, smaakverandering, huiduitslag',
                'interactions': 'Interactie met kaliumsparende diuretica en NSAIDs',
                'dosage_info': '10mg 1x per dag, geleidelijk opbouwen indien nodig'
            },
            {
                'name': 'Amlodipine 5mg',
                'description': 'Calciumantagonist - verlaagt bloeddruk door vaatverwijding',
                'pros': 'Effectief, langwerkend, beschermt tegen beroerte, goed verdraagbaar',
                'cons': 'Kan enkelzwelling veroorzaken, hoofdpijn, niet geschikt bij ernstig hartfalen',
                'warnings': 'Voorzichtig bij hartfalen, regelmatig controleren, geleidelijk opbouwen',
                'pregnancy_warning': 'Gebruik tijdens zwangerschap alleen als noodzakelijk',
                'side_effects': 'Enkeloedeem, hoofdpijn, duizeligheid, blozen, misselijkheid',
                'interactions': 'Interactie met grapefruitssap, voorzichtig met andere bloeddruk medicatie',
                'dosage_info': '5mg 1x per dag, geleidelijk opbouwen indien nodig'
            },
            {
                'name': 'Simvastatine 40mg',
                'description': 'Statine - verlaagt cholesterol en beschermt tegen hart- en vaatziekten',
                'pros': 'Effectief cholesterolverlaging, beschermt tegen hartinfarct en beroerte',
                'cons': 'Kan spierpijn veroorzaken, zeldzaam leverprobleme, hoofdpijn',
                'warnings': 'Regelmatige leverfunctie controle, stop bij spierpijn, voorzichtig met grapefruit',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap - stop bij kinderwens',
                'side_effects': 'Spierpijn, hoofdpijn, misselijkheid, leverfunctie afwijkingen, slapeloosheid',
                'interactions': 'Veel interacties met andere medicatie, voorzichtig met grapefruit',
                'dosage_info': '40mg 1x per dag savonds, met of zonder voedsel'
            },
            {
                'name': 'Atorvastatine 20mg',
                'description': 'Statine - krachtige cholesterolverlager voor cardiovasculaire bescherming',
                'pros': 'Zeer effectief, beschermt hart en hersenen, vermindert ontsteking',
                'cons': 'Kan spierpijn veroorzaken, leverprobleme mogelijk, diabetes risico',
                'warnings': 'Regelmatige controles nodig, stop bij spierpijn, voorzichtig bij diabetes',
                'pregnancy_warning': 'Niet gebruiken tijdens zwangerschap of bij kinderwens',
                'side_effects': 'Spierpijn, hoofdpijn, misselijkheid, leverfunctie afwijkingen, slapeloosheid',
                'interactions': 'Veel interacties, vooral met antimycotica en antibiotica',
                'dosage_info': '20mg 1x per dag, tijd van inname niet kritiek'
            },
            {
                'name': 'Ibuprofen 400mg',
                'description': 'NSAID - pijnstiller en ontstekingsremmer voor verschillende aandoeningen',
                'pros': 'Effectief tegen pijn en ontsteking, koorts reducerend, snel werkend',
                'cons': 'Kan maagklachten veroorzaken, niet langdurig gebruiken, nierschade mogelijk',
                'warnings': 'Niet bij maagzweren, voorzichtig bij hartproblemen, kortstondig gebruik',
                'pregnancy_warning': 'Vermijden tijdens zwangerschap, vooral laatste trimester',
                'side_effects': 'Maagklachten, hoofdpijn, duizeligheid, nierproblemen, verhoogde bloeddruk',
                'interactions': 'Interactie met bloedverdunners en bloeddruk medicatie',
                'dosage_info': '400mg 1-3x per dag bij maaltijd, maximaal 1200mg per dag'
            },
            {
                'name': 'Omeprazol 20mg',
                'description': 'Protonpompremmer - vermindert maagzuur productie bij maagklachten',
                'pros': 'Effectief bij maagklachten, goed verdraagbaar, beschermt maag',
                'cons': 'Langdurig gebruik kan botontkalking veroorzaken, vitamine B12 tekort',
                'warnings': 'Niet langer dan 8 weken zonder overleg, voorzichtig bij ouderen',
                'pregnancy_warning': 'Overleg met arts tijdens zwangerschap',
                'side_effects': 'Hoofdpijn, diarree, misselijkheid, botontkalking, vitamine B12 tekort',
                'interactions': 'Kan interactie hebben met andere medicatie, vermindert opname van sommige medicijnen',
                'dosage_info': '20mg 1x per dag voor ontbijt, 30 minuten voor maaltijd'
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
            
        else:
            # Nieuwe patiënt toevoegen
            ttk.Label(info_frame, text="Nog geen patiënt profiel aangemaakt", 
                     font=('Arial', 12, 'bold')).pack(pady=20)
            
            # Knoppen frame
            buttons_frame = ttk.Frame(info_frame)
            buttons_frame.pack(pady=20)
            
            ttk.Button(buttons_frame, text="Patiënt Toevoegen", 
                      command=self.add_patient).pack(side=tk.LEFT, padx=(0, 15))
            
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
                    entry.insert(0, str(patient_data[field] or ''))
        
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
                # Refresh GUI
                if self.patient_window:
                    self.patient_window.destroy()
                    self.create_patient_window()
            except Exception as e:
                messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
        ttk.Button(form_window, text="Opslaan", command=save_patient).grid(row=len(fields), column=0, columnspan=2, pady=20)
        
    def load_patients(self):
        """Laad patiënten in de lijst"""
        # Dit wordt niet meer gebruikt omdat we 1 patiënt per systeem hebben
        pass
            
    def edit_patient_data(self, patient_data):
        """Bewerk patiënt data"""
        self.show_patient_form(patient_data)

    # Medicatie functionaliteit blijft hetzelfde...
    def add_patient_medication_modern(self):
        """Voeg medicatie toe aan patiënt"""
        patient_data = self.get_patient_data()
        if not patient_data:
            messagebox.showwarning("Waarschuwing", "Voeg eerst een patiënt toe.")
            return
        
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
        
        # Formulier velden
        ttk.Label(form_window, text="Medicatie Naam:", font=('Arial', 12)).grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        # Autocomplete combobox voor medicatie naam
        med_name_var = tk.StringVar()
        med_name_combo = ttk.Combobox(form_window, textvariable=med_name_var, 
                                     values=available_medications, width=40, font=('Arial', 12))
        med_name_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Andere velden
        ttk.Label(form_window, text="Dosering:", font=('Arial', 12)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        dosage_entry = ttk.Entry(form_window, width=40, font=('Arial', 12))
        dosage_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(form_window, text="Frequentie:", font=('Arial', 12)).grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        frequency_combo = ttk.Combobox(form_window, values=["1x per dag", "2x per dag", "3x per dag", "4x per dag", "Zo nodig"], 
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
        ttk.Button(button_frame, text="❌ Annuleren", command=form_window.destroy).pack(side=tk.LEFT)
    
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

    def open_medication_details_popup(self, event):
        """Toon medicatie details popup"""
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
        """Toon medicatie details in popup"""
        popup = tk.Toplevel(self.patient_window)
        popup.title(f"💊 Details: {med_dict['medication_name']}")
        popup.geometry("600x400")
        
        # Formulier met medicatie details
        info_frame = ttk.LabelFrame(popup, text="Medicatie Informatie", padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        details = [
            ("Medicatie:", med_dict.get('medication_name', '')),
            ("Dosering:", med_dict.get('dosage', '')),
            ("Frequentie:", med_dict.get('frequency', '')),
            ("Ochtend:", "Ja" if med_dict.get('morning') else "Nee"),
            ("Middag:", "Ja" if med_dict.get('afternoon') else "Nee"),
            ("Avond:", "Ja" if med_dict.get('evening') else "Nee"),
            ("Nacht:", "Ja" if med_dict.get('night') else "Nee"),
            ("Opmerkingen:", med_dict.get('notes', ''))
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(info_frame, text=label, font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=str(value), font=('Arial', 10)).grid(row=i, column=1, sticky=tk.W, padx=(20, 0), pady=5)
        
        # Sluit knop
        ttk.Button(popup, text="Sluiten", command=popup.destroy).pack(pady=10)

    def view_schedule(self):
        """Bekijk medicatie schema"""
        patient_data = self.get_patient_data()
        if not patient_data:
            messagebox.showwarning("Waarschuwing", "Geen patiënt gevonden.")
            return
        
        messagebox.showinfo("Medicatie Schema", "Medicatie schema functionaliteit - in ontwikkeling")