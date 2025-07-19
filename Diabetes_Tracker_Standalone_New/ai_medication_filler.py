import openai
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import json

class AIMedicationFiller:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        
    def get_medication_info(self, medication_name):
        """Haal gedetailleerde medicatie informatie op via OpenAI"""
        try:
            prompt = f"""
            Geef gedetailleerde informatie over het medicijn: {medication_name}
            
            Geef de informatie in JSON formaat met de volgende velden:
            {{
                "description": "Korte beschrijving van het medicijn",
                "pros": "Voordelen van het medicijn (minstens 3 punten)",
                "cons": "Nadelen en risico's (minstens 3 punten)",
                "warnings": "Belangrijke waarschuwingen en contra-indicaties",
                "pregnancy_warning": "Specifieke waarschuwingen voor zwangerschap",
                "side_effects": "Mogelijke bijwerkingen (minstens 5)",
                "interactions": "Interacties met andere medicijnen en stoffen",
                "dosage_info": "Dosering informatie en instructies"
            }}
            
            Zorg dat alle informatie accuraat en medisch verantwoord is.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Je bent een medisch expert die gedetailleerde informatie geeft over medicijnen. Geef altijd accurate, medisch verantwoorde informatie in het Nederlands."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Probeer JSON te parsen
            content = response.choices[0].message.content
            try:
                # Zoek JSON in de response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
                else:
                    # Fallback: maak een gestructureerde response
                    return self._parse_medication_response(content, medication_name)
            except json.JSONDecodeError:
                return self._parse_medication_response(content, medication_name)
                
        except Exception as e:
            print(f"Error getting medication info: {e}")
            return None
    
    def _parse_medication_response(self, content, medication_name):
        """Parse tekst response naar gestructureerde data"""
        lines = content.split('\n')
        info = {
            "description": f"Medicijn: {medication_name}",
            "pros": "Voordelen: Effectief, goed verdraagbaar",
            "cons": "Nadelen: Mogelijke bijwerkingen",
            "warnings": "Raadpleeg altijd een arts",
            "pregnancy_warning": "Overleg met arts tijdens zwangerschap",
            "side_effects": "Mogelijke bijwerkingen: hoofdpijn, misselijkheid",
            "interactions": "Kan interactie hebben met andere medicijnen",
            "dosage_info": "Dosering volgens voorschrift arts"
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "voordelen" in line.lower() or "pros" in line.lower():
                current_section = "pros"
            elif "nadelen" in line.lower() or "cons" in line.lower():
                current_section = "cons"
            elif "waarschuwing" in line.lower() or "warning" in line.lower():
                current_section = "warnings"
            elif "bijwerking" in line.lower() or "side effect" in line.lower():
                current_section = "side_effects"
            elif "interactie" in line.lower() or "interaction" in line.lower():
                current_section = "interactions"
            elif "dosering" in line.lower() or "dosage" in line.lower():
                current_section = "dosage_info"
            elif current_section and line.startswith('-') or line.startswith('•'):
                info[current_section] += f"\n{line}"
            elif current_section:
                info[current_section] = line
                
        return info

class MedicationFillerGUI:
    def __init__(self, parent):
        self.parent = parent
        self.api_key = "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"
        self.ai_filler = AIMedicationFiller(self.api_key)
        
    def show_filler(self):
        """Toon de AI medicatie filler GUI"""
        self.create_filler_window()
        
    def create_filler_window(self):
        """Maak venster voor AI medicatie fiche invulling"""
        self.filler_window = tk.Toplevel(self.parent)
        self.filler_window.title("🤖 AI Medicatie Fiche Invuller")
        self.filler_window.geometry("800x600")
        
        # Hoofdframe
        main_frame = ttk.Frame(self.filler_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="🤖 AI Medicatie Fiche Invuller", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Medicatie naam invoer
        input_frame = ttk.LabelFrame(main_frame, text="📝 Medicatie Informatie", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_frame, text="Medicatie Naam:", font=('Arial', 12)).pack(anchor=tk.W)
        self.medication_entry = ttk.Entry(input_frame, width=50, font=('Arial', 12))
        self.medication_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Voorbeelden
        examples_frame = ttk.Frame(input_frame)
        examples_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(examples_frame, text="Voorbeelden:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        examples = ["Metformine 500mg", "Insuline (kortwerkend)", "Omeprazol 20mg", "Ibuprofen 400mg"]
        
        for example in examples:
            example_btn = ttk.Button(examples_frame, text=example, 
                                   command=lambda x=example: self.medication_entry.delete(0, tk.END) or self.medication_entry.insert(0, x),
                                   style='secondary.TButton', width=20)
            example_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        
        # AI Invullen knop
        fill_button = ttk.Button(input_frame, text="🤖 AI Invullen", 
                                command=self.fill_medication_info, 
                                style='primary.TButton', width=20)
        fill_button.pack(pady=10)
        
        # Resultaat sectie
        result_frame = ttk.LabelFrame(main_frame, text="📋 Resultaat", padding="15")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook voor tabs
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Preview
        self.preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text="Preview")
        
        # Tab 2: JSON
        self.json_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.json_tab, text="JSON Data")
        
        # Preview text widget
        self.preview_text = tk.Text(self.preview_tab, wrap=tk.WORD, font=('Arial', 11))
        preview_scrollbar = ttk.Scrollbar(self.preview_tab, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # JSON text widget
        self.json_text = tk.Text(self.json_tab, wrap=tk.WORD, font=('Courier', 10))
        json_scrollbar = ttk.Scrollbar(self.json_tab, orient=tk.VERTICAL, command=self.json_text.yview)
        self.json_text.configure(yscrollcommand=json_scrollbar.set)
        
        self.json_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        json_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 Opslaan in Database", 
                  command=self.save_to_database, 
                  style='success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Nieuwe Medicatie", 
                  command=self.clear_form, 
                  style='secondary.TButton').pack(side=tk.LEFT)
        
        self.current_medication_info = None
        
    def fill_medication_info(self):
        """Vul medicatie informatie in met AI"""
        medication_name = self.medication_entry.get().strip()
        if not medication_name:
            messagebox.showwarning("Waarschuwing", "Voer een medicatie naam in.")
            return
        
        # Toon loading
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "🤖 AI is bezig met het ophalen van medicatie informatie...\n\nEven geduld a.u.b.")
        self.filler_window.update()
        
        try:
            # Haal informatie op via AI
            medication_info = self.ai_filler.get_medication_info(medication_name)
            
            if medication_info:
                self.current_medication_info = medication_info
                
                # Toon preview
                self.show_preview(medication_info)
                
                # Toon JSON
                self.json_text.delete(1.0, tk.END)
                self.json_text.insert(tk.END, json.dumps(medication_info, indent=2, ensure_ascii=False))
                
                messagebox.showinfo("Succes", "Medicatie informatie succesvol opgehaald!")
            else:
                messagebox.showerror("Fout", "Kon geen medicatie informatie ophalen.")
                
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een fout opgetreden: {str(e)}")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"❌ Fout bij ophalen informatie:\n{str(e)}")
    
    def show_preview(self, medication_info):
        """Toon preview van medicatie informatie"""
        self.preview_text.delete(1.0, tk.END)
        
        preview = f"""💊 {medication_info.get('description', 'Medicatie Informatie')}

