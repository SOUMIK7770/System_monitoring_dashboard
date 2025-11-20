import tkinter as tk
from tkinter import ttk, messagebox
import threading
from collections import deque

try:
	import psutil
	_PSUTIL_AVAILABLE = True
except ImportError:
	psutil = None
	_PSUTIL_AVAILABLE = False

try:
	from matplotlib.figure import Figure
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	_MATPLOTLIB_AVAILABLE = True
except Exception:
	Figure = None
	FigureCanvasTkAgg = None
	_MATPLOTLIB_AVAILABLE = False

from .db import DBHelper
from .auth import AuthManager
from .logger import ActionLogger
from .monitor import Monitor

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

		self._psutil_missing = not _PSUTIL_AVAILABLE
		self._mpl_missing = not _MATPLOTLIB_AVAILABLE

		# chart state
		self.cpu_history = deque(maxlen=60)
		self.mem_history = deque(maxlen=60)
		self.history_x = deque(maxlen=60)
		self._chart_canvas = None
		self._chart_fig = None
		self._cpu_line = None
		self._mem_line = None
		self._chart_frame = None

		# dual table references
		self.tree_top = None       # top 10 processes
		self.tree_all = None       # all processes

		self._build_login()

	# -------------------
	# Login UI
	# -------------------
	def _build_login(self):
		for w in self.root.winfo_children():
			w.destroy()
		
		# Center frame
		frame = ttk.Frame(self.root, padding=30)
		frame.place(relx=0.5, rely=0.5, anchor='center')

		# Title
		title = ttk.Label(frame, text="Process Monitor", font=('Arial', 18, 'bold'))
		title.grid(row=0, column=0, columnspan=2, pady=(0,20))

		if self._psutil_missing or self._mpl_missing:
			warn_parts = []
			if self._psutil_missing:
				warn_parts.append("psutil")
			if self._mpl_missing:
				warn_parts.append("matplotlib")
			msg = "Missing: " + ", ".join(warn_parts) + " — pip install " + " ".join(warn_parts)
			ttk.Label(frame, text=msg, foreground="red", font=('Arial', 9)).grid(row=1, column=0, columnspan=2, pady=(0,12))

		ttk.Label(frame, text="Username", font=('Arial', 10)).grid(row=2, column=0, sticky='e', padx=(0,8), pady=6)
		self.username_var = tk.StringVar()
		entry_user = ttk.Entry(frame, textvariable=self.username_var, width=25)
		entry_user.grid(row=2, column=1, pady=6)

		ttk.Label(frame, text="Password", font=('Arial', 10)).grid(row=3, column=0, sticky='e', padx=(0,8), pady=6)
		self.password_var = tk.StringVar()
		entry_pass = ttk.Entry(frame, textvariable=self.password_var, show="*", width=25)
		entry_pass.grid(row=3, column=1, pady=6)

		login_btn = ttk.Button(frame, text="Login", command=self._handle_login)
		login_btn.grid(row=4, column=0, columnspan=2, pady=(16,8))

		ttk.Label(frame, text="Default: admin / admin123", font=('Arial', 9), foreground='gray').grid(row=5, column=0, columnspan=2)

	# -------------------
	# Dashboard UI
	# -------------------
	def _build_dashboard(self):
		for w in self.root.winfo_children():
			w.destroy()

		# Header bar with gradient-like color
		header = ttk.Frame(self.root, padding=8, relief='raised')
		header.pack(fill='x', side='top')
		ttk.Label(header, text=f"👤 {self.user} ({self.role})", font=('Arial', 11, 'bold'), foreground='#2c3e50').pack(side='left', padx=8)
		ttk.Button(header, text="Logout", command=self._logout).pack(side='right', padx=8)

		if self._psutil_missing or self._mpl_missing:
			warn_text = ""
			if self._psutil_missing:
				warn_text += "⚠ psutil missing. "
			if self._mpl_missing:
				warn_text += "⚠ matplotlib missing."
			lbl = ttk.Label(self.root, text=warn_text, foreground="red", font=('Arial', 9))
			lbl.pack(fill='x', padx=8, pady=2)

		# Main container
		main_container = ttk.Frame(self.root)
		main_container.pack(fill='both', expand=True, padx=8, pady=8)

		# Charts section
		if _MATPLOTLIB_AVAILABLE:
			if self._chart_frame:
				try:
					self._chart_frame.destroy()
				except Exception:
					pass
			self._chart_frame = ttk.LabelFrame(main_container, text="System Metrics", padding=8)
			self._chart_frame.pack(fill='x', side='top', pady=(0,8))
			self._init_charts(self._chart_frame)
		else:
			placeholder = ttk.Label(main_container, text="Charts unavailable (install matplotlib)", foreground='gray')
			placeholder.pack(fill='x', pady=4)

		# Tables container
		tables_container = ttk.Frame(main_container)
		tables_container.pack(fill='both', expand=True)

		# Top Processes (RUNNING ONLY, alphabetical by name)
		top_frame = ttk.LabelFrame(tables_container, text="🟢 Running Processes (A-Z)", padding=8)
		top_frame.pack(fill='both', expand=True, side='top', pady=(0,8))

		cols = ("pid", "name", "user", "cpu", "mem", "status")
		self.tree_top = ttk.Treeview(top_frame, columns=cols, show='headings', height=8)
		# configure tags for alternating row colors
		self.tree_top.tag_configure('evenrow', background='#f0f0f0')
		self.tree_top.tag_configure('oddrow', background='#ffffff')
		self.tree_top.tag_configure('high_cpu', foreground='#e74c3c')
		self.tree_top.tag_configure('medium_cpu', foreground='#f39c12')
		self.tree_top.tag_configure('low_cpu', foreground='#27ae60')

		for c in cols:
			self.tree_top.heading(c, text=c.upper())
			if c == "pid":
				self.tree_top.column(c, width=60, anchor='center')
			elif c == "name":
				self.tree_top.column(c, width=200)
			elif c in ("cpu", "mem"):
				self.tree_top.column(c, width=80, anchor='center')
			else:
				self.tree_top.column(c, width=100)
		self.tree_top.pack(fill='both', expand=True)

		# All Processes (ALL, alphabetical by name)
		all_frame = ttk.LabelFrame(tables_container, text="📋 All Processes (A-Z)", padding=8)
		all_frame.pack(fill='both', expand=True, side='top')

		self.tree_all = ttk.Treeview(all_frame, columns=cols, show='headings', height=10)
		self.tree_all.tag_configure('evenrow', background='#f0f0f0')
		self.tree_all.tag_configure('oddrow', background='#ffffff')
		self.tree_all.tag_configure('high_cpu', foreground='#e74c3c')
		self.tree_all.tag_configure('medium_cpu', foreground='#f39c12')
		self.tree_all.tag_configure('low_cpu', foreground='#27ae60')

		for c in cols:
			self.tree_all.heading(c, text=c.upper())
			if c == "pid":
				self.tree_all.column(c, width=60, anchor='center')
			elif c == "name":
				self.tree_all.column(c, width=200)
			elif c in ("cpu", "mem"):
				self.tree_all.column(c, width=80, anchor='center')
			else:
				self.tree_all.column(c, width=100)
		
		scrollbar = ttk.Scrollbar(all_frame, orient='vertical', command=self.tree_all.yview)
		self.tree_all.configure(yscrollcommand=scrollbar.set)
		scrollbar.pack(side='right', fill='y')
		self.tree_all.pack(fill='both', expand=True, side='left')

		# Action buttons
		btn_frame = ttk.Frame(self.root, padding=8)
		btn_frame.pack(fill='x', side='bottom')
		ttk.Button(btn_frame, text="🔄 Refresh", command=self._refresh_processes).pack(side='left', padx=4)
		self.btn_kill = ttk.Button(btn_frame, text="🗙 Kill (Admin)", command=self._kill_selected)
		self.btn_kill.pack(side='left', padx=4)
		self.btn_suspend = ttk.Button(btn_frame, text="⏸ Suspend (Admin)", command=self._suspend_selected)
		self.btn_suspend.pack(side='left', padx=4)

		if self.role != "admin":
			self.btn_kill.state(['disabled'])
			self.btn_suspend.state(['disabled'])

		self._refresh_processes()
		self._schedule_refresh()

	def _init_charts(self, parent):
		"""Initialize matplotlib figure and lines for CPU and Memory."""
		# create figure
		self._chart_fig = Figure(figsize=(8,2.5), dpi=100)
		ax1 = self._chart_fig.add_subplot(121)
		ax2 = self._chart_fig.add_subplot(122)

		# initial empty data
		x = list(range(-59,1))  # show last 60 points as negative -> 0
		y_cpu = [0]*60
		y_mem = [0]*60

		# CPU plot
		self._cpu_line, = ax1.plot(x, y_cpu, color='#e74c3c', linewidth=2)
		ax1.set_title("CPU Usage (%)", fontsize=11, fontweight='bold')
		ax1.set_ylim(0, 100)
		ax1.set_xlim(-59, 0)
		ax1.grid(True, alpha=0.3)
		ax1.set_facecolor('#f9f9f9')

		# Memory plot
		self._mem_line, = ax2.plot(x, y_mem, color='#3498db', linewidth=2)
		ax2.set_title("Memory Usage (%)", fontsize=11, fontweight='bold')
		ax2.set_ylim(0, 100)
		ax2.set_xlim(-59, 0)
		ax2.grid(True, alpha=0.3)
		ax2.set_facecolor('#f9f9f9')

		# create canvas and pack
		if self._chart_canvas:
			try:
				self._chart_canvas.get_tk_widget().destroy()
			except Exception:
				pass
		self._chart_canvas = FigureCanvasTkAgg(self._chart_fig, master=parent)
		self._chart_canvas.draw()
		self._chart_canvas.get_tk_widget().pack(fill='both', expand=True)

		# reset histories to align with x axis
		self.cpu_history = deque(y_cpu, maxlen=60)
		self.mem_history = deque(y_mem, maxlen=60)
		self.history_x = deque(x, maxlen=60)

	def _update_charts(self, cpu_val, mem_val):
		# append new samples
		self.cpu_history.append(cpu_val)
		self.mem_history.append(mem_val)
		l = len(self.cpu_history)
		self.history_x = deque(range(-l+1, 1), maxlen=60)

		try:
			self._cpu_line.set_xdata(list(self.history_x))
			self._cpu_line.set_ydata(list(self.cpu_history))
			self._mem_line.set_xdata(list(self.history_x))
			self._mem_line.set_ydata(list(self.mem_history))

			for ax in self._chart_fig.axes:
				ax.set_xlim(-59, 0)
				ax.set_ylim(0, 100)
			self._chart_canvas.draw_idle()
		except Exception:
			pass

	def _schedule_refresh(self):
		# start a periodic refresh loop that calls _refresh_processes every 1 second
		def _periodic():
			try:
				self._refresh_processes()
			except Exception:
				pass
			self.root.after(1000, _periodic)
		self.root.after(1000, _periodic)

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
		# update metrics
		if _PSUTIL_AVAILABLE:
			try:
				cpu = psutil.cpu_percent(interval=None)
				mem = psutil.virtual_memory().percent
			except Exception:
				cpu = 0
				mem = 0
		else:
			cpu = 0
			mem = 0

		if _MATPLOTLIB_AVAILABLE:
			try:
				self._update_charts(cpu, mem)
			except Exception:
				pass

		# get process list
		try:
			procs = self.monitor.list_processes()
		except RuntimeError as e:
			print(str(e))
			procs = []

		# filter and sort: top = running processes (alphabetical), all = all processes (alphabetical)
		running_procs = [p for p in procs if p.get('status', '').lower() == 'running']
		running_procs.sort(key=lambda x: (x.get('name') or "").lower())
		
		all_procs_sorted = sorted(procs, key=lambda x: (x.get('name') or "").lower())

		# update tables in-place with color coding
		self._update_tree_stable(self.tree_top, running_procs)
		self._update_tree_stable(self.tree_all, all_procs_sorted)

	def _update_tree_stable(self, tree, procs):
		"""Update tree in-place: rows in fixed alphabetical order, color-coded."""
		# build map of current items by PID
		existing = {}
		for item_id in tree.get_children():
			vals = tree.item(item_id, 'values')
			if vals:
				existing[int(vals[0])] = item_id

		# build map of new procs by PID
		new_procs = {p.get('pid'): p for p in procs}

		# remove items not in new list
		for pid, item_id in list(existing.items()):
			if pid not in new_procs:
				tree.delete(item_id)
				del existing[pid]

		# update or insert each process (procs already sorted alphabetically)
		for idx, p in enumerate(procs):
			pid = p.get('pid')
			cpu_val = p.get('cpu_percent') or 0
			mem_val = p.get('memory_percent') or 0
			values = (
				pid,
				p.get('name')[:30] if p.get('name') else "",
				p.get('username') or "",
				f"{cpu_val:.1f}",
				f"{mem_val:.2f}",
				p.get('status') or ""
			)
			
			# determine color tags
			tags = ['evenrow' if idx % 2 == 0 else 'oddrow']
			if cpu_val > 50:
				tags.append('high_cpu')
			elif cpu_val > 20:
				tags.append('medium_cpu')
			else:
				tags.append('low_cpu')

			if pid in existing:
				# update in-place
				item_id = existing[pid]
				tree.item(item_id, values=values, tags=tags)
				# move to correct alphabetical position
				tree.move(item_id, '', idx)
			else:
				# insert new at correct position
				tree.insert("", idx, values=values, tags=tags)

	def _get_selected_pid(self):
		# check both tables (prefer tree_all)
		sel = self.tree_all.selection()
		if not sel:
			sel = self.tree_top.selection()
		if not sel:
			return None
		item = self.tree_all.item(sel[0]) if sel in self.tree_all.get_children() else self.tree_top.item(sel[0])
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
			msg = "✓ Killed" if ok else f"✗ Failed: {err}"
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
			msg = "✓ Suspended" if ok else f"✗ Failed: {err}"
			messagebox.showinfo("Suspend", msg)
			self._refresh_processes()
		threading.Thread(target=task, daemon=True).start()