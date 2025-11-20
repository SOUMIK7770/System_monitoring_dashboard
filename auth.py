import bcrypt
from .db import DBHelper

class AuthManager:
	def __init__(self, db_helper: DBHelper):
		self.db = db_helper
		self._ensure_default_admin()

	def _ensure_default_admin(self):
		conn = self.db.conn()
		c = conn.cursor()
		c.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
		if c.fetchone()[0] == 0:
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
		except Exception:
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
		return ok, role if ok else None
