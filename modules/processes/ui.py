"""
UI for process management
"""
import tkinter as tk
from tkinter import ttk, messagebox
from modules.processes.backend import ProcessManager
from modules.utils.helpers import check_psutil


class ProcessesUI:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ProcessManager()
        self.update_running = False
        self.update_job = None
        
        if not check_psutil():
            tk.Label(parent, text="Install psutil: pip install psutil",
                    font=("Arial", 12), fg="red").pack(pady=20)
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        tk.Label(self.parent, text="Processes", font=("Arial", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(self.parent, bg="white")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_processes,
                 bg="#0078d4", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Kill Process", command=self.kill_selected_process,
                 bg="#d13438", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Suspend", command=self.suspend_selected_process,
                 bg="#ff8c00", fg="white", padx=10).pack(side=tk.LEFT, padx=2)
        
        # Process table
        table_frame = tk.Frame(self.parent, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbars
        vsb = tk.Scrollbar(table_frame, orient="vertical")
        hsb = tk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ("PID", "Name", "User", "CPU %", "Memory %", "Status")
        self.process_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.process_tree.yview)
        hsb.config(command=self.process_tree.xview)
        
        # Configure columns
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)
        
        # Pack
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.refresh_processes()
    
    def refresh_processes(self):
        """Refresh the process list"""
        if not hasattr(self, 'process_tree'):
            return
        
        # Save current scroll position and selection
        try:
            yview_position = self.process_tree.yview()[0]
            selected_items = self.process_tree.selection()
            selected_pid = None
            if selected_items:
                item = self.process_tree.item(selected_items[0])
                selected_pid = item['values'][0] if item['values'] else None
        except:
            yview_position = 0
            selected_pid = None
        
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        try:
            processes = self.manager.list_processes()
            item_to_select = None
            
            for proc in processes:
                pid = proc.get('pid', 'N/A')
                item_id = self.process_tree.insert("", "end", values=(
                    pid,
                    proc.get('name', 'N/A'),
                    proc.get('username', 'N/A'),
                    f"{proc.get('cpu_percent', 0):.1f}",
                    f"{proc.get('memory_percent', 0):.1f}",
                    proc.get('status', 'N/A')
                ))
                
                # Track the item if it matches the previously selected PID
                if pid == selected_pid:
                    item_to_select = item_id
            
            # Restore selection without scrolling to it
            if item_to_select:
                self.process_tree.selection_set(item_to_select)
            
            # Restore scroll position (this is the key part)
            self.process_tree.update_idletasks()
            self.process_tree.yview_moveto(yview_position)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load processes: {e}")
    
    def kill_selected_process(self):
        """Kill the selected process"""
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a process")
            return
        
        item = self.process_tree.item(selected[0])
        pid = int(item['values'][0])
        
        if messagebox.askyesno("Confirm", f"Kill process {pid}?"):
            success, msg = self.manager.kill_process(pid)
            if success:
                messagebox.showinfo("Success", msg)
                self.refresh_processes()
            else:
                messagebox.showerror("Error", msg)
    
    def suspend_selected_process(self):
        """Suspend the selected process"""
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a process")
            return
        
        item = self.process_tree.item(selected[0])
        pid = int(item['values'][0])
        
        success, msg = self.manager.suspend_process(pid)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_processes()
        else:
            messagebox.showerror("Error", msg)
    
    def start_updates(self):
        """Start auto-refresh using tkinter's after() method"""
        self.update_running = True
        self._schedule_update()
    
    def _schedule_update(self):
        """Schedule the next update"""
        if self.update_running:
            try:
                self.refresh_processes()
            except:
                pass
            # Schedule next update after 3 seconds
            self.update_job = self.parent.after(3000, self._schedule_update)
    
    def stop_updates(self):
        """Stop auto-refresh"""
        self.update_running = False
        if self.update_job:
            try:
                self.parent.after_cancel(self.update_job)
            except:
                pass
            self.update_job = None
