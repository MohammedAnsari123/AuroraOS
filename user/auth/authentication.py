"""
AuroraOS User Authentication System
Handles user login, password management, and session creation
"""

import hashlib
import json
import os
import time
from typing import Optional, Dict
from datetime import datetime

# ============================================================================
# CONSTANTS
# ============================================================================

USERS_FILE = "config/user/users.json"
SESSION_FILE = "config/user/session.json"
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_TIME = 300  # 5 minutes

# ============================================================================
# USER CLASS
# ============================================================================

class User:
    """Represents a user account"""
    
    def __init__(self, username: str, password_hash: str, full_name: str = "",
                 is_admin: bool = False):
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name or username
        self.is_admin = is_admin
        self.created = time.time()
        self.last_login: Optional[float] = None
        self.login_count = 0
        
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'full_name': self.full_name,
            'is_admin': self.is_admin,
            'created': self.created,
            'last_login': self.last_login,
            'login_count': self.login_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create from dictionary"""
        user = cls(
            data['username'],
            data['password_hash'],
            data.get('full_name', data['username']),
            data.get('is_admin', False)
        )
        user.created = data.get('created', time.time())
        user.last_login = data.get('last_login')
        user.login_count = data.get('login_count', 0)
        return user


# ============================================================================
# AUTHENTICATION MANAGER
# ============================================================================

class AuthenticationManager:
    """Manages user authentication and sessions"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_session = None
        self.failed_attempts = {}
        self.lockout_until = {}
        
        # Ensure config directory exists
        os.makedirs("config/user", exist_ok=True)
        
        # Load existing users or create default
        self._load_users()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self):
        """Load users from file"""
        try:
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    data = json.load(f)
                    self.users = {
                        username: User.from_dict(user_data)
                        for username, user_data in data.items()
                    }
                print(f"[AUTH] Loaded {len(self.users)} user(s)")
            else:
                # Create default user
                self._create_default_users()
        except Exception as e:
            print(f"[AUTH] Error loading users: {e}")
            self._create_default_users()
    
    def _create_default_users(self):
        """Create default user accounts"""
        print("[AUTH] Creating default user accounts...")
        
        # Create admin user
        admin = User(
            "aurora",
            self._hash_password("admin123"),
            "Aurora Administrator",
            is_admin=True
        )
        self.users["aurora"] = admin
        
        # Create guest user
        guest = User(
            "guest",
            self._hash_password("guest"),
            "Guest User",
            is_admin=False
        )
        self.users["guest"] = guest
        
        self._save_users()
        print("[AUTH] [OK] Default users created")
        print("[AUTH]   Username: aurora | Password: admin123")
        print("[AUTH]   Username: guest  | Password: guest")
    
    def _save_users(self):
        """Save users to file"""
        try:
            data = {
                username: user.to_dict()
                for username, user in self.users.items()
            }
            with open(USERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AUTH] Error saving users: {e}")
    
    def _is_locked_out(self, username: str) -> bool:
        """Check if user is locked out"""
        if username in self.lockout_until:
            if time.time() < self.lockout_until[username]:
                return True
            else:
                # Lockout expired
                del self.lockout_until[username]
                self.failed_attempts[username] = 0
        return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user credentials
        Returns True if authentication successful, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(username):
            remaining = int(self.lockout_until[username] - time.time())
            print(f"[AUTH] Account locked. Try again in {remaining} seconds")
            return False
        
        # Check if user exists
        if username not in self.users:
            print(f"[AUTH] User '{username}' not found")
            self._record_failed_attempt(username)
            return False
        
        # Verify password
        user = self.users[username]
        password_hash = self._hash_password(password)
        
        if password_hash != user.password_hash:
            print(f"[AUTH] Invalid password for user '{username}'")
            self._record_failed_attempt(username)
            return False
        
        # Authentication successful
        print(f"[AUTH] [OK] User '{username}' authenticated successfully")
        
        # Update user info
        user.last_login = time.time()
        user.login_count += 1
        self._save_users()
        
        # Reset failed attempts
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        
        return True
    
    def _record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = 0
        
        self.failed_attempts[username] += 1
        
        if self.failed_attempts[username] >= MAX_LOGIN_ATTEMPTS:
            self.lockout_until[username] = time.time() + LOCKOUT_TIME
            print(f"[AUTH] ⚠️  Account '{username}' locked for {LOCKOUT_TIME} seconds")
    
    def create_user(self, username: str, password: str, full_name: str = "",
                   is_admin: bool = False) -> bool:
        """Create a new user account"""
        if username in self.users:
            print(f"[AUTH] User '{username}' already exists")
            return False
        
        user = User(
            username,
            self._hash_password(password),
            full_name,
            is_admin
        )
        
        self.users[username] = user
        self._save_users()
        
        print(f"[AUTH] [OK] Created user '{username}'")
        return True
    
    def change_password(self, username: str, old_password: str,
                       new_password: str) -> bool:
        """Change user password"""
        if not self.authenticate(username, old_password):
            return False
        
        user = self.users[username]
        user.password_hash = self._hash_password(new_password)
        self._save_users()
        
        print(f"[AUTH] [OK] Password changed for user '{username}'")
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user account"""
        if username not in self.users:
            print(f"[AUTH] User '{username}' not found")
            return False
        
        if username == "aurora":
            print("[AUTH] Cannot delete default admin user")
            return False
        
        del self.users[username]
        self._save_users()
        
        print(f"[AUTH] [OK] Deleted user '{username}'")
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
    
    def list_users(self) -> list:
        """List all users"""
        return [
            {
                'username': user.username,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'last_login': datetime.fromtimestamp(user.last_login).strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'login_count': user.login_count
            }
            for user in self.users.values()
        ]


# ============================================================================
# GLOBAL AUTHENTICATION MANAGER
# ============================================================================

auth_manager = None

def get_auth_manager() -> AuthenticationManager:
    """Get global authentication manager instance"""
    global auth_manager
    if auth_manager is None:
        auth_manager = AuthenticationManager()
    return auth_manager