✅ VOORDELEN:
{medication_info.get('pros', 'Geen informatie beschikbaar')}

❌ NADELEN:
{medication_info.get('cons', 'Geen informatie beschikbaar')}

⚠️ WAARSCHUWINGEN:
{medication_info.get('warnings', 'Geen informatie beschikbaar')}

🤰 ZWANGERSCHAP WAARSCHUWING:
{medication_info.get('pregnancy_warning', 'Geen informatie beschikbaar')}

💊 BIJWERKINGEN:
{medication_info.get('side_effects', 'Geen informatie beschikbaar')}

🔗 INTERACTIES:
{medication_info.get('interactions', 'Geen informatie beschikbaar')}

💊 DOSERING:
{medication_info.get('dosage_info', 'Geen informatie beschikbaar')}
"""
        
        self.preview_text.insert(tk.END, preview)
    
    def save_to_database(self):
        """Sla medicatie informatie op in de database"""
        if not self.current_medication_info:
            messagebox.showwarning("Waarschuwing", "Geen medicatie informatie om op te slaan.")
            return
        
        medication_name = self.medication_entry.get().strip()
        if not medication_name:
            messagebox.showwarning("Waarschuwing", "Voer een medicatie naam in.")
            return
        
        try:
            # Verbind met database
            conn = sqlite3.connect('patient_data.db')
            cursor = conn.cursor()
            
            # Voeg medicatie toe
            cursor.execute('''
                INSERT OR REPLACE INTO medication_info 
                (medication_name, description, pros, cons, warnings, pregnancy_warning, 
                 side_effects, interactions, dosage_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                medication_name,
                self.current_medication_info.get('description', ''),
                self.current_medication_info.get('pros', ''),
                self.current_medication_info.get('cons', ''),
                self.current_medication_info.get('warnings', ''),
                self.current_medication_info.get('pregnancy_warning', ''),
                self.current_medication_info.get('side_effects', ''),
                self.current_medication_info.get('interactions', ''),
                self.current_medication_info.get('dosage_info', '')
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Succes", f"Medicatie '{medication_name}' succesvol opgeslagen in de database!")
            
        except Exception as e:
            messagebox.showerror("Fout", f"Er is een fout opgetreden bij opslaan: {str(e)}")
    
    def clear_form(self):
        """Formulier leegmaken"""
        self.medication_entry.delete(0, tk.END)
        self.preview_text.delete(1.0, tk.END)
        self.json_text.delete(1.0, tk.END)
        self.current_medication_info = None
        self.notebook.select(0)  # Ga naar eerste tab 