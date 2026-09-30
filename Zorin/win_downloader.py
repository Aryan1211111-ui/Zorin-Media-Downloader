import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

class WindowsDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Media Downloader")
        self.root.geometry("550x400")
        self.root.resizable(False, False)
        
        # Dark Theme Palette
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#0078d4" # Windows Blue
        self.card_color = "#2d2d2d"
        
        self.root.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Segoe UI", 10))
        self.style.configure("TProgressbar", thickness=15, troughcolor=self.card_color, background=self.accent_color)
        self.create_widgets()
        
    def create_widgets(self):
        header = tk.Label(self.root, text="📥 Universal Media Downloader", font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=20)
        
        card = tk.Frame(self.root, bg=self.card_color, bd=0, highlightbackground="#3d3d3d", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        lbl_url = ttk.Label(card, text="Paste Media URL Link:", background=self.card_color)
        lbl_url.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.url_entry = tk.Entry(card, width=50, bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, bd=0, highlightbackground="#4d4d4d", highlightthickness=1, font=("Segoe UI", 11))
        self.url_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        lbl_format = ttk.Label(card, text="Choose Output Media Format:", background=self.card_color)
        lbl_format.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.format_var = tk.StringVar(value="video")
        radio_frame = tk.Frame(card, bg=self.card_color)
        radio_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        formats = [("Video (MP4)", "video"), ("Audio (MP3)", "audio"), ("Direct Graphic / Image", "image")]
        for text, mode in formats:
            rb = tk.Radiobutton(radio_frame, text=text, variable=self.format_var, value=mode, bg=self.card_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.card_color, activeforeground=self.fg_color, font=("Segoe UI", 10))
            rb.pack(side="left", padx=(0, 15))
            
        self.btn_download = tk.Button(card, text="Download Media Now", bg=self.accent_color, fg=self.fg_color, activebackground="#005a9e", activeforeground=self.fg_color, bd=0, font=("Segoe UI", 11, "bold"), cursor="hand2", command=self.start_download_thread)
        self.btn_download.pack(fill="x", padx=15, pady=(5, 15))
        
        self.lbl_status = ttk.Label(card, text="System Ready.", background=self.card_color, font=("Segoe UI", 9, "italic"))
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
        self.update_status("Initializing download engines...", 10)
        threading.Thread(target=self.execute_download, args=(url, self.format_var.get()), daemon=True).start()

    def execute_download(self, url, mode):
        # Default destination path to User's Windows Downloads directory
        output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader")
        os.makedirs(output_dir, exist_ok=True)
        try:
            if mode == "image":
                self.update_status("Downloading direct image asset...", 50)
                filename = url.split("/")[-1].split("?")[0] or "downloaded_asset.jpg"
                dest_path = os.path.join(output_dir, filename)
                # Windows built-in curl execution
                res = subprocess.run(f'curl -L -o "{dest_path}" "{url}"', shell=True, capture_output=True, text=True)
                if res.returncode != 0: raise Exception(res.stderr)
            else:
                self.update_status("Extracting stream pipelines via yt-dlp...", 40)
                # Calls the yt-dlp execution command directly
                cmd = f'yt-dlp -P "{output_dir}"'
                if mode == "audio":
                    cmd += " -x --audio-format mp3 --audio-quality 0"
                else:
                    cmd += " -f \"bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]\""
                cmd += f' "{url}"'
                
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode != 0: raise Exception(res.stderr)
                
            self.update_status("Download Complete!", 100)
            messagebox.showinfo("Success", f"Media files successfully saved to folder:\n{output_dir}")
        except Exception as e:
            self.update_status("An engine compilation error occurred.", 0)
            messagebox.showerror("Error", f"Download Engine Failure Details:\n{str(e)}\n\nNote: Ensure yt-dlp.exe and ffmpeg.exe are placed on your system PATH variables.")
        finally:
            self.btn_download.config(state="normal")
            self.url_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsDownloader(root)
    root.mainloop()

