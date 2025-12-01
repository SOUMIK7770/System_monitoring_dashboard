import psutil
import random

class PerformanceMonitor:
    def __init__(self):
        # 60 data points for each graph (1 minute history)
        self.history_length = 60

        self.cpu_history = [0] * self.history_length
        self.mem_history = [0] * self.history_length
        self.disk_history = [0] * self.history_length
        self.gpu_history = [0] * self.history_length      # Dummy GPU %
        self.gpu_mem_history = [0] * self.history_length  # Dummy GPU Mem %

    # Maintains rolling window
    def _push(self, arr, value):
        arr.append(value)
        if len(arr) > self.history_length:
            arr.pop(0)
        return arr

    def get_all_data(self):
        # REAL system values
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        # Disk usage % (simplified)
        disk = psutil.disk_usage('/').percent

        # GPU placeholders (because you're not using NVML yet)
        gpu = random.uniform(0, 10)   
        gpu_mem = random.uniform(0, 10)

        # Update histories
        self._push(self.cpu_history, cpu)
        self._push(self.mem_history, mem)
        self._push(self.disk_history, disk)
        self._push(self.gpu_history, gpu)
        self._push(self.gpu_mem_history, gpu_mem)

        # Return dictionary EXACTLY as UI expects
        return {
            "cpu": self.cpu_history,
            "memory": self.mem_history,
            "disk": self.disk_history,
            "gpu": self.gpu_history,
            "gpu_memory": self.gpu_mem_history,
        }
