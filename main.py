import os
import sqlite3
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

class DBHelper:
	"""Simple sqlite helper to init DB, users and logs tables."""
	def __init__(self, path=DB_PATH):
		self.path = path
		self._ensure_db()

	def _ensure_db(self):
		conn = sqlite3.connect(self.path)
		c = conn.cursor()
		c.execute("""CREATE TABLE IF NOT EXISTS users (
			username TEXT PRIMARY KEY,
			password_hash BLOB,
			role TEXT
		)""")
		c.execute("""CREATE TABLE IF NOT EXISTS logs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp TEXT,
			username TEXT,
			action TEXT,
			target_pid INTEGER,
			success INTEGER,
			details TEXT
		)""")
		conn.commit()
		conn.close()

	def conn(self):
		return sqlite3.connect(self.path)

class AuthManager:
	"""Handles user creation and verification using bcrypt."""
	def __init__(self, db_helper: DBHelper):
		self.db = db_helper
		# create default admin if missing
		self._ensure_default_admin()

	def _ensure_default_admin(self):
		conn = self.db.conn()
		c = conn.cursor()
		c.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
		if c.fetchone()[0] == 0:
			# default password admin123 (change after first login)
			pw = "admin123".encode()
			hash_ = bcrypt.hashpw(pw, bcrypt.gensalt())
			c.execute("INSERT INTO users(username, password_hash, role) VALUES (?,?,?)",
			          ("admin", hash_, "admin"))
			conn.commit()
		conn.close()

	def create_user(self, username, password, role="user"):
		pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
		conn = self.db.conn()
		try:
			conn.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)",
			             (username, pw_hash, role))
			conn.commit()
			return True
		except sqlite3.IntegrityError:
			return False
		finally:
			conn.close()

	def verify(self, username, password):
		conn = self.db.conn()
		c = conn.cursor()
		c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
		row = c.fetchone()
		conn.close()
		if not row:
			return False, None
		stored_hash, role = row
		try:
			ok = bcrypt.checkpw(password.encode(), stored_hash)
		except Exception:
			ok = False
		return ok, role if ok else (False, None)[1]

class ActionLogger:
	"""Log actions to sqlite logs table"""
	def __init__(self, db_helper: DBHelper):
		self.db = db_helper

	def log(self, username, action, target_pid=None, success=1, details=""):
		conn = self.db.conn()
		conn.execute(
			"INSERT INTO logs(timestamp,username,action,target_pid,success,details) VALUES (?,?,?,?,?,?)",
			(datetime.utcnow().isoformat(), username, action, target_pid, int(bool(success)), details)
		)
		conn.commit()
		conn.close()

class Monitor:
	"""psutil-based monitor helpers"""
	def list_processes(self):
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
		try:
			p = psutil.Process(pid)
			p.kill()
			return True, ""
		except Exception as e:
			return False, str(e)

	def suspend(self, pid):
		try:
			p = psutil.Process(pid)
			p.suspend()
			return True, ""
		except Exception as e:
			return False, str(e)

