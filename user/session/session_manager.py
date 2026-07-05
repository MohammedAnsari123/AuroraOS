"""
AuroraOS Session Manager
Manages user sessions after authentication
"""

import json
import time
import os
from typing import Optional, Dict
from datetime import datetime

SESSION_FILE = "config/user/session.json"

class UserSession:
    """Represents an active user session"""
    
    def __init__(self, username: str, full_name: str, is_admin: bool):
        self.username = username
        self.full_name = full_name
        self.is_admin = is_admin
        self.login_time = time.time()
        self.last_activity = time.time()
        self.session_id = f"{username}_{int(self.login_time)}"
        
    def update_activity(self):
        """Update last activity time"""
        self.last_activity = time.time()
    
    def get_session_duration(self) -> int:
        """Get session duration in seconds"""
        return int(time.time() - self.login_time)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'username': self.username,
            'full_name': self.full_name,
            'is_admin': self.is_admin,
            'login_time': self.login_time,
            'last_activity': self.last_activity,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserSession':
        """Create from dictionary"""
        session = cls(
            data['username'],
            data['full_name'],
            data['is_admin']
        )
        session.login_time = data['login_time']
        session.last_activity = data['last_activity']
        session.session_id = data['session_id']
        return session


class SessionManager:
    """Manages user sessions"""
    
    def __init__(self):
        self.current_session: Optional[UserSession] = None
        self._load_session()
    
    def _load_session(self):
        """Load existing session if any"""
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    if data:
                        self.current_session = UserSession.from_dict(data)
                        print(f"[SESSION] Restored session for '{self.current_session.username}'")
        except Exception as e:
            print(f"[SESSION] Could not load session: {e}")
    
    def _save_session(self):
        """Save current session"""
        try:
            os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
            with open(SESSION_FILE, 'w') as f:
                if self.current_session:
                    json.dump(self.current_session.to_dict(), f, indent=2)
                else:
                    json.dump({}, f)
        except Exception as e:
            print(f"[SESSION] Error saving session: {e}")
    
    def create_session(self, username: str, full_name: str, is_admin: bool) -> UserSession:
        """Create a new user session"""
        self.current_session = UserSession(username, full_name, is_admin)
        self._save_session()
        print(f"[SESSION] [OK] Created session for '{username}'")
        return self.current_session
    
    def end_session(self):
        """End the current session"""
        if self.current_session:
            print(f"[SESSION] Ending session for '{self.current_session.username}'")
            duration = self.current_session.get_session_duration()
            print(f"[SESSION] Session duration: {duration // 60} min {duration % 60} sec")
            self.current_session = None
            self._save_session()
    
    def get_current_session(self) -> Optional[UserSession]:
        """Get current active session"""
        if self.current_session:
            self.current_session.update_activity()
            self._save_session()
        return self.current_session
    
    def is_active(self) -> bool:
        """Check if there's an active session"""
        return self.current_session is not None


# Global session manager
session_manager = None

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager
