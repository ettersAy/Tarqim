import tkinter as tk
from tkinter import ttk, filedialog
import os
import time
from app.ui.sidebar import Sidebar
from app.ui.preview import PreviewPanel
from app.core.config import ConfigManager

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tarqim - Markdown Viewer")
        self.root.geometry("1000x700")
        self.sidebar_visible = True
        
        # Config
        self.config = ConfigManager.load_config()
        self.current_dir = self.config.get("last_dir", os.getcwd())
        if not os.path.exists(self.current_dir):
            self.current_dir = os.getcwd()

        # Theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Layout
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = Sidebar(self.paned, self.load_file, self.on_folder_change, self.current_dir)
        self.paned.add(self.sidebar, weight=1)
        
        # Preview
        self.preview = PreviewPanel(self.paned, self.update_stats)
        self.paned.add(self.preview, weight=4)
        
        # Status Bar Frame
        self.status_frame = ttk.Frame(root, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Sidebar Toggle
        self.btn_sidebar = ttk.Button(self.status_frame, text="◀ ☰", width=4, command=self.toggle_sidebar)
        self.btn_sidebar.pack(side=tk.LEFT)
        
        # Stats Label
        self.stats_var = tk.StringVar()
        self.stats_var.set("0 lines | 0 Chars")
        self.lbl_stats = ttk.Label(self.status_frame, textvariable=self.stats_var, anchor=tk.CENTER)
        self.lbl_stats.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Scroll Buttons
        self.btn_scroll_up = ttk.Button(self.status_frame, text="▲", width=3, command=lambda: self.preview.scroll_view(-1))
        self.btn_scroll_up.pack(side=tk.RIGHT)
        
        self.btn_scroll_down = ttk.Button(self.status_frame, text="▼", width=3, command=lambda: self.preview.scroll_view(1))
        self.btn_scroll_down.pack(side=tk.RIGHT)
        
        # Bindings
        root.bind("<Control-o>", lambda e: self.sidebar.browse_folder())
        root.bind("<Control-q>", lambda e: self.quit())
        
        # Save config on exit
        root.protocol("WM_DELETE_WINDOW", self.quit)

    def on_folder_change(self, new_path: str):
        self.current_dir = new_path
        self.save_state()

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.paned.forget(self.sidebar)
            self.btn_sidebar.config(text="☰ ▶")
        else:
            self.paned.insert(0, self.sidebar, weight=1)
            self.btn_sidebar.config(text="◀ ☰")
        self.sidebar_visible = not self.sidebar_visible

    def update_stats(self, lines: int, chars: int):
        self.stats_var.set(f"{lines} lines | {chars} Chars")

    def load_file(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            self.preview.load_content(text, path)
            self.root.title(f"Tarqim - {os.path.basename(path)}")
        except Exception as e:
            print(f"Error loading file: {e}")

    def save_state(self):
        config = ConfigManager.load_config()
        config["last_dir"] = self.current_dir
        ConfigManager.save_config(config)

    def quit(self):
        self.save_state()
        self.root.quit()
