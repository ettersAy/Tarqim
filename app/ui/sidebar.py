import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Callable, Optional
from app.core.config import ConfigManager

class Sidebar(ttk.Frame):
    def __init__(self, master, on_file_select: Callable[[str], None], on_folder_change: Callable[[str], None], initial_path: str):
        super().__init__(master, width=250)
        self.on_file_select = on_file_select
        self.on_folder_change = on_folder_change
        self.current_path = initial_path
        
        # --- Pinned Section ---
        self.pinned_frame = ttk.Frame(self)
        self.pinned_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Header
        pinned_header = ttk.Frame(self.pinned_frame)
        pinned_header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pinned_header, text="Pinned", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        ttk.Button(pinned_header, text="➕", width=3, command=self.add_pinned).pack(side=tk.RIGHT)
        
        # List
        self.pinned_list = tk.Listbox(self.pinned_frame, height=5, borderwidth=0, highlightthickness=0, bg="#f5f5f5", activestyle="none", font=("Helvetica", 10))
        self.pinned_list.pack(fill=tk.X, padx=5)
        self.pinned_list.bind("<<ListboxSelect>>", self.on_pinned_select)
        self.refresh_pinned()

        # --- Explorer Section ---
        self.explorer_frame = ttk.Frame(self)
        self.explorer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        explorer_header = ttk.Frame(self.explorer_frame)
        explorer_header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(explorer_header, text="Explorer", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        ttk.Button(explorer_header, text="📂", width=3, command=self.browse_folder).pack(side=tk.RIGHT)

        # Treeview
        self.tree = ttk.Treeview(self.explorer_frame, show="tree")
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(self.explorer_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        
        self.create_context_menus()
        self.populate_root(initial_path)

    def refresh_pinned(self):
        self.pinned_list.delete(0, tk.END)
        files = ConfigManager.get_pinned_files()
        for f in files:
            self.pinned_list.insert(tk.END, f" {os.path.basename(f)}")
            
    def add_pinned(self):
        path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md *.markdown"), ("All Files", "*.*")])
        if path:
            ConfigManager.add_pinned_file(path)
            self.refresh_pinned()

    def on_pinned_select(self, event):
        selection = self.pinned_list.curselection()
        if selection:
            index = selection[0]
            files = ConfigManager.get_pinned_files()
            if index < len(files):
                path = files[index]
                if os.path.exists(path):
                    self.on_file_select(path)
                    # Deselect tree
                    if self.tree.selection():
                        self.tree.selection_remove(self.tree.selection())

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_path)
        if folder:
            self.current_path = folder
            self.populate_root(folder)
            self.on_folder_change(folder)

    def populate_root(self, path: str):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        root_text = os.path.basename(path) or path
        root_node = self.tree.insert("", "end", text=root_text, open=True, values=[path])
        self.populate_node(root_node, path)

    def populate_node(self, parent_id, path):
        children = self.tree.get_children(parent_id)
        if children:
            self.tree.delete(*children)
            
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for p in items:
                abspath = os.path.join(path, p)
                isdir = os.path.isdir(abspath)
                
                if not isdir and not p.lower().endswith(('.md', '.markdown')):
                    continue
                
                oid = self.tree.insert(parent_id, "end", text=p, open=False, values=[abspath])
                
                if isdir:
                    self.tree.insert(oid, "end", text="dummy")
                    
        except PermissionError:
            pass
        except Exception as e:
            print(f"Error reading {path}: {e}")

    def on_tree_open(self, event):
        selected = self.tree.selection()
        if not selected: return
        item_id = selected[0]
        item = self.tree.item(item_id)
        path = item['values'][0]
        
        if os.path.isdir(path):
            self.populate_node(item_id, path)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        item_id = selected[0]
        item = self.tree.item(item_id)
        
        if 'values' in item and item['values']:
            path = item['values'][0]
            if os.path.isfile(path):
                self.on_file_select(path)
                # Deselect pinned list
                self.pinned_list.selection_clear(0, tk.END)

    # --- Context Menu Logic ---
    def create_context_menus(self):
        # Pinned List Menu
        self.pinned_menu = tk.Menu(self, tearoff=0)
        self.pinned_menu.add_command(label="Move Up", command=lambda: self.move_selected_list_item('up'))
        self.pinned_menu.add_command(label="Move Down", command=lambda: self.move_selected_list_item('down'))
        self.pinned_menu.add_separator()
        self.pinned_menu.add_command(label="Unpin", command=self.unpin_selected_list_item)
        self.pinned_list.bind("<Button-3>", self.show_pinned_menu)
        
        # Tree Menu
        self.tree_menu = tk.Menu(self, tearoff=0)
        self.tree.bind("<Button-3>", self.show_tree_menu)

        # Drag and Drop for Pinned List
        self.pinned_list.bind('<ButtonPress-1>', self.on_drag_start)
        self.pinned_list.bind('<B1-Motion>', self.on_drag_motion)
        self.pinned_list.bind('<ButtonRelease-1>', self.on_drop)

    def show_pinned_menu(self, event):
        # Select item under cursor
        index = self.pinned_list.nearest(event.y)
        if index >= 0:
            self.pinned_list.selection_clear(0, tk.END)
            self.pinned_list.selection_set(index)
            self.pinned_list.activate(index)
            self.pinned_menu.post(event.x_root, event.y_root)

    def move_selected_list_item(self, direction):
        selection = self.pinned_list.curselection()
        if selection:
            index = selection[0]
            files = ConfigManager.get_pinned_files()
            if index < len(files):
                path = files[index]
                ConfigManager.move_pinned_file(path, direction)
                self.refresh_pinned()
                
                # Reselect the moved item
                new_index = index
                if direction == 'up' and index > 0:
                    new_index = index - 1
                elif direction == 'down' and index < len(files) - 1:
                    new_index = index + 1
                
                self.pinned_list.selection_set(new_index)
                self.pinned_list.activate(new_index)

    def unpin_selected_list_item(self):
        selection = self.pinned_list.curselection()
        if selection:
            index = selection[0]
            files = ConfigManager.get_pinned_files()
            if index < len(files):
                path = files[index]
                ConfigManager.remove_pinned_file(path)
                self.refresh_pinned()

    def show_tree_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            item = self.tree.item(item_id)
            if 'values' in item and item['values']:
                path = item['values'][0]
                if os.path.isfile(path):
                    # Rebuild menu based on state
                    self.tree_menu.delete(0, tk.END)
                    if ConfigManager.is_pinned(path):
                        self.tree_menu.add_command(label="Unpin", command=lambda: self.toggle_pin_tree(path, False))
                    else:
                        self.tree_menu.add_command(label="Pin", command=lambda: self.toggle_pin_tree(path, True))
                    self.tree_menu.post(event.x_root, event.y_root)

    def toggle_pin_tree(self, path, pin):
        if pin:
            ConfigManager.add_pinned_file(path)
        else:
            ConfigManager.remove_pinned_file(path)
        self.refresh_pinned()

    # --- Drag and Drop Logic ---
    def on_drag_start(self, event):
        self.drag_start_index = self.pinned_list.nearest(event.y)
        # Allow default selection behavior to happen so we can see what we clicked
        # But we might want to suppress the file loading if it's a drag?
        # For now, let's just track the index.

    def on_drag_motion(self, event):
        # Optional: Visual feedback could go here
        pass

    def on_drop(self, event):
        target_index = self.pinned_list.nearest(event.y)
        if self.drag_start_index is not None and target_index != self.drag_start_index:
            files = ConfigManager.get_pinned_files()
            if self.drag_start_index < len(files) and target_index < len(files):
                # Move item
                item = files.pop(self.drag_start_index)
                files.insert(target_index, item)
                
                # Save
                config = ConfigManager.load_config()
                config["pinned_files"] = files
                ConfigManager.save_config(config)
                
                self.refresh_pinned()
                
                # Restore selection
                self.pinned_list.selection_clear(0, tk.END)
                self.pinned_list.selection_set(target_index)
                self.pinned_list.activate(target_index)
                
        self.drag_start_index = None
