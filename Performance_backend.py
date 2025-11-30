"""
Backend logic for performance monitoring
"""
from collections import deque
from modules.utils.helpers import get_psutil


class PerformanceMonitor:
    def __init__(self, maxlen=60):
        self.psutil = get_psutil()
        self.cpu_data = deque(maxlen=maxlen)
        self.memory_data = deque(maxlen=maxlen)
        self.disk_data = deque(maxlen=maxlen)
        self.gpu_data = deque(maxlen=maxlen)
        self.gpu_memory_data = deque(maxlen=maxlen)
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        if self.psutil:
            return self.psutil.cpu_percent(interval=0.1)
        return 0
    
    def get_memory_usage(self):
        """Get current memory usage percentage"""
        if self.psutil:
            mem = self.psutil.virtual_memory()
            return mem.percent
        return 0
    
    def get_disk_usage(self):
        """Get current disk usage percentage"""
        if self.psutil:
            disk = self.psutil.disk_usage('/')
            return disk.percent
        return 0
    
    def get_gpu_usage(self):
        """Get GPU usage (placeholder)"""
        # Would require pynvml or similar library
        return 0
    
    def get_gpu_memory_usage(self):
        """Get GPU memory usage (placeholder)"""
        # Would require pynvml or similar library
        return 0
    
    def update_data(self):
        """Update all data collections"""
        self.cpu_data.append(self.get_cpu_usage())
        self.memory_data.append(self.get_memory_usage())
        self.disk_data.append(self.get_disk_usage())
        self.gpu_data.append(self.get_gpu_usage())
        self.gpu_memory_data.append(self.get_gpu_memory_usage())
    
    def get_all_data(self):
        """Get all collected data"""
        return {
            'cpu': list(self.cpu_data),
            'memory': list(self.memory_data),
            'disk': list(self.disk_data),
            'gpu': list(self.gpu_data),
            'gpu_memory': list(self.gpu_memory_data)
        }
