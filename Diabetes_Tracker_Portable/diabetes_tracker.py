import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from patient_management import PatientProfile
import ttkbootstrap as tb

class DiabetesTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Diabetes Bloedwaarden Tracker - Complete Dashboard")
        self.root.geometry("1800x1200")
        self.root.state('zoomed')  # Start maximized
        
        # Configuratie instellingen
        self.config = {
            'auto_backup': True,
            'backup_interval': 7,  # dagen
            'max_records_display': 100,
            'auto_save': True
        }
        
        # Database initialisatie
        self.init_database()
        
        # Patiënten management - initialiseer database direct
        self.patient_profile = PatientProfile(self.root)
        self.patient_profile.init_patient_database()  # Initialiseer database direct
        
        # Medicatie lijst
        self.medications = [
            "Metformine", "Insuline", "Gliclazide", "Sitagliptine", 
            "Empagliflozine", "Dapagliflozine", "Canagliflozine",
            "Acarbose", "Repaglinide", "Nateglinide", "Pioglitazone",
            "Geen medicatie", "Andere"
        ]
        
        # Activiteiten lijst
        self.activities = [
            "Rust", "Wandelen", "Fietsen", "Sporten", "Zwemmen",
            "Fitness", "Hardlopen", "Yoga", "Andere"
        ]
        
        self.insulin_advice = tk.StringVar()
        self.insulin_advice.set("")
        
        # Medicatie multiselect variabelen
        self.selected_medications = []
        self.medication_details = {}
        self.period_var = tk.StringVar()
        self.period_var.set("vandaag")

        # Maak menu
        self.create_menu()
        
        # Maak widgets
        self.create_widgets()
        
        # Laad data
        self.load_data()
        
        # Start backup scheduler
        self.schedule_backup()
        
        # Welkom bericht
        self.update_status("Applicatie geladen - Klaar voor gebruik")
    
    def create_menu(self):
        """Maak menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Bestand menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bestand", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Herstel Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Export Alle Data", command=self.export_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Afsluiten", command=self.root.quit)
        
        # Beheer menu
        manage_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Beheer", menu=manage_menu)
        manage_menu.add_command(label="Database Optimaliseren", command=self.optimize_database)
        manage_menu.add_command(label="Configuratie", command=self.show_config)
        manage_menu.add_separator()
        manage_menu.add_command(label="Statistieken", command=self.show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Gebruikershandleiding", command=self.show_help)
        help_menu.add_command(label="Over", command=self.show_about)
    
    def backup_database(self):
        """Maak backup van database"""
        try:
            self.update_status("Backup maken...")
            
            backup_filename = f"diabetes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Kopieer database
            import shutil
            shutil.copy2('diabetes_data.db', backup_filename)
            
            self.update_status("Backup succesvol gemaakt!")
            messagebox.showinfo("Backup", f"Database backup gemaakt: {backup_filename}")
            
        except Exception as e:
            messagebox.showerror("Backup Fout", f"Kon geen backup maken: {str(e)}")
            self.update_status("Backup mislukt")
    
    def restore_database(self):
        """Herstel database van backup"""
        try:
            filename = filedialog.askopenfilename(
                title="Selecteer backup bestand",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if filename:
                self.update_status("Database herstellen...")
                
                # Sluit huidige connectie
                self.conn.close()
                
                # Kopieer backup
                import shutil
                shutil.copy2(filename, 'diabetes_data.db')
                
                # Heropen connectie
                self.conn = sqlite3.connect('diabetes_data.db')
                self.cursor = self.conn.cursor()
                
                # Reload data
                self.load_data()
                self.update_overview_stats()
                
                self.update_status("Database hersteld!")
                messagebox.showinfo("Herstel", "Database succesvol hersteld!")
                
        except Exception as e:
            messagebox.showerror("Herstel Fout", f"Kon database niet herstellen: {str(e)}")
            self.update_status("Herstel mislukt")
    
    def export_all_data(self):
        """Export alle data naar Excel"""
        try:
            self.update_status("Alle data exporteren...")
            
            data = self.load_all_data()
            
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen data gevonden om te exporteren.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Export Alle Data"
            )
            
            if filename:
                df = pd.DataFrame(data, columns=[
                    'Datum', 'Tijd', 'Bloedwaarde (mg/dL)', 'Medicatie', 
                    'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
                ])
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Alle Data', index=False)
                    
                    # Statistieken
                    stats_data = {
                        'Statistiek': ['Totaal metingen', 'Gemiddelde bloedwaarde', 'Hoogste bloedwaarde', 
                                      'Laagste bloedwaarde', 'Gemiddeld gewicht', 'Eerste meting', 'Laatste meting'],
                        'Waarde': [
                            len(data),
                            f"{df['Bloedwaarde (mg/dL)'].mean():.1f}",
                            f"{df['Bloedwaarde (mg/dL)'].max():.1f}",
                            f"{df['Bloedwaarde (mg/dL)'].min():.1f}",
                            f"{df['Gewicht (kg)'].mean():.1f}" if not df['Gewicht (kg)'].isna().all() else "N/A",
                            df['Datum'].min(),
                            df['Datum'].max()
                        ]
                    }
                    
                    stats_df = pd.DataFrame(stats_data)
                    stats_df.to_excel(writer, sheet_name='Statistieken', index=False)
                
                self.update_status("Alle data geëxporteerd!")
                messagebox.showinfo("Export", f"Alle data geëxporteerd naar {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Fout", f"Er is een fout opgetreden: {str(e)}")
            self.update_status("Export mislukt")
    
    def show_config(self):
        """Toon configuratie venster"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuratie")
        config_window.geometry("400x300")
        
        # Configuratie opties
        ttk.Label(config_window, text="Configuratie Instellingen", font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Auto backup
        auto_backup_var = tk.BooleanVar(value=self.config['auto_backup'])
        ttk.Checkbutton(config_window, text="Automatische backup", variable=auto_backup_var).pack(pady=5)
        
        # Backup interval
        ttk.Label(config_window, text="Backup interval (dagen):").pack(pady=5)
        interval_var = tk.StringVar(value=str(self.config['backup_interval']))
        ttk.Entry(config_window, textvariable=interval_var, width=10).pack()
        
        # Max records
        ttk.Label(config_window, text="Max records in tabel:").pack(pady=5)
        max_records_var = tk.StringVar(value=str(self.config['max_records_display']))
        ttk.Entry(config_window, textvariable=max_records_var, width=10).pack()
        
        # Opslaan knop
        def save_config():
            try:
                self.config['auto_backup'] = auto_backup_var.get()
                self.config['backup_interval'] = int(interval_var.get())
                self.config['max_records_display'] = int(max_records_var.get())
                config_window.destroy()
                messagebox.showinfo("Configuratie", "Instellingen opgeslagen!")
            except ValueError:
                messagebox.showerror("Fout", "Voer geldige getallen in")
        
        ttk.Button(config_window, text="Opslaan", command=save_config).pack(pady=20)
    
    def show_statistics(self):
        """Toon gedetailleerde statistieken"""
        try:
            data = self.load_all_data()
            
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen data beschikbaar voor statistieken.")
                return
            
            df = pd.DataFrame(data, columns=[
                'Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
            ])
            
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Gedetailleerde Statistieken")
            stats_window.geometry("600x400")
            
            # Statistieken tekst
            stats_text = f"""
            📊 GEDETAILLEERDE STATISTIEKEN
            
            📈 Algemene Statistieken:
            • Totaal aantal metingen: {len(data)}
            • Periode: {df['Datum'].min()} tot {df['Datum'].max()}
            • Aantal dagen met metingen: {df['Datum'].nunique()}
            
            🩸 Bloedwaarden:
            • Gemiddelde: {df['Bloedwaarde'].mean():.1f} mg/dL
            • Mediaan: {df['Bloedwaarde'].median():.1f} mg/dL
            • Hoogste: {df['Bloedwaarde'].max():.1f} mg/dL
            • Laagste: {df['Bloedwaarde'].min():.1f} mg/dL
            • Standaardafwijking: {df['Bloedwaarde'].std():.1f} mg/dL
            
            ⚖️ Gewicht (indien beschikbaar):
            • Gemiddeld gewicht: {df['Gewicht'].mean():.1f} kg
            • Gewichtsverandering: {df['Gewicht'].max() - df['Gewicht'].min():.1f} kg
            
            💊 Medicatie:
            • Meest gebruikte medicatie: {df['Medicatie'].mode().iloc[0] if not df['Medicatie'].mode().empty else 'Geen'}
            
            🏃 Activiteiten:
            • Meest voorkomende activiteit: {df['Activiteit'].mode().iloc[0] if not df['Activiteit'].mode().empty else 'Geen'}
            """
            
            text_widget = tk.Text(stats_window, wrap=tk.WORD, font=('Arial', 11))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Fout", f"Kon statistieken niet laden: {str(e)}")
    
    def show_help(self):
        """Toon help venster"""
        help_text = """
        DIABETES BLOEDWAARDEN TRACKER - GEBRUIKERSHANDLEIDING
        
        📝 NIEUWE METING TOEVOEGEN:
        1. Vul datum en tijd in (standaard: huidige datum/tijd)
        2. Voer bloedwaarde in (0-1000 mg/dL)
        3. Selecteer medicatie uit dropdown
        4. Kies activiteit
        5. Voer gewicht in (optioneel)
        6. Voeg opmerkingen toe (optioneel)
        7. Klik "Toevoegen" of druk Ctrl+S
        
        💊 MEDICATIE COMPLIANCE:
        • Gebruik de checkboxes om aan te geven of medicatie is genomen
        • Klik "💾" om status op te slaan
        • Statistieken worden automatisch bijgewerkt
        
        📊 OVERZICHT:
        • Bekijk statistieken voor vandaag, deze week en deze maand
        • Hoge en lage bloedwaarden worden gemarkeerd met ⚠️
        
        📤 EXPORT:
        • Kies periode uit dropdown
        • Export naar Excel of PDF
        • Voor aangepaste periode: vul start- en einddatum in
        
        🗑️ VERWIJDEREN:
        • Selecteer rij in geschiedenis
        • Klik "Verwijder Selectie"
        
        ⌨️ KEYBOARD SHORTCUTS:
        • Ctrl+S: Meting toevoegen
        • Ctrl+L: Velden wissen
        
        💾 BACKUP:
        • Menu → Bestand → Backup Database
        • Automatische backup elke 7 dagen
        
        Voor vragen of problemen, raadpleeg de README.md
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Gebruikershandleiding")
        help_window.geometry("700x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, font=('Arial', 11))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """Toon over venster"""
        about_text = """
        Diabetes Bloedwaarden Tracker
        Versie 2.0
        
        Een desktop applicatie voor het bijhouden van bloedwaarden, 
        medicatie en activiteiten voor diabetes patiënten.
        
        Functionaliteiten:
        • Bloedwaarden tracking
        • Medicatie management
        • Compliance monitoring
        • Statistieken en grafieken
        • Export naar Excel/PDF
        • Database backup/restore
        
        Ontwikkeld met Python en tkinter
        Database: SQLite
        
        Voor vragen of support, raadpleeg de documentatie.
        """
        
        messagebox.showinfo("Over", about_text)
    
    def schedule_backup(self):
        """Plan automatische backup"""
        if self.config['auto_backup']:
            # Check of backup nodig is
            try:
                backup_files = [f for f in os.listdir('.') if f.startswith('diabetes_backup_')]
                if not backup_files:
                    self.backup_database()
                else:
                    # Check laatste backup datum
                    latest_backup = max(backup_files)
                    backup_date = datetime.strptime(latest_backup[15:30], '%Y%m%d_%H%M%S')
                    days_since_backup = (datetime.now() - backup_date).days
                    
                    if days_since_backup >= self.config['backup_interval']:
                        self.backup_database()
            except Exception:
                pass  # Backup mislukt, probeer later opnieuw
        
        # Plan volgende check over 24 uur
        self.root.after(24 * 60 * 60 * 1000, self.schedule_backup)

    def init_database(self):
        """Database initialisatie met optimalisaties"""
        self.conn = sqlite3.connect('diabetes_data.db')
        self.cursor = self.conn.cursor()
        
        # Tabel aanmaken als deze nog niet bestaat
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bloedwaarden (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datum TEXT NOT NULL,
                tijd TEXT NOT NULL,
                bloedwaarde REAL NOT NULL,
                medicatie TEXT,
                activiteit TEXT,
                gewicht REAL,
                opmerkingen TEXT,
                insuline_advies TEXT,
                insuline_ingenomen INTEGER,
                insuline_vergeten INTEGER
            )
        ''')
        
        # Maak indexes voor snellere queries
        try:
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_datum ON bloedwaarden(datum)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_datum_tijd ON bloedwaarden(datum, tijd)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_bloedwaarde ON bloedwaarden(bloedwaarde)')
        except sqlite3.Error:
            pass  # Indexes bestaan mogelijk al
        
        # Probeer kolommen toe te voegen indien nodig
        try:
            self.cursor.execute('ALTER TABLE bloedwaarden ADD COLUMN insuline_advies TEXT')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE bloedwaarden ADD COLUMN insuline_ingenomen INTEGER')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE bloedwaarden ADD COLUMN insuline_vergeten INTEGER')
        except:
            pass
        
        # Optimaliseer database
        self.cursor.execute('PRAGMA optimize')
        self.conn.commit()
    
    def optimize_database(self):
        """Database optimaliseren voor betere performance"""
        try:
            # VACUUM om database te comprimeren
            self.cursor.execute('VACUUM')
            
            # ANALYZE voor query optimalisatie
            self.cursor.execute('ANALYZE')
            
            # Update statistieken
            self.cursor.execute('PRAGMA optimize')
            
            self.conn.commit()
            print("Database geoptimaliseerd")
        except sqlite3.Error as e:
            print(f"Database optimalisatie fout: {e}")
    
    def create_widgets(self):
        """GUI widgets aanmaken met Material Design en verbeterde UX"""
        # Canvas met scrollbar voor scrollbare content
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Hoofdframe met veel padding
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        
        # Configure rows voor betere spacing - uitgebreide layout
        main_frame.rowconfigure(0, weight=0)  # Header
        main_frame.rowconfigure(1, weight=0)  # Input card
        main_frame.rowconfigure(2, weight=0)  # Compliance card
        main_frame.rowconfigure(3, weight=0)  # Quick Stats card
        main_frame.rowconfigure(4, weight=0)  # Export card
        main_frame.rowconfigure(5, weight=0)  # Overview card
        main_frame.rowconfigure(6, weight=0)  # Charts card
        main_frame.rowconfigure(7, weight=1)  # History card (expandable)
        main_frame.rowconfigure(8, weight=0)  # Status bar

        # Header met titel en patiënt knop
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)

        title_label = ttk.Label(header_frame, text="Diabetes Bloedwaarden Tracker", font=('Arial', 24, 'bold'))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Patiënten fiche knop met tooltip
        patient_button = ttk.Button(header_frame, text="👤 Patiënten Fiche", 
                                   command=self.patient_profile.create_patient_window, 
                                   style='primary.TButton', width=20)
        patient_button.grid(row=0, column=1, sticky="e", padx=(20, 0))
        self.create_tooltip(patient_button, "Beheer patiëntgegevens en medicatie")

        # Nieuwe Meting Card
        input_card = ttk.LabelFrame(main_frame, text="📝 Nieuwe Meting", padding="25")
        input_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        input_card.columnconfigure(0, weight=1)
        
        # Datum en tijd rij
        datetime_frame = ttk.Frame(input_card)
        datetime_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(datetime_frame, text="📅 Datum:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(datetime_frame, width=15, font=('Arial', 12))
        self.date_entry.pack(side=tk.LEFT, padx=(10, 30))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.create_tooltip(self.date_entry, "Voer datum in (YYYY-MM-DD)")
        
        ttk.Label(datetime_frame, text="🕐 Tijd:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(datetime_frame, width=10, font=('Arial', 12))
        self.time_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.create_tooltip(self.time_entry, "Voer tijd in (HH:MM)")
        
        # Bloedwaarde rij
        blood_frame = ttk.Frame(input_card)
        blood_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(blood_frame, text="🩸 Bloedwaarde (mg/dL):", font=('Arial', 12)).pack(side=tk.LEFT)
        self.blood_entry = ttk.Entry(blood_frame, width=15, font=('Arial', 12))
        self.blood_entry.pack(side=tk.LEFT, padx=(10, 20))
        self.blood_entry.bind('<KeyRelease>', lambda e: self.on_blood_entry_change())
        self.create_tooltip(self.blood_entry, "Voer bloedglucose waarde in (0-1000 mg/dL)")
        
        # Insuline advies label
        self.insulin_advice_label = ttk.Label(blood_frame, textvariable=self.insulin_advice, 
                                             foreground='blue', font=('Arial', 12, 'bold'))
        self.insulin_advice_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Medicatie multiselect sectie
        medication_frame = ttk.Frame(input_card)
        medication_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(medication_frame, text="💊 Medicatie:", font=('Arial', 12)).pack(side=tk.LEFT)
        
        # Medicatie dropdown met pro/con preview
        self.medication_var = tk.StringVar()
        self.medication_combo = ttk.Combobox(medication_frame, textvariable=self.medication_var, 
                                           values=self.get_patient_medications(), width=30, font=('Arial', 12))
        self.medication_combo.pack(side=tk.LEFT, padx=(10, 10))
        self.medication_combo.bind('<<ComboboxSelected>>', self.on_medication_select)
        self.medication_combo.bind('<KeyRelease>', self.on_medication_type)
        self.medication_combo.bind('<Button-1>', self.open_medication_dropdown)
        self.create_tooltip(self.medication_combo, "Selecteer medicatie of begin te typen voor autocomplete")
        
        # Toevoegen knop voor medicatie
        add_med_button = ttk.Button(medication_frame, text="➕ Toevoegen", 
                                   command=self.add_medication_to_list, style='success.TButton')
        add_med_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(add_med_button, "Voeg geselecteerde medicatie toe aan de lijst")
        
        # Geselecteerde medicatie lijst
        self.selected_medications_frame = ttk.Frame(input_card)
        self.selected_medications_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Activiteit en gewicht rij
        activity_weight_frame = ttk.Frame(input_card)
        activity_weight_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(activity_weight_frame, text="🏃 Activiteit:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.activity_var = tk.StringVar()
        self.activity_combo = ttk.Combobox(activity_weight_frame, textvariable=self.activity_var, 
                                         values=self.activities, width=25, font=('Arial', 12))
        self.activity_combo.pack(side=tk.LEFT, padx=(10, 30))
        self.activity_combo.bind('<Button-1>', lambda e: self.activity_combo.event_generate('<<ComboboxOpen>>'))
        self.create_tooltip(self.activity_combo, "Selecteer je activiteit")
        
        ttk.Label(activity_weight_frame, text="⚖️ Gewicht (kg):", font=('Arial', 12)).pack(side=tk.LEFT)
        self.weight_entry = ttk.Entry(activity_weight_frame, width=15, font=('Arial', 12))
        self.weight_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.weight_entry, "Voer gewicht in (optioneel)")
        
        # Opmerkingen
        notes_frame = ttk.Frame(input_card)
        notes_frame.pack(fill=tk.X, pady=(0, 25))
        
        ttk.Label(notes_frame, text="📝 Opmerkingen:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.notes_entry = ttk.Entry(notes_frame, width=60, font=('Arial', 12))
        self.notes_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.notes_entry, "Voeg extra notities toe (optioneel)")
        
        # Knoppen - groot en prominent met keyboard shortcuts
        button_frame = ttk.Frame(input_card)
        button_frame.pack(fill=tk.X)
        
        add_button = ttk.Button(button_frame, text="✅ Toevoegen (Ctrl+S)", command=self.add_entry, 
                               style='success.TButton', width=15)
        add_button.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(add_button, "Voeg meting toe (Ctrl+S)")
        
        clear_button = ttk.Button(button_frame, text="🗑️ Wissen (Ctrl+L)", command=self.clear_entries, 
                                 style='secondary.TButton', width=15)
        clear_button.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(clear_button, "Wis alle velden (Ctrl+L)")
        
        # Keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.add_entry())
        self.root.bind('<Control-l>', lambda e: self.clear_entries())
        
        # Medicatie Compliance Card
        compliance_card = ttk.LabelFrame(main_frame, text="💊 Medicatie Compliance - Vandaag", padding="25")
        compliance_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        compliance_card.columnconfigure(0, weight=1)

        # Maak compliance frame
        compliance_frame = ttk.Frame(compliance_card)
        compliance_frame.pack(fill=tk.BOTH, expand=True)

        # Tijdstippen
        times = [
            ("🌅 Ochtend (08:00)", "morning"),
            ("☀️ Middag (12:00)", "afternoon"), 
            ("🌆 Avond (18:00)", "evening"),
            ("🌙 Nacht (22:00)", "night")
        ]

        self.compliance_vars = {}

        for i, (time_label, time_key) in enumerate(times):
            time_frame = ttk.LabelFrame(compliance_frame, text=time_label, padding="15")
            time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            time_frame.columnconfigure(0, weight=1)

            # Haal medicatie op voor dit tijdstip
            medications_for_time = self.get_medications_for_time(time_key)

            if medications_for_time:
                for med in medications_for_time:
                    med_frame = ttk.Frame(time_frame)
                    med_frame.pack(fill=tk.X, expand=True, pady=2)

                    # Medicatie naam
                    ttk.Label(med_frame, text=f"{med['name']} - {med['dosage']}", 
                             font=('Arial', 10)).pack(side=tk.LEFT)

                    # Checkboxen
                    taken_var = tk.BooleanVar()
                    missed_var = tk.BooleanVar()

                    ttk.Checkbutton(med_frame, text="✅ Genomen", variable=taken_var, 
                                  command=lambda t=taken_var, m=missed_var: self.on_taken_check(t, m)).pack(side=tk.LEFT, padx=(10, 5))
                    ttk.Checkbutton(med_frame, text="❌ Vergeten", variable=missed_var,
                                  command=lambda t=taken_var, m=missed_var: self.on_missed_check(t, m)).pack(side=tk.LEFT, padx=5)

                    # Opslaan knop
                    ttk.Button(med_frame, text="💾", width=3,
                              command=lambda med_id=med['id'], time_key=time_key, taken=taken_var, missed=missed_var: 
                              self.save_medication_compliance(med_id, time_key, taken, missed)).pack(side=tk.LEFT, padx=(10, 0))

                    # Sla variabelen op
                    self.compliance_vars[f"{med['id']}_{time_key}"] = {
                        'taken': taken_var,
                        'missed': missed_var
                    }
            else:
                ttk.Label(time_frame, text="Geen medicatie", 
                         font=('Arial', 10), foreground='gray').pack(pady=10)

        # Compliance statistieken
        stats_frame = ttk.Frame(compliance_card)
        stats_frame.pack(fill=tk.X, pady=(20, 0))

        self.compliance_stats_label = ttk.Label(stats_frame, text="", font=('Arial', 12, 'bold'))
        self.compliance_stats_label.pack()

        # Update compliance statistieken
        self.update_compliance_stats()

        # Quick Stats Card - Nieuwe uitgebreide sectie
        quick_stats_card = ttk.LabelFrame(main_frame, text="⚡ Snelle Statistieken", padding="25")
        quick_stats_card.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        quick_stats_card.columnconfigure(0, weight=1)

        # Quick stats frame met 4 kolommen
        quick_stats_frame = ttk.Frame(quick_stats_card)
        quick_stats_frame.pack(fill=tk.BOTH, expand=True)

        # Bloedwaarden stats
        blood_stats_frame = ttk.LabelFrame(quick_stats_frame, text="🩸 Bloedwaarden", padding="15")
        blood_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.blood_stats_label = ttk.Label(blood_stats_frame, text="Laden...", font=('Arial', 11))
        self.blood_stats_label.pack(anchor=tk.W)

        # Gewicht stats
        weight_stats_frame = ttk.LabelFrame(quick_stats_frame, text="⚖️ Gewicht", padding="15")
        weight_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.weight_stats_label = ttk.Label(weight_stats_frame, text="Laden...", font=('Arial', 11))
        self.weight_stats_label.pack(anchor=tk.W)

        # Medicatie stats
        medication_stats_frame = ttk.LabelFrame(quick_stats_frame, text="💊 Medicatie", padding="15")
        medication_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.medication_stats_label = ttk.Label(medication_stats_frame, text="Laden...", font=('Arial', 11))
        self.medication_stats_label.pack(anchor=tk.W)

        # Activiteit stats
        activity_stats_frame = ttk.LabelFrame(quick_stats_frame, text="🏃 Activiteit", padding="15")
        activity_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.activity_stats_label = ttk.Label(activity_stats_frame, text="Laden...", font=('Arial', 11))
        self.activity_stats_label.pack(anchor=tk.W)

        # Export Card
        export_card = ttk.LabelFrame(main_frame, text="📤 Export", padding="25")
        export_card.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        export_card.columnconfigure(0, weight=1)

        export_frame = ttk.Frame(export_card)
        export_frame.pack(fill=tk.BOTH, expand=True)

        # Export knoppen
        export_btn_frame = ttk.Frame(export_frame)
        export_btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(export_btn_frame, text="Export naar Excel", command=self.export_excel, style='info.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_btn_frame, text="Export naar PDF", command=self.export_pdf, style='info.TButton').pack(side=tk.LEFT)

        # Periode selectie
        period_frame = ttk.Frame(export_frame)
        period_frame.pack(fill=tk.X)
        ttk.Label(period_frame, text="Periode:").pack(side=tk.LEFT)
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var, values=["vandaag", "gisteren", "deze week", "deze maand", "dit jaar", "aangepast"], width=15)
        period_combo.pack(side=tk.LEFT, padx=(10, 0))
        period_combo.set("vandaag")
        # Start- en einddatum voor aangepaste periode
        self.start_date = ttk.Entry(period_frame, width=12)
        self.end_date = ttk.Entry(period_frame, width=12)
        ttk.Label(period_frame, text="Start:").pack(side=tk.LEFT, padx=(10, 0))
        self.start_date.pack(side=tk.LEFT, padx=(2, 0))
        ttk.Label(period_frame, text="Einde:").pack(side=tk.LEFT, padx=(10, 0))
        self.end_date.pack(side=tk.LEFT, padx=(2, 0))
        self.start_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        # Toon alleen bij 'aangepast'
        def on_period_change(event=None):
            if self.period_var.get() == "aangepast":
                self.start_date.pack(side=tk.LEFT, padx=(2, 0))
                self.end_date.pack(side=tk.LEFT, padx=(2, 0))
            else:
                self.start_date.pack_forget()
                self.end_date.pack_forget()
        period_combo.bind('<<ComboboxSelected>>', on_period_change)
        on_period_change()

        # Overzicht Card
        overview_card = ttk.LabelFrame(main_frame, text="📊 Overzicht Ingevoerde Waarden", padding="25")
        overview_card.grid(row=5, column=0, sticky="ew", pady=(0, 20))
        overview_card.columnconfigure(0, weight=1)

        # Overzicht frame
        overview_frame = ttk.Frame(overview_card)
        overview_frame.pack(fill=tk.BOTH, expand=True)

        # Vandaag sectie
        today_frame = ttk.LabelFrame(overview_frame, text="📅 Vandaag", padding="15")
        today_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.today_stats_label = ttk.Label(today_frame, text="Laden...", font=('Arial', 11))
        self.today_stats_label.pack(anchor=tk.W)

        # Deze week sectie
        week_frame = ttk.LabelFrame(overview_frame, text="📅 Deze Week", padding="15")
        week_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.week_stats_label = ttk.Label(week_frame, text="Laden...", font=('Arial', 11))
        self.week_stats_label.pack(anchor=tk.W)

        # Deze maand sectie
        month_frame = ttk.LabelFrame(overview_frame, text="📅 Deze Maand", padding="15")
        month_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.month_stats_label = ttk.Label(month_frame, text="Laden...", font=('Arial', 11))
        self.month_stats_label.pack(anchor=tk.W)

        # Update overzicht
        self.update_overview_stats()
        self.update_quick_stats()
        
        # Geschiedenis Card
        history_card = ttk.LabelFrame(main_frame, text="📋 Geschiedenis", padding="20")
        history_card.grid(row=7, column=0, sticky="nsew", pady=(0, 20))
        history_card.columnconfigure(0, weight=1)
        history_card.rowconfigure(0, weight=1)
        
        # Treeview voor data met grotere font
        columns = ('Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten')
        self.tree = ttk.Treeview(history_card, columns=columns, show='headings', height=12)
        
        # Kolom headers
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Verwijder knop
        ttk.Button(history_card, text="🗑️ Verwijder Selectie", command=self.delete_selected, 
                  style='danger.TButton').grid(row=1, column=0, pady=(15, 0))
        
        # Grafiek Card
        chart_card = ttk.LabelFrame(main_frame, text="📈 Grafieken", padding="20")
        chart_card.grid(row=6, column=0, sticky="ew", pady=(0, 20))
        
        # Grafiek knoppen
        chart_buttons = ttk.Frame(chart_card)
        chart_buttons.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(chart_buttons, text="🩸 Bloedwaarden Grafiek", command=self.show_blood_chart, 
                  style='primary.TButton').pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(chart_buttons, text="⚖️ Gewicht Grafiek", command=self.show_weight_chart, 
                  style='primary.TButton').pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(chart_buttons, text="🔄 Vernieuw Grafieken", command=self.refresh_charts, 
                  style='secondary.TButton').pack(side=tk.LEFT)
        
        # Grafiek canvas
        self.chart_canvas = None

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Klaar")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=8, column=0, sticky="ew", pady=(10, 0))
    
    def get_patient_medications(self):
        """Haal medicatie op van de patiënt uit de patiënten fiche"""
        try:
            # Probeer medicatie op te halen uit patiënten database
            patient_conn = sqlite3.connect('patient_data.db')
            patient_cursor = patient_conn.cursor()
            
            patient_cursor.execute('''
                SELECT DISTINCT medication_name FROM medications WHERE active = 1
            ''')
            
            medications = [row[0] for row in patient_cursor.fetchall()]
            patient_conn.close()
            
            if medications:
                return medications
            else:
                # Fallback naar standaard medicatie als geen patiënt medicatie gevonden
                return self.medications
                
        except Exception:
            # Als patiënten database niet bestaat, gebruik standaard medicatie
            return self.medications
            
    def calculate_insulin_advice(self, value):
        """
        Bepaal insuline advies op basis van bloedwaarde.
        Aangepaste verhoudingen voor verschillende medicatie types.
        """
        try:
            value = float(value)
            
            # Controleer eerst of patiënt insuline gebruikt
            patient_medications = self.get_patient_medications()
            uses_insulin = any('insuline' in med.lower() for med in patient_medications)
            
            if not uses_insulin:
                return "Geen insuline voorgeschreven"
            
            # Verschillende adviezen op basis van bloedwaarde
            if value < 80:
                return "0 eenheden (laag risico)"
            elif 80 <= value <= 120:
                return "2-3 eenheden"
            elif 121 <= value <= 180:
                return "4-6 eenheden"
            elif 181 <= value <= 250:
                return "6-8 eenheden"
            else:
                return "8+ eenheden (overleg arts)"
        except Exception:
            return "-"

    def on_blood_entry_change(self, *args):
        advies = self.calculate_insulin_advice(self.blood_entry.get())
        self.insulin_advice.set(f"Advies: {advies}")

    def on_medication_select(self, event):
        """Toon pro/con info bij medicatie selectie"""
        selected_med = self.medication_var.get()
        if selected_med:
            # Haal medicatie info op uit patiënten database
            try:
                patient_conn = sqlite3.connect('patient_data.db')
                patient_cursor = patient_conn.cursor()
                
                patient_cursor.execute('''
                    SELECT pros, cons FROM medication_info WHERE medication_name = ?
                ''', (selected_med,))
                
                result = patient_cursor.fetchone()
                patient_conn.close()
                
                if result:
                    pros, cons = result
                    # Toon pro/con info in een tooltip-achtige label
                    info_text = f"✅ {pros[:50]}... | ❌ {cons[:50]}..."
                    self.medication_info_label = ttk.Label(self.medication_combo.master, 
                                                         text=info_text, 
                                                         foreground='blue', 
                                                         font=('Arial', 10))
                    self.medication_info_label.pack(side=tk.LEFT, padx=(10, 0))
            except Exception:
                pass
    
    def on_medication_type(self, event):
        """Autocomplete en pro/con preview bij typen"""
        typed = self.medication_var.get().lower()
        patient_meds = self.get_patient_medications()
        
        # Voeg veelvoorkomende medicatie toe als suggesties
        common_medications = [
            "Metformine 500mg", "Insuline (kortwerkend)", "Omeprazol 20mg", "Ibuprofen 400mg",
            "Paracetamol 500mg", "Gliclazide", "Sitagliptine", "Empagliflozine",
            "Dapagliflozine", "Canagliflozine", "Acarbose", "Repaglinide",
            "Nateglinide", "Pioglitazone", "Bisoprolol", "Metoprolol",
            "Atenolol", "Enalapril", "Lisinopril", "Perindopril",
            "Amlodipine", "Simvastatine", "Atorvastatine", "Rosuvastatine"
        ]
        
        all_suggestions = list(set(patient_meds + common_medications))
        
        # Filter medicatie op basis van wat getypt is
        filtered_meds = [med for med in all_suggestions if typed in med.lower()]
        
        if filtered_meds:
            self.medication_combo['values'] = filtered_meds
            # Toon eerste match als preview
            if filtered_meds:
                self.on_medication_select(None)
        else:
            self.medication_combo['values'] = all_suggestions
    
    def open_medication_dropdown(self, event):
        """Open de medicatie dropdown bij klik op het hele invoerveld"""
        self.medication_combo.event_generate('<<ComboboxOpen>>')
    
    def add_medication_to_list(self):
        """Voeg geselecteerde medicatie toe aan de lijst voor deze meting"""
        selected_med = self.medication_var.get()
        if not selected_med:
            messagebox.showwarning("Waarschuwing", "Selecteer eerst een medicatie.")
            return
        
        # Maak een medicatie frame met tijdstippen en hoeveelheid
        med_frame = ttk.Frame(self.selected_medications_frame)
        med_frame.pack(fill=tk.X, pady=2)
        
        # Medicatie naam
        ttk.Label(med_frame, text=f"💊 {selected_med}", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        # Tijdstippen
        time_frame = ttk.Frame(med_frame)
        time_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        morning_var = tk.BooleanVar()
        afternoon_var = tk.BooleanVar()
        evening_var = tk.BooleanVar()
        night_var = tk.BooleanVar()
        
        ttk.Checkbutton(time_frame, text="🌅 Ochtend", variable=morning_var).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(time_frame, text="☀️ Middag", variable=afternoon_var).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(time_frame, text="🌆 Avond", variable=evening_var).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(time_frame, text="🌙 Nacht", variable=night_var).pack(side=tk.LEFT, padx=(0, 10))
        
        # Hoeveelheid (optioneel)
        ttk.Label(time_frame, text="Hoeveelheid:").pack(side=tk.LEFT, padx=(0, 5))
        amount_entry = ttk.Entry(time_frame, width=10, font=('Arial', 10))
        amount_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Verwijder knop
        def remove_medication():
            med_frame.destroy()
            if selected_med in self.selected_medications:
                self.selected_medications.remove(selected_med)
        
        ttk.Button(time_frame, text="❌", command=remove_medication, 
                  style='danger.TButton', width=3).pack(side=tk.LEFT)
        
        # Sla medicatie info op
        self.selected_medications.append(selected_med)
        self.medication_details[selected_med] = {
            'frame': med_frame,
            'morning': morning_var,
            'afternoon': afternoon_var,
            'evening': evening_var,
            'night': night_var,
            'amount': amount_entry
        }
        
        # Reset dropdown
        self.medication_var.set("")
        self.medication_combo['values'] = self.get_patient_medications()
        
        # Verwijder info label als die bestaat
        if hasattr(self, 'medication_info_label'):
            self.medication_info_label.destroy()

    def add_entry(self):
        """Voeg nieuwe meting toe"""
        try:
            self.update_status("Valideren van invoer...")
            
            # Valideer datum
            datum = self.date_entry.get().strip()
            if not datum:
                messagebox.showerror("Fout", "Voer een geldige datum in (YYYY-MM-DD)")
                self.update_status("Fout: Ongeldige datum")
                return
            try:
                datetime.strptime(datum, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Fout", "Datum moet in het formaat YYYY-MM-DD zijn")
                self.update_status("Fout: Ongeldig datumformaat")
                return
            
            # Valideer tijd
            tijd = self.time_entry.get().strip()
            if not tijd:
                messagebox.showerror("Fout", "Voer een geldige tijd in (HH:MM)")
                self.update_status("Fout: Ongeldige tijd")
                return
            try:
                datetime.strptime(tijd, "%H:%M")
            except ValueError:
                messagebox.showerror("Fout", "Tijd moet in het formaat HH:MM zijn")
                self.update_status("Fout: Ongeldig tijdformaat")
                return
            
            # Valideer bloedwaarde
            bloedwaarde_str = self.blood_entry.get().strip()
            if not bloedwaarde_str:
                messagebox.showerror("Fout", "Voer een bloedwaarde in")
                self.update_status("Fout: Bloedwaarde ontbreekt")
                return
            try:
                bloedwaarde = float(bloedwaarde_str)
                if bloedwaarde <= 0 or bloedwaarde > 1000:
                    messagebox.showerror("Fout", "Bloedwaarde moet tussen 0 en 1000 mg/dL zijn")
                    self.update_status("Fout: Ongeldige bloedwaarde")
                    return
            except ValueError:
                messagebox.showerror("Fout", "Bloedwaarde moet een geldig getal zijn")
                self.update_status("Fout: Ongeldige bloedwaarde")
                return
            
            # Valideer gewicht (optioneel)
            gewicht = None
            gewicht_str = self.weight_entry.get().strip()
            if gewicht_str:
                try:
                    gewicht = float(gewicht_str)
                    if gewicht <= 0 or gewicht > 500:
                        messagebox.showerror("Fout", "Gewicht moet tussen 0 en 500 kg zijn")
                        self.update_status("Fout: Ongeldig gewicht")
                        return
                except ValueError:
                    messagebox.showerror("Fout", "Gewicht moet een geldig getal zijn")
                    self.update_status("Fout: Ongeldig gewicht")
                    return
            
            self.update_status("Opslaan van meting...")
            
            # Haal andere waarden op
            medicatie = ", ".join(self.selected_medications) if self.selected_medications else ""
            activiteit = self.activity_var.get()
            opmerkingen = self.notes_entry.get()
            
            # Voeg toe aan database
            self.cursor.execute('''
                INSERT INTO bloedwaarden (datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, insuline_advies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, self.insulin_advice.get()))
            
            self.conn.commit()
            
            # Update overzicht
            self.update_status("Updaten van statistieken...")
            self.update_overview_stats()
            
            # Clear entries
            self.clear_entries()
            
            # Reload data
            self.update_status("Laden van nieuwe data...")
            self.load_data()
            
            self.update_status("Meting succesvol toegevoegd!")
            messagebox.showinfo("Succes", "Meting succesvol toegevoegd!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
            self.update_status("Database fout opgetreden")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een onverwachte fout opgetreden: {str(e)}")
            self.update_status("Onverwachte fout opgetreden")
    
    def clear_entries(self):
        """Wis alle invoervelden"""
        try:
            self.update_status("Wissen van velden...")
            
            # Reset alle velden
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
            self.blood_entry.delete(0, tk.END)
            self.activity_var.set("")
            self.weight_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
            self.insulin_advice.set("")
            
            # Verwijder alle geselecteerde medicatie
            for med in self.selected_medications:
                if med in self.medication_details:
                    self.medication_details[med]['frame'].destroy()
            
            self.selected_medications.clear()
            self.medication_details.clear()
            
            # Reset medicatie dropdown
            self.medication_var.set("")
            self.medication_combo['values'] = self.get_patient_medications()
            
            # Verwijder info label als die bestaat
            if hasattr(self, 'medication_info_label'):
                self.medication_info_label.destroy()
            
            self.update_status("Velden gewist")
            
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
            self.update_status("Fout bij wissen")
    
    def load_data(self):
        """Data laden in tabel met lazy loading voor grote datasets"""
        try:
            # Tabel leegmaken
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Eerst alleen de laatste 100 records laden voor snelle weergave
            self.cursor.execute('''
                SELECT datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, insuline_advies, insuline_ingenomen, insuline_vergeten
                FROM bloedwaarden
                ORDER BY datum DESC, tijd DESC
                LIMIT 100
            ''')
            
            # Voeg data toe met betere formatting
            for row in self.cursor.fetchall():
                # Gewicht formatting
                gewicht = f"{row[5]:.1f}" if row[5] else ""
                ingenomen = "Ja" if row[8] else "Nee"
                vergeten = "Ja" if row[9] else "Nee"
                
                # Voeg rij toe met tags voor styling
                item = self.tree.insert('', 'end', values=(
                    row[0], row[1], f"{row[2]:.1f}", row[3], row[4], gewicht, row[6], row[7], ingenomen, vergeten
                ))
                
                # Kleur rij op basis van bloedwaarde
                if row[2] > 180:
                    self.tree.set(item, 'Bloedwaarde', f"{row[2]:.1f} ⚠️")
                elif row[2] < 80:
                    self.tree.set(item, 'Bloedwaarde', f"{row[2]:.1f} ⚠️")
                    
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een onverwachte fout opgetreden: {str(e)}")
    
    def load_all_data(self):
        """Laad alle data (voor export en statistieken)"""
        try:
            self.cursor.execute('''
                SELECT datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, insuline_advies, insuline_ingenomen, insuline_vergeten
                FROM bloedwaarden
                ORDER BY datum DESC, tijd DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
            return []
    
    def delete_selected(self):
        """Geselecteerde rij verwijderen"""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Waarschuwing", "Selecteer eerst een rij om te verwijderen.")
                self.update_status("Geen rij geselecteerd")
                return
            
            if messagebox.askyesno("Bevestiging", "Weet je zeker dat je deze meting wilt verwijderen?"):
                self.update_status("Verwijderen van meting...")
                
                item = self.tree.item(selected[0])
                datum = item['values'][0]
                tijd = item['values'][1]
                
                self.cursor.execute('''
                    DELETE FROM bloedwaarden WHERE datum = ? AND tijd = ?
                ''', (datum, tijd))
                self.conn.commit()
                
                self.load_data()
                self.update_overview_stats()
                self.update_status("Meting succesvol verwijderd!")
                messagebox.showinfo("Succes", "Meting succesvol verwijderd!")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
            self.update_status("Database fout opgetreden")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een onverwachte fout opgetreden: {str(e)}")
            self.update_status("Onverwachte fout opgetreden")
    
    def get_export_data(self):
        """Data ophalen voor export op basis van geselecteerde periode"""
        try:
            period = self.period_var.get()
            today = datetime.now()
            
            if period == "vandaag":
                start_date = today.strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
            elif period == "gisteren":
                yesterday = today - timedelta(days=1)
                start_date = yesterday.strftime("%Y-%m-%d")
                end_date = yesterday.strftime("%Y-%m-%d")
            elif period == "deze week":
                start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
            elif period == "deze maand":
                start_date = today.replace(day=1).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
            elif period == "dit jaar":
                start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
            elif period == "aangepast":
                start_date = self.start_date.get().strip()
                end_date = self.end_date.get().strip()
                
                # Valideer aangepaste datums
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Fout", "Voer geldige datums in (YYYY-MM-DD)")
                    return None, None, None
            else:
                start_date = today.strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
            
            # Gebruik geoptimaliseerde query met index hints
            self.cursor.execute('''
                SELECT datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, insuline_advies, insuline_ingenomen, insuline_vergeten
                FROM bloedwaarden
                WHERE datum BETWEEN ? AND ?
                ORDER BY datum DESC, tijd DESC
            ''', (start_date, end_date))
            
            return self.cursor.fetchall(), start_date, end_date
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
            return None, None, None
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een onverwachte fout opgetreden: {str(e)}")
            return None, None, None
    
    def export_excel(self):
        """Export naar Excel met geoptimaliseerde performance"""
        try:
            data, start_date, end_date = self.get_export_data()
            
            if data is None:
                return
                
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen data gevonden voor de geselecteerde periode.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Opslaan als Excel bestand"
            )
            
            if filename:
                # Gebruik chunks voor grote datasets
                chunk_size = 1000
                chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Schrijf data in chunks
                    all_data = []
                    for chunk in chunks:
                        all_data.extend(chunk)
                    
                    df = pd.DataFrame(all_data, columns=[
                        'Datum', 'Tijd', 'Bloedwaarde (mg/dL)', 'Medicatie', 
                        'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
                    ])
                    
                    df.to_excel(writer, sheet_name='Bloedwaarden', index=False)
                    
                    # Statistieken toevoegen
                    stats_data = {
                        'Statistiek': ['Aantal metingen', 'Gemiddelde bloedwaarde', 'Hoogste bloedwaarde', 
                                      'Laagste bloedwaarde', 'Gemiddeld gewicht'],
                        'Waarde': [
                            len(data),
                            f"{df['Bloedwaarde (mg/dL)'].mean():.1f}",
                            f"{df['Bloedwaarde (mg/dL)'].max():.1f}",
                            f"{df['Bloedwaarde (mg/dL)'].min():.1f}",
                            f"{df['Gewicht (kg)'].mean():.1f}" if not df['Gewicht (kg)'].isna().all() else "N/A"
                        ]
                    }
                    
                    stats_df = pd.DataFrame(stats_data)
                    stats_df.to_excel(writer, sheet_name='Statistieken', index=False)
                
                messagebox.showinfo("Succes", f"Data succesvol geëxporteerd naar {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Fout", f"Er is een fout opgetreden bij het exporteren: {str(e)}")
    
    def export_pdf(self):
        """Export naar PDF met geoptimaliseerde performance"""
        try:
            data, start_date, end_date = self.get_export_data()
            
            if data is None:
                return
                
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen data gevonden voor de geselecteerde periode.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Opslaan als PDF bestand"
            )
            
            if filename:
                doc = SimpleDocTemplate(filename, pagesize=A4)
                styles = getSampleStyleSheet()
                story = []
                
                # Titel
                title = Paragraph("Diabetes Bloedwaarden Rapport", styles['Title'])
                story.append(title)
                story.append(Spacer(1, 12))
                
                # Periode informatie
                period_text = f"Periode: {start_date} tot {end_date}"
                period_para = Paragraph(period_text, styles['Normal'])
                story.append(period_para)
                story.append(Spacer(1, 12))
                
                # Data tabel - beperk tot eerste 1000 rijen voor performance
                max_rows = 1000
                data_to_show = data[:max_rows]
                
                table_data = [['Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten']]
                
                for row in data_to_show:
                    gewicht = f"{row[5]:.1f}" if row[5] else ""
                    ingenomen = "Ja" if row[8] else "Nee"
                    vergeten = "Ja" if row[9] else "Nee"
                    table_data.append([
                        row[0], row[1], f"{row[2]:.1f}", row[3], row[4], gewicht, row[6] or "", row[7] or "", ingenomen, vergeten
                    ])
                
                if len(data) > max_rows:
                    table_data.append([f"... en {len(data) - max_rows} meer rijen", "", "", "", "", "", "", "", "", ""])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 12))
                
                # Statistieken
                df = pd.DataFrame(data, columns=['Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'])
                
                stats_text = f"""
                Statistieken:
                • Aantal metingen: {len(data)}
                • Gemiddelde bloedwaarde: {df['Bloedwaarde'].mean():.1f} mg/dL
                • Hoogste bloedwaarde: {df['Bloedwaarde'].max():.1f} mg/dL
                • Laagste bloedwaarde: {df['Bloedwaarde'].min():.1f} mg/dL
                """
                
                stats_para = Paragraph(stats_text, styles['Normal'])
                story.append(stats_para)
                
                doc.build(story)
                messagebox.showinfo("Succes", f"PDF succesvol geëxporteerd naar {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Fout", f"Er is een fout opgetreden bij het exporteren: {str(e)}")
    
    def show_blood_chart(self):
        """Bloedwaarden grafiek tonen"""
        try:
            self.cursor.execute('''
                SELECT datum, bloedwaarde FROM bloedwaarden 
                ORDER BY datum ASC, tijd ASC
            ''')
            data = self.cursor.fetchall()
            
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen data beschikbaar voor grafiek.")
                return
            
            # Nieuwe window voor grafiek
            chart_window = tk.Toplevel(self.root)
            chart_window.title("Bloedwaarden Grafiek")
            chart_window.geometry("800x600")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            dates = [row[0] for row in data]
            values = [row[1] for row in data]
            
            ax.plot(dates, values, marker='o', linewidth=2, markersize=6)
            ax.set_title("Bloedwaarden Over Tijd", fontsize=16, fontweight='bold')
            ax.set_xlabel("Datum")
            ax.set_ylabel("Bloedwaarde (mg/dL)")
            ax.grid(True, alpha=0.3)
            
            # X-as labels roteren voor betere leesbaarheid
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
        except Exception as e:
            messagebox.showerror("Grafiek Fout", f"Er is een fout opgetreden bij het maken van de grafiek: {str(e)}")
    
    def show_weight_chart(self):
        """Gewicht grafiek tonen"""
        try:
            self.cursor.execute('''
                SELECT datum, gewicht FROM bloedwaarden 
                WHERE gewicht IS NOT NULL
                ORDER BY datum ASC, tijd ASC
            ''')
            data = self.cursor.fetchall()
            
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen gewicht data beschikbaar voor grafiek.")
                return
            
            # Nieuwe window voor grafiek
            chart_window = tk.Toplevel(self.root)
            chart_window.title("Gewicht Grafiek")
            chart_window.geometry("800x600")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            dates = [row[0] for row in data]
            weights = [row[1] for row in data]
            
            ax.plot(dates, weights, marker='s', linewidth=2, markersize=6, color='green')
            ax.set_title("Gewicht Over Tijd", fontsize=16, fontweight='bold')
            ax.set_xlabel("Datum")
            ax.set_ylabel("Gewicht (kg)")
            ax.grid(True, alpha=0.3)
            
            # X-as labels roteren voor betere leesbaarheid
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
        except Exception as e:
            messagebox.showerror("Grafiek Fout", f"Er is een fout opgetreden bij het maken van de grafiek: {str(e)}")
    
    def refresh_charts(self):
        """Grafieken vernieuwen"""
        try:
            # Dit zou de grafieken kunnen vernieuwen als ze open zijn
            messagebox.showinfo("Info", "Grafieken zijn vernieuwd. Open een nieuwe grafiek om de laatste data te zien.")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een fout opgetreden bij het vernieuwen: {str(e)}")
    
    def __del__(self):
        """Cleanup bij afsluiten"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except:
            pass

    def get_medications_for_time(self, time_key):
        """Haal medicatie op voor een specifiek tijdstip"""
        try:
            # Controleer of patient_cursor bestaat
            if not hasattr(self.patient_profile, 'patient_cursor'):
                print("Patient cursor niet beschikbaar")
                return []
            
            # Haal patiënt ID op
            self.patient_profile.patient_cursor.execute('''
                SELECT id FROM patients ORDER BY id LIMIT 1
            ''')
            patient_result = self.patient_profile.patient_cursor.fetchone()
            
            if not patient_result:
                return []
            
            patient_id = patient_result[0]
            
            # Haal medicatie op voor dit tijdstip
            self.patient_profile.patient_cursor.execute('''
                SELECT id, medication_name, dosage, frequency
                FROM medications 
                WHERE patient_id = ? AND active = 1 AND {} = 1
                ORDER BY medication_name
            '''.format(time_key), (patient_id,))
            
            medications = []
            for row in self.patient_profile.patient_cursor.fetchall():
                medications.append({
                    'id': row[0],
                    'name': row[1],
                    'dosage': row[2],
                    'frequency': row[3]
                })
            
            return medications
        except Exception as e:
            print(f"Fout bij ophalen medicatie: {e}")
            return []
    
    def on_taken_check(self, taken_var, missed_var):
        """Checkbox voor genomen medicatie"""
        if taken_var.get():
            missed_var.set(False)
    
    def on_missed_check(self, taken_var, missed_var):
        """Checkbox voor vergeten medicatie"""
        if missed_var.get():
            taken_var.set(False)
    
    def save_medication_compliance(self, med_id, time_key, taken_var, missed_var):
        """Sla medicatie compliance op"""
        try:
            # Haal patiënt ID op
            self.patient_profile.patient_cursor.execute('''
                SELECT id FROM patients ORDER BY id LIMIT 1
            ''')
            patient_result = self.patient_profile.patient_cursor.fetchone()
            
            if not patient_result:
                messagebox.showwarning("Waarschuwing", "Geen patiënt gevonden.")
                return
            
            patient_id = patient_result[0]
            today = datetime.now().strftime("%Y-%m-%d")
            time_hour = {"morning": "08", "afternoon": "12", "evening": "18", "night": "22"}[time_key]
            
            taken = taken_var.get()
            missed = missed_var.get()
            
            # Verwijder bestaande entry voor vandaag
            self.patient_profile.patient_cursor.execute('''
                DELETE FROM medication_schedule 
                WHERE patient_id = ? AND medication_id = ? AND date = ? AND scheduled_time = ?
            ''', (patient_id, med_id, today, f"{time_hour}:00"))
            
            # Voeg nieuwe status toe
            if taken or missed:
                self.patient_profile.patient_cursor.execute('''
                    INSERT INTO medication_schedule (patient_id, medication_id, scheduled_time, taken, missed, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (patient_id, med_id, f"{time_hour}:00", taken, missed, today))
                
                self.patient_profile.patient_conn.commit()
                messagebox.showinfo("Succes", "Medicatie status succesvol opgeslagen!")
            
            # Update statistieken
            self.update_compliance_stats()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een onverwachte fout opgetreden: {str(e)}")
    
    def update_compliance_stats(self):
        """Update compliance statistieken"""
        try:
            # Haal patiënt ID op
            self.patient_profile.patient_cursor.execute('''
                SELECT id FROM patients ORDER BY id LIMIT 1
            ''')
            patient_result = self.patient_profile.patient_cursor.fetchone()
            
            if not patient_result:
                self.compliance_stats_label.config(text="Geen patiënt gevonden")
                return
            
            patient_id = patient_result[0]
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Tel totale medicatie voor vandaag
            self.patient_profile.patient_cursor.execute('''
                SELECT COUNT(*) FROM medications 
                WHERE patient_id = ? AND active = 1 AND (morning = 1 OR afternoon = 1 OR evening = 1 OR night = 1)
            ''', (patient_id,))
            
            total_meds = self.patient_profile.patient_cursor.fetchone()[0]
            
            # Tel genomen en vergeten medicatie
            self.patient_profile.patient_cursor.execute('''
                SELECT SUM(taken), SUM(missed) FROM medication_schedule 
                WHERE patient_id = ? AND date = ?
            ''', (patient_id, today))
            
            result = self.patient_profile.patient_cursor.fetchone()
            taken_meds = result[0] if result[0] else 0
            missed_meds = result[1] if result[1] else 0
            
            compliance_rate = (taken_meds / total_meds * 100) if total_meds > 0 else 0
            
            stats_text = f"📊 Compliance: {compliance_rate:.1f}% | ✅ Genomen: {taken_meds} | ❌ Vergeten: {missed_meds} | 📋 Totaal: {total_meds}"
            
            if compliance_rate < 80:
                stats_text += " ⚠️ Verbetering nodig"
                self.compliance_stats_label.config(text=stats_text, foreground='red')
            elif compliance_rate >= 90:
                stats_text += " 🎉 Uitstekend!"
                self.compliance_stats_label.config(text=stats_text, foreground='green')
            else:
                stats_text += " 👍 Goed bezig"
                self.compliance_stats_label.config(text=stats_text, foreground='blue')
                
        except Exception as e:
            self.compliance_stats_label.config(text=f"Fout bij laden statistieken: {str(e)}")
    
    def create_overview_section(self):
        """Maak overzicht sectie aan"""
        # Overzicht Card
        overview_card = ttk.LabelFrame(self.root, text="📊 Overzicht Ingevoerde Waarden", padding="25")
        overview_card.grid(row=3, column=0, sticky="ew", pady=(0, 30))
        
        # Overzicht frame
        overview_frame = ttk.Frame(overview_card)
        overview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vandaag sectie
        today_frame = ttk.LabelFrame(overview_frame, text="📅 Vandaag", padding="15")
        today_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.today_stats_label = ttk.Label(today_frame, text="Laden...", font=('Arial', 11))
        self.today_stats_label.pack(anchor=tk.W)
        
        # Deze week sectie
        week_frame = ttk.LabelFrame(overview_frame, text="📅 Deze Week", padding="15")
        week_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.week_stats_label = ttk.Label(week_frame, text="Laden...", font=('Arial', 11))
        self.week_stats_label.pack(anchor=tk.W)
        
        # Deze maand sectie
        month_frame = ttk.LabelFrame(overview_frame, text="📅 Deze Maand", padding="15")
        month_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.month_stats_label = ttk.Label(month_frame, text="Laden...", font=('Arial', 11))
        self.month_stats_label.pack(anchor=tk.W)
        
        # Update overzicht
        self.update_overview_stats()
    
    def update_overview_stats(self):
        """Update overzicht statistieken met geoptimaliseerde queries"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
            month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            
            # Vandaag statistieken - gebruik geoptimaliseerde query
            self.cursor.execute('''
                SELECT COUNT(*), AVG(bloedwaarde), MIN(bloedwaarde), MAX(bloedwaarde), AVG(gewicht)
                FROM bloedwaarden WHERE datum = ?
            ''', (today,))
            
            today_result = self.cursor.fetchone()
            if today_result and today_result[0] > 0:
                count, avg_blood, min_blood, max_blood, avg_weight = today_result
                today_text = f"📊 Metingen: {count}\n"
                today_text += f"🩸 Gemiddelde: {avg_blood:.1f} mg/dL\n" if avg_blood else "🩸 Gemiddelde: Geen data\n"
                today_text += f"📉 Laagste: {min_blood:.1f} mg/dL\n" if min_blood else "📉 Laagste: Geen data\n"
                today_text += f"📈 Hoogste: {max_blood:.1f} mg/dL\n" if max_blood else "📈 Hoogste: Geen data\n"
                today_text += f"⚖️ Gemiddeld gewicht: {avg_weight:.1f} kg" if avg_weight else "⚖️ Gemiddeld gewicht: Geen data"
            else:
                today_text = "📊 Geen metingen vandaag"
            
            self.today_stats_label.config(text=today_text)
            
            # Deze week statistieken
            self.cursor.execute('''
                SELECT COUNT(*), AVG(bloedwaarde), MIN(bloedwaarde), MAX(bloedwaarde), AVG(gewicht)
                FROM bloedwaarden WHERE datum >= ?
            ''', (week_start,))
            
            week_result = self.cursor.fetchone()
            if week_result and week_result[0] > 0:
                count, avg_blood, min_blood, max_blood, avg_weight = week_result
                week_text = f"📊 Metingen: {count}\n"
                week_text += f"🩸 Gemiddelde: {avg_blood:.1f} mg/dL\n" if avg_blood else "🩸 Gemiddelde: Geen data\n"
                week_text += f"📉 Laagste: {min_blood:.1f} mg/dL\n" if min_blood else "📉 Laagste: Geen data\n"
                week_text += f"📈 Hoogste: {max_blood:.1f} mg/dL\n" if max_blood else "📈 Hoogste: Geen data\n"
                week_text += f"⚖️ Gemiddeld gewicht: {avg_weight:.1f} kg" if avg_weight else "⚖️ Gemiddeld gewicht: Geen data"
            else:
                week_text = "📊 Geen metingen deze week"
            
            self.week_stats_label.config(text=week_text)
            
            # Deze maand statistieken
            self.cursor.execute('''
                SELECT COUNT(*), AVG(bloedwaarde), MIN(bloedwaarde), MAX(bloedwaarde), AVG(gewicht)
                FROM bloedwaarden WHERE datum >= ?
            ''', (month_start,))
            
            month_result = self.cursor.fetchone()
            if month_result and month_result[0] > 0:
                count, avg_blood, min_blood, max_blood, avg_weight = month_result
                month_text = f"📊 Metingen: {count}\n"
                month_text += f"🩸 Gemiddelde: {avg_blood:.1f} mg/dL\n" if avg_blood else "🩸 Gemiddelde: Geen data\n"
                month_text += f"📉 Laagste: {min_blood:.1f} mg/dL\n" if min_blood else "📉 Laagste: Geen data\n"
                month_text += f"📈 Hoogste: {max_blood:.1f} mg/dL\n" if max_blood else "📈 Hoogste: Geen data\n"
                month_text += f"⚖️ Gemiddeld gewicht: {avg_weight:.1f} kg" if avg_weight else "⚖️ Gemiddeld gewicht: Geen data"
            else:
                month_text = "📊 Geen metingen deze maand"
            
            self.month_stats_label.config(text=month_text)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Fout", f"Er is een database fout opgetreden: {str(e)}")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een onverwachte fout opgetreden: {str(e)}")

    def update_quick_stats(self):
        """Update de snelle statistieken sectie"""
        try:
            data = self.load_all_data()
            if not data:
                self.blood_stats_label.config(text="Geen data")
                self.weight_stats_label.config(text="Geen data")
                self.medication_stats_label.config(text="Geen data")
                self.activity_stats_label.config(text="Geen data")
                return
            df = pd.DataFrame(data, columns=[
                'Datum', 'Tijd', 'Bloedwaarde (mg/dL)', 'Medicatie', 
                'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
            ])
            # Bloedwaarden
            if not df['Bloedwaarde (mg/dL)'].isna().all():
                bloedwaarden = df['Bloedwaarde (mg/dL)'].dropna().astype(float)
                self.blood_stats_label.config(text=f"Gemiddelde: {bloedwaarden.mean():.1f}\nMin: {bloedwaarden.min():.1f}\nMax: {bloedwaarden.max():.1f}")
            else:
                self.blood_stats_label.config(text="N/A")
            # Gewicht
            if not df['Gewicht (kg)'].isna().all():
                gewichten = df['Gewicht (kg)'].dropna().astype(float)
                self.weight_stats_label.config(text=f"Gemiddelde: {gewichten.mean():.1f}\nMin: {gewichten.min():.1f}\nMax: {gewichten.max():.1f}")
            else:
                self.weight_stats_label.config(text="N/A")
            # Medicatie
            medicatie_tellingen = df['Medicatie'].value_counts().head(3)
            if not medicatie_tellingen.empty:
                self.medication_stats_label.config(text="\n".join([f"{med}: {a}" for med, a in medicatie_tellingen.items()]))
            else:
                self.medication_stats_label.config(text="N/A")
            # Activiteit
            activiteit_tellingen = df['Activiteit'].value_counts().head(3)
            if not activiteit_tellingen.empty:
                self.activity_stats_label.config(text="\n".join([f"{act}: {a}" for act, a in activiteit_tellingen.items()]))
            else:
                self.activity_stats_label.config(text="N/A")
        except Exception as e:
            self.blood_stats_label.config(text="Fout")
            self.weight_stats_label.config(text="Fout")
            self.medication_stats_label.config(text="Fout")
            self.activity_stats_label.config(text="Fout")

    def create_tooltip(self, widget, text):
        """Maak een tooltip voor een widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            widget.bind('<Button-1>', lambda e: hide_tooltip())
            
        widget.bind('<Enter>', show_tooltip)

    def update_status(self, message):
        """Update status bar bericht"""
        self.status_var.set(message)
        self.root.after(3000, lambda: self.status_var.set("Klaar"))  # Reset na 3 seconden

def main():
    root = tb.Window(themename="cosmo")
    app = DiabetesTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main() 