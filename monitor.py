import sys
# try importing psutil; make module import-safe if psutil is missing
try:
	import psutil
	_PSUTIL_AVAILABLE = True
except ImportError:
	psutil = None
	_PSUTIL_AVAILABLE = False

class Monitor:
	"""psutil-based monitor helpers (graceful if psutil is not installed)."""
	def list_processes(self):
		if not _PSUTIL_AVAILABLE:
			# raise at call-time with a helpful message
			raise RuntimeError("psutil is not installed. Install it with: pip install psutil")
		procs = []
		for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
			try:
				info = p.info
				procs.append(info)
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				continue
		# sort by cpu desc
		procs.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
		return procs

	def kill(self, pid):
		if not _PSUTIL_AVAILABLE:
			return False, "psutil not installed; cannot kill processes (pip install psutil)"
		try:
			p = psutil.Process(pid)
			p.kill()
			return True, ""
		except Exception as e:
			return False, str(e)

	def suspend(self, pid):
		if not _PSUTIL_AVAILABLE:
			return False, "psutil not installed; cannot suspend processes (pip install psutil)"
		try:
			p = psutil.Process(pid)
			p.suspend()
			return True, ""
		except Exception as e:
			return False, str(e)
