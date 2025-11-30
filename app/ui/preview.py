import tkinter as tk
from tkinter import ttk
from app.core.renderer import render_markdown

import os
from typing import Callable, Optional

class PreviewPanel(ttk.Frame):
    def __init__(self, master, on_stats_change: Optional[Callable[[int, int], None]] = None):
        super().__init__(master)
        self.on_stats_change = on_stats_change
        self.current_file_path = None
        self.current_content = ""
        self.is_editing = False
        
        # Header
        self.header = ttk.Frame(self)
        self.header.pack(fill=tk.X, padx=5, pady=5)
        
        self.path_label = ttk.Label(self.header, text="", font=("Helvetica", 10, "italic"), foreground="#555")
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_edit = ttk.Button(self.header, text="📝", width=3, command=self.toggle_edit)
        self.btn_edit.pack(side=tk.RIGHT, padx=2)
        
        self.btn_copy = ttk.Button(self.header, text="📋", width=3, command=self.copy_to_clipboard)
        self.btn_copy.pack(side=tk.RIGHT, padx=2)
        
        # Text Area
        self.text_area = tk.Text(self, wrap=tk.WORD, padx=30, pady=30, borderwidth=0, highlightthickness=0, state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.text_area.bind("<KeyRelease>", self.on_text_change)

    def load_content(self, text: str, file_path: str = ""):
        self.current_content = text
        self.current_file_path = file_path
        self.path_label.config(text=file_path)
        self.is_editing = False
        self.btn_edit.config(text="📝") # Reset to edit icon
        
        self.render_view()
        self.update_stats()

    def render_view(self):
        if self.is_editing:
            # Edit Mode: Show raw text
            self.text_area.config(state=tk.NORMAL, font=("Courier New", 11))
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", self.current_content)
        else:
            # Preview Mode: Render Markdown
            render_markdown(self.text_area, self.current_content)

    def toggle_edit(self):
        if not self.current_file_path:
            return

        self.is_editing = not self.is_editing
        
        if self.is_editing:
            self.btn_edit.config(text="💾") # Show save/done icon (visual cue)
            self.render_view()
        else:
            # Saving is handled automatically on change, but let's ensure we capture the latest
            self.current_content = self.text_area.get("1.0", "end-1c")
            self.save_file()
            self.btn_edit.config(text="📝")
            self.render_view()

    def on_text_change(self, event=None):
        if self.is_editing:
            content = self.text_area.get("1.0", "end-1c")
            self.current_content = content
            self.update_stats()
            self.save_file()

    def save_file(self):
        if self.current_file_path and self.is_editing:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_content)
            except Exception as e:
                print(f"Error saving file: {e}")

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.current_content)
        self.update()

    def update_stats(self):
        if self.on_stats_change:
            lines = int(self.text_area.index('end-1c').split('.')[0])
            chars = len(self.current_content)
            self.on_stats_change(lines, chars)

    def scroll_view(self, direction: int):
        # direction: 1 for down, -1 for up
        self.text_area.yview_scroll(direction * 20, "units")
