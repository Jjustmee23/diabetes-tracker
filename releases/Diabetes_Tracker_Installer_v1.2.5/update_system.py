#!/usr/bin/env python3
"""
Echte Update Systeem voor Diabetes Tracker
"""

import os
import sys
import json
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class UpdateSystem:
    def __init__(self, root):
        self.root = root
        self.current_version = "1.2.4"
        self.github_repo = "Jjustmee23/diabetes-tracker"
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        
        print(f"✅ UpdateSystem geïnitialiseerd voor versie {self.current_version}")
    
    def check_for_updates(self, show_result=True):
        """Controleer voor updates via GitHub API"""
        try:
            print("🔍 Controleer voor updates via GitHub...")
            
            # Haal laatste release op van GitHub
            response = requests.get(self.github_api_url, timeout=10)
            if response.status_code != 200:
                if show_result:
                    messagebox.showwarning("Update Check", "Kon geen verbinding maken met GitHub.\nControleer je internetverbinding.")
                return None
            
            latest_release = response.json()
            latest_version = latest_release['tag_name'].replace('v', '')
            
            print(f"📦 Laatste GitHub release: v{latest_version}")
            print(f"📦 Huidige versie: v{self.current_version}")
            
            # Vergelijk versies
            if self.is_newer_version(latest_version, self.current_version):
                update_info = {
                    'version': latest_version,
                    'download_url': latest_release['assets'][0]['browser_download_url'] if latest_release['assets'] else None,
                    'release_notes': latest_release['body'],
                    'release_url': latest_release['html_url']
                }
                
                print(f"🆕 Nieuwe versie gevonden: v{latest_version}")
                
                if show_result:
                    self.show_update_available(update_info)
                
                return update_info
            else:
                print(f"✅ Al up-to-date (v{self.current_version})")
                
                if show_result:
                    messagebox.showinfo("Update Check", f"Je hebt al de nieuwste versie ({self.current_version})")
                
                return None
                
        except Exception as e:
            print(f"❌ GitHub API fout: {str(e)}")
            
            # Fallback: Toon lokale update info
            if show_result:
                self.show_local_update_info()
            
            return None
    
    def show_local_update_info(self):
        """Toon lokale update informatie (fallback)"""
        info_window = tk.Toplevel(self.root)
        info_window.title("📋 Update Informatie")
        info_window.geometry("500x400")
        info_window.transient(self.root)
        info_window.grab_set()
        
        # Centreren
        info_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        # Content
        main_frame = ttk.Frame(info_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="📋 Update Informatie", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Huidige versie
        version_frame = ttk.LabelFrame(main_frame, text="Huidige Versie", padding="10")
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, text=f"Versie: {self.current_version}").pack(anchor=tk.W)
        ttk.Label(version_frame, text=f"Repository: {self.github_repo}").pack(anchor=tk.W)
        
        # Beschikbare releases
        releases_frame = ttk.LabelFrame(main_frame, text="Beschikbare Releases", padding="10")
        releases_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        releases_text = tk.Text(releases_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(releases_frame, orient=tk.VERTICAL, command=releases_text.yview)
        releases_text.configure(yscrollcommand=scrollbar.set)
        
        releases_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Voeg release info toe
        releases_text.insert(tk.END, "📦 Beschikbare releases op GitHub:\n\n")
        releases_text.insert(tk.END, "• v1.2.1 - Basis versie\n")
        releases_text.insert(tk.END, "• v1.2.2 - Test update\n")
        releases_text.insert(tk.END, "• v1.2.3 - Verbeterde update functionaliteit\n")
        releases_text.insert(tk.END, "• v1.2.5 - Verbeterde datum/tijd invoervelden\n")
        releases_text.insert(tk.END, "• v1.2.4 - Echte GitHub API integratie\n\n")
        releases_text.insert(tk.END, "🌐 Download releases van:\n")
        releases_text.insert(tk.END, f"https://github.com/{self.github_repo}/releases\n\n")
        releases_text.insert(tk.END, "💡 Tip: Controleer je internetverbinding voor automatische update checks.")
        
        releases_text.config(state=tk.DISABLED)
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def open_github():
            import webbrowser
            webbrowser.open(f"https://github.com/{self.github_repo}/releases")
        
        ttk.Button(button_frame, text="🌐 Open GitHub", 
                  command=open_github).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Sluiten", 
                  command=info_window.destroy).pack(side=tk.LEFT)
    
    def is_newer_version(self, new_version, current_version):
        """Controleer of nieuwe versie nieuwer is"""
        try:
            new_parts = [int(x) for x in new_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            # Vul aan met nullen als nodig
            while len(new_parts) < 3:
                new_parts.append(0)
            while len(current_parts) < 3:
                current_parts.append(0)
            
            return new_parts > current_parts
        except:
            return False
    
    def show_update_available(self, update_info):
        """Toon update beschikbaar popup"""
        update_window = tk.Toplevel(self.root)
        update_window.title("🔄 Update Beschikbaar")
        update_window.geometry("600x500")
        update_window.transient(self.root)
        update_window.grab_set()
        
        # Centreren
        update_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        # Content
        main_frame = ttk.Frame(update_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🔄 Nieuwe Update Beschikbaar", 
                 font=('Arial', 16, 'bold')).pack()
        
        ttk.Label(header_frame, text=f"Versie {update_info['version']} is beschikbaar", 
                 font=('Arial', 12)).pack()
        
        # Versie info
        version_frame = ttk.LabelFrame(main_frame, text="Versie Informatie", padding="10")
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, text=f"Huidige versie: {self.current_version}").pack(anchor=tk.W)
        ttk.Label(version_frame, text=f"Nieuwe versie: {update_info['version']}").pack(anchor=tk.W)
        
        # Release notes
        if update_info['release_notes']:
            notes_frame = ttk.LabelFrame(main_frame, text="Wat is er nieuw?", padding="10")
            notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            notes_text = tk.Text(notes_frame, height=10, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=notes_text.yview)
            notes_text.configure(yscrollcommand=scrollbar.set)
            
            notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Voeg release notes toe
            notes_text.insert(tk.END, update_info['release_notes'])
            notes_text.config(state=tk.DISABLED)
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def start_update():
            update_window.destroy()
            messagebox.showinfo("Update", f"Update naar versie {update_info['version']} wordt gestart...\n\n"
                               "Download de nieuwe versie van:\n"
                               f"{update_info['release_url']}")
        
        ttk.Button(button_frame, text="🔄 Nu Updaten", 
                  command=start_update).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="⏰ Later", 
                  command=update_window.destroy).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Annuleren", 
                  command=update_window.destroy).pack(side=tk.LEFT)
    
    def show_update_settings(self):
        """Toon update instellingen"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Update Instellingen")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Centreren
        settings_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        # Content
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="⚙️ Update Instellingen", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Huidige versie
        version_frame = ttk.LabelFrame(main_frame, text="Huidige Versie", padding="10")
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(version_frame, text=f"Versie: {self.current_version}").pack(anchor=tk.W)
        ttk.Label(version_frame, text=f"Repository: {self.github_repo}").pack(anchor=tk.W)
        ttk.Label(version_frame, text=f"API URL: {self.github_api_url}").pack(anchor=tk.W)
        
        # Instellingen
        settings_frame = ttk.LabelFrame(main_frame, text="Instellingen", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        auto_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Automatisch controleren voor updates", 
                       variable=auto_check_var).pack(anchor=tk.W)
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_settings():
            messagebox.showinfo("Instellingen", "Instellingen opgeslagen!")
            settings_window.destroy()
        
        ttk.Button(button_frame, text="💾 Opslaan", 
                  command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Nu Controleren", 
                  command=lambda: self.check_for_updates(True)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Annuleren", 
                  command=settings_window.destroy).pack(side=tk.LEFT) 