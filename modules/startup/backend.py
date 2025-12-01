"""
Backend logic for startup applications management
"""
import platform
import os


class StartupAppsManager:
    def __init__(self):
        self.platform = platform.system()
    
    def list_startup_apps(self):
        """List all startup applications"""
        if self.platform == "Windows":
            return self._list_windows_startup()
        elif self.platform == "Linux":
            return self._list_linux_startup()
        else:
            return []
    
    def _list_windows_startup(self):
        """List Windows startup applications"""
        apps = []
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    apps.append({
                        'name': name,
                        'path': value,
                        'publisher': 'Unknown',
                        'status': 'Enabled',
                        'impact': 'Not measured'
                    })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            apps.append({
                'name': f'Error: {e}',
                'path': '',
                'publisher': 'N/A',
                'status': 'N/A',
                'impact': 'N/A'
            })
        return apps
    
    def _list_linux_startup(self):
        """List Linux startup applications"""
        apps = []
        autostart_dir = os.path.expanduser("~/.config/autostart/")
        
        if os.path.exists(autostart_dir):
            for filename in os.listdir(autostart_dir):
                if filename.endswith(".desktop"):
                    name = filename.replace(".desktop", "")
                    apps.append({
                        'name': name,
                        'path': os.path.join(autostart_dir, filename),
                        'publisher': 'Unknown',
                        'status': 'Enabled',
                        'impact': 'Not measured'
                    })
        else:
            apps.append({
                'name': 'No autostart directory',
                'path': '',
                'publisher': 'N/A',
                'status': 'N/A',
                'impact': 'N/A'
            })
        return apps
    
    def enable_app(self, app_name):
        """Enable a startup application"""
        return False, "Not implemented yet"

    def disable_app(self, app_name):
        """Disable a startup application"""
        return False, "Not implemented yet"
    
    def add_app(self, app_name, app_path):
        """Add a new startup application"""
        return False, "Not implemented yet"
    
    def remove_app(self, app_name):
        """Remove a startup application"""
        return False, "Not implemented yet"
