import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

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
