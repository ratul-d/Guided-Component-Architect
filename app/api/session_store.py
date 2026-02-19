from typing import Dict, Optional
from threading import Lock

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, str] = {}
        self.lock = Lock()

    def get_previous_code(self, session_id: str) -> Optional[str]:
        with self.lock:
            return self.sessions.get(session_id)

    def save_code(self, session_id: str, code: str):
        with self.lock:
            self.sessions[session_id] = code

    def reset(self, session_id: str):
        with self.lock:
            self.sessions.pop(session_id, None)

session_store = SessionStore()