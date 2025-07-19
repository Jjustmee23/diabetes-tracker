import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import json

class AIAnalysis:
    def __init__(self, parent):
        self.parent = parent
        self.analysis_window = None
        
    def analyze_patient_health(self, patient_id):
        """Analyseer patiënt gezondheid en geef aanbevelingen"""
        if self.analysis_window:
            self.analysis_window.destroy()
            
        self.analysis_window = tk.Toplevel(self.parent)
        self.analysis_window.title("AI Gezondheidsanalyse")
        self.analysis_window.geometry("800x600")
        
        # Haal patiënt data op
        conn = sqlite3.connect('patient_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT first_name, last_name, weight, blood_group FROM patients WHERE id = ?
        ''', (patient_id,))
        
        patient_data = cursor.fetchone()
        if not patient_data:
            messagebox.showerror("Fout", "Patiënt niet gevonden")
            return
            
        patient_name = f"{patient_data[0]} {patient_data[1]}"
        
        # Haal bloedwaarden op
        blood_conn = sqlite3.connect('diabetes_data.db')
        blood_cursor = blood_conn.cursor()
        
        # Laatste 30 dagen
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        blood_cursor.execute('''
            SELECT bloedwaarde, datum, insuline_ingenomen, insuline_vergeten
            FROM bloedwaarden 
            WHERE datum >= ? 
            ORDER BY datum DESC
        ''', (thirty_days_ago,))
        
        blood_data = blood_cursor.fetchall()
        
        # Haal medicatie compliance op
        cursor.execute('''
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN taken = 1 THEN 1 ELSE 0 END) as taken,
                   SUM(CASE WHEN missed = 1 THEN 1 ELSE 0 END) as missed
            FROM medication_schedule 
            WHERE patient_id = ? AND date >= ?
        ''', (patient_id, thirty_days_ago))
        
        compliance_data = cursor.fetchone()
        
        # Maak analyse
        self.create_analysis_gui(patient_name, blood_data, compliance_data, patient_data)
        
        conn.close()
        blood_conn.close()
        
    def create_analysis_gui(self, patient_name, blood_data, compliance_data, patient_data):
        """Maak GUI voor analyse resultaten"""
        
        # Hoofdframe
        main_frame = ttk.Frame(self.analysis_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text=f"AI Gezondheidsanalyse - {patient_name}", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook voor verschillende analyses
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Bloedwaarden Analyse
        blood_frame = ttk.Frame(notebook)
        notebook.add(blood_frame, text="Bloedwaarden Analyse")
        
        if blood_data:
            self.analyze_blood_values(blood_frame, blood_data)
        else:
            ttk.Label(blood_frame, text="Geen bloedwaarden data beschikbaar voor analyse").pack(pady=20)
        
        # Tab 2: Medicatie Compliance
        compliance_frame = ttk.Frame(notebook)
        notebook.add(compliance_frame, text="Medicatie Compliance")
        
        if compliance_data and compliance_data[0] > 0:
            self.analyze_compliance(compliance_frame, compliance_data)
        else:
            ttk.Label(compliance_frame, text="Geen medicatie compliance data beschikbaar").pack(pady=20)
        
        # Tab 3: Algemene Aanbevelingen
        recommendations_frame = ttk.Frame(notebook)
        notebook.add(recommendations_frame, text="Algemene Aanbevelingen")
        
        self.generate_general_recommendations(recommendations_frame, blood_data, compliance_data, patient_data)
        
    def analyze_blood_values(self, parent, blood_data):
        """Analyseer bloedwaarden en geef aanbevelingen"""
        
        # Bereken statistieken
        values = [row[0] for row in blood_data]
        avg_value = sum(values) / len(values)
        max_value = max(values)
        min_value = min(values)
        
        # Tel hoge en lage waarden
        high_count = sum(1 for v in values if v > 180)
        low_count = sum(1 for v in values if v < 80)
        normal_count = len(values) - high_count - low_count
        
        # Maak analyse frame
        analysis_frame = ttk.LabelFrame(parent, text="Bloedwaarden Analyse (Laatste 30 dagen)", padding="10")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistieken
        stats_frame = ttk.Frame(analysis_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(stats_frame, text=f"Gemiddelde bloedwaarde: {avg_value:.1f} mg/dL", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Hoogste waarde: {max_value:.1f} mg/dL").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Laagste waarde: {min_value:.1f} mg/dL").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Aantal metingen: {len(values)}").pack(anchor=tk.W)
        
        # Distributie
        ttk.Label(stats_frame, text=f"\nDistributie:").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"• Normale waarden (80-180): {normal_count} ({normal_count/len(values)*100:.1f}%)").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"• Hoge waarden (>180): {high_count} ({high_count/len(values)*100:.1f}%)").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"• Lage waarden (<80): {low_count} ({low_count/len(values)*100:.1f}%)").pack(anchor=tk.W)
        
        # Aanbevelingen
        recommendations_frame = ttk.LabelFrame(analysis_frame, text="Aanbevelingen", padding="10")
        recommendations_frame.pack(fill=tk.X, pady=(10, 0))
        
        if avg_value > 150:
            ttk.Label(recommendations_frame, text="⚠️ Gemiddelde bloedwaarde is te hoog", 
                     foreground='red', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(recommendations_frame, text="• Overleg met arts over medicatie aanpassing").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Let op voeding en koolhydraat inname").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Verhoog fysieke activiteit").pack(anchor=tk.W, padx=(20, 0))
        elif avg_value < 100:
            ttk.Label(recommendations_frame, text="⚠️ Gemiddelde bloedwaarde is te laag", 
                     foreground='orange', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(recommendations_frame, text="• Overleg met arts over medicatie reductie").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Let op hypoglykemie symptomen").pack(anchor=tk.W, padx=(20, 0))
        else:
            ttk.Label(recommendations_frame, text="✅ Bloedwaarden zijn goed gereguleerd", 
                     foreground='green', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(recommendations_frame, text="• Blijf huidige regime volhouden").pack(anchor=tk.W, padx=(20, 0))
        
        if high_count > len(values) * 0.3:
            ttk.Label(recommendations_frame, text="⚠️ Te veel hoge bloedwaarden", 
                     foreground='red').pack(anchor=tk.W, pady=(10, 0))
            ttk.Label(recommendations_frame, text="• Controleer medicatie timing").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Overweeg insuline aanpassing").pack(anchor=tk.W, padx=(20, 0))
        
        if low_count > len(values) * 0.2:
            ttk.Label(recommendations_frame, text="⚠️ Te veel lage bloedwaarden", 
                     foreground='orange').pack(anchor=tk.W, pady=(10, 0))
            ttk.Label(recommendations_frame, text="• Verminder medicatie dosering").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Eet regelmatig").pack(anchor=tk.W, padx=(20, 0))
        
    def analyze_compliance(self, parent, compliance_data):
        """Analyseer medicatie compliance"""
        
        total, taken, missed = compliance_data
        compliance_rate = (taken / total * 100) if total > 0 else 0
        
        # Maak analyse frame
        analysis_frame = ttk.LabelFrame(parent, text="Medicatie Compliance Analyse", padding="10")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistieken
        stats_frame = ttk.Frame(analysis_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(stats_frame, text=f"Totaal voorgeschreven doses: {total}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Genomen doses: {taken}").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Gemiste doses: {missed}").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Compliance percentage: {compliance_rate:.1f}%").pack(anchor=tk.W)
        
        # Aanbevelingen
        recommendations_frame = ttk.LabelFrame(analysis_frame, text="Aanbevelingen", padding="10")
        recommendations_frame.pack(fill=tk.X, pady=(10, 0))
        
        if compliance_rate >= 90:
            ttk.Label(recommendations_frame, text="✅ Uitstekende medicatie compliance!", 
                     foreground='green', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(recommendations_frame, text="• Blijf zo doorgaan").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Overweeg beloningssysteem").pack(anchor=tk.W, padx=(20, 0))
        elif compliance_rate >= 70:
            ttk.Label(recommendations_frame, text="👍 Goede medicatie compliance", 
                     foreground='blue', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(recommendations_frame, text="• Probeer compliance te verbeteren").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Gebruik herinneringen").pack(anchor=tk.W, padx=(20, 0))
        else:
            ttk.Label(recommendations_frame, text="⚠️ Lage medicatie compliance", 
                     foreground='red', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(recommendations_frame, text="• Stel dagelijkse herinneringen in").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Gebruik pillendoosje").pack(anchor=tk.W, padx=(20, 0))
            ttk.Label(recommendations_frame, text="• Overleg met arts over vereenvoudiging").pack(anchor=tk.W, padx=(20, 0))
        
        # Praktische tips
        tips_frame = ttk.LabelFrame(analysis_frame, text="Praktische Tips", padding="10")
        tips_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(tips_frame, text="• Zet medicatie op zichtbare plek").pack(anchor=tk.W)
        ttk.Label(tips_frame, text="• Koppel medicatie aan dagelijkse routine").pack(anchor=tk.W)
        ttk.Label(tips_frame, text="• Gebruik smartphone herinneringen").pack(anchor=tk.W)
        ttk.Label(tips_frame, text="• Houd medicatie logboek bij").pack(anchor=tk.W)
        
    def generate_general_recommendations(self, parent, blood_data, compliance_data, patient_data):
        """Genereer algemene aanbevelingen"""
        
        recommendations_frame = ttk.LabelFrame(parent, text="Algemene Gezondheidsaanbevelingen", padding="10")
        recommendations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basis aanbevelingen
        ttk.Label(recommendations_frame, text="Gezondheidsaanbevelingen:", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Voeding
        nutrition_frame = ttk.LabelFrame(recommendations_frame, text="Voeding", padding="5")
        nutrition_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(nutrition_frame, text="• Eet regelmatig (3 hoofdmaaltijden + 2-3 tussendoortjes)").pack(anchor=tk.W)
        ttk.Label(nutrition_frame, text="• Kies complexe koolhydraten (volkoren, groenten)").pack(anchor=tk.W)
        ttk.Label(nutrition_frame, text="• Beperk suiker en geraffineerde koolhydraten").pack(anchor=tk.W)
        ttk.Label(nutrition_frame, text="• Eet voldoende eiwitten en gezonde vetten").pack(anchor=tk.W)
        
        # Beweging
        exercise_frame = ttk.LabelFrame(recommendations_frame, text="Beweging", padding="5")
        exercise_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exercise_frame, text="• Beweeg minimaal 30 minuten per dag").pack(anchor=tk.W)
        ttk.Label(exercise_frame, text="• Combineer cardio en krachttraining").pack(anchor=tk.W)
        ttk.Label(exercise_frame, text="• Controleer bloedsuiker voor en na beweging").pack(anchor=tk.W)
        ttk.Label(exercise_frame, text="• Pas medicatie aan bij intensieve beweging").pack(anchor=tk.W)
        
        # Monitoring
        monitoring_frame = ttk.LabelFrame(recommendations_frame, text="Monitoring", padding="5")
        monitoring_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(monitoring_frame, text="• Meet bloedsuiker regelmatig").pack(anchor=tk.W)
        ttk.Label(monitoring_frame, text="• Houd symptomen bij").pack(anchor=tk.W)
        ttk.Label(monitoring_frame, text="• Controleer voeten dagelijks").pack(anchor=tk.W)
        ttk.Label(monitoring_frame, text="• Ga regelmatig naar controles").pack(anchor=tk.W)
        
        # Specifieke aanbevelingen op basis van data
        if blood_data:
            values = [row[0] for row in blood_data]
            avg_value = sum(values) / len(values)
            
            if avg_value > 150:
                specific_frame = ttk.LabelFrame(recommendations_frame, text="Specifieke Aanbevelingen", padding="5")
                specific_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(specific_frame, text="⚠️ Bloedsuiker is te hoog:", 
                         foreground='red', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                ttk.Label(specific_frame, text="• Overleg met arts over medicatie").pack(anchor=tk.W, padx=(20, 0))
                ttk.Label(specific_frame, text="• Verhoog fysieke activiteit").pack(anchor=tk.W, padx=(20, 0))
                ttk.Label(specific_frame, text="• Let op portiegroottes").pack(anchor=tk.W, padx=(20, 0))
        
        if compliance_data and compliance_data[0] > 0:
            total, taken, missed = compliance_data
            compliance_rate = (taken / total * 100) if total > 0 else 0
            
            if compliance_rate < 70:
                compliance_frame = ttk.LabelFrame(recommendations_frame, text="Medicatie Aanbevelingen", padding="5")
                compliance_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(compliance_frame, text="⚠️ Medicatie compliance kan beter:", 
                         foreground='orange', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                ttk.Label(compliance_frame, text="• Stel dagelijkse herinneringen in").pack(anchor=tk.W, padx=(20, 0))
                ttk.Label(compliance_frame, text="• Gebruik pillendoosje").pack(anchor=tk.W, padx=(20, 0))
                ttk.Label(compliance_frame, text="• Overleg met arts over vereenvoudiging").pack(anchor=tk.W, padx=(20, 0))
        
        # Gewicht aanbevelingen
        if patient_data[2]:  # weight
            weight = patient_data[2]
            bmi = weight / ((1.70) ** 2)  # Geschatte lengte van 1.70m
            
            if bmi > 25:
                weight_frame = ttk.LabelFrame(recommendations_frame, text="Gewicht Aanbevelingen", padding="5")
                weight_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(weight_frame, text="⚠️ BMI is verhoogd:", 
                         foreground='orange', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                ttk.Label(weight_frame, text="• Streef naar 5-10% gewichtsverlies").pack(anchor=tk.W, padx=(20, 0))
                ttk.Label(weight_frame, text="• Combineer voeding en beweging").pack(anchor=tk.W, padx=(20, 0))
                ttk.Label(weight_frame, text="• Overleg met diëtist").pack(anchor=tk.W, padx=(20, 0))
        
        # Actieplan
        action_frame = ttk.LabelFrame(recommendations_frame, text="Actieplan", padding="5")
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(action_frame, text="Korte termijn (1-2 weken):").pack(anchor=tk.W, font=('Arial', 10, 'bold'))
        ttk.Label(action_frame, text="• Stel dagelijkse routine in").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(action_frame, text="• Begin met kleine veranderingen").pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Label(action_frame, text="Middellange termijn (1-3 maanden):").pack(anchor=tk.W, font=('Arial', 10, 'bold'), pady=(10, 0))
        ttk.Label(action_frame, text="• Evalueer en pas aan").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(action_frame, text="• Streef naar consistente resultaten").pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Label(action_frame, text="Lange termijn (3+ maanden):").pack(anchor=tk.W, font=('Arial', 10, 'bold'), pady=(10, 0))
        ttk.Label(action_frame, text="• Behoud gezonde gewoonten").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(action_frame, text="• Regelmatige evaluatie met zorgteam").pack(anchor=tk.W, padx=(20, 0)) 