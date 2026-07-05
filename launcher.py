"""
AuroraOS Launcher
Main entry point for the operating system
Handles boot sequence, authentication, and shell launch
"""

import sys
import os
import time
import tkinter as tk
from tkinter import messagebox

# Force stdout/stderr to use UTF-8 to prevent charmap UnicodeEncodeErrors in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user.auth.authentication import get_auth_manager
from user.session.session_manager import get_session_manager
from system.core.filesystem import get_filesystem

# ============================================================================
# AURORA THEME COLORS
# ============================================================================

BG_PRIMARY = "#0A0E27"
BG_SECONDARY = "#1A1F3A"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#B8C1EC"
ACCENT = "#00D9FF"
ACCENT_SECONDARY = "#9D4EDD"
ERROR = "#EF4444"


# ============================================================================
# BOOT SCREEN
# ============================================================================

class BootScreen:
    """System boot screen with loading animation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AuroraOS")
        self.root.geometry("600x400")
        self.root.configure(bg=BG_PRIMARY)
        self.root.overrideredirect(True)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create boot screen UI"""
        # Logo
        tk.Label(
            self.root,
            text="🌌",
            font=('Segoe UI', 80),
            bg=BG_PRIMARY,
            fg=ACCENT,
            pady=30
        ).pack()
        
        # Title
        tk.Label(
            self.root,
            text="AuroraOS",
            font=('Segoe UI', 36, 'bold'),
            bg=BG_PRIMARY,
            fg=ACCENT
        ).pack()
        
        tk.Label(
            self.root,
            text="Northern Lights Edition",
            font=('Segoe UI', 14),
            bg=BG_PRIMARY,
            fg=TEXT_SECONDARY,
            pady=10
        ).pack()
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Initializing...",
            font=('Segoe UI', 11),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY,
            pady=30
        )
        self.status_label.pack()
        
        # Progress animation
        self.progress_frame = tk.Frame(self.root, bg=BG_PRIMARY)
        self.progress_frame.pack(pady=20)
        
        self.progress_dots = []
        for i in range(5):
            dot = tk.Label(
                self.progress_frame,
                text="●",
                font=('Segoe UI', 20),
                bg=BG_PRIMARY,
                fg=BG_SECONDARY
            )
            dot.pack(side=tk.LEFT, padx=5)
            self.progress_dots.append(dot)
    
    def update_status(self, text):
        """Update status text"""
        self.status_label.config(text=text)
        self.root.update()
    
    def animate_progress(self, step):
        """Animate progress dots"""
        for i, dot in enumerate(self.progress_dots):
            if i <= step % len(self.progress_dots):
                dot.config(fg=ACCENT)
            else:
                dot.config(fg=BG_SECONDARY)
        self.root.update()
    
    def close(self):
        """Close boot screen"""
        self.root.destroy()


# ============================================================================
# LOGIN SCREEN
# ============================================================================

