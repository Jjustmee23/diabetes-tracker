#!/usr/bin/env python3
"""
Volledig Update Systeem voor Diabetes Tracker v1.2.5
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
        self.current_version = "1.4.1"
        self.github_repo = "Jjustmee23/diabetes-tracker"
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases"
        
        print(f"✅ UpdateSystem geïnitialiseerd voor versie {self.current_version}")
        
        # Controleer of repository bestaat
        self.check_repository_exists()
    
    def check_repository_exists(self):
        """Controleer of de repository bestaat"""
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Diabetes-Tracker-Update-Checker",
                "Authorization": "token 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"
            }
            response = requests.get(f"https://api.github.com/repos/{self.github_repo}", headers=headers, timeout=5)
            if response.status_code == 404:
                print(f"⚠️ Repository {self.github_repo} bestaat niet")
                print("ℹ️ Update systeem gebruikt lokale informatie")
            elif response.status_code == 200:
                print(f"✅ Repository {self.github_repo} is bereikbaar (privé)")
            elif response.status_code == 401:
                print(f"⚠️ Repository {self.github_repo} vereist authenticatie")
                print("ℹ️ Update systeem gebruikt lokale informatie")
            else:
                print(f"⚠️ Repository status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Kan repository niet controleren: {str(e)}")
    
    def check_for_updates(self, show_result=True):
        """Controleer voor updates via GitHub API"""
        try:
            print("🔍 Controleer voor updates via GitHub...")
            
            # Haal alle releases op van GitHub
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Diabetes-Tracker-Update-Checker",
                "Authorization": "token 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"
            }
            
            response = requests.get(self.github_api_url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                print(f"❌ Repository {self.github_repo} bestaat niet")
                if show_result:
                    self.show_repository_not_found()
                return None
            elif response.status_code == 401:
                print(f"❌ Repository {self.github_repo} vereist authenticatie")
                if show_result:
                    self.show_authentication_error()
                return None
            elif response.status_code != 200:
                print(f"❌ GitHub API fout: {response.status_code}")
                if show_result:
                    self.show_connection_error()
                return None
            
            releases = response.json()
            
            if not releases:
                print("❌ Geen releases gevonden")
                if show_result:
                    self.show_no_releases()
                return None
            
            # Zoek de nieuwste release
            latest_release = None
            latest_version = None
            
            for release in releases:
                if not release.get('draft', False) and not release.get('prerelease', False):
                    version = release['tag_name'].replace('v', '')
                    if self.is_newer_version(version, self.current_version):
                        if latest_version is None or self.is_newer_version(version, latest_version):
                            latest_release = release
                            latest_version = version
            
            print(f"📦 Huidige versie: v{self.current_version}")
            
            if latest_release:
                print(f"🆕 Nieuwe versie gevonden: v{latest_version}")
                
                update_info = {
                    'version': latest_version,
                    'download_url': self.get_download_url(latest_release),
                    'release_notes': latest_release.get('body', ''),
                    'release_url': latest_release['html_url']
                }
                
                if show_result:
                    self.show_update_available(update_info)
                
                return update_info
            else:
                print(f"✅ Al up-to-date (v{self.current_version})")
                
                if show_result:
                    self.show_up_to_date()
                
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Netwerk fout: {str(e)}")
            if show_result:
                self.show_connection_error()
            return None
        except Exception as e:
            print(f"❌ Onverwachte fout: {str(e)}")
            if show_result:
                self.show_error(str(e))
            return None
    
    def get_download_url(self, release):
        """Haal download URL op van release assets"""
        assets = release.get('assets', [])
        
        # Zoek naar installer
        for asset in assets:
            if 'installer' in asset['name'].lower() and asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        
        # Fallback naar eerste asset
        if assets:
            return assets[0]['browser_download_url']
        
        return None
    
    def show_up_to_date(self):
        """Toon dat je up-to-date bent"""
        messagebox.showinfo(
            "✅ Up-to-Date", 
            f"Je hebt al de nieuwste versie!\n\n"
            f"Huidige versie: {self.current_version}\n\n"
            "De applicatie controleert automatisch op updates."
        )
    
    def show_connection_error(self):
        """Toon verbindingsfout"""
        messagebox.showwarning(
            "🌐 Verbindingsfout", 
            "Kon geen verbinding maken met GitHub.\n\n"
            "Mogelijke oorzaken:\n"
            "• Geen internetverbinding\n"
            "• GitHub is niet bereikbaar\n"
            "• Firewall blokkeert de verbinding\n\n"
            "Controleer je internetverbinding en probeer opnieuw."
        )
    
    def show_no_releases(self):
        """Toon dat er geen releases zijn"""
        messagebox.showinfo(
            "📦 Geen Releases", 
            "Er zijn nog geen releases beschikbaar op GitHub.\n\n"
            f"Repository: {self.github_repo}"
        )
    
    def show_repository_not_found(self):
        """Toon dat repository niet bestaat"""
        messagebox.showwarning(
            "⚠️ Repository Niet Gevonden", 
            f"De repository {self.github_repo} bestaat niet.\n\n"
            "Mogelijke oorzaken:\n"
            "• Repository naam is incorrect\n"
            "• Repository is verwijderd\n\n"
            "Updates werken mogelijk niet correct.\n"
            "Controleer de repository instellingen."
        )
    
    def show_authentication_error(self):
        """Toon authenticatie fout"""
        messagebox.showwarning(
            "🔐 Authenticatie Vereist", 
            f"De repository {self.github_repo} is privé en vereist authenticatie.\n\n"
            "De applicatie probeert automatisch te authenticeren.\n"
            "Als dit probleem blijft bestaan, controleer dan:\n"
            "• API key is geldig\n"
            "• API key heeft juiste rechten\n"
            "• Repository toegangsrechten\n\n"
            "Updates werken mogelijk niet correct."
        )
    
    def show_error(self, error_msg):
        """Toon algemene fout"""
        messagebox.showerror(
            "❌ Fout", 
            f"Er is een fout opgetreden bij het controleren van updates:\n\n{error_msg}"
        )
    
    def show_local_update_info(self):
        """Toon lokale update informatie (fallback)"""
        info_window = tk.Toplevel(self.root)
        info_window.title("📋 Update Informatie")
        info_window.geometry("600x500")
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
        ttk.Label(version_frame, text=f"Status: ✅ Up-to-date").pack(anchor=tk.W)
        
        # Beschikbare releases
        releases_frame = ttk.LabelFrame(main_frame, text="Beschikbare Releases", padding="10")
        releases_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        releases_text = tk.Text(releases_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(releases_frame, orient=tk.VERTICAL, command=releases_text.yview)
        releases_text.configure(yscrollcommand=scrollbar.set)
        
        releases_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Voeg release info toe
        releases_text.insert(tk.END, "📦 Beschikbare releases op GitHub:\n\n")
        releases_text.insert(tk.END, "• v1.2.0 - Initiële release\n")
        releases_text.insert(tk.END, "• v1.2.1 - Eerste stabiele versie\n")
        releases_text.insert(tk.END, "• v1.2.2 - Test update systeem\n")
        releases_text.insert(tk.END, "• v1.2.3 - Verbeterde update functionaliteit\n")
        releases_text.insert(tk.END, "• v1.2.4 - Echte GitHub API integratie\n")
        releases_text.insert(tk.END, f"• v{self.current_version} - Verbeterde datum/tijd invoervelden (HUIDIG)\n\n")
        releases_text.insert(tk.END, "🌐 Download releases van:\n")
        releases_text.insert(tk.END, f"https://github.com/{self.github_repo}/releases\n\n")
        releases_text.insert(tk.END, "💡 Tip: De applicatie controleert automatisch op updates.")
        
        releases_text.config(state=tk.DISABLED)
        
        # Knoppen
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def open_github():
            import webbrowser
            webbrowser.open(f"https://github.com/{self.github_repo}/releases")
        
        def check_again():
            info_window.destroy()
            self.check_for_updates(True)
        
        ttk.Button(button_frame, text="🔄 Opnieuw Controleren", 
                  command=check_again).pack(side=tk.LEFT, padx=(0, 10))
        
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
        update_window.geometry("700x600")
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
        
        if update_info['download_url']:
            ttk.Label(version_frame, text=f"Download: Beschikbaar").pack(anchor=tk.W)
        else:
            ttk.Label(version_frame, text=f"Download: Alleen source code").pack(anchor=tk.W)
        
        # Release notes
        if update_info['release_notes']:
            notes_frame = ttk.LabelFrame(main_frame, text="Wat is er nieuw?", padding="10")
            notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            notes_text = tk.Text(notes_frame, height=12, wrap=tk.WORD)
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
            self.perform_automatic_update(update_info)
        
        def download_direct():
            if update_info['download_url']:
                import webbrowser
                webbrowser.open(update_info['download_url'])
                messagebox.showinfo(
                    "📥 Download", 
                    "Directe download gestart!\n\n"
                    "Het bestand wordt gedownload naar je Downloads map."
                )
            else:
                messagebox.showwarning(
                    "⚠️ Geen Directe Download", 
                    "Er is geen directe download beschikbaar.\n\n"
                    "Ga naar GitHub om de release te downloaden."
                )
        
        ttk.Button(button_frame, text="🔄 Nu Updaten", 
                  command=start_update).pack(side=tk.LEFT, padx=(0, 10))
        
        if update_info['download_url']:
            ttk.Button(button_frame, text="📥 Direct Downloaden", 
                      command=download_direct).pack(side=tk.LEFT, padx=(0, 10))
        
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
        ttk.Label(version_frame, text=f"Status: ✅ Actief").pack(anchor=tk.W)
        
        # Instellingen
        settings_frame = ttk.LabelFrame(main_frame, text="Instellingen", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        auto_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Automatisch controleren voor updates", 
                       variable=auto_check_var).pack(anchor=tk.W)
        
        ttk.Label(settings_frame, text="Controleert elke keer bij opstarten").pack(anchor=tk.W, padx=(20, 0))
        
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
    
    def perform_automatic_update(self, update_info):
        """Voer automatische update uit"""
        try:
            # Toon progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("🔄 Automatische Update")
            progress_window.geometry("500x300")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            # Centreren
            progress_window.geometry("+%d+%d" % (
                self.root.winfo_rootx() + 200,
                self.root.winfo_rooty() + 200
            ))
            
            # Content
            main_frame = ttk.Frame(progress_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            ttk.Label(main_frame, text="🔄 Automatische Update", 
                     font=('Arial', 16, 'bold')).pack(pady=(0, 20))
            
            ttk.Label(main_frame, text=f"Update naar versie {update_info['version']}", 
                     font=('Arial', 12)).pack(pady=(0, 20))
            
            # Progress bar
            progress_var = tk.StringVar(value="Voorbereiden...")
            progress_label = ttk.Label(main_frame, textvariable=progress_var)
            progress_label.pack(pady=(0, 10))
            
            progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
            progress_bar.pack(fill=tk.X, pady=(0, 20))
            progress_bar.start()
            
            # Status text
            status_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
            status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            def update_status(message):
                status_text.insert(tk.END, f"• {message}\n")
                status_text.see(tk.END)
                progress_window.update()
            
            def download_and_install():
                try:
                    update_status("Start automatische update...")
                    
                    if not update_info['download_url']:
                        update_status("❌ Geen directe download beschikbaar")
                        update_status("Ga naar GitHub om handmatig te downloaden")
                        progress_window.after(2000, progress_window.destroy)
                        return
                    
                    # Download de nieuwe versie
                    update_status("📥 Download nieuwe versie...")
                    progress_var.set("Downloaden...")
                    
                    response = requests.get(update_info['download_url'], stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Bepaal download locatie
                    downloads_dir = os.path.expanduser("~/Downloads")
                    if not os.path.exists(downloads_dir):
                        downloads_dir = os.getcwd()
                    
                    filename = f"Diabetes_Tracker_Update_{update_info['version']}.zip"
                    filepath = os.path.join(downloads_dir, filename)
                    
                    # Download bestand
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    progress_var.set(f"Downloaden... {progress:.1f}%")
                    
                    update_status(f"✅ Download voltooid: {filename}")
                    
                    # Extract en installeer
                    update_status("📦 Extract bestanden...")
                    progress_var.set("Installeren...")
                    
                    import zipfile
                    import shutil
                    
                    # Maak backup van huidige versie
                    backup_dir = os.path.join(os.getcwd(), "backup_current_version")
                    if os.path.exists(backup_dir):
                        shutil.rmtree(backup_dir)
                    os.makedirs(backup_dir)
                    
                    # Backup belangrijke bestanden
                    important_files = ['diabetes_tracker.py', 'patient_management.py', 'update_system.py']
                    for file in important_files:
                        if os.path.exists(file):
                            shutil.copy2(file, backup_dir)
                    
                    update_status("💾 Backup gemaakt van huidige versie")
                    
                    # Extract nieuwe versie
                    extract_dir = os.path.join(downloads_dir, f"Diabetes_Tracker_{update_info['version']}")
                    if os.path.exists(extract_dir):
                        shutil.rmtree(extract_dir)
                    
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    update_status("📁 Bestanden geëxtract")
                    
                    # Kopieer nieuwe bestanden
                    for root, dirs, files in os.walk(extract_dir):
                        for file in files:
                            if file.endswith('.py') or file.endswith('.txt') or file.endswith('.md'):
                                src_path = os.path.join(root, file)
                                dst_path = os.path.join(os.getcwd(), file)
                                shutil.copy2(src_path, dst_path)
                                update_status(f"📄 Bijgewerkt: {file}")
                    
                    # Kopieer templates directory
                    templates_src = os.path.join(extract_dir, "templates")
                    templates_dst = os.path.join(os.getcwd(), "templates")
                    if os.path.exists(templates_src):
                        if os.path.exists(templates_dst):
                            shutil.rmtree(templates_dst)
                        shutil.copytree(templates_src, templates_dst)
                        update_status("📁 Templates bijgewerkt")
                    
                    # Cleanup
                    try:
                        os.remove(filepath)
                        shutil.rmtree(extract_dir)
                        update_status("🧹 Tijdelijke bestanden opgeruimd")
                    except:
                        pass
                    
                    update_status("✅ Update succesvol voltooid!")
                    progress_var.set("Update voltooid!")
                    
                    # Toon succes bericht
                    progress_window.after(2000, lambda: self.show_update_success(update_info['version']))
                    
                except Exception as e:
                    update_status(f"❌ Fout tijdens update: {str(e)}")
                    progress_var.set("Update mislukt")
                    progress_window.after(3000, progress_window.destroy)
            
            # Start update in thread
            import threading
            update_thread = threading.Thread(target=download_and_install)
            update_thread.daemon = True
            update_thread.start()
            
        except Exception as e:
            messagebox.showerror("Update Fout", f"Kon automatische update niet starten: {str(e)}")
    
    def show_update_success(self, new_version):
        """Toon succes bericht na update"""
        result = messagebox.askyesno(
            "✅ Update Succesvol", 
            f"De applicatie is succesvol bijgewerkt naar versie {new_version}!\n\n"
            "De applicatie moet opnieuw worden gestart om de wijzigingen toe te passen.\n\n"
            "Wil je de applicatie nu opnieuw starten?"
        )
        
        if result:
            # Herstart de applicatie
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            messagebox.showinfo(
                "Herstart", 
                "Start de applicatie handmatig opnieuw om de update toe te passen."
            ) 