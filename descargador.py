import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import yt_dlp
import os

class ZorviDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("ZorviDownloader - v1.0.0")
        self.root.geometry("600x620")
        self.root.resizable(False, False)
        
        # Paleta de Colores Oficial (Morado & Negro)
        self.bg_color = "#09070D"
        self.card_bg = "#130f1c"
        self.accent_color = "#7138B8"
        self.accent_hover = "#8b4ee0"
        self.text_color = "#f0ecf7"
        self.subtext_color = "#9f93b8"
        
        self.download_folder = os.path.expanduser("~/Descargas")
        self.root.configure(bg=self.bg_color)
        
        # Banderas de control
        self.is_paused = False
        self.is_cancelled = False
        self.is_downloading = False

        self.create_menu()
        self.create_widgets()
        self.create_context_menu()
        self.bind_shortcuts()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.card_bg, fg=self.text_color, activebackground=self.accent_color, activeforeground="white")
        
        options_menu = tk.Menu(menubar, tearoff=0, bg=self.card_bg, fg=self.text_color, activebackground=self.accent_color)
        options_menu.add_command(label="Cambiar Carpeta de Descargas", command=self.select_folder)
        options_menu.add_separator()
        options_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.card_bg, fg=self.text_color, activebackground=self.accent_color)
        help_menu.add_command(label="Acerca de ZorviDownloader", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        title_label = tk.Label(
            self.root, text="ZorviDownloader", font=("Segoe UI", 22, "bold"),
            bg=self.bg_color, fg=self.accent_color
        )
        title_label.pack(pady=(15, 2))
        
        subtitle_label = tk.Label(
            self.root, text="Gestor de descargas nativo de Zorvi Linux • v1.0.0",
            font=("Segoe UI", 9), bg=self.bg_color, fg=self.subtext_color
        )
        subtitle_label.pack(pady=(0, 15))

        card = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=15)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        url_label = tk.Label(card, text="Enlace (YouTube, Facebook Reels, IG, etc.):", font=("Segoe UI", 10, "bold"), bg=self.card_bg, fg=self.text_color)
        url_label.pack(anchor="w", pady=(0, 5))
        
        entry_frame = tk.Frame(card, bg=self.card_bg)
        entry_frame.pack(fill="x", pady=(0, 10))
        
        self.url_entry = tk.Entry(entry_frame, font=("Segoe UI", 10), bg="#1e182b", fg=self.text_color, insertbackground="white", relief="flat")
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 5))
        
        btn_preview = tk.Button(entry_frame, text="👁️ Ver", font=("Segoe UI", 9, "bold"), bg=self.accent_color, fg="white", relief="flat", command=self.fetch_preview)
        btn_preview.pack(side="right", ipady=3, ipadx=5)

        self.preview_frame = tk.Frame(card, bg="#1a1426", height=60)
        self.preview_frame.pack(fill="x", pady=(0, 10))
        
        self.preview_label = tk.Label(self.preview_frame, text="Pega un enlace y presiona '👁️ Ver' para cargar la vista previa", font=("Segoe UI", 8), bg="#1a1426", fg=self.subtext_color)
        self.preview_label.pack(side="left", padx=10, pady=5)

        format_label = tk.Label(card, text="Formato de Salida:", font=("Segoe UI", 10, "bold"), bg=self.card_bg, fg=self.text_color)
        format_label.pack(anchor="w", pady=(0, 5))
        
        self.format_var = tk.StringVar(value="mp4")
        
        format_grid = tk.Frame(card, bg=self.card_bg)
        format_grid.pack(anchor="w", pady=(0, 10))
        
        formats = [
            ("Video MP4", "mp4"), ("Video WEBM", "webm"),
            ("Audio MP3", "mp3"), ("Audio M4A", "m4a"), ("Audio FLAC", "flac")
        ]
        
        for text, mode in formats:
            rb = tk.Radiobutton(
                format_grid, text=text, variable=self.format_var, value=mode,
                bg=self.card_bg, fg=self.text_color, selectcolor=self.bg_color,
                activebackground=self.card_bg, activeforeground=self.accent_color
            )
            rb.pack(side="left", padx=(0, 10))

        self.playlist_var = tk.BooleanVar(value=False)
        chk_playlist = tk.Checkbutton(
            card, text="Descargar Playlist Completa (si aplica)",
            variable=self.playlist_var, bg=self.card_bg, fg=self.text_color,
            selectcolor=self.bg_color, activebackground=self.card_bg, activeforeground=self.accent_color
        )
        chk_playlist.pack(anchor="w", pady=(0, 8))

        folder_frame = tk.Frame(card, bg=self.card_bg)
        folder_frame.pack(fill="x", pady=(0, 12))
        
        self.folder_label = tk.Label(folder_frame, text=f"Guardar en: {self.shorten_path(self.download_folder)}", font=("Segoe UI", 8), bg=self.card_bg, fg=self.subtext_color)
        self.folder_label.pack(side="left")
        
        btn_folder = tk.Button(folder_frame, text="Cambiar", font=("Segoe UI", 8), bg="#2d2242", fg="white", relief="flat", command=self.select_folder)
        btn_folder.pack(side="right")

        self.download_btn = tk.Button(
            card, text="Descargar Ahora", font=("Segoe UI", 11, "bold"),
            bg=self.accent_color, fg="white", activebackground=self.accent_hover, activeforeground="white",
            relief="flat", cursor="hand2", command=self.start_download_thread
        )
        self.download_btn.pack(fill="x", ipady=8, pady=(0, 8))

        control_frame = tk.Frame(card, bg=self.card_bg)
        control_frame.pack(fill="x", pady=(0, 8))

        self.pause_btn = tk.Button(
            control_frame, text="Pausar", font=("Segoe UI", 9, "bold"),
            bg="#44335c", fg="white", state="disabled", relief="flat", command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.cancel_btn = tk.Button(
            control_frame, text="Cancelar", font=("Segoe UI", 9, "bold"),
            bg="#731f2f", fg="white", state="disabled", relief="flat", command=self.cancel_download
        )
        self.cancel_btn.pack(side="right", expand=True, fill="x", padx=(4, 0))

        self.status_label = tk.Label(card, text="Listo para descargar", font=("Segoe UI", 9), bg=self.card_bg, fg=self.subtext_color)
        self.status_label.pack(anchor="center", pady=(0, 5))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar", thickness=10, troughcolor='#1e182b', background=self.accent_color)
        
        self.progress_bar = ttk.Progressbar(card, style="Custom.Horizontal.TProgressbar", mode="determinate")
        self.progress_bar.pack(fill="x")

    def bind_shortcuts(self):
        self.url_entry.bind("<Control-a>", self.select_all_text)
        self.url_entry.bind("<Control-A>", self.select_all_text)

    def select_all_text(self, event=None):
        self.url_entry.select_range(0, tk.END)
        self.url_entry.icursor(tk.END)
        return "break"

    def shorten_path(self, path):
        return path if len(path) < 35 else "..." + path[-32:]

    def select_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.download_folder)
        if chosen:
            self.download_folder = chosen
            self.folder_label.config(text=f"Guardar en: {self.shorten_path(self.download_folder)}")

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#1e182b", fg="white", activebackground=self.accent_color, activeforeground="white")
        self.context_menu.add_command(label="Cortar", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copiar", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Pegar", command=lambda: self.url_entry.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Seleccionar Todo (Ctrl+A)", command=self.select_all_text)
        self.context_menu.add_command(label="Limpiar", command=lambda: self.url_entry.delete(0, tk.END))
        
        self.url_entry.bind("<Button-3>", lambda e: self.context_menu.tk_popup(e.x_root, e.y_root))

    def fetch_preview(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Atención", "Pega un enlace antes de ver la vista previa.")
            return
        
        self.preview_label.config(text="Cargando datos del enlace...", fg=self.accent_color)
        threading.Thread(target=self._get_preview_info, args=(url,), daemon=True).start()

    def _get_preview_info(self, url):
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Sin título')
                uploader = info.get('uploader', info.get('extractor', 'Desconocido'))
                
                txt = f"📌 {title[:45]}...\n👤 {uploader}"
                self.root.after(0, self.preview_label.config, {"text": txt, "fg": self.text_color})
        except Exception:
            self.root.after(0, self.preview_label.config, {"text": "No se pudo cargar la vista previa de este enlace.", "fg": "#F44336"})

    def show_about(self):
        messagebox.showinfo(
            "Acerca de ZorviDownloader",
            "ZorviDownloader v1.0.0\n\n"
            "Aplicación nativa para la distribución Zorvi Linux.\n"
            "Diseñada para descargar multimedia de forma limpia, rápida y sin anuncios.\n\n"
            "Desarrollada con Python, Tkinter y yt-dlp."
        )

    def toggle_pause(self):
        if not self.is_downloading:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="Reanudar", bg="#2196F3")
            self.status_label.config(text="Pausado (se detendrá tras el archivo actual)", fg="#FFC107")
        else:
            self.pause_btn.config(text="Pausar", bg="#44335c")
            self.status_label.config(text="Reanudando descarga...", fg=self.accent_color)

    def cancel_download(self):
        if self.is_downloading:
            self.is_cancelled = True
            self.status_label.config(text="Cancelando descarga...", fg="#F44336")

    def progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("CANCELADO")
        while self.is_paused:
            if self.is_cancelled:
                raise Exception("CANCELADO")

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            p_idx = d.get('info_dict', {}).get('playlist_index')
            p_cnt = d.get('info_dict', {}).get('playlist_count')
            prefix = f"[{p_idx}/{p_cnt}] " if p_idx and p_cnt else ""

            if total > 0:
                pct = (downloaded / total) * 100
                self.progress_bar['value'] = pct
                speed = d.get('_speed_str', 'N/A').strip()
                eta = d.get('_eta_str', 'N/A').strip()
                
                txt = f"{prefix}Descargando: {pct:.1f}% ({speed}) - ETA: {eta}"
                self.root.after(0, self.status_label.config, {"text": txt, "fg": self.accent_color})
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.root.after(0, self.status_label.config, {"text": "Procesando/Convirtiendo...", "fg": "#FFC107"})

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Atención", "Por favor ingresa un enlace válido.")
            return
            
        self.is_downloading = True
        self.is_paused = False
        self.is_cancelled = False
        
        self.download_btn.config(state="disabled", bg="#332247")
        self.pause_btn.config(state="normal", text="Pausar", bg="#44335c")
        self.cancel_btn.config(state="normal", bg="#731f2f")
        
        self.progress_bar['value'] = 0
        self.status_label.config(text="Iniciando descarga...", fg=self.accent_color)
        
        threading.Thread(target=self.download_content, args=(url,), daemon=True).start()

    def download_content(self, url):
        fmt = self.format_var.get()
        allow_playlist = self.playlist_var.get()
        
        ydl_opts = {
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
            'noplaylist': not allow_playlist
        }
        
        if fmt in ['mp3', 'm4a', 'flac']:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': '320' if fmt == 'mp3' else '0',
                }],
            })
        elif fmt == 'webm':
            ydl_opts.update({'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]'})
        else:
            ydl_opts.update({'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, self.on_success)
        except Exception as e:
            if "CANCELADO" in str(e):
                self.root.after(0, self.on_cancel)
            else:
                self.root.after(0, self.on_error, str(e))

    def reset_buttons(self):
        self.is_downloading = False
        self.download_btn.config(state="normal", bg=self.accent_color)
        self.pause_btn.config(state="disabled", text="Pausar", bg="#44335c")
        self.cancel_btn.config(state="disabled", bg="#731f2f")

    def on_success(self):
        self.reset_buttons()
        self.status_label.config(text="¡Descarga completada!", fg="#4CAF50")
        self.url_entry.delete(0, tk.END)
        messagebox.showinfo("Éxito", f"Archivo(s) guardado(s) en:\n{self.download_folder}")

    def on_cancel(self):
        self.reset_buttons()
        self.progress_bar['value'] = 0
        self.status_label.config(text="Descarga cancelada.", fg="#F44336")

    def on_error(self, error_msg):
        self.reset_buttons()
        self.status_label.config(text="Error durante la descarga", fg="#F44336")
        messagebox.showerror("Error", f"No se pudo descargar:\n{error_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ZorviDownloader(root)
    root.mainloop()

