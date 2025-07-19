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
import threading
import time
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import update systeem
try:
    from update_system import UpdateSystem
    UPDATE_SYSTEM_AVAILABLE = True
    print("✅ Update systeem geladen")
except ImportError as e:
    UPDATE_SYSTEM_AVAILABLE = False
    print(f"❌ Update systeem niet beschikbaar: {e}")

class NotificationManager:
    """Beheer notificaties en herinneringen"""
    
    def __init__(self, root):
        self.root = root
        self.notifications = []
        self.reminders = []
        self.notification_window = None
        
    def add_medication_reminder(self, medication, time_slot):
        """Voeg medicatie herinnering toe"""
        reminder = {
            'type': 'medication',
            'medication': medication,
            'time_slot': time_slot,
            'time': datetime.now(),
            'active': True
        }
        self.reminders.append(reminder)
        self.schedule_reminder(reminder)
    
    def add_blood_test_reminder(self, hours=4):
        """Voeg bloedwaarde meting herinnering toe"""
        reminder = {
            'type': 'blood_test',
            'hours': hours,
            'time': datetime.now() + timedelta(hours=hours),
            'active': True
        }
        self.reminders.append(reminder)
        self.schedule_reminder(reminder)
    
    def schedule_reminder(self, reminder):
        """Plan herinnering"""
        def show_reminder():
            if reminder['active']:
                self.show_notification(reminder)
        threading.Timer(reminder['hours'] * 3600, show_reminder).start()
    
    def show_notification(self, reminder):
        """Toon notificatie"""
        if reminder['type'] == 'medication':
            message = f"💊 Medicatie herinnering!\n\nNeem je {reminder['medication']} in voor {reminder['time_slot']}"
        else:
            message = f"🩸 Bloedwaarde meting!\n\nTijd voor een nieuwe bloedwaarde meting"
        
        self.show_notification_window(message)
    
    def show_notification_window(self, message):
        """Toon notificatie venster"""
        if self.notification_window:
            self.notification_window.destroy()
        
        self.notification_window = tk.Toplevel(self.root)
        self.notification_window.title("Herinnering")
        self.notification_window.geometry("400x200")
        self.notification_window.attributes('-topmost', True)
        
        # Centreren
        self.notification_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Styling
        style = ttk.Style()
        style.configure('Notification.TLabel', font=('Arial', 12))
        
        # Content
        ttk.Label(self.notification_window, text="🔔 Herinnering", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        ttk.Label(self.notification_window, text=message, 
                 style='Notification.TLabel', wraplength=350).pack(pady=10)
        
        # Knoppen
        button_frame = ttk.Frame(self.notification_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="✅ Begrepen", 
                  command=self.notification_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏰ 15 min uitstellen", 
                  command=lambda: self.postpone_notification(15)).pack(side=tk.LEFT, padx=5)
    
    def postpone_notification(self, minutes):
        """Stel notificatie uit"""
        self.notification_window.destroy()
        threading.Timer(minutes * 60, lambda: self.show_notification_window("🩸 Bloedwaarde meting!\n\nTijd voor een nieuwe bloedwaarde meting")).start()

class AIAnalytics:
    """Geavanceerde AI analytics voor diabetes tracking"""
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_data(self, data):
        """Bereid data voor voor AI analyse"""
        if not data:
            return None, None
        
        df = pd.DataFrame(data, columns=[
            'Datum', 'Tijd', 'Bloedwaarde (mg/dL)', 'Medicatie', 
            'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
        ])
        
        # Converteer datum naar numerieke waarden
        df['Datum'] = pd.to_datetime(df['Datum'])
        df['Dag_van_week'] = df['Datum'].dt.dayofweek
        df['Dag_van_maand'] = df['Datum'].dt.day
        df['Maand'] = df['Datum'].dt.month
        
        # Converteer tijd naar numerieke waarden
        df['Tijd'] = pd.to_datetime(df['Tijd'], format='%H:%M')
        df['Uur'] = df['Tijd'].dt.hour
        df['Minuten'] = df['Tijd'].dt.minute
        
        # Converteer bloedwaarden naar float
        df['Bloedwaarde (mg/dL)'] = pd.to_numeric(df['Bloedwaarde (mg/dL)'], errors='coerce')
        
        # Verwijder rijen met ontbrekende bloedwaarden
        df = df.dropna(subset=['Bloedwaarde (mg/dL)'])
        
        if len(df) < 5:
            return None, None
        
        # Features voor voorspelling
        features = ['Dag_van_week', 'Dag_van_maand', 'Maand', 'Uur', 'Minuten']
        X = df[features]
        y = df['Bloedwaarde (mg/dL)']
        
        return X, y
    
    def train_model(self, data):
        """Train AI model op historische data"""
        X, y = self.prepare_data(data)
        
        if X is None or len(X) < 5:
            return False
        
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            return True
        except Exception as e:
            print(f"AI training error: {e}")
            return False
    
    def predict_blood_value(self, date, time):
        """Voorspel bloedwaarde voor gegeven datum/tijd"""
        if not self.is_trained:
            return None
        
        try:
            # Converteer datum en tijd
            dt = pd.to_datetime(f"{date} {time}")
            
            # Maak features
            features = np.array([[
                dt.dayofweek,
                dt.day,
                dt.month,
                dt.hour,
                dt.minute
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Voorspelling
            prediction = self.model.predict(features_scaled)[0]
            
            return max(0, prediction)  # Bloedwaarde kan niet negatief zijn
            
        except Exception as e:
            print(f"AI prediction error: {e}")
            return None
    
    def analyze_trends(self, data):
        """Analyseer trends in bloedwaarden"""
        if not data:
            return {}
        
        df = pd.DataFrame(data, columns=[
            'Datum', 'Tijd', 'Bloedwaarde (mg/dL)', 'Medicatie', 
            'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
        ])
        
        df['Bloedwaarde (mg/dL)'] = pd.to_numeric(df['Bloedwaarde (mg/dL)'], errors='coerce')
        df = df.dropna(subset=['Bloedwaarde (mg/dL)'])
        
        if len(df) < 3:
            return {}
        
        analysis = {}
        
        # Dagelijkse trends
        df['Datum'] = pd.to_datetime(df['Datum'])
        daily_avg = df.groupby(df['Datum'].dt.date)['Bloedwaarde (mg/dL)'].mean()
        if len(daily_avg) > 1:
            analysis['daily_trend'] = 'stijgend' if daily_avg.iloc[-1] > daily_avg.iloc[0] else 'dalend'
            analysis['daily_change'] = daily_avg.iloc[-1] - daily_avg.iloc[0]
        
        # Risico analyse
        high_values = df[df['Bloedwaarde (mg/dL)'] > 180]
        low_values = df[df['Bloedwaarde (mg/dL)'] < 70]
        
        analysis['high_risk_percentage'] = (len(high_values) / len(df)) * 100
        analysis['low_risk_percentage'] = (len(low_values) / len(df)) * 100
        
        # Stabiliteit
        analysis['stability'] = 'stabiel' if df['Bloedwaarde (mg/dL)'].std() < 30 else 'instabiel'
        
        return analysis
    
    def get_ai_recommendations(self, data):
        """Krijg AI-gebaseerde aanbevelingen"""
        analysis = self.analyze_trends(data)
        recommendations = []
        
        if analysis.get('high_risk_percentage', 0) > 20:
            recommendations.append("⚠️ Veel hoge bloedwaarden - overleg met arts over medicatie aanpassing")
        
        if analysis.get('low_risk_percentage', 0) > 10:
            recommendations.append("⚠️ Veel lage bloedwaarden - pas insuline dosering aan")
        
        if analysis.get('stability') == 'instabiel':
            recommendations.append("📊 Bloedwaarden zijn instabiel - probeer consistentere metingstijden")
        
        if analysis.get('daily_trend') == 'stijgend':
            recommendations.append("📈 Bloedwaarden stijgen - controleer voeding en medicatie")
        
        if not recommendations:
            recommendations.append("✅ Bloedwaarden lijken stabiel - blijf zo doorgaan!")
        
        return recommendations

class DiabetesTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Diabetes Bloedwaarden Tracker v1.2.5 - Complete Dashboard")
        self.root.geometry("1800x1200")
        self.root.state('zoomed')  # Start maximized
        
        # Configuratie instellingen
        self.config = {
            'auto_backup': True,
            'backup_interval': 7,  # dagen
            'max_records_display': 100,
            'auto_save': True,
            'notifications_enabled': True,
            'ai_analytics_enabled': True
        }
        
        # Database initialisatie
        self.init_database()
        
        # Patiënten management - initialiseer database direct
        self.patient_profile = PatientProfile(self.root)
        self.patient_profile.init_patient_database()  # Initialiseer database direct
        
        # Nieuwe features initialisatie
        self.notification_manager = NotificationManager(self.root)
        self.ai_analytics = AIAnalytics()
        
        # Update systeem
        if UPDATE_SYSTEM_AVAILABLE:
            self.update_system = UpdateSystem(root)
            # Controleer voor updates bij startup
            self.check_for_updates_on_startup()
        
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
        
        # Insuline advies verwijderd
        
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
        manage_menu.add_command(label="🤖 AI Analytics", command=self.show_ai_analytics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Gebruikershandleiding", command=self.show_help)
        help_menu.add_separator()
        if UPDATE_SYSTEM_AVAILABLE:
            help_menu.add_command(label="🔄 Check voor Updates", command=self.manual_update_check)
        help_menu.add_separator()
        help_menu.add_command(label="Over", command=self.show_about)
        
        # Update menu (alleen als update systeem beschikbaar is)
        if UPDATE_SYSTEM_AVAILABLE:
            update_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="🔄 Updates", menu=update_menu)
            update_menu.add_command(label="Controleer voor Updates", command=self.manual_update_check)
            update_menu.add_command(label="Update Instellingen", command=self.show_update_settings)
            update_menu.add_separator()
            update_menu.add_command(label="Update Geschiedenis", command=self.show_update_history)
    
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
                    'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Medicatie Hoeveelheid', 'Insuline ingenomen', 'Insuline vergeten'
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
        """Toon gedetailleerde statistieken en grafieken"""
        try:
            data = self.load_all_data()
            
            if not data:
                messagebox.showwarning("Waarschuwing", "Geen data beschikbaar voor statistieken.")
                return
            
            df = pd.DataFrame(data, columns=[
                'Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Insuline Advies', 'Insuline ingenomen', 'Insuline vergeten'
            ])
            
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Statistieken & Grafieken")
            stats_window.geometry("800x600")
            
            # Notebook voor tabs
            notebook = ttk.Notebook(stats_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Statistieken tab
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="📊 Statistieken")
            
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
            
            # Scrollable text widget
            text_widget = tk.Text(stats_frame, wrap=tk.WORD, font=('Arial', 11))
            scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
            
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
            # Grafieken tab
            charts_frame = ttk.Frame(notebook)
            notebook.add(charts_frame, text="📈 Grafieken")
            
            # Grafiek knoppen
            chart_buttons = ttk.Frame(charts_frame)
            chart_buttons.pack(fill=tk.X, pady=(20, 10))
            
            ttk.Button(chart_buttons, text="🩸 Bloedwaarden Grafiek", command=self.show_blood_chart, 
                      style='primary.TButton').pack(side=tk.LEFT, padx=(0, 15))
            ttk.Button(chart_buttons, text="⚖️ Gewicht Grafiek", command=self.show_weight_chart, 
                      style='primary.TButton').pack(side=tk.LEFT, padx=(0, 15))
            ttk.Button(chart_buttons, text="🔄 Vernieuw Grafieken", command=self.refresh_charts, 
                      style='secondary.TButton').pack(side=tk.LEFT)
            
            # Grafiek canvas
            self.chart_canvas = None
            
        except Exception as e:
            messagebox.showerror("Fout", f"Kon statistieken niet laden: {str(e)}")
    
    def show_export_dialog(self):
        """Toon export dialog"""
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Data")
        export_window.geometry("800x600")
        export_window.transient(self.root)
        export_window.grab_set()
        
        # Hoofdframe
        main_frame = ttk.Frame(export_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        ttk.Label(main_frame, text="📤 Export Data", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Periode selectie
        period_frame = ttk.LabelFrame(main_frame, text="📅 Periode", padding="15")
        period_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(period_frame, text="Periode:").pack(side=tk.LEFT)
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var, 
                                   values=["vandaag", "gisteren", "deze week", "deze maand", "dit jaar", "aangepast"], 
                                   width=15)
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
        
        # Export opties
        export_frame = ttk.LabelFrame(main_frame, text="📤 Export Opties", padding="15")
        export_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(export_frame, text="📊 Export naar Excel", 
                  command=self.export_excel, style='info.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="📄 Export naar PDF", 
                  command=self.export_pdf, style='info.TButton').pack(side=tk.LEFT)
        
        # Sluiten knop
        ttk.Button(main_frame, text="❌ Sluiten", 
                  command=export_window.destroy, style='secondary.TButton').pack(pady=(20, 0))
    
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
                insuline_ingenomen INTEGER,
                insuline_vergeten INTEGER,
                medicatie_hoeveelheid TEXT
            )
        ''')
        
        # Maak indexes voor snellere queries
        try:
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_datum ON bloedwaarden(datum)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_datum_tijd ON bloedwaarden(datum, tijd)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_bloedwaarde ON bloedwaarden(bloedwaarde)')
        except sqlite3.Error:
            pass  # Indexes bestaan mogelijk al
        
        # Veilige database migratie - voeg kolommen toe zonder data verlies
        self.safe_add_column('insuline_ingenomen', 'INTEGER')
        self.safe_add_column('insuline_vergeten', 'INTEGER')
        self.safe_add_column('medicatie_hoeveelheid', 'TEXT')
        
        # Optimaliseer database
        self.cursor.execute('PRAGMA optimize')
        self.conn.commit()
    
    def safe_add_column(self, column_name, column_type):
        """Veilig een kolom toevoegen aan de database zonder data verlies"""
        try:
            # Controleer eerst of de kolom al bestaat
            self.cursor.execute("PRAGMA table_info(bloedwaarden)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if column_name not in columns:
                # Maak automatische backup voordat migratie
                self.create_migration_backup()
                
                # Maak backup van huidige data
                self.cursor.execute("SELECT * FROM bloedwaarden")
                old_data = self.cursor.fetchall()
                
                # Voeg kolom toe
                self.cursor.execute(f"ALTER TABLE bloedwaarden ADD COLUMN {column_name} {column_type}")
                
                # Herstel data met nieuwe kolom (NULL waarden voor nieuwe kolom)
                if old_data:
                    # Maak nieuwe tabel met gewenste structuur
                    self.cursor.execute("""
                        CREATE TABLE bloedwaarden_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            datum TEXT NOT NULL,
                            tijd TEXT NOT NULL,
                            bloedwaarde REAL NOT NULL,
                            medicatie TEXT,
                            activiteit TEXT,
                            gewicht REAL,
                            opmerkingen TEXT,
                            insuline_ingenomen INTEGER,
                            insuline_vergeten INTEGER,
                            medicatie_hoeveelheid TEXT
                        )
                    """)
                    
                    # Kopieer data naar nieuwe tabel
                    for row in old_data:
                        # Pas de row aan voor nieuwe structuur
                        if len(row) == 9:  # Oude structuur zonder medicatie_hoeveelheid
                            new_row = row + (None,)  # Voeg NULL toe voor medicatie_hoeveelheid
                        elif len(row) == 8:  # Nog oudere structuur
                            new_row = row + (None, None)  # Voeg NULL toe voor beide nieuwe kolommen
                        else:
                            new_row = row
                        
                        self.cursor.execute("""
                            INSERT INTO bloedwaarden_new 
                            (datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, 
                             insuline_ingenomen, insuline_vergeten, medicatie_hoeveelheid)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, new_row)
                    
                    # Vervang oude tabel
                    self.cursor.execute("DROP TABLE bloedwaarden")
                    self.cursor.execute("ALTER TABLE bloedwaarden_new RENAME TO bloedwaarden")
                
                self.conn.commit()
                print(f"✅ Kolom '{column_name}' succesvol toegevoegd")
            else:
                print(f"ℹ️ Kolom '{column_name}' bestaat al")
                
        except Exception as e:
            print(f"⚠️ Fout bij toevoegen kolom '{column_name}': {e}")
            # Probeer gewone ALTER TABLE als fallback
            try:
                self.cursor.execute(f"ALTER TABLE bloedwaarden ADD COLUMN {column_name} {column_type}")
                self.conn.commit()
                print(f"✅ Kolom '{column_name}' toegevoegd via fallback")
            except:
                print(f"❌ Kon kolom '{column_name}' niet toevoegen")
    
    def create_migration_backup(self):
        """Maak automatische backup voordat database migratie"""
        try:
            import shutil
            from datetime import datetime
            
            # Maak backup bestandsnaam met timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"migration_backup_{timestamp}.db"
            
            # Kopieer huidige database
            shutil.copy2('diabetes_data.db', backup_filename)
            
            print(f"🔄 Automatische backup gemaakt: {backup_filename}")
            
        except Exception as e:
            print(f"⚠️ Kon geen automatische backup maken: {e}")
    
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
        
        # Configure rows voor betere spacing - nieuwe layout
        main_frame.rowconfigure(0, weight=0)  # Header
        main_frame.rowconfigure(1, weight=0)  # Quick Actions buttons
        main_frame.rowconfigure(2, weight=0)  # Input card
        main_frame.rowconfigure(3, weight=0)  # Overview card
        main_frame.rowconfigure(4, weight=1)  # History card (expandable)
        main_frame.rowconfigure(5, weight=0)  # Status bar

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
        
        # Quick Actions knoppen bovenaan
        actions_card = ttk.LabelFrame(main_frame, text="🔧 Snelle Acties", padding="20")
        actions_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        actions_card.columnconfigure(0, weight=1)

        # Knoppen frame
        buttons_frame = ttk.Frame(actions_card)
        buttons_frame.pack(fill=tk.X)

        # Medicatie Compliance knop
        compliance_button = ttk.Button(buttons_frame, text="💊 Medicatie Compliance", 
                                     command=self.show_medication_compliance, style='warning.TButton', width=25)
        compliance_button.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(compliance_button, "Beheer medicatie compliance voor vandaag")

        # Statistieken knop
        stats_button = ttk.Button(buttons_frame, text="📊 Statistieken & Grafieken", 
                                 command=self.show_statistics, style='primary.TButton', width=25)
        stats_button.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(stats_button, "Bekijk gedetailleerde statistieken en grafieken")

        # Export knop
        export_button = ttk.Button(buttons_frame, text="📤 Export Data", 
                                  command=self.show_export_dialog, style='info.TButton', width=20)
        export_button.pack(side=tk.LEFT, padx=(0, 15))
        self.create_tooltip(export_button, "Export data naar Excel of PDF")

        # AI Analytics knop
        ai_button = ttk.Button(buttons_frame, text="🤖 AI Analytics", 
                              command=self.show_ai_analytics, style='success.TButton', width=20)
        ai_button.pack(side=tk.LEFT)
        self.create_tooltip(ai_button, "Bekijk AI voorspellingen en aanbevelingen")

        # Nieuwe Meting Card
        input_card = ttk.LabelFrame(main_frame, text="📝 Nieuwe Meting", padding="25")
        input_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        input_card.columnconfigure(0, weight=1)
        
        # Datum en tijd rij
        datetime_frame = ttk.Frame(input_card)
        datetime_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(datetime_frame, text="📅 Datum:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(datetime_frame, width=20, font=('Arial', 12))
        self.date_entry.pack(side=tk.LEFT, padx=(10, 10))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.create_tooltip(self.date_entry, "Voer datum in (YYYY-MM-DD)")
        
        # Date picker knop
        date_picker_button = ttk.Button(datetime_frame, text="📅", width=3, 
                                       command=self.show_date_picker, style='info.TButton')
        date_picker_button.pack(side=tk.LEFT, padx=(0, 20))
        self.create_tooltip(date_picker_button, "Kies datum uit kalender")
        
        ttk.Label(datetime_frame, text="🕐 Tijd:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(datetime_frame, width=15, font=('Arial', 12))
        self.time_entry.pack(side=tk.LEFT, padx=(10, 10))
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.create_tooltip(self.time_entry, "Voer tijd in (HH:MM)")
        
        # Time picker knop
        time_picker_button = ttk.Button(datetime_frame, text="🕐", width=3, 
                                       command=self.show_time_picker, style='info.TButton')
        time_picker_button.pack(side=tk.LEFT)
        self.create_tooltip(time_picker_button, "Kies tijd uit klok")
        
        # Bloedwaarde rij
        blood_frame = ttk.Frame(input_card)
        blood_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(blood_frame, text="🩸 Bloedwaarde (mg/dL):", font=('Arial', 12)).pack(side=tk.LEFT)
        self.blood_entry = ttk.Entry(blood_frame, width=15, font=('Arial', 12))
        self.blood_entry.pack(side=tk.LEFT, padx=(10, 20))
        self.blood_entry.bind('<KeyRelease>', lambda e: self.on_blood_entry_change())
        self.create_tooltip(self.blood_entry, "Voer bloedglucose waarde in (0-1000 mg/dL)")
        
        # Insuline advies label verwijderd
        
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
        self.activity_combo.pack(side=tk.LEFT, padx=(10, 10))
        self.activity_combo.bind('<Button-1>', lambda e: self.activity_combo.event_generate('<<ComboboxOpen>>'))
        self.activity_combo.bind('<<ComboboxSelected>>', self.on_activity_select)
        self.create_tooltip(self.activity_combo, "Selecteer je activiteit")
        
        ttk.Label(activity_weight_frame, text="⚖️ Gewicht (kg):", font=('Arial', 12)).pack(side=tk.LEFT)
        self.weight_entry = ttk.Entry(activity_weight_frame, width=15, font=('Arial', 12))
        self.weight_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.weight_entry, "Voer gewicht in (optioneel)")
        
        # Extra activiteit tekstveld (verborgen standaard) - tussen activiteit en opmerkingen
        self.activity_other_frame = ttk.Frame(input_card)
        self.activity_other_frame.pack(fill=tk.X, pady=(0, 20))
        self.activity_other_frame.pack_forget()  # Verborgen standaard
        
        ttk.Label(self.activity_other_frame, text="📝 Andere activiteit:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.activity_other_entry = ttk.Entry(self.activity_other_frame, width=40, font=('Arial', 12))
        self.activity_other_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.activity_other_entry, "Voer je eigen activiteit in")
        
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
        
        # Geschiedenis Card
        history_card = ttk.LabelFrame(main_frame, text="📋 Geschiedenis", padding="20")
        history_card.grid(row=7, column=0, sticky="nsew", pady=(0, 20))
        history_card.columnconfigure(0, weight=1)
        history_card.rowconfigure(0, weight=1)
        
        # Treeview voor data met grotere font
        columns = ('Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Medicatie Hoeveelheid', 'Insuline ingenomen', 'Insuline vergeten')
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
            
    def on_blood_entry_change(self, *args):
        # Lege functie - insuline advies verwijderd
        pass

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
            
            # Verzamel medicatie hoeveelheden
            medicatie_hoeveelheden = []
            for med in self.selected_medications:
                if med in self.medication_details:
                    amount = self.medication_details[med]['amount'].get().strip()
                    if amount:
                        medicatie_hoeveelheden.append(f"{med}: {amount}")
            
            medicatie_hoeveelheid = "; ".join(medicatie_hoeveelheden) if medicatie_hoeveelheden else ""
            activiteit = self.activity_var.get()
            
            # Als "Andere" is geselecteerd, gebruik de custom activiteit
            if activiteit == "Andere":
                activiteit = self.activity_other_entry.get().strip()
                if not activiteit:
                    messagebox.showerror("Fout", "Voer een activiteit in bij 'Andere'")
                    self.update_status("Fout: Activiteit ontbreekt")
                    return
            
            opmerkingen = self.notes_entry.get()
            
            # Voeg toe aan database
            self.cursor.execute('''
                            INSERT INTO bloedwaarden (datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, medicatie_hoeveelheid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, medicatie_hoeveelheid))
            
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
            self.activity_other_entry.delete(0, tk.END)
            self.activity_other_frame.pack_forget()  # Verberg extra activiteit veld
            self.weight_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
            # Insuline advies verwijderd
            
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
                SELECT datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, medicatie_hoeveelheid, insuline_ingenomen, insuline_vergeten
                FROM bloedwaarden
                ORDER BY datum DESC, tijd DESC
                LIMIT 100
            ''')
            
            # Voeg data toe met betere formatting
            for row in self.cursor.fetchall():
                # Gewicht formatting
                gewicht = f"{row[5]:.1f}" if row[5] else ""
                medicatie_hoeveelheid = row[7] or ""
                ingenomen = "Ja" if row[8] else "Nee"
                vergeten = "Ja" if row[9] else "Nee"
                
                # Voeg rij toe met tags voor styling
                item = self.tree.insert('', 'end', values=(
                    row[0], row[1], f"{row[2]:.1f}", row[3], row[4], gewicht, row[6], medicatie_hoeveelheid, ingenomen, vergeten
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
                SELECT datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, medicatie_hoeveelheid, insuline_ingenomen, insuline_vergeten
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
                SELECT datum, tijd, bloedwaarde, medicatie, activiteit, gewicht, opmerkingen, medicatie_hoeveelheid, insuline_ingenomen, insuline_vergeten
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
                        'Activiteit', 'Gewicht (kg)', 'Opmerkingen', 'Medicatie Hoeveelheid', 'Insuline ingenomen', 'Insuline vergeten'
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
                
                table_data = [['Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Medicatie Hoeveelheid', 'Insuline ingenomen', 'Insuline vergeten']]
                
                for row in data_to_show:
                    gewicht = f"{row[5]:.1f}" if row[5] else ""
                    medicatie_hoeveelheid = row[7] or ""
                    ingenomen = "Ja" if row[8] else "Nee"
                    vergeten = "Ja" if row[9] else "Nee"
                    table_data.append([
                        row[0], row[1], f"{row[2]:.1f}", row[3], row[4], gewicht, row[6] or "", medicatie_hoeveelheid, ingenomen, vergeten
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
                df = pd.DataFrame(data, columns=['Datum', 'Tijd', 'Bloedwaarde', 'Medicatie', 'Activiteit', 'Gewicht', 'Opmerkingen', 'Medicatie Hoeveelheid', 'Insuline ingenomen', 'Insuline vergeten'])
                
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
        if hasattr(self, 'status_var'):
            self.status_var.set(message)
            self.root.after(3000, lambda: self.status_var.set("Klaar"))  # Reset na 3 seconden

    def train_ai_model(self):
        """Train het AI model op historische data"""
        try:
            data = self.load_all_data()
            if data and len(data) >= 5:
                success = self.ai_analytics.train_model(data)
                if success:
                    self.update_status("AI model getraind op historische data")
                else:
                    self.update_status("AI training mislukt - onvoldoende data")
            else:
                self.update_status("AI training uitgesteld - wacht op meer data")
        except Exception as e:
            self.update_status(f"AI training fout: {str(e)}")

    def show_ai_analytics(self):
        """Toon AI analytics venster"""
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("🤖 AI Analytics & Voorspellingen")
        analytics_window.geometry("1200x900")
        analytics_window.attributes('-topmost', True)
        
        # Centreren
        analytics_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Main frame
        main_frame = ttk.Frame(analytics_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        ttk.Label(main_frame, text="🤖 AI Analytics & Voorspellingen", 
                 font=('Arial', 18, 'bold')).pack(pady=(0, 20))
        
        # Data laden
        data = self.load_all_data()
        
        if not data or len(data) < 5:
            ttk.Label(main_frame, text="❌ Onvoldoende data voor AI analyse\n\nVoeg minimaal 5 metingen toe", 
                     font=('Arial', 12)).pack(pady=50)
            return
        
        # Train model
        self.train_ai_model()
        
        # AI Analyse sectie
        analysis_frame = ttk.LabelFrame(main_frame, text="📊 AI Analyse", padding="15")
        analysis_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Trends analyse
        analysis = self.ai_analytics.analyze_trends(data)
        
        if analysis:
            trend_text = f"📈 Dagelijkse trend: {analysis.get('daily_trend', 'onbekend')}"
            if 'daily_change' in analysis:
                trend_text += f" ({analysis['daily_change']:+.1f} mg/dL)"
            
            ttk.Label(analysis_frame, text=trend_text, font=('Arial', 11)).pack(anchor=tk.W)
            
            stability_text = f"📊 Stabiliteit: {analysis.get('stability', 'onbekend')}"
            ttk.Label(analysis_frame, text=stability_text, font=('Arial', 11)).pack(anchor=tk.W)
            
            risk_text = f"⚠️ Hoog risico: {analysis.get('high_risk_percentage', 0):.1f}% | Laag risico: {analysis.get('low_risk_percentage', 0):.1f}%"
            ttk.Label(analysis_frame, text=risk_text, font=('Arial', 11)).pack(anchor=tk.W)
        
        # AI Aanbevelingen sectie
        recommendations_frame = ttk.LabelFrame(main_frame, text="💡 AI Aanbevelingen", padding="15")
        recommendations_frame.pack(fill=tk.X, pady=(0, 20))
        
        recommendations = self.ai_analytics.get_ai_recommendations(data)
        
        for rec in recommendations:
            ttk.Label(recommendations_frame, text=f"• {rec}", 
                     font=('Arial', 11), wraplength=700).pack(anchor=tk.W, pady=2)
        
        # Voorspelling sectie
        prediction_frame = ttk.LabelFrame(main_frame, text="🔮 Bloedwaarde Voorspelling", padding="15")
        prediction_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Voorspelling input
        input_frame = ttk.Frame(prediction_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Datum:").pack(side=tk.LEFT)
        pred_date = ttk.Entry(input_frame, width=15)
        pred_date.pack(side=tk.LEFT, padx=(10, 20))
        pred_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(input_frame, text="Tijd:").pack(side=tk.LEFT)
        pred_time = ttk.Entry(input_frame, width=10)
        pred_time.pack(side=tk.LEFT, padx=(10, 0))
        pred_time.insert(0, datetime.now().strftime("%H:%M"))
        
        # Voorspelling resultaat
        self.prediction_result = tk.StringVar()
        prediction_label = ttk.Label(prediction_frame, textvariable=self.prediction_result, 
                                   font=('Arial', 12, 'bold'), foreground='blue')
        prediction_label.pack(pady=10)
        
        # Voorspelling knop
        def make_prediction():
            try:
                date = pred_date.get()
                time = pred_time.get()
                
                if self.ai_analytics.is_trained:
                    prediction = self.ai_analytics.predict_blood_value(date, time)
                    if prediction:
                        self.prediction_result.set(f"🔮 Voorspelde bloedwaarde: {prediction:.1f} mg/dL")
                    else:
                        self.prediction_result.set("❌ Kon geen voorspelling maken")
                else:
                    self.prediction_result.set("❌ AI model niet getraind")
            except Exception as e:
                self.prediction_result.set(f"❌ Fout: {str(e)}")
        
        ttk.Button(prediction_frame, text="🔮 Maak Voorspelling", 
                  command=make_prediction, style='primary.TButton').pack(pady=10)
        
        # Notificaties sectie
        notifications_frame = ttk.LabelFrame(main_frame, text="🔔 Notificaties & Herinneringen", padding="15")
        notifications_frame.pack(fill=tk.X)
        
        # Medicatie herinnering
        med_frame = ttk.Frame(notifications_frame)
        med_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(med_frame, text="Medicatie:").pack(side=tk.LEFT)
        med_var = tk.StringVar()
        med_combo = ttk.Combobox(med_frame, textvariable=med_var, 
                                values=self.get_patient_medications(), width=20)
        med_combo.pack(side=tk.LEFT, padx=(10, 10))
        
        ttk.Label(med_frame, text="Tijdstip:").pack(side=tk.LEFT)
        time_var = tk.StringVar()
        time_combo = ttk.Combobox(med_frame, textvariable=time_var, 
                                 values=["Ochtend", "Middag", "Avond", "Nacht"], width=10)
        time_combo.pack(side=tk.LEFT, padx=(10, 10))
        
        def add_medication_reminder():
            if med_var.get() and time_var.get():
                self.notification_manager.add_medication_reminder(med_var.get(), time_var.get())
                messagebox.showinfo("Herinnering", f"Medicatie herinnering toegevoegd voor {med_var.get()} - {time_var.get()}")
        
        ttk.Button(med_frame, text="➕ Voeg Herinnering", 
                  command=add_medication_reminder, style='success.TButton').pack(side=tk.LEFT, padx=10)
        
        # Bloedwaarde herinnering
        blood_frame = ttk.Frame(notifications_frame)
        blood_frame.pack(fill=tk.X)
        
        ttk.Label(blood_frame, text="Bloedwaarde herinnering elke:").pack(side=tk.LEFT)
        hours_var = tk.StringVar(value="4")
        hours_combo = ttk.Combobox(blood_frame, textvariable=hours_var, 
                                  values=["2", "4", "6", "8", "12"], width=5)
        hours_combo.pack(side=tk.LEFT, padx=(10, 10))
        ttk.Label(blood_frame, text="uur").pack(side=tk.LEFT)
        
        def add_blood_reminder():
            try:
                hours = int(hours_var.get())
                self.notification_manager.add_blood_test_reminder(hours)
                messagebox.showinfo("Herinnering", f"Bloedwaarde herinnering toegevoegd elke {hours} uur")
            except ValueError:
                messagebox.showerror("Fout", "Voer een geldig aantal uren in")
        
        ttk.Button(blood_frame, text="➕ Voeg Herinnering", 
                  command=add_blood_reminder, style='success.TButton').pack(side=tk.LEFT, padx=10)

    # Update systeem functies
    def check_for_updates_on_startup(self):
        """Controleer voor updates bij startup"""
        if UPDATE_SYSTEM_AVAILABLE:
            # Start update check in aparte thread om UI niet te blokkeren
            def startup_check():
                try:
                    update_info = self.update_system.check_for_updates(show_result=False)
                    if update_info:
                        # Toon update melding in hoofdthread
                        self.root.after(0, lambda: self.update_system.show_update_available(update_info))
                except Exception as e:
                    print(f"Startup update check fout: {e}")
            
            import threading
            update_thread = threading.Thread(target=startup_check)
            update_thread.daemon = True
            update_thread.start()
    
    def manual_update_check(self):
        """Handmatige update check"""
        if UPDATE_SYSTEM_AVAILABLE:
            self.update_system.check_for_updates(show_result=True)
        else:
            messagebox.showinfo("Updates", "Update systeem is momenteel niet beschikbaar.\n\nIn een echte implementatie zou hier een update server gekoppeld zijn.")
            self.update_status("Update systeem uitgeschakeld")
    
    def show_update_settings(self):
        """Toon update instellingen"""
        if not UPDATE_SYSTEM_AVAILABLE:
            messagebox.showwarning("Updates", "Update systeem niet beschikbaar")
            return
        
        self.update_system.show_update_settings()
    

    
    def show_update_history(self):
        """Toon update geschiedenis"""
        if not UPDATE_SYSTEM_AVAILABLE:
            messagebox.showwarning("Updates", "Update systeem niet beschikbaar")
            return
        
        try:
            history_window = tk.Toplevel(self.root)
            history_window.title("Update Geschiedenis")
            history_window.geometry("500x400")
            history_window.transient(self.root)
            history_window.grab_set()
            
            # Content
            ttk.Label(history_window, text="📋 Update Geschiedenis", 
                     font=('Arial', 16, 'bold')).pack(pady=20)
            
            # Lees update geschiedenis
            history_text = tk.Text(history_window, height=15, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=history_text.yview)
            history_text.configure(yscrollcommand=scrollbar.set)
            
            history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            # Voeg geschiedenis toe
            if os.path.exists('version.json'):
                with open('version.json', 'r') as f:
                    version_info = json.load(f)
                
                history_text.insert(tk.END, f"🔄 Laatste Update:\n")
                history_text.insert(tk.END, f"Versie: {version_info.get('version', 'Onbekend')}\n")
                history_text.insert(tk.END, f"Datum: {version_info.get('updated_at', 'Onbekend')}\n")
                history_text.insert(tk.END, f"Update Systeem: {'Ja' if version_info.get('update_system', False) else 'Nee'}\n\n")
            
            # Backup geschiedenis
            if os.path.exists('backups'):
                history_text.insert(tk.END, "📁 Backup Geschiedenis:\n")
                backups = [f for f in os.listdir('backups') if f.startswith('backup_')]
                backups.sort(reverse=True)
                
                for backup in backups[:10]:  # Toon laatste 10 backups
                    history_text.insert(tk.END, f"• {backup}\n")
            
            history_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Geschiedenis Fout", f"Kon update geschiedenis niet laden: {str(e)}")

    def show_medication_compliance(self):
        """Toon medicatie compliance in een popup venster"""
        compliance_window = tk.Toplevel(self.root)
        compliance_window.title("💊 Medicatie Compliance - Vandaag")
        compliance_window.geometry("900x400")
        compliance_window.transient(self.root)
        compliance_window.grab_set()

        # Hoofdframe
        main_frame = ttk.Frame(compliance_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tijdstippen
        times = [
            ("🌅 Ochtend (08:00)", "morning"),
            ("☀️ Middag (12:00)", "afternoon"), 
            ("🌆 Avond (18:00)", "evening"),
            ("🌙 Nacht (22:00)", "night")
        ]

        self.compliance_vars = {}

        for i, (time_label, time_key) in enumerate(times):
            time_frame = ttk.LabelFrame(main_frame, text=time_label, padding="15")
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
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(20, 0))

        self.compliance_stats_label = ttk.Label(stats_frame, text="", font=('Arial', 12, 'bold'))
        self.compliance_stats_label.pack()

        # Update compliance statistieken
        self.update_compliance_stats()

        # Sluiten knop
        ttk.Button(main_frame, text="❌ Sluiten", command=compliance_window.destroy, style='secondary.TButton').pack(pady=(20, 0))

    def show_date_picker(self):
        """Toon date picker popup"""
        date_window = tk.Toplevel(self.root)
        date_window.title("📅 Kies Datum")
        date_window.resizable(False, False)  # Niet resizable
        date_window.transient(self.root)
        date_window.grab_set()
        
        # Bereken optimale grootte en positie
        window_width = 400
        window_height = 300
        
        # Haal scherm grootte op
        screen_width = date_window.winfo_screenwidth()
        screen_height = date_window.winfo_screenheight()
        
        # Bereken positie voor centrering
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        date_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main frame met padding
        main_frame = ttk.Frame(date_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="📅 Kies Datum", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 25))
        
        # Datum input frame
        date_input_frame = ttk.LabelFrame(main_frame, text="Datum Invoer", padding="20")
        date_input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Dag input
        day_frame = ttk.Frame(date_input_frame)
        day_frame.pack(fill=tk.X, pady=5)
        ttk.Label(day_frame, text="Dag:", font=('Arial', 12)).pack(side=tk.LEFT)
        day_var = tk.StringVar(value=str(datetime.now().day))
        day_spinbox = ttk.Spinbox(day_frame, from_=1, to=31, width=12, 
                                 textvariable=day_var, wrap=True, font=('Arial', 12))
        day_spinbox.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Maand input
        month_frame = ttk.Frame(date_input_frame)
        month_frame.pack(fill=tk.X, pady=5)
        ttk.Label(month_frame, text="Maand:", font=('Arial', 12)).pack(side=tk.LEFT)
        month_var = tk.StringVar(value=str(datetime.now().month))
        month_spinbox = ttk.Spinbox(month_frame, from_=1, to=12, width=12, 
                                   textvariable=month_var, wrap=True, font=('Arial', 12))
        month_spinbox.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Jaar input
        year_frame = ttk.Frame(date_input_frame)
        year_frame.pack(fill=tk.X, pady=5)
        ttk.Label(year_frame, text="Jaar:", font=('Arial', 12)).pack(side=tk.LEFT)
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_spinbox = ttk.Spinbox(year_frame, from_=2020, to=2030, width=15, 
                                  textvariable=year_var, wrap=True, font=('Arial', 12))
        year_spinbox.pack(side=tk.RIGHT, padx=(10, 0))
        
        def set_date():
            try:
                day = int(day_var.get())
                month = int(month_var.get())
                year = int(year_var.get())
                
                # Valideer datum
                test_date = datetime(year, month, day)
                date_str = test_date.strftime("%Y-%m-%d")
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, date_str)
                date_window.destroy()
            except ValueError:
                messagebox.showerror("Fout", "Ongeldige datum ingevoerd")
        
        # Knoppen frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Knoppen met gelijke grootte
        confirm_btn = ttk.Button(button_frame, text="✅ Bevestig", command=set_date, 
                                style='success.TButton', width=15)
        confirm_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="❌ Annuleer", command=date_window.destroy, 
                               style='secondary.TButton', width=15)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Focus op eerste spinbox
        day_spinbox.focus_set()
        
        # Enter key binding
        date_window.bind('<Return>', lambda e: set_date())
        date_window.bind('<Escape>', lambda e: date_window.destroy())
    
    def show_time_picker(self):
        """Toon time picker popup"""
        time_window = tk.Toplevel(self.root)
        time_window.title("🕐 Kies Tijd")
        time_window.resizable(False, False)  # Niet resizable
        time_window.transient(self.root)
        time_window.grab_set()
        
        # Bereken optimale grootte en positie
        window_width = 400
        window_height = 300
        
        # Haal scherm grootte op
        screen_width = time_window.winfo_screenwidth()
        screen_height = time_window.winfo_screenheight()
        
        # Bereken positie voor centrering
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        time_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main frame met padding
        main_frame = ttk.Frame(time_window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="🕐 Kies Tijd", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 25))
        
        # Tijd input frame
        time_input_frame = ttk.LabelFrame(main_frame, text="Tijd Invoer", padding="20")
        time_input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Uren input
        hour_frame = ttk.Frame(time_input_frame)
        hour_frame.pack(fill=tk.X, pady=5)
        ttk.Label(hour_frame, text="Uren:", font=('Arial', 12)).pack(side=tk.LEFT)
        hour_var = tk.StringVar(value=str(datetime.now().hour))
        hour_spinbox = ttk.Spinbox(hour_frame, from_=0, to=23, width=12, 
                                  textvariable=hour_var, wrap=True, font=('Arial', 12))
        hour_spinbox.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Minuten input
        minute_frame = ttk.Frame(time_input_frame)
        minute_frame.pack(fill=tk.X, pady=5)
        ttk.Label(minute_frame, text="Minuten:", font=('Arial', 12)).pack(side=tk.LEFT)
        minute_var = tk.StringVar(value=str(datetime.now().minute))
        minute_spinbox = ttk.Spinbox(minute_frame, from_=0, to=59, width=12, 
                                    textvariable=minute_var, wrap=True, font=('Arial', 12))
        minute_spinbox.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Snelle tijd knoppen
        quick_time_frame = ttk.LabelFrame(main_frame, text="Snelle Selectie", padding="15")
        quick_time_frame.pack(fill=tk.X, pady=(0, 20))
        
        quick_times = [
            ("🌅 Ochtend", "08:00"),
            ("☀️ Middag", "12:00"),
            ("🌆 Avond", "18:00"),
            ("🌙 Nacht", "22:00")
        ]
        
        for i, (label, time_str) in enumerate(quick_times):
            btn = ttk.Button(quick_time_frame, text=label, 
                           command=lambda t=time_str: quick_set_time(t),
                           width=12)
            btn.grid(row=i//2, column=i%2, padx=5, pady=2, sticky="ew")
        
        def quick_set_time(time_str):
            hour, minute = map(int, time_str.split(':'))
            hour_var.set(str(hour))
            minute_var.set(str(minute))
        
        def set_time():
            try:
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                
                # Valideer tijd
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Ongeldige tijd")
                
                time_str = f"{hour:02d}:{minute:02d}"
                self.time_entry.delete(0, tk.END)
                self.time_entry.insert(0, time_str)
                time_window.destroy()
            except ValueError:
                messagebox.showerror("Fout", "Ongeldige tijd ingevoerd")
        
        # Knoppen frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Knoppen met gelijke grootte
        confirm_btn = ttk.Button(button_frame, text="✅ Bevestig", command=set_time, 
                                style='success.TButton', width=15)
        confirm_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="❌ Annuleer", command=time_window.destroy, 
                               style='secondary.TButton', width=15)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Focus op eerste spinbox
        hour_spinbox.focus_set()
        
        # Enter key binding
        time_window.bind('<Return>', lambda e: set_time())
        time_window.bind('<Escape>', lambda e: time_window.destroy())
    
    def on_activity_select(self, event=None):
        """Toon/verberg extra activiteit veld bij 'Andere' selectie"""
        selected = self.activity_var.get()
        if selected == "Andere":
            # Plaats het veld tussen activity_weight_frame en notes_frame
            self.activity_other_frame.pack(fill=tk.X, pady=(0, 20), after=self.activity_combo.master)
        else:
            self.activity_other_frame.pack_forget()

def main():
    root = tb.Window(themename="cosmo")
    app = DiabetesTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main() 