class LoginScreen:
    """User login screen"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AuroraOS Login")
        self.root.geometry("500x600")
        self.root.configure(bg=BG_PRIMARY)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"500x600+{x}+{y}")
        
        self.auth_manager = get_auth_manager()
        self.session_manager = get_session_manager()
        self.authenticated = False
        self.username = None
        
        self._create_ui()
        
    def _create_ui(self):
        """Create login UI"""
        # Logo
        tk.Label(
            self.root,
            text="🌌",
            font=('Segoe UI', 60),
            bg=BG_PRIMARY,
            fg=ACCENT,
            pady=30
        ).pack()
        
        # Title
        tk.Label(
            self.root,
            text="Welcome to AuroraOS",
            font=('Segoe UI', 24, 'bold'),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY
        ).pack()
        
        tk.Label(
            self.root,
            text="Please sign in to continue",
            font=('Segoe UI', 11),
            bg=BG_PRIMARY,
            fg=TEXT_SECONDARY,
            pady=10
        ).pack()
        
        # Login form
        form_frame = tk.Frame(self.root, bg=BG_SECONDARY)
        form_frame.pack(pady=40, padx=60, fill=tk.BOTH)
        
        # Username
        tk.Label(
            form_frame,
            text="Username",
            font=('Segoe UI', 11),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, padx=30, pady=(30, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 12),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT,
            border=0,
            relief=tk.FLAT
        )
        self.username_entry.pack(fill=tk.X, padx=30, pady=5, ipady=8)
        self.username_entry.insert(0, "aurora")
        
        # Password
        tk.Label(
            form_frame,
            text="Password",
            font=('Segoe UI', 11),
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, padx=30, pady=(20, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 12),
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT,
            show="●",
            border=0,
            relief=tk.FLAT
        )
        self.password_entry.pack(fill=tk.X, padx=30, pady=5, ipady=8)
        self.password_entry.insert(0, "admin123")
        
        # Error label
        self.error_label = tk.Label(
            form_frame,
            text="",
            font=('Segoe UI', 10),
            bg=BG_SECONDARY,
            fg=ERROR,
            pady=10
        )
        self.error_label.pack()
        
        # Login button
        login_btn = tk.Button(
            form_frame,
            text="Sign In",
            font=('Segoe UI', 12, 'bold'),
            bg=ACCENT,
            fg=TEXT_PRIMARY,
            activebackground=ACCENT_SECONDARY,
            border=0,
            cursor='hand2',
            command=self._do_login,
            pady=12
        )
        login_btn.pack(fill=tk.X, padx=30, pady=(10, 30))
        
        # Bind enter key
        self.password_entry.bind('<Return>', lambda e: self._do_login())
        
        # Help text
        tk.Label(
            self.root,
            text="Default credentials:\nUsername: aurora | Password: admin123",
            font=('Segoe UI', 9),
            bg=BG_PRIMARY,
            fg=TEXT_SECONDARY,
            justify=tk.CENTER,
            pady=20
        ).pack()
        
        self.username_entry.focus()
    
    def _do_login(self):
        """Perform login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.config(text="⚠️ Please enter username and password")
            return
        
        # Authenticate
        if self.auth_manager.authenticate(username, password):
            # Get user info
            user = self.auth_manager.get_user(username)
            
            if user:
                # Create session
                self.session_manager.create_session(
                    username,
                    user.full_name,
                    user.is_admin
                )
                
                self.authenticated = True
                self.username = username
                self.root.destroy()
            else:
                self.error_label.config(text="⚠️ User data not found")
        else:
            self.error_label.config(text="⚠️ Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def run(self):
        """Run login screen"""
        self.root.mainloop()
        return self.authenticated


# ============================================================================
# MAIN LAUNCHER
# ============================================================================

def print_banner():
    """Print AuroraOS banner"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║              🌌  A U R O R A   O S  🌌                        ║")
    print("║                                                              ║")
    print("║                 Northern Lights Edition                      ║")
    print("║                       Version 1.0.0                          ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n")


def boot_system():
    """Boot the system with loading screen"""
    print_banner()
    print("[BOOT] Starting AuroraOS boot sequence...")
    
    # Show boot screen
    boot_screen = BootScreen()
    
    # Boot steps
    steps = [
        ("Initializing kernel...", 0.5),
        ("Loading system services...", 0.7),
        ("Mounting file system...", 0.6),
        ("Starting network services...", 0.5),
        ("Preparing user environment...", 0.6),
        ("Boot complete!", 0.5)
    ]
    
    for i, (status, delay) in enumerate(steps):
        boot_screen.update_status(status)
        boot_screen.animate_progress(i)
        time.sleep(delay)
    
    boot_screen.close()
    print("[BOOT] ✓ System boot complete!\n")


def compile_kernel():
    """Try to compile the C kernel DLL on boot if gcc is available"""
    import subprocess
    import platform
    
    sys_os = platform.system()
    if sys_os == "Windows":
        lib_name = "kernel.dll"
    elif sys_os == "Darwin":
        lib_name = "kernel.dylib"
    else:
        lib_name = "kernel.so"
        
    if os.path.exists(lib_name):
        return
        
    print(f"[BOOT] C kernel library ({lib_name}) not found. Attempting auto-compilation...")
    try:
        # Check if gcc is installed
        result = subprocess.run(["gcc", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("[BOOT] gcc compiler found. Compiling C kernel...")
            # Run compilation command
            compile_cmd = [
                "gcc", "-shared", "-o", lib_name,
                "-Ikernel/include",
                "kernel/src/kernel.c", "kernel/src/memory.c"
            ]
            compile_res = subprocess.run(compile_cmd, capture_output=True, text=True, check=False)
            if compile_res.returncode == 0:
                print(f"[BOOT] ✓ C kernel compiled successfully as {lib_name}!")
            else:
                print(f"[BOOT] Warning: Auto-compilation failed: {compile_res.stderr}")
        else:
            print("[BOOT] Warning: gcc compiler not found. Fallback to simulated kernel.")
    except Exception as e:
        print(f"[BOOT] Warning: Could not check/compile C kernel: {e}")


def initialize_system():
    """Initialize system components"""
    print("[INIT] Initializing system components...")
    
    # Try to compile kernel DLL if missing
    compile_kernel()
    
    # Initialize file system
    print("[INIT] Initializing virtual file system...")
    vfs = get_filesystem()
    
    # Initialize authentication
    print("[INIT] Loading user authentication system...")
    auth = get_auth_manager()
    
    # Initialize session manager
    print("[INIT] Starting session manager...")
    session = get_session_manager()
    
    # Initialize C Kernel Connection
    print("[INIT] Connecting to C Kernel...")
    try:
        from system.core.kernel_connector import get_kernel_connector
        get_kernel_connector().kernel_init()
    except Exception as e:
        print(f"[INIT] Warning: Could not connect to C Kernel: {e}")
        
    print("[INIT] ✓ System initialization complete!\n")


def start_login():
    """Start login screen"""
    print("[LOGIN] Starting login screen...")
    
    login_screen = LoginScreen()
    authenticated = login_screen.run()
    
    if not authenticated:
        print("[LOGIN] Authentication cancelled. Shutting down...")
        return False
    
    print("[LOGIN] ✓ User authenticated successfully!\n")
    return True


def start_shell():
    """Start Aurora Shell"""
    print("[SHELL] Launching Aurora Shell...")
    
    from ui.shell.aurora_shell import AuroraShell
    
    shell = AuroraShell()
    shell.run()
    
    print(f"\n[SHELL] Shell terminated with status: {shell.exit_status}")
    return shell.exit_status


def shutdown_system():
    """Shutdown the system"""
    print("\n[SHUTDOWN] Shutting down AuroraOS...")
    
    # End session
    session_manager = get_session_manager()
    session_manager.end_session()
    
    # Shutdown C Kernel
    try:
        from system.core.kernel_connector import get_kernel_connector
        get_kernel_connector().kernel_shutdown()
    except Exception:
        pass
        
    print("[SHUTDOWN] ✓ Goodbye!")
    print("\n")


def main():
    """Main launcher entry point"""
    try:
        # Boot system
        boot_system()
        
        # Initialize components
        initialize_system()
        
        # Login and Shell Loop
        while True:
            if not start_login():
                break
            
            exit_status = start_shell()
            
            if exit_status == "logout":
                print("[SYSTEM] User logged out. Returning to login screen...")
                time.sleep(1)
                continue
            elif exit_status == "restart":
                print("[SYSTEM] Restarting system components...")
                initialize_system()
                continue
            else:
                # Includes "shutdown" or any other value
                break
        
        # Shutdown
        shutdown_system()
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Received keyboard interrupt")
        shutdown_system()
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        shutdown_system()


if __name__ == "__main__":
    main()
