import tkinter as tk
from modules.performance.ui import PerformanceUI
from modules.performance.backend import PerformanceMonitor
from modules.processes.ui import ProcessesUI
from modules.startup.ui import StartupAppsUI
from modules.settings.ui import SettingsUI


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("1200x700")
        self.current_tab = "Performance"
        
        # Initialize module UIs BEFORE setup_ui()
        self.performance_ui = None
        self.processes_ui = None
        self.startup_apps_ui = None
        self.settings_ui = None
        
        # Create a persistent performance monitor
        self.performance_monitor = PerformanceMonitor()
        self.monitor_update_job = None
        
        self.setup_ui()
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar
        sidebar = tk.Frame(main_container, bg="#2b2b2b", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Sidebar buttons
        buttons = [
            ("Performance", self.show_performance),
            ("Processes", self.show_processes),
            ("Startup Apps", self.show_startup_apps),
            ("Settings", self.show_settings)
        ]
        
        for text, command in buttons:
            btn = tk.Button(sidebar, text=text, command=command, 
                          bg="#3c3c3c", fg="white", font=("Arial", 11),
                          relief=tk.FLAT, padx=20, pady=15, anchor="w")
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Right content area
        self.content_frame = tk.Frame(main_container, bg="white")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Show performance by default
        self.show_performance()
    
    def clear_content(self):
        # Stop updates from previous tab
        if self.performance_ui:
            self.performance_ui.stop_updates()
        if self.processes_ui:
            self.processes_ui.stop_updates()
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_performance(self):
        self.current_tab = "Performance"
        self.clear_content()
        # Pass the persistent monitor to the UI
        self.performance_ui = PerformanceUI(self.content_frame, self.performance_monitor)
        self.performance_ui.start_updates()
    
    def show_processes(self):
        self.current_tab = "Processes"
        self.clear_content()
        self.processes_ui = ProcessesUI(self.content_frame)
        self.processes_ui.start_updates()
    
    def show_startup_apps(self):
        self.current_tab = "Startup Apps"
        self.clear_content()
        self.startup_apps_ui = StartupAppsUI(self.content_frame)
    
    def show_settings(self):
        self.current_tab = "Settings"
        self.clear_content()
        self.settings_ui = SettingsUI(self.content_frame)
    
    def _start_background_monitoring(self):
        """Continuously collect performance data in background"""
        try:
            self.performance_monitor.update_data()
        except:
            pass
        # Schedule next update (every 1 second)
        self.monitor_update_job = self.root.after(1000, self._start_background_monitoring)
    
    def on_closing(self):
        # Stop background monitoring
        if self.monitor_update_job:
            self.root.after_cancel(self.monitor_update_job)
        
        if self.performance_ui:
            self.performance_ui.stop_updates()
        if self.processes_ui:
            self.processes_ui.stop_updates()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
