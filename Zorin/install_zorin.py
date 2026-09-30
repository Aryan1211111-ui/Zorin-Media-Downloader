import os, subprocess, sys, shutil

APP_CODE = """#!/usr/bin/env python3
import os, sys, threading, subprocess
import tkinter as tk
from tkinter import ttk, messagebox

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
        
        formats = [("Video (MP4)", "video"), ("Audio (MP3)", "audio"), ("Direct Graphic / Image", "image")]
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
        threading.Thread(target=self.execute_download, args=(url, self.format_var.get()), daemon=True).start()

    def execute_download(self, url, mode):
        output_dir = os.path.expanduser("~/Downloads/MediaDownloader")
        os.makedirs(output_dir, exist_ok=True)
        try:
            if mode == "image":
                self.update_status("Pulling image via curl...", 50)
                filename = url.split("/")[-1].split("?")[0] or "downloaded_asset.jpg"
                dest_path = os.path.join(output_dir, filename)
                res = subprocess.run(["curl", "-L", "-o", dest_path, url], capture_output=True, text=True)
                if res.returncode != 0: raise Exception(res.stderr)
            else:
                self.update_status("Parsing streaming metadata...", 40)
                cmd = ["yt-dlp", "-P", output_dir]
                if mode == "audio":
                    cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
                else:
                    cmd.extend(["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"])
                cmd.append(url)
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode != 0: raise Exception(res.stderr)
            self.update_status("Download Complete!", 100)
            messagebox.showinfo("Success", f"Media saved inside: {output_dir}")
        except Exception as e:
            self.update_status("An error occurred.", 0)
            messagebox.showerror("Error", f"Engine details: {str(e)}")
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
Exec={bin_path}
Icon=system-file-manager
Categories=Utility;Network;
Terminal=false
"""

def setup():
    missing = [d for d in ["curl", "ffmpeg"] if not shutil.which(d)]
    try:
        import tkinter
    except ImportError:
        missing.append("python3-tk")
        
    if missing:
        print("📦 Adding system framework engines...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y"] + missing, check=True)
        
    if not shutil.which("yt-dlp"):
        print("🔗 Fetching parsing backend...")
        subprocess.run(["sudo", "curl", "-L", "https://github.com", "-o", "/usr/local/bin/yt-dlp"], check=True)
        subprocess.run(["sudo", "chmod", "a+rx", "/usr/local/bin/yt-dlp"], check=True)

    bin_dir = os.path.expanduser("~/.local/bin")
    apps_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(apps_dir, exist_ok=True)
    
    bp = os.path.join(bin_dir, "zorin-downloader")
    dp = os.path.join(apps_dir, "zorin-downloader.desktop")
    
    with open(bp, "w") as f: f.write(APP_CODE)
    os.chmod(bp, 0o755)
    with open(dp, "w") as f: f.write(DESKTOP_ENTRY.format(bin_path=bp))
    os.chmod(dp, 0o755)
    print("\n🎉 SUCCESS! Find 'Zorin Media Downloader' inside your Zorin Start Menu.")

if __name__ == "__main__":
    setup()
