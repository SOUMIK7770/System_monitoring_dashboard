"""
UI for startup applications management
"""
import tkinter as tk
from tkinter import ttk, messagebox
from modules.startup.backend import StartupAppsManager


class StartupAppsUI:
    def __init__(self, parent):
        self.parent = parent
        self.manager = StartupAppsManager()
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        tk.Label(self.parent, text="Startup Applications", font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(self.parent, bg="white")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(toolbar, text="Enable", command=self.enable_startup_app,
                 bg="#00a651", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Disable", command=self.disable_startup_app,
                 bg="#ff8c00", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Add New", command=self.add_startup_app,
                 bg="#0078d4", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Remove", command=self.remove_startup_app,
                 bg="#d13438", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        
        # Startup apps table
        table_frame = tk.Frame(self.parent, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        vsb = tk.Scrollbar(table_frame, orient="vertical")
        
        columns = ("Name", "Publisher", "Status", "Impact")
        self.startup_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         yscrollcommand=vsb.set)
        
        vsb.config(command=self.startup_tree.yview)
        
        for col in columns:
            self.startup_tree.heading(col, text=col)
            self.startup_tree.column(col, width=150)
        
        self.startup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_startup_apps()
    
    def load_startup_apps(self):
        """Load and display startup applications"""
        # Clear existing
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)
        
        # Load apps
        apps = self.manager.list_startup_apps()
        for app in apps:
            self.startup_tree.insert("", "end", values=(
                app['name'],
                app['publisher'],
                app['status'],
                app['impact']
            ))
    
    def enable_startup_app(self):
        messagebox.showinfo("Info", "Enable startup app functionality coming soon")
    
    def disable_startup_app(self):
        messagebox.showinfo("Info", "Disable startup app functionality coming soon")
    
    def add_startup_app(self):
        messagebox.showinfo("Info", "Add startup app functionality coming soon")
    
    def remove_startup_app(self):
        messagebox.showinfo("Info", "Remove startup app functionality coming soon")
