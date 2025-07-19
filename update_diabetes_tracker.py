#!/usr/bin/env python3
"""
Diabetes Tracker Update Script
==============================

Dit script maakt het gemakkelijk om het diabetes tracker programma te updaten.
Het controleert voor updates, maakt backups en installeert nieuwe versies.
"""

import os
import sys
import json
import shutil
import zipfile
import requests
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import urllib.request
import urllib.error

class DiabetesTrackerUpdater:
    """Update script voor Diabetes Tracker"""
    
    def __init__(self):
        self.current_version = "1.0.0"
        self.update_url = "https://api.github.com/repos/your-repo/diabetes-tracker/releases/latest"
        self.backup_dir = "backups"
        self.temp_dir = "temp_update"
        self.app_name = "diabetes_tracker.py"
        
        # Zorg ervoor dat backup directory bestaat
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def show_welcome_dialog(self):
        """Toon welkom dialoog"""
        root = tk.Tk()
        root.withdraw()  # Verberg hoofdvenster
        
        dialog = tk.Toplevel(root)
        dialog.title("Diabetes Tracker Updater")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Centreren
        dialog.geometry("+%d+%d" % (
            root.winfo_screenwidth()//2 - 250,
            root.winfo_screenheight()//2 - 150
        ))
        
        # Content
        ttk.Label(dialog, text="🔄 Diabetes Tracker Updater", 
                 font=('Arial', 18, 'bold')).pack(pady=20)
        
        ttk.Label(dialog, text="Welkom bij de Diabetes Tracker Updater!", 
                 font=('Arial', 12)).pack(pady=10)
        
        ttk.Label(dialog, text="Dit script helpt je om je diabetes tracker applicatie up-to-date te houden.", 
                 font=('Arial', 10), wraplength=400).pack(pady=10)
        
        # Knoppen
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="🔄 Controleer voor Updates", 
                  command=lambda: self.start_update_check(dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 Backup Maken", 
                  command=lambda: self.create_backup_only(dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Sluiten", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        root.mainloop()
    
    def start_update_check(self, dialog):
        """Start update check"""
        dialog.destroy()
        
        # Toon progress dialog
        progress_dialog = self.show_progress_dialog("Controleer voor updates...")
        
        # Start update check in aparte thread
        update_thread = threading.Thread(
            target=self.perform_update_check, 
            args=(progress_dialog,)
        )
        update_thread.start()
    
    def create_backup_only(self, dialog):
        """Maak alleen een backup"""
        dialog.destroy()
        
        # Toon progress dialog
        progress_dialog = self.show_progress_dialog("Backup maken...")
        
        # Start backup in aparte thread
        backup_thread = threading.Thread(
            target=self.perform_backup_only, 
            args=(progress_dialog,)
        )
        backup_thread.start()
    
    def show_progress_dialog(self, initial_message):
        """Toon progress dialog"""
        root = tk.Tk()
        root.withdraw()
        
        dialog = tk.Toplevel(root)
        dialog.title("Updater")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()
        
        # Centreren
        dialog.geometry("+%d+%d" % (
            root.winfo_screenwidth()//2 - 200,
            root.winfo_screenheight()//2 - 100
        ))
        
        # Content
        ttk.Label(dialog, text="🔄 Bezig...", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        progress = ttk.Progressbar(dialog, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=10)
        progress.start()
        
        status_label = ttk.Label(dialog, text=initial_message, 
                                font=('Arial', 10))
        status_label.pack(pady=10)
        
        return dialog, status_label, root
    
    def perform_update_check(self, progress_dialog):
        """Voer update check uit"""
        dialog, status_label, root = progress_dialog
        
        try:
            # Stap 1: Controleer huidige versie
            self.update_status(status_label, "Controleer huidige versie...")
            current_version = self.get_current_version()
            
            # Stap 2: Controleer voor updates
            self.update_status(status_label, "Controleer voor updates...")
            has_update, update_info = self.check_for_updates()
            
            if has_update:
                self.update_status(status_label, "Update gevonden!")
                dialog.after(1000, lambda: self.show_update_dialog(update_info, dialog))
            else:
                self.update_status(status_label, "Geen updates beschikbaar")
                dialog.after(2000, dialog.destroy)
                messagebox.showinfo("Updates", "Je hebt al de nieuwste versie!")
            
        except Exception as e:
            self.update_status(status_label, f"Fout: {str(e)}")
            dialog.after(2000, dialog.destroy)
            messagebox.showerror("Update Fout", f"Update check mislukt: {str(e)}")
    
    def perform_backup_only(self, progress_dialog):
        """Voer alleen backup uit"""
        dialog, status_label, root = progress_dialog
        
        try:
            self.update_status(status_label, "Backup maken...")
            
            if self.create_backup():
                self.update_status(status_label, "Backup succesvol gemaakt!")
                dialog.after(2000, dialog.destroy)
                messagebox.showinfo("Backup", "Backup succesvol gemaakt!")
            else:
                raise Exception("Backup mislukt")
                
        except Exception as e:
            self.update_status(status_label, f"Fout: {str(e)}")
            dialog.after(2000, dialog.destroy)
            messagebox.showerror("Backup Fout", f"Backup mislukt: {str(e)}")
    
    def update_status(self, status_label, message):
        """Update status bericht"""
        if status_label:
            status_label.config(text=message)
    
    def get_current_version(self):
        """Haal huidige versie op"""
        try:
            if os.path.exists('version.json'):
                with open('version.json', 'r') as f:
                    version_info = json.load(f)
                return version_info.get('version', '1.0.0')
            else:
                return '1.0.0'
        except Exception as e:
            print(f"Version check error: {e}")
            return '1.0.0'
    
    def check_for_updates(self):
        """Controleer voor updates"""
        try:
            # Simuleer update check (in echte implementatie zou dit naar server gaan)
            return True, {
                'version': '1.1.0',
                'download_url': None,
                'release_notes': [
                    'Verbeterde gebruikersinterface',
                    'Nieuwe analytics functies',
                    'Betere data export opties',
                    'Bug fixes en stabiliteit verbeteringen',
                    'Nieuw update systeem'
                ],
                'size': '2.5 MB',
                'requires_restart': True
            }
        except Exception as e:
            print(f"Update check error: {e}")
            return False, None
    
    def show_update_dialog(self, update_info, progress_dialog):
        """Toon update dialoog"""
        dialog, status_label, root = progress_dialog
        dialog.destroy()
        
        update_dialog = tk.Toplevel(root)
        update_dialog.title("Update Beschikbaar")
        update_dialog.geometry("500x400")
        update_dialog.resizable(False, False)
        update_dialog.transient(root)
        update_dialog.grab_set()
        
        # Centreren
        update_dialog.geometry("+%d+%d" % (
            root.winfo_screenwidth()//2 - 250,
            root.winfo_screenheight()//2 - 200
        ))
        
        # Styling
        style = ttk.Style()
        style.configure('UpdateTitle.TLabel', font=('Arial', 16, 'bold'))
        style.configure('UpdateText.TLabel', font=('Arial', 10))
        
        # Header
        header_frame = ttk.Frame(update_dialog)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header_frame, text="🔄 Update Beschikbaar", 
                 style='UpdateTitle.TLabel').pack()
        
        ttk.Label(header_frame, 
                 text=f"Versie {update_info['version']} is beschikbaar",
                 style='UpdateText.TLabel').pack(pady=5)
        
        # Release notes
        notes_frame = ttk.Frame(update_dialog)
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
        button_frame = ttk.Frame(update_dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text="🔄 Nu Updaten", 
                  command=lambda: self.start_update(update_dialog, update_info)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏰ Later", 
                  command=update_dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Nee, bedankt", 
                  command=update_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def start_update(self, dialog, update_info):
        """Start het update proces"""
        dialog.destroy()
        
        # Toon progress dialog
        progress_dialog = self.show_progress_dialog("Update installeren...")
        
        # Start update in aparte thread
        update_thread = threading.Thread(
            target=self.perform_update, 
            args=(update_info, progress_dialog)
        )
        update_thread.start()
    
    def perform_update(self, update_info, progress_dialog):
        """Voer de update uit"""
        dialog, status_label, root = progress_dialog
        
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
                'README.md',
                'update_system.py'
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
        """Download update bestanden"""
        try:
            # Voor demo doeleinden maken we een lokale update
            # In een echte implementatie zou dit een download zijn
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            
            # Simuleer update bestanden
            self.create_demo_update_files()
            
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def create_demo_update_files(self):
        """Maak demo update bestanden"""
        # Maak een demo update package
        update_files = {
            'diabetes_tracker.py': '# Updated version\nprint("Updated!")',
            'update_info.json': json.dumps({
                'version': '1.1.0',
                'timestamp': datetime.now().isoformat()
            }),
            'version.json': json.dumps({
                'version': '1.1.0',
                'updated_at': datetime.now().isoformat(),
                'update_system': True
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
            
            return True
        except Exception as e:
            print(f"Install error: {e}")
            return False
    
    def restart_application(self):
        """Herstart de applicatie"""
        try:
            # Start nieuwe versie
            subprocess.Popen([sys.executable, self.app_name])
            
        except Exception as e:
            print(f"Restart error: {e}")
    
    def cleanup_temp_files(self):
        """Ruim tijdelijke bestanden op"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    """Hoofdfunctie"""
    print("🔄 Diabetes Tracker Updater")
    print("=" * 40)
    
    updater = DiabetesTrackerUpdater()
    updater.show_welcome_dialog()

if __name__ == "__main__":
    main() 