class AppGUI:
	def __init__(self, root):
		self.root = root
		self.root.title("Secure Real-Time Process Monitoring Dashboard")
		self.db = DBHelper()
		self.auth = AuthManager(self.db)
		self.logger = ActionLogger(self.db)
		self.monitor = Monitor()
		self.user = None
		self.role = None

		self._build_login()

	# -------------------
	# Login UI
	# -------------------
	def _build_login(self):
		for w in self.root.winfo_children():
			w.destroy()
		frame = ttk.Frame(self.root, padding=12)
		frame.pack(fill='both', expand=True)

		ttk.Label(frame, text="Username").grid(row=0, column=0, sticky='w')
		self.username_var = tk.StringVar()
		ttk.Entry(frame, textvariable=self.username_var).grid(row=0, column=1)

		ttk.Label(frame, text="Password").grid(row=1, column=0, sticky='w')
		self.password_var = tk.StringVar()
		ttk.Entry(frame, textvariable=self.password_var, show="*").grid(row=1, column=1)

		login_btn = ttk.Button(frame, text="Login", command=self._handle_login)
		login_btn.grid(row=2, column=0, columnspan=2, pady=8)

		ttk.Label(frame, text="(Default admin: admin / admin123)").grid(row=3, column=0, columnspan=2)

	# -------------------
	# Dashboard UI
	# -------------------
	def _build_dashboard(self):
		for w in self.root.winfo_children():
			w.destroy()
		top = ttk.Frame(self.root)
		top.pack(fill='x')
		ttk.Label(top, text=f"User: {self.user}  Role: {self.role}").pack(side='left', padx=8)
		ttk.Button(top, text="Logout", command=self._logout).pack(side='right', padx=8)

		# Process table
		cols = ("pid", "name", "user", "cpu", "mem", "status")
		self.tree = ttk.Treeview(self.root, columns=cols, show='headings', height=20)
		for c in cols:
			self.tree.heading(c, text=c.upper())
		self.tree.pack(fill='both', expand=True, padx=8, pady=8)

		# Buttons
		btn_frame = ttk.Frame(self.root)
		btn_frame.pack(fill='x', pady=4)
		self.btn_refresh = ttk.Button(btn_frame, text="Refresh", command=self._refresh_processes)
		self.btn_refresh.pack(side='left', padx=4)
		self.btn_kill = ttk.Button(btn_frame, text="Kill (Admin)", command=self._kill_selected)
		self.btn_kill.pack(side='left', padx=4)
		self.btn_suspend = ttk.Button(btn_frame, text="Suspend (Admin)", command=self._suspend_selected)
		self.btn_suspend.pack(side='left', padx=4)

		# Disable admin buttons for non-admins
		if self.role != "admin":
			self.btn_kill.state(['disabled'])
			self.btn_suspend.state(['disabled'])

		# Auto-refresh
		self._refresh_processes()
		self._schedule_refresh()

	def _schedule_refresh(self):
		self.root.after(2000, self._refresh_processes)  # every 2s

	# -------------------
	# Handlers
	# -------------------
	def _handle_login(self):
		username = self.username_var.get().strip()
		password = self.password_var.get().strip()
		ok, role = self.auth.verify(username, password)
		if ok:
			self.user = username
			self.role = role or "user"
			self.logger.log(self.user, "login", success=1)
			self._build_dashboard()
		else:
			self.logger.log(username, "login_failed", success=0)
			messagebox.showerror("Login failed", "Invalid credentials")

	def _logout(self):
		self.logger.log(self.user, "logout", success=1)
		self.user = None
		self.role = None
		self._build_login()

	def _refresh_processes(self):
		# Clear
		for i in self.tree.get_children():
			self.tree.delete(i)
		procs = self.monitor.list_processes()
		for p in procs:
			self.tree.insert("", "end", values=(
				p.get('pid'),
				p.get('name')[:30] if p.get('name') else "",
				p.get('username') or "",
				p.get('cpu_percent') or 0,
				round(p.get('memory_percent') or 0, 2),
				p.get('status') or ""
			))
		# keep scheduling
		self.root.after(2000, lambda: None)

	def _get_selected_pid(self):
		sel = self.tree.selection()
		if not sel:
			return None
		item = self.tree.item(sel[0])
		return int(item['values'][0])

	def _kill_selected(self):
		pid = self._get_selected_pid()
		if pid is None:
			messagebox.showinfo("Select", "Select a process first")
			return
		if self.role != "admin":
			messagebox.showwarning("Permission", "Only admin can kill processes")
			return
		def task():
			ok, err = self.monitor.kill(pid)
			self.logger.log(self.user, "kill", target_pid=pid, success=ok, details=err or "")
			msg = "Killed" if ok else f"Failed: {err}"
			messagebox.showinfo("Kill", msg)
			self._refresh_processes()
		threading.Thread(target=task, daemon=True).start()

	def _suspend_selected(self):
		pid = self._get_selected_pid()
		if pid is None:
			messagebox.showinfo("Select", "Select a process first")
			return
		if self.role != "admin":
			messagebox.showwarning("Permission", "Only admin can suspend processes")
			return
		def task():
			ok, err = self.monitor.suspend(pid)
			self.logger.log(self.user, "suspend", target_pid=pid, success=ok, details=err or "")
			msg = "Suspended" if ok else f"Failed: {err}"
			messagebox.showinfo("Suspend", msg)
			self._refresh_processes()
		threading.Thread(target=task, daemon=True).start()

# -------------------
# Entry point
# -------------------
def main():
	root = tk.Tk()
	app = AppGUI(root)
	root.geometry("800x600")
	root.mainloop()

if __name__ == "__main__":
	main()
