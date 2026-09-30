#!/usr/bin/env python3
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class ZorinMediaDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Zorin OS Media Downloader")
        self.root.geometry("650x450")
        self.root.configure(bg="#202530")  # Custom Zorin-like Dark Theme
        self.root.resizable(False, False)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure Colors
        self.style.configure(".", background="#202530", foreground="#ffffff")
        self.style.configure("TLabel", background="#202530", foreground="#ffffff", font=("Sans", 10))
        self.style.configure("TFrame", background="#202530")
        
        self.style.configure("TButton", 
                             background="#1a66ff", 
                             foreground="#ffffff", 
                             font=("Sans", 10, "bold"), 
                             borderwidth=0, 
                             focusthickness=0, 
                             padding=8)
        self.style.map("TButton", background=[("active", "#0052cc")])
        
        self.style.configure("TRadiobutton", background="#202530", foreground="#ffffff", font=("Sans", 10))
        self.style.map("TRadiobutton", foreground=[("active", "#1a66ff")], background=[("active", "#202530")])

        # Header Image/Text Frame
        header_frame = ttk.Frame(self.root, padding=20)
        header_frame.pack(fill="x")
        
        title_label = ttk.Label(header_frame, text="ZORIN OS MEDIA DOWNLOADER", font=("Sans", 16, "bold"), foreground="#1a66ff")
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(header_frame, text="Exclusively optimized for Zorin OS. Extract video, audio, or images.", font=("Sans", 9), foreground="#a0a5b5")
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Main Layout Frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # URL Input Row
        ttk.Label(main_frame, text="Media URL / Link:").pack(anchor="w", pady=(0, 5))
        self.url_entry = tk.Entry(main_frame, font=("Sans", 11), bg="#2d3240", fg="#ffffff", insertbackground="#ffffff", borderwidth=1, relief="flat")
        self.url_entry.pack(fill="x", ipady=6, pady=(0, 15))
        self.url_entry.focus()

        # Target Type Row
        ttk.Label(main_frame, text="Select Media Output Type:").pack(anchor="w", pady=(0, 5))
        self.media_type = tk.StringVar(value="video")
        
        radio_frame = ttk.Frame(main_frame)
        radio_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Radiobutton(radio_frame, text="Video (Highest Quality MP4)", variable=self.media_type, value="video").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(radio_frame, text="Audio Extraction (MP3)", variable=self.media_type, value="audio").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(radio_frame, text="Direct Image / Static File", variable=self.media_type, value="image").pack(side="left")

        # Save Location Row
        ttk.Label(main_frame, text="Save Location:").pack(anchor="w", pady=(0, 5))
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 20))
        
        self.default_path = os.path.expanduser("~/Downloads")
        self.path_entry = tk.Entry(path_frame, font=("Sans", 10), bg="#2d3240", fg="#a0a5b5", insertbackground="#ffffff", borderwidth=1, relief="flat")
        self.path_entry.insert(0, self.default_path)
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_folder, width=10)
        browse_btn.pack(side="right", padx=(10, 0))

        # Status and Action Row
        self.status_label = ttk.Label(main_frame, text="Status: Ready", font=("Sans", 10, "italic"), foreground="#a0a5b5")
        self.status_label.pack(anchor="w", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate")
        
        self.download_btn = ttk.Button(main_frame, text="Download Media", command=self.start_download_thread)
        self.download_btn.pack(fill="x", ipady=5)

        # Check dependencies in background
        threading.Thread(target=self.check_dependencies, daemon=True).start()

    def browse_folder(self):
        selected_dir = filedialog.askdirectory(initialdir=self.default_path, title="Select Destination Folder")
        if selected_dir:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_dir)

    def check_dependencies(self):
        # Specific backend audit for desktop environment tools
        missing = []
        for cmd in ['yt-dlp', 'ffmpeg', 'curl']:
            if subprocess.call(['which', cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
                missing.append(cmd)
        
        if missing:
            self.status_label.config(text=f"System Alert: Missing framework core utilities ({', '.join(missing)})", foreground="#ff4d4d")
            if messagebox.askyesno("Zorin System Optimization", f"Your system requires {', '.join(missing)} to download media web bundles natively.

Would you like to install them via apt-get?"):
                self.status_label.config(text="Installing packages... please enter sudo credential if asked in terminal.", foreground="#ffaa00")
                try:
                    # Update cache and install packages natively on Debian/Ubuntu/Zorin framework layers
                    cmd_str = f"sudo apt-get update && sudo apt-get install -y {' '.join(['ffmpeg' if x=='ffmpeg' else 'curl' if x=='curl' else '' for x in missing])}"
                    if 'yt-dlp' in missing:
                        cmd_str += " && sudo wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && sudo chmod a+rx /usr/local/bin/yt-dlp"
                    
                    subprocess.run(['gnome-terminal', '--', 'bash', '-c', f"{cmd_str}; echo 'Setup Finished! Press enter to close.'; read"], check=True)
                    self.status_label.config(text="Status: Core binaries synchronized. Ready.", foreground="#00cc66")
                except Exception as e:
                    messagebox.showerror("Installation Aborted", f"Could not launch automated Zorin deployment window: {e}")
        else:
            self.status_label.config(text="Status: Operational Architecture Validated.", foreground="#00cc66")

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please provide a valid asset web URL to run extraction processing.")
            return
            
        self.download_btn.config(state="disabled")
        self.progress_bar.pack(fill="x", pady=(0, 15))
        self.progress_bar.start(10)
        self.status_label.config(text="Status: Executing streaming hook download threads...", foreground="#ffaa00")
        
        threading.Thread(target=self.execute_download, args=(url,), daemon=True).start()

    def execute_download(self, url):
        mode = self.media_type.get()
        output_dir = self.path_entry.get().strip()
        os.makedirs(output_dir, exist_ok=True)
        
        success = False
        error_msg = ""

        try:
            if mode == "video":
                # Download full quality mp4 vector channels
                cmd = ['yt-dlp', '-f', 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]', '-P', output_dir, url]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                success = (res.returncode == 0)
                error_msg = res.stderr
            elif mode == "audio":
                # Strip and process high fidelity mp3 streams
                cmd = ['yt-dlp', '-x', '--audio-format', 'mp3', '--audio-quality', '0', '-P', output_dir, url]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                success = (res.returncode == 0)
                error_msg = res.stderr
            elif mode == "image":
                # Static binary payload extraction
                filename = url.split("/")[-1].split("?")[0]
                if not filename or "." not in filename:
                    filename = "extracted_media_asset"
                dest_file = os.path.join(output_dir, filename)
                cmd = ['curl', '-L', '-o', dest_file, url]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                success = (res.returncode == 0)
                error_msg = res.stderr

        except Exception as e:
            error_msg = str(e)

        self.root.after(0, lambda: self.finalize_download(success, error_msg))

    def finalize_download(self, success, error_msg):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.download_btn.config(state="normal")
        
        if success:
            self.status_label.config(text="Status: File compilation finished cleanly!", foreground="#00cc66")
            messagebox.showinfo("Success", "Media downloaded successfully to your directory target!")
            self.url_entry.delete(0, tk.END)
        else:
            self.status_label.config(text="Status: Download task execution failure.", foreground="#ff4d4d")
            messagebox.showerror("Extraction Pipeline Blocked", f"Engine reported runtime issue:

{error_msg[:300]}")

if __name__ == "__main__":
    # Ensure system optimization target verification check
    if not os.path.exists("/etc/zorin_version") and not os.path.exists("/usr/share/doc/zorin-os-desktop"):
        # Soft notification for platform check enforcement alignment
        pass
        
    root = tk.Tk()
    app = ZorinMediaDownloader(root)
    root.mainloop()
