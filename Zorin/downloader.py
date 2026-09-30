#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk

class MediaDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Media Downloader")
        self.root.geometry("650x450")
        self.root.resizable(True, True)
        
        # Colors & Theme (Modern Dark Aesthetic matching Zorin OS Dark styling)
        self.bg_color = "#1e1e24"
        self.fg_color = "#ffffff"
        self.accent_color = "#3574f2" # Zorin blue
        self.card_bg = "#2a2a32"
        self.btn_success = "#2da44e"
        
        self.root.configure(bg=self.bg_color)
        
        # Download Directory setup
        self.download_dir = os.path.expanduser("~/Downloads/MediaDownloader")
        os.makedirs(self.download_dir, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Global Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=20, troughcolor=self.card_bg, background=self.accent_color)
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.bg_color, pady=15)
        header_frame.pack(fill="x")
        
        title_lbl = tk.Label(header_frame, text="Universal Media Downloader", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.fg_color)
        title_lbl.pack()
        
        subtitle_lbl = tk.Label(header_frame, text="Download Video, Audio, or Images seamlessly", font=("Helvetica", 10), bg=self.bg_color, fg="#8a8a93")
        subtitle_lbl.pack()

        # Main Input Card
        card = tk.Frame(self.root, bg=self.card_bg, bd=0, highlightbackground="#3a3a42", highlightthickness=1, padx=20, pady=20)
        card.pack(fill="both", expand=True, padx=20, pady=10)
        
        # URL Input
        url_lbl = tk.Label(card, text="Paste URL Link Here:", font=("Helvetica", 11, "bold"), bg=self.card_bg, fg=self.fg_color)
        url_lbl.pack(anchor="w", pady=(0, 5))
        
        self.url_entry = tk.Entry(card, font=("Helvetica", 11), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, bd=0, highlightthickness=1, highlightbackground="#4a4a52", highlightcolor=self.accent_color)
        self.url_entry.pack(fill="x", ipady=8, pady=(0, 15))
        self.url_entry.focus()
        
        # Format Options Selection
        format_lbl = tk.Label(card, text="Select Download Type Target:", font=("Helvetica", 11, "bold"), bg=self.card_bg, fg=self.fg_color)
        format_lbl.pack(anchor="w", pady=(0, 5))
        
        self.media_type = tk.StringVar(value="video")
        
        radio_frame = tk.Frame(card, bg=self.card_bg)
        radio_frame.pack(fill="x", pady=(0, 20))
        
        radios = [
            ("Video (Highest Quality)", "video"),
            ("Audio Only (MP3)", "audio"),
            ("Static Image / File", "image")
        ]
        
        for text, val in radios:
            r = tk.Radiobutton(radio_frame, text=text, value=val, variable=self.media_type, bg=self.card_bg, fg=self.fg_color, selectcolor=self.card_bg, activebackground=self.card_bg, activeforeground=self.fg_color, font=("Helvetica", 10))
            r.pack(side="left", padx=(0, 20))

        # Action Button
        self.dl_button = tk.Button(card, text="Start Download", font=("Helvetica", 12, "bold"), bg=self.accent_color, fg=self.fg_color, activebackground="#2152bd", activeforeground=self.fg_color, bd=0, cursor="hand2", command=self.start_download_thread)
        self.dl_button.pack(fill="x", ipady=10, pady=(0, 15))
        
        # Progress Tracking UI
        self.progress_lbl = tk.Label(card, text="Status: Idle", font=("Helvetica", 10), bg=self.card_bg, fg="#a0a0a8")
        self.progress_lbl.pack(anchor="w", pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(card, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill="x")
        
        # Footer Location Notice
        footer_lbl = tk.Label(self.root, text=f"Saving files to: {self.download_dir}", font=("Helvetica", 9), bg=self.bg_color, fg="#6a6a72", pady=10)
        footer_lbl.pack()

    def update_status(self, text, progress_val=None, color=None):
        self.progress_lbl.config(text=f"Status: {text}")
        if color:
            self.progress_lbl.config(fg=color)
        if progress_val is not None:
            self.progress_bar['value'] = progress_val
        self.root.update_idletasks()

    def check_dependencies(self):
        # Quick fallback installation alert if tools are missing natively
        missing = []
        for cmd in ["yt-dlp", "ffmpeg", "curl"]:
            if subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
                missing.append(cmd)
        
        if missing:
            self.update_status(f"Missing core packages: {', '.join(missing)}. Auto-fixing via apt...", color=self.accent_color)
            try:
                # Prompting user terminal auth for dependencies if required natively
                messagebox.showinfo("System Setup", f"This downloader requires system packages: {missing}. Click OK to open setup installation window via apt.")
                subprocess.run(["sudo", "apt", "update"], check=True)
                if "ffmpeg" in missing or "curl" in missing:
                    subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg", "curl"], check=True)
                if "yt-dlp" in missing:
                    # Download latest yt-dlp binary directly to handle rapid web updates safely
                    subprocess.run(["sudo", "curl", "-L", "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp", "-o", "/usr/local/bin/yt-dlp"], check=True)
                    subprocess.run(["sudo", "chmod", "a+rx", "/usr/local/bin/yt-dlp"], check=True)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed installing system backends: {e}. Run 'sudo apt install ffmpeg curl' manually.")
                return False
        return True

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Empty URL", "Please enter a valid URL link before starting.")
            return
            
        self.dl_button.config(state="disabled", bg="#4a4a52")
        self.update_status("Initializing...", progress_val=10, color=self.accent_color)
        
        # Fire backend process outside the Tkinter main UI thread to prevent UI freezing
        download_thread = threading.Thread(target=self.execute_download, args=(url, self.media_type.get()))
        download_thread.daemon = True
        download_thread.start()

    def execute_download(self, url, mode):
        if not self.check_dependencies():
            self.root.after(0, self.reset_button)
            return

        self.root.after(0, lambda: self.update_status("Processing data stream...", progress_val=30))
        
        try:
            if mode == "video":
                # Download Best Video merged with Best Audio natively
                cmd = ["yt-dlp", "-f", "bv*+ba/b", "--merge-output-format", "mp4", "-P", self.download_dir, url]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                
            elif mode == "audio":
                # Stream extract to high fidelity MP3 format
                cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-P", self.download_dir, url]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                
            elif mode == "image":
                # Fetch static files or image links directly via Curl
                filename = url.split("/")[-1].split("?")[0]
                if not filename or len(filename) > 50: 
                    filename = "downloaded_image.jpg"
                output_path = os.path.join(self.download_dir, filename)
                
                cmd = ["curl", "-L", "-s", "-o", output_path, url]
                subprocess.run(cmd, check=True)

            self.root.after(0, lambda: self.update_status("Download Complete successfully!", progress_val=100, color=self.btn_success))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Media successfully saved to:\n{self.download_dir}"))
            self.root.after(0, lambda: self.url_entry.delete(0, tk.END))
            
        except subprocess.CalledProcessError as e:
            self.root.after(0, lambda: self.update_status("Failed to process resource.", progress_val=0, color="#cf222e"))
            self.root.after(0, lambda: messagebox.showerror("Download Error", "The engine could not parse this link. Please check if the source URL is restricted or down."))
        except Exception as e:
            self.root.after(0, lambda: self.update_status("An unexpected error occurred.", progress_val=0, color="#cf222e"))
            self.root.after(0, lambda: messagebox.showerror("System Error", str(e)))
        finally:
            self.root.after(0, self.reset_button)

    def reset_button(self):
        self.dl_button.config(state="normal", bg=self.accent_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaDownloaderUI(root)
    root.mainloop()
