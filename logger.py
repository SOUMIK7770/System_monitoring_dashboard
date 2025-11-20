from datetime import datetime
from .db import DBHelper

class ActionLogger:
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
