import os
import subprocess
import sys
import shutil

APP_CODE = """#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import shutil

class ZorinDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Zorin Media Downloader")
        self.root.geometry("550x400")
        self.root.resizable(False, False)
        
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#1a73e8"
        self.card_color = "#2d2d2d"
        
        self.root.configure(bg=self.bg_color)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Sans", 10))
        self.style.configure("TProgressbar", thickness=15, troughcolor=self.card_color, background=self.accent_color)
        
        self.create_widgets()
        
    def create_widgets(self):
        header = tk.Label(self.root, text="💥 Zorin Media Downloader", font=("Sans", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=20)
        
        card = tk.Frame(self.root, bg=self.card_color, bd=0, highlightbackground="#3d3d3d", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        lbl_url = ttk.Label(card, text="Paste Media URL Link:", background=self.card_color)
        lbl_url.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.url_entry = tk.Entry(card, width=50, bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, bd=0, highlightbackground="#4d4d4d", highlightthickness=1, font=("Sans", 11))
        self.url_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        lbl_format = ttk.Label(card, text="Choose Output Media Format:", background=self.card_color)
        lbl_format.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.format_var = tk.StringVar(value="video")
        
        radio_frame = tk.Frame(card, bg=self.card_color)
        radio_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        formats = [("Video (Highest MP4)", "video"), ("Audio (High Extract MP3)", "audio"), ("Direct Graphic / Image File", "image")]
        for text, mode in formats:
            rb = tk.Radiobutton(radio_frame, text=text, variable=self.format_var, value=mode, bg=self.card_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.card_color, activeforeground=self.fg_color, font=("Sans", 10))
            rb.pack(side="left", padx=(0, 15))
            
        self.btn_download = tk.Button(card, text="Download Media Now", bg=self.accent_color, fg=self.fg_color, activebackground="#155cb4", activeforeground=self.fg_color, bd=0, font=("Sans", 11, "bold"), cursor="hand2", command=self.start_download_thread)
        self.btn_download.pack(fill="x", padx=15, pady=(5, 15))
        
        self.lbl_status = ttk.Label(card, text="System Ready.", background=self.card_color, font=("Sans", 9, "italic"))
        self.lbl_status.pack(anchor="w", padx=15)
        
        self.progress = ttk.Progressbar(card, mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=(5, 15))

    def update_status(self, text, progress_val=0):
        self.lbl_status.config(text=text)
        self.progress["value"] = progress_val
        self.root.update_idletasks()

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Empty Link", "Please input a web media link address first.")
            return
        
        self.btn_download.config(state="disabled")
        self.update_status("Initializing engine tasks...", 10)
        
        thread = threading.Thread(target=self.execute_download, args=(url, self.format_var.get()), daemon=True)
        thread.start()

    def execute_download(self, url, mode):
        output_dir = os.path.expanduser("~/Downloads/MediaDownloader")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            if mode == "image":
                self.update_status("Pulling direct asset file via curl...", 40)
                filename = url.split("/")[-1].split("?")[0]
                if not filename:
                    filename = "downloaded_asset.jpg"
                dest_path = os.path.join(output_dir, filename)
                
                cmd = ["curl", "-L", "-o", dest_path, url]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode != 0:
                    raise Exception(res.stderr)
            else:
                self.update_status(f"Parsing webpage streaming headers ({mode})...", 30)
                cmd = ["yt-dlp", "-P", output_dir]
                
                if mode == "audio":
                    cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
                else:
                    cmd.extend(["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"])
                    
                cmd.append(url)
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode != 0:
                    raise Exception(res.stderr)
            
            self.update_status("Download Complete!", 100)
            messagebox.showinfo("Success", f"Media files safely saved inside:\\n{output_dir}")
        except Exception as e:
            self.update_status("An error occurred during extraction.", 0)
            messagebox.showerror("Download Error", f"Extraction Engine failure details:\\n{str(e)}")
        finally:
            self.btn_download.config(state="normal")
            self.url_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZorinDownloader(root)
    root.mainloop()
"""

DESKTOP_ENTRY = """[Desktop Entry]
Version=1.0
Type=Application
Name=Zorin Media Downloader
Comment=Download video, audio, and images from anywhere
Exec={bin_path}
Icon=system-file-manager
Categories=Utility;Network;
Terminal=false
StartupNotify=true
"""

def install_system_dependencies():
    print("📦 Validating runtime environment structures on Zorin OS...")
    dependencies = ["curl", "ffmpeg", "python3-tk"]
    missing = []
    
    for dep in dependencies:
        if dep == "python3-tk":
            try:
                import tkinter
            except ImportError:
                missing.append(dep)
        elif not shutil.which(dep):
            missing.append(dep)
            
    if missing:
        print(f"⚠️  Missing system dependencies found: {', '.join(missing)}")
        print("🔧 Attempting automatic setup (Requires standard sudo authorization)...")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y"] + missing, check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install required system components. Verify internet connection and sudo rights.")
            sys.exit(1)
            
    if not shutil.which("yt-dlp"):
        print("🔗 Fetching specialized media extraction engine (yt-dlp)...")
        try:
            subprocess.run(["sudo", "curl", "-L", "https://github.com", "-o", "/usr/local/bin/yt-dlp"], check=True)
            subprocess.run(["sudo", "chmod", "a+rx", "/usr/local/bin/yt-dlp"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Critical tracking engine compilation failed. Please configure yt-dlp manually.")
            sys.exit(1)
            
    print("✅ System dependencies configured successfully.")

def build_application():
    print("📂 Mapping file system deployment structures...")
    bin_dir = os.path.expanduser("~/.local/bin")
    apps_dir = os.path.expanduser("~/.local/share/applications")
    
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(apps_dir, exist_ok=True)
    
    bin_path = os.path.join(bin_dir, "zorin-downloader")
    desktop_path = os.path.join(apps_dir, "zorin-downloader.desktop")
    
    with open(bin_path, "w") as f:
        f.write(APP_CODE)
    os.chmod(bin_path, 0o755)
    
    with open(desktop_path, "w") as f:
        f.write(DESKTOP_ENTRY.format(bin_path=bin_path))
    os.chmod(desktop_path, 0o755)
    
    print(f"🚀 Application deployed locally at: {bin_path}")
    print(f"🖥️  Desktop entry shortcut injected into system framework layout.")

if __name__ == "__main__":
    if os.geteuid() == 0:
        print("❌ Do not run this script as root/sudo directly. Run it as your normal user.")
        sys.exit(1)
        
    install_system_dependencies()
    build_application()
    print("\n🎉 SUCCESS: Zorin Media Downloader is installed completely!")
    print("👉 Press your keyboard's Super/Zorin Key, search for 'Zorin Media Downloader' and enjoy!")
