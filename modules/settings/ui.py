"""
UI for application settings
"""
import tkinter as tk
from tkinter import messagebox
from modules.settings.backend import SettingsManager


class SettingsUI:
    def _init_(self, parent):
        self.parent = parent
        self.manager = SettingsManager()
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        tk.Label(self.parent, text="Settings", font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        settings_frame = tk.Frame(self.parent, bg="white")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Update interval
        tk.Label(settings_frame, text="Update interval (seconds):", bg="white",
                font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=10)
        
        self.interval_var = tk.StringVar(value=str(self.manager.get_setting('update_interval', 1)))
        tk.Entry(settings_frame, textvariable=self.interval_var, width=10).grid(row=0, column=1, sticky="w")
        
        # Start with system
        self.start_with_system_var = tk.BooleanVar(value=self.manager.get_setting('start_with_system', False))
        tk.Checkbutton(settings_frame, text="Start with system", bg="white",
                      font=("Arial", 11), variable=self.start_with_system_var).grid(
                          row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Minimize to tray
        self.minimize_to_tray_var = tk.BooleanVar(value=self.manager.get_setting('minimize_to_tray', False))
        tk.Checkbutton(settings_frame, text="Minimize to tray", bg="white",
                      font=("Arial", 11), variable=self.minimize_to_tray_var).grid(
                          row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        # Save button
        tk.Button(settings_frame, text="Save Settings", bg="#0078d4", fg="white",
                 padx=20, pady=5, command=self.save_settings).grid(row=3, column=0, columnspan=2, pady=20)
    
    def save_settings(self):
        """Save all settings"""
        try:
            interval = int(self.interval_var.get())
            if interval < 1:
                raise ValueError("Interval must be at least 1 second")
            
            new_settings = {
                'update_interval': interval,
                'start_with_system': self.start_with_system_var.get(),
                'minimize_to_tray': self.minimize_to_tray_var.get()
            }
            
            success, msg = self.manager.update_settings(new_settings)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
        except ValueError as e:
            messagebox.showerror("Error", str(e))