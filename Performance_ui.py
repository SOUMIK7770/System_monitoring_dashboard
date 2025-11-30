"""
UI for performance monitoring
"""
import tkinter as tk
from modules.performance.Performance_backend import PerformanceMonitor
from modules.utils.helpers import check_matplotlib, check_psutil


class PerformanceUI:
    def __init__(self, parent, monitor=None):
        self.parent = parent
        # Use provided monitor or create new one
        self.monitor = monitor if monitor else PerformanceMonitor()
        self.update_running = False
        self.update_job = None
        
        # Check dependencies
        if not check_matplotlib():
            tk.Label(parent, text="Install matplotlib for graphs: pip install matplotlib",
                    font=("Arial", 12), fg="red").pack(pady=20)
            return
        
        if not check_psutil():
            tk.Label(parent, text="Install psutil: pip install psutil",
                    font=("Arial", 12), fg="red").pack(pady=20)
            return
        
        self._setup_matplotlib()
        self.setup_ui()
    
    def _setup_matplotlib(self):
        """Setup matplotlib imports"""
        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.Figure = Figure
        self.FigureCanvasTkAgg = FigureCanvasTkAgg
    
    def setup_ui(self):
        # Title
        tk.Label(self.parent, text="Performance", font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Create graphs container
        graphs_container = tk.Frame(self.parent, bg="white")
        graphs_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create graphs
        self.create_graphs(graphs_container)
    
    def create_graphs(self, parent):
        # CPU Graph
        cpu_frame = tk.LabelFrame(parent, text="CPU Usage", font=("Arial", 10, "bold"))
        cpu_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.cpu_fig = self.Figure(figsize=(4, 2.5), dpi=80)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_canvas = self.FigureCanvasTkAgg(self.cpu_fig, cpu_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Memory Graph
        mem_frame = tk.LabelFrame(parent, text="Memory Usage", font=("Arial", 10, "bold"))
        mem_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.mem_fig = self.Figure(figsize=(4, 2.5), dpi=80)
        self.mem_ax = self.mem_fig.add_subplot(111)
        self.mem_canvas = self.FigureCanvasTkAgg(self.mem_fig, mem_frame)
        self.mem_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Disk Graph
        disk_frame = tk.LabelFrame(parent, text="Disk Usage", font=("Arial", 10, "bold"))
        disk_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.disk_fig = self.Figure(figsize=(4, 2.5), dpi=80)
        self.disk_ax = self.disk_fig.add_subplot(111)
        self.disk_canvas = self.FigureCanvasTkAgg(self.disk_fig, disk_frame)
        self.disk_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # GPU Graph
        gpu_frame = tk.LabelFrame(parent, text="GPU Usage", font=("Arial", 10, "bold"))
        gpu_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.gpu_fig = self.Figure(figsize=(4, 2.5), dpi=80)
        self.gpu_ax = self.gpu_fig.add_subplot(111)
        self.gpu_canvas = self.FigureCanvasTkAgg(self.gpu_fig, gpu_frame)
        self.gpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # GPU Memory Graph
        gpu_mem_frame = tk.LabelFrame(parent, text="GPU Memory", font=("Arial", 10, "bold"))
        gpu_mem_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.gpu_mem_fig = self.Figure(figsize=(8, 2.5), dpi=80)
        self.gpu_mem_ax = self.gpu_mem_fig.add_subplot(111)
        self.gpu_mem_canvas = self.FigureCanvasTkAgg(self.gpu_mem_fig, gpu_mem_frame)
        self.gpu_mem_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        for i in range(3):
            parent.grid_rowconfigure(i, weight=1)
        for i in range(2):
            parent.grid_columnconfigure(i, weight=1)
    
    def update_graphs(self):
        """Update all performance graphs"""
        # Don't update data here anymore, just fetch existing data
        data = self.monitor.get_all_data()
        
        # Update CPU graph
        self.cpu_ax.clear()
        self.cpu_ax.plot(data['cpu'], color='#0078d4', linewidth=2)
        self.cpu_ax.fill_between(range(len(data['cpu'])), data['cpu'], alpha=0.3, color='#0078d4')
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_xlim(0, 60)
        self.cpu_ax.set_ylabel('%')
        self.cpu_ax.grid(True, alpha=0.3)
        self.cpu_canvas.draw()
        
        # Update Memory graph
        self.mem_ax.clear()
        self.mem_ax.plot(data['memory'], color='#00a651', linewidth=2)
        self.mem_ax.fill_between(range(len(data['memory'])), data['memory'], alpha=0.3, color='#00a651')
        self.mem_ax.set_ylim(0, 100)
        self.mem_ax.set_xlim(0, 60)
        self.mem_ax.set_ylabel('%')
        self.mem_ax.grid(True, alpha=0.3)
        self.mem_canvas.draw()
        
        # Update Disk graph
        self.disk_ax.clear()
        self.disk_ax.plot(data['disk'], color='#ff8c00', linewidth=2)
        self.disk_ax.fill_between(range(len(data['disk'])), data['disk'], alpha=0.3, color='#ff8c00')
        self.disk_ax.set_ylim(0, 100)
        self.disk_ax.set_xlim(0, 60)
        self.disk_ax.set_ylabel('%')
        self.disk_ax.grid(True, alpha=0.3)
        self.disk_canvas.draw()
        
        # Update GPU graph
        self.gpu_ax.clear()
        self.gpu_ax.plot(data['gpu'], color='#7719aa', linewidth=2)
        self.gpu_ax.fill_between(range(len(data['gpu'])), data['gpu'], alpha=0.3, color='#7719aa')
        self.gpu_ax.set_ylim(0, 100)
        self.gpu_ax.set_xlim(0, 60)
        self.gpu_ax.set_ylabel('%')
        self.gpu_ax.grid(True, alpha=0.3)
        self.gpu_ax.text(30, 50, 'GPU monitoring requires\nadditional libraries', 
                        ha='center', va='center', fontsize=9, color='gray')
        self.gpu_canvas.draw()
        
        # Update GPU Memory graph
        self.gpu_mem_ax.clear()
        self.gpu_mem_ax.plot(data['gpu_memory'], color='#d13438', linewidth=2)
        self.gpu_mem_ax.fill_between(range(len(data['gpu_memory'])), data['gpu_memory'], alpha=0.3, color='#d13438')
        self.gpu_mem_ax.set_ylim(0, 100)
        self.gpu_mem_ax.set_xlim(0, 60)
        self.gpu_mem_ax.set_ylabel('%')
        self.gpu_mem_ax.grid(True, alpha=0.3)
        self.gpu_mem_canvas.draw()
    
    def start_updates(self):
        """Start the update thread"""
        self.update_running = True
        self._schedule_update()
    
    def _schedule_update(self):
        """Schedule the next graph update"""
        if self.update_running:
            try:
                self.update_graphs()
            except:
                pass
            # Update graphs every 500ms for smooth animation
            self.update_job = self.parent.after(500, self._schedule_update)
    
    def stop_updates(self):
        """Stop the update thread"""
        self.update_running = False
        if self.update_job:
            try:
                self.parent.after_cancel(self.update_job)
            except:
                pass
            self.update_job = None
