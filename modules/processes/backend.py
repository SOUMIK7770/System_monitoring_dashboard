"""
Backend logic for process management
"""
from modules.utils.helpers import get_psutil


class ProcessManager:
    def __init__(self):
        self.psutil = get_psutil()
    
    def list_processes(self):
        """Get list of all running processes"""
        if not self.psutil:
            return []
        
        processes = []
        for proc in self.psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except (self.psutil.NoSuchProcess, self.psutil.AccessDenied):
                pass
        return processes
    
    def kill_process(self, pid):
        """Kill a process by PID"""
        if not self.psutil:
            return False, "psutil not available"
        
        try:
            proc = self.psutil.Process(pid)
            proc.kill()
            return True, f"Process {pid} killed successfully"
        except self.psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except self.psutil.AccessDenied:
            return False, f"Access denied to kill process {pid}"
        except Exception as e:
            return False, str(e)
    
    def suspend_process(self, pid):
        """Suspend a process by PID"""
        if not self.psutil:
            return False, "psutil not available"
        
        try:
            proc = self.psutil.Process(pid)
            proc.suspend()
            return True, f"Process {pid} suspended successfully"
        except self.psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except self.psutil.AccessDenied:
            return False, f"Access denied to suspend process {pid}"
        except Exception as e:
            return False, str(e)
    
    def resume_process(self, pid):
        """Resume a suspended process"""
        if not self.psutil:
            return False, "psutil not available"
        
        try:
            proc = self.psutil.Process(pid)
            proc.resume()
            return True, f"Process {pid} resumed successfully"
        except self.psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except self.psutil.AccessDenied:
            return False, f"Access denied to resume process {pid}"
        except Exception as e:
            return False, str(e)
