import os
import sys
import json
import zipfile
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import hashlib
from datetime import datetime
import urllib.request
import urllib.error

# Probeer requests te importeren, maar maak het optioneel
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class UpdateSystem:
    """Systeem voor het updaten van de diabetes tracker applicatie via GitHub"""
    
    def __init__(self, root=None):
        self.root = root
        self.current_version = "1.0.0"
        # GitHub repository URL - pas dit aan naar jouw repository
        self.github_repo = "your-username/diabetes-tracker"  # Pas dit aan!
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.backup_dir = "backups"
        self.temp_dir = "temp_update"
        
        # Zorg ervoor dat backup directory bestaat
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def check_for_updates(self):
        """Controleer of er updates beschikbaar zijn via GitHub"""
        try:
            if not REQUESTS_AVAILABLE:
                print("Requests library niet beschikbaar - update check uitgeschakeld")
                return False, None
            
            # Haal laatste release op van GitHub
            response = requests.get(self.github_api_url, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name'].lstrip('v')  # Verwijder 'v' prefix
                
                if self.is_newer_version(latest_version, self.current_version):
                    return True, {
                        'version': latest_version,
                        'download_url': release_data['assets'][0]['browser_download_url'] if release_data['assets'] else None,
                        'release_notes': release_data['body'].split('\n') if release_data['body'] else ['Nieuwe versie beschikbaar'],
                        'size': f"{release_data['assets'][0]['size'] / 1024 / 1024:.1f} MB" if release_data['assets'] else "Onbekend"
                    }
            
            return False, None
            
        except Exception as e:
            print(f"GitHub update check error: {e}")
            return False, None
    
    def is_newer_version(self, new_version, current_version):
        """Vergelijk versies om te bepalen of nieuwe versie nieuwer is"""
        try:
            new_parts = [int(x) for x in new_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            # Vul kortere versie aan met nullen
            max_len = max(len(new_parts), len(current_parts))
            new_parts.extend([0] * (max_len - len(new_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return new_parts > current_parts
        except:
            return False
    
    def check_local_updates(self):
        """Controleer lokale updates (voor demo doeleinden)"""
        # Simuleer een update beschikbaarheid
        # In een echte implementatie zou dit een API call zijn
        return True, {
            'version': '1.1.0',
            'download_url': None,  # Lokale update
            'release_notes': [
                'Verbeterde gebruikersinterface',
                'Nieuwe analytics functies',
                'Betere data export opties',
                'Bug fixes en stabiliteit verbeteringen'
            ],
            'size': '2.5 MB'
        }
    
    def show_update_dialog(self, update_info):
        """Toon update dialoog"""
        if not self.root:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Beschikbaar")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        # Centreren
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Styling
        style = ttk.Style()
        style.configure('UpdateTitle.TLabel', font=('Arial', 16, 'bold'))
        style.configure('UpdateText.TLabel', font=('Arial', 10))
        
        # Header
        header_frame = ttk.Frame(dialog)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header_frame, text="🔄 Update Beschikbaar", 
                 style='UpdateTitle.TLabel').pack()
        
        ttk.Label(header_frame, 
                 text=f"Versie {update_info['version']} is beschikbaar",
                 style='UpdateText.TLabel').pack(pady=5)
        
        # Release notes
        notes_frame = ttk.Frame(dialog)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(notes_frame, text="Wat is er nieuw:", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Scrollable text voor release notes
        text_frame = ttk.Frame(notes_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        text_widget = tk.Text(text_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Voeg release notes toe
        for note in update_info['release_notes']:
            text_widget.insert(tk.END, f"• {note}\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Knoppen
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text="🔄 Nu Updaten", 
                  command=lambda: self.start_update(dialog, update_info)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏰ Later", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Nee, bedankt", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def start_update(self, dialog, update_info):
        """Start het update proces"""
        dialog.destroy()
        
        # Toon progress dialog
        progress_dialog = self.show_progress_dialog()
        
        # Start update in aparte thread
        update_thread = threading.Thread(
            target=self.perform_update, 
            args=(update_info, progress_dialog)
        )
        update_thread.start()
    
    def show_progress_dialog(self):
        """Toon progress dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Updaten...")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centreren
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Content
        ttk.Label(dialog, text="🔄 Applicatie wordt geüpdatet...", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        progress = ttk.Progressbar(dialog, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=10)
        progress.start()
        
        status_label = ttk.Label(dialog, text="Backup maken...", 
                                font=('Arial', 10))
        status_label.pack(pady=10)
        
        return dialog, status_label
    
    def perform_update(self, update_info, progress_dialog):
        """Voer de update uit"""
        dialog, status_label = progress_dialog
        
        try:
            # Stap 1: Backup maken
            self.update_status(status_label, "Backup maken...")
            if not self.create_backup():
                raise Exception("Backup mislukt")
            
            # Stap 2: Update bestanden downloaden
            self.update_status(status_label, "Update bestanden downloaden...")
            if not self.download_update(update_info):
                raise Exception("Download mislukt")
            
            # Stap 3: Update installeren
            self.update_status(status_label, "Update installeren...")
            if not self.install_update():
                raise Exception("Installatie mislukt")
            
            # Stap 4: Applicatie herstarten
            self.update_status(status_label, "Applicatie herstarten...")
            self.restart_application()
            
        except Exception as e:
            self.update_status(status_label, f"Fout: {str(e)}")
            dialog.after(2000, dialog.destroy)
            messagebox.showerror("Update Fout", f"Update mislukt: {str(e)}")
    
    def update_status(self, status_label, message):
        """Update status bericht"""
        if status_label:
            status_label.config(text=message)
    
    def create_backup(self):
        """Maak backup van huidige applicatie"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Kopieer belangrijke bestanden
            important_files = [
                'diabetes_tracker.py',
                'patient_management.py',
                'diabetes_data.db',
                'requirements.txt',
                'templates/',
                'README.md'
            ]
            
            os.makedirs(backup_path, exist_ok=True)
            
            for file in important_files:
                if os.path.exists(file):
                    if os.path.isdir(file):
                        shutil.copytree(file, os.path.join(backup_path, file))
                    else:
                        shutil.copy2(file, backup_path)
            
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False
    
    def download_update(self, update_info):
        """Download update bestanden van GitHub"""
        try:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            
            download_url = update_info.get('download_url')
            if not download_url:
                print("Geen download URL beschikbaar")
                return False
            
            # Download het update bestand
            print(f"Downloading update from: {download_url}")
            
            if REQUESTS_AVAILABLE:
                response = requests.get(download_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Bepaal bestandsnaam
                filename = download_url.split('/')[-1]
                filepath = os.path.join(self.temp_dir, filename)
                
                # Download bestand
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract ZIP bestand als het een ZIP is
                if filename.endswith('.zip'):
                    self.extract_update_zip(filepath)
                
                return True
            else:
                # Fallback naar urllib
                urllib.request.urlretrieve(download_url, os.path.join(self.temp_dir, 'update.zip'))
                self.extract_update_zip(os.path.join(self.temp_dir, 'update.zip'))
                return True
                
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def extract_update_zip(self, zip_path):
        """Extract update ZIP bestand"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            print("Update bestanden geëxtraheerd")
        except Exception as e:
            print(f"Extract error: {e}")
            raise
    
    def create_demo_update_files(self):
        """Maak demo update bestanden"""
        # Maak een demo update package
        update_files = {
            'diabetes_tracker.py': '# Updated version\nprint("Updated!")',
            'update_info.json': json.dumps({
                'version': '1.1.0',
                'timestamp': datetime.now().isoformat()
            })
        }
        
        for filename, content in update_files.items():
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def install_update(self):
        """Installeer de update"""
        try:
            # Kopieer update bestanden naar hoofdmap
            for file in os.listdir(self.temp_dir):
                src = os.path.join(self.temp_dir, file)
                dst = os.path.join('.', file)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            
            # Update versie informatie
            self.update_version_info()
            
            return True
        except Exception as e:
            print(f"Install error: {e}")
            return False
    
    def update_version_info(self):
        """Update versie informatie"""
        version_info = {
            'version': '1.1.0',
            'updated_at': datetime.now().isoformat(),
            'update_system': True
        }
        
        with open('version.json', 'w') as f:
            json.dump(version_info, f, indent=2)
    
    def restart_application(self):
        """Herstart de applicatie"""
        try:
            # Sluit huidige applicatie
            if self.root:
                self.root.after(1000, self.root.quit)
            
            # Start nieuwe versie
            subprocess.Popen([sys.executable, 'diabetes_tracker.py'])
            
        except Exception as e:
            print(f"Restart error: {e}")
    
    def check_update_schedule(self):
        """Controleer of er een geplande update check is"""
        try:
            if os.path.exists('update_schedule.json'):
                with open('update_schedule.json', 'r') as f:
                    schedule = json.load(f)
                
                last_check = datetime.fromisoformat(schedule.get('last_check', '2000-01-01'))
                check_interval = schedule.get('check_interval_days', 7)
                
                if (datetime.now() - last_check).days >= check_interval:
                    return True
            
            return False
        except Exception as e:
            print(f"Schedule check error: {e}")
            return False
    
    def schedule_update_check(self, interval_days=7):
        """Plan een update check"""
        schedule = {
            'last_check': datetime.now().isoformat(),
            'check_interval_days': interval_days,
            'auto_check': True
        }
        
        with open('update_schedule.json', 'w') as f:
            json.dump(schedule, f, indent=2)
    
    def show_update_settings(self):
        """Toon update instellingen"""
        if not self.root:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Instellingen")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Content
        ttk.Label(dialog, text="🔄 Update Instellingen", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Auto check instellingen
        auto_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Automatisch controleren op updates", 
                       variable=auto_check_var).pack(pady=10)
        
        # Check interval
        interval_frame = ttk.Frame(dialog)
        interval_frame.pack(pady=10)
        
        ttk.Label(interval_frame, text="Controleer elke:").pack(side=tk.LEFT)
        
        interval_var = tk.StringVar(value="7")
        interval_combo = ttk.Combobox(interval_frame, textvariable=interval_var, 
                                     values=["1", "3", "7", "14", "30"], width=5)
        interval_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(interval_frame, text="dagen").pack(side=tk.LEFT)
        
        # Knoppen
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_settings():
            schedule = {
                'last_check': datetime.now().isoformat(),
                'check_interval_days': int(interval_var.get()),
                'auto_check': auto_check_var.get()
            }
            
            with open('update_schedule.json', 'w') as f:
                json.dump(schedule, f, indent=2)
            
            dialog.destroy()
            messagebox.showinfo("Instellingen", "Update instellingen opgeslagen!")
        
        ttk.Button(button_frame, text="💾 Opslaan", 
                  command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Annuleren", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def manual_update_check(self):
        """Handmatige update check"""
        has_update, update_info = self.check_for_updates()
        
        if has_update:
            self.show_update_dialog(update_info)
        else:
            messagebox.showinfo("Updates", "Je hebt al de nieuwste versie!")
    
    def cleanup_temp_files(self):
        """Ruim tijdelijke bestanden op"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    """Test functie voor update systeem"""
    root = tk.Tk()
    root.withdraw()  # Verberg hoofdvenster
    
    update_system = UpdateSystem(root)
    
    # Test update check
    has_update, update_info = update_system.check_for_updates()
    
    if has_update:
        update_system.show_update_dialog(update_info)
    else:
        print("Geen updates beschikbaar")
    
    root.mainloop()

if __name__ == "__main__":
    main() 