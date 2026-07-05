"""
AuroraOS Terminal Emulator
Command-line interface with Aurora theme
"""

import tkinter as tk
from tkinter import scrolledtext
import sys
import os

# Add system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from system.core.filesystem import get_filesystem
from user.session.session_manager import get_session_manager

try:
    from ui.themes.colors import CURRENT_THEME as Theme
except ImportError:
    class Theme:
        BG_PRIMARY = "#0A0E27"
        BG_SECONDARY = "#1A1F3A"
        TEXT_PRIMARY = "#FFFFFF"
        TEXT_SECONDARY = "#B8C1EC"
        ACCENT = "#00D9FF"
        SUCCESS = "#10B981"
        ERROR = "#EF4444"

# Global colors for easy reference and callback defaults
TEXT_PRIMARY = Theme.TEXT_PRIMARY
TEXT_SECONDARY = Theme.TEXT_SECONDARY
ACCENT = Theme.ACCENT
BG_PRIMARY = Theme.BG_PRIMARY
BG_SECONDARY = Theme.BG_SECONDARY
SUCCESS = Theme.SUCCESS
ERROR = Theme.ERROR



class TerminalApp:
    """Terminal emulator application"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("AuroraOS Terminal")
        self.window.geometry("800x600")
        self.window.configure(bg=Theme.BG_PRIMARY)
        
        self.vfs = get_filesystem()
        self.current_dir = "/home/aurora"
        self.command_history = []
        self.history_index = 0
        
        self._create_ui()
        self._print_welcome()
        
    def _create_ui(self):
        """Create terminal UI"""
        # Output area
        self.output = scrolledtext.ScrolledText(
            self.window,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.ACCENT,
            font=('Consolas', 10),
            wrap=tk.WORD,
            border=0,
            padx=10,
            pady=10
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=40)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        input_frame.pack_propagate(False)
        
        # Prompt label
        self.prompt_label = tk.Label(
            input_frame,
            text=f"aurora@aurora:~$ ",
            bg=Theme.BG_SECONDARY,
            fg=Theme.ACCENT,
            font=('Consolas', 10, 'bold')
        )
        self.prompt_label.pack(side=tk.LEFT, padx=5)
        
        # Command input
        self.input = tk.Entry(
            input_frame,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.ACCENT,
            font=('Consolas', 10),
            border=0
        )
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input.bind('<Return>', self._on_submit)
        self.input.bind('<Up>', self._history_up)
        self.input.bind('<Down>', self._history_down)
        self.input.focus()
    
    def _print_welcome(self):
        """Print welcome message"""
        self._print_output("╔═══════════════════════════════════════════════════════╗")
        self._print_output("║         🌌 AuroraOS Terminal v1.0 🌌                  ║")
        self._print_output("╚═══════════════════════════════════════════════════════╝")
        self._print_output("")
        self._print_output("Welcome to Aurora Terminal!")
        self._print_output("Type 'help' for available commands.")
        self._print_output("")
    
    def _print_output(self, text, color=TEXT_PRIMARY):
        """Print text to output"""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
    
    def _print_prompt(self):
        """Print command prompt"""
        short_dir = self.current_dir.replace('/home/aurora', '~')
        self._print_output(f"\naurora@aurora:{short_dir}$ ", ACCENT)
    
    def _on_submit(self, event):
        """Handle command submission"""
        command = self.input.get().strip()
        self.input.delete(0, tk.END)
        
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Echo command
        short_dir = self.current_dir.replace('/home/aurora', '~')
        self._print_output(f"aurora@aurora:{short_dir}$ {command}", TEXT_SECONDARY)
        
        # Execute command
        self._execute_command(command)
    
    def _history_up(self, event):
        """Navigate command history up"""
        if self.history_index > 0:
            self.history_index -= 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self.command_history[self.history_index])
    
    def _history_down(self, event):
        """Navigate command history down"""
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.input.delete(0, tk.END)
    
    def _execute_command(self, command):
        """Execute terminal command"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0]
        args = parts[1:]
        
        # Command routing
        commands = {
            'help': self._cmd_help,
            'clear': self._cmd_clear,
            'ls': self._cmd_ls,
            'cd': self._cmd_cd,
            'pwd': self._cmd_pwd,
            'cat': self._cmd_cat,
            'echo': self._cmd_echo,
            'mkdir': self._cmd_mkdir,
            'touch': self._cmd_touch,
            'rm': self._cmd_rm,
            'whoami': self._cmd_whoami,
            'date': self._cmd_date,
            'uptime': self._cmd_uptime,
            'sysinfo': self._cmd_sysinfo,
            'kstats': self._cmd_kstats,
            'exit': self._cmd_exit,
        }
        
        if cmd in commands:
            commands[cmd](args)
        else:
            self._print_output(f"aurora: command not found: {cmd}", ERROR)
    
    def _cmd_help(self, args):
        """Show help"""
        self._print_output("\nAvailable commands:")
        self._print_output("  help      - Show this help message")
        self._print_output("  clear     - Clear the terminal")
        self._print_output("  ls        - List directory contents")
        self._print_output("  cd <dir>  - Change directory")
        self._print_output("  pwd       - Print working directory")
        self._print_output("  cat <file>- Display file contents")
        self._print_output("  echo <msg>- Print message")
        self._print_output("  mkdir <d> - Create directory")
        self._print_output("  touch <f> - Create empty file")
        self._print_output("  rm <path> - Remove file/directory")
        self._print_output("  whoami    - Show current user")
        self._print_output("  date      - Show current date/time")
        self._print_output("  uptime    - Show system uptime")
        self._print_output("  sysinfo   - Show system information")
        self._print_output("  kstats    - Show low-level C Kernel diagnostics")
        self._print_output("  exit      - Close terminal")
    
    def _cmd_clear(self, args):
        """Clear terminal"""
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.config(state=tk.DISABLED)
        self._print_welcome()
        
    def _cmd_kstats(self, args):
        """Show low-level C Kernel statistics"""
        try:
            from system.core.kernel_connector import get_kernel_connector
            conn = get_kernel_connector()
            
            self._print_output("\n🌌 Aurora C-Kernel Diagnostics", ACCENT)
            self._print_output("─" * 50, TEXT_SECONDARY)
            
            # Linking Mode
            mode_str = "Dynamic DLL linking (CTypes)" if not conn.use_simulator else "Python Simulator (Fallback)"
            self._print_output(f"Linking Mode:  {mode_str}")
            self._print_output(f"Kernel Uptime: {conn.get_uptime()} ms")
            
            # Memory Info
            mem = conn.memory_get_info()
            self._print_output("\n[MEMORY INFO]", ACCENT)
            self._print_output(f"  Total Heap Memory: {mem['total_memory'] / 1024:.2f} MB ({mem['total_memory']} KB)")
            self._print_output(f"  Used Heap Memory:  {mem['used_memory'] / 1024:.2f} MB ({mem['used_memory']} KB)")
            self._print_output(f"  Free Heap Memory:  {mem['free_memory'] / 1024:.2f} MB ({mem['free_memory']} KB)")
            
            # Processes
            procs = conn.get_process_list()
            self._print_output("\n[PROCESS LIST]", ACCENT)
            self._print_output(f"  {'PID':<5} {'NAME':<15} {'PRIORITY':<10} {'STATE':<10} {'CPU TIME':<10}", TEXT_SECONDARY)
            self._print_output(f"  " + "─" * 45, TEXT_SECONDARY)
            
            # Map state enum to string
            state_map = {
                0: "NEW",
                1: "READY",
                2: "RUNNING",
                3: "WAITING",
                4: "TERMINATED"
            }
            
            for p in procs:
                state_str = state_map.get(p['state'], f"UNKNOWN ({p['state']})")
                self._print_output(f"  {p['pid']:<5} {p['name']:<15} {p['priority']:<10} {state_str:<10} {p['cpu_time']:<10}")
                
            self._print_output("\n  Use 'touch'/'mkdir' to interact with virtual disk. C-Kernel manages heap allocations.\n")
        except Exception as e:
            self._print_output(f"Error reading kernel stats: {e}", ERROR)
    
    def _cmd_ls(self, args):
        """List directory"""
        path = args[0] if args else self.current_dir
        files = self.vfs.list_dir(path)
        
        if not files:
            self._print_output("(empty directory)")
            return
        
        for f in files:
            color = ACCENT if f['type'] == 'dir' else TEXT_PRIMARY
            icon = "📁" if f['type'] == 'dir' else "📄"
            self._print_output(f"{icon} {f['name']:<30} {f['size']:>10} bytes  {f['modified']}", color)
    
    def _cmd_cd(self, args):
        """Change directory"""
        if not args:
            self.current_dir = "/home/aurora"
            return
        
        path = args[0]
        if path == "..":
            if self.current_dir != "/":
                self.current_dir = os.path.dirname(self.current_dir) or "/"
        elif path.startswith("/"):
            # Absolute path
            if self.vfs._normalize_path(path) in self.vfs.inodes:
                self.current_dir = self.vfs._normalize_path(path)
            else:
                self._print_output(f"cd: no such directory: {path}", ERROR)
        else:
            # Relative path
            new_path = os.path.join(self.current_dir, path)
            new_path = self.vfs._normalize_path(new_path)
            if new_path in self.vfs.inodes:
                self.current_dir = new_path
            else:
                self._print_output(f"cd: no such directory: {path}", ERROR)
        
        # Update prompt
        short_dir = self.current_dir.replace('/home/aurora', '~')
        self.prompt_label.config(text=f"aurora@aurora:{short_dir}$ ")
    
    def _cmd_pwd(self, args):
        """Print working directory"""
        self._print_output(self.current_dir)
    
    def _cmd_cat(self, args):
        """Display file contents"""
        if not args:
            self._print_output("cat: missing file operand", ERROR)
            return
        
        path = args[0]
        if not path.startswith('/'):
            path = os.path.join(self.current_dir, path)
        
        content = self.vfs.read_file(path)
        if content is not None:
            self._print_output(content)
        else:
            self._print_output(f"cat: {args[0]}: No such file", ERROR)
    
    def _cmd_echo(self, args):
        """Echo message"""
        self._print_output(" ".join(args))
    
    def _cmd_mkdir(self, args):
        """Create directory"""
        if not args:
            self._print_output("mkdir: missing operand", ERROR)
            return
        
        path = args[0]
        if not path.startswith('/'):
            path = os.path.join(self.current_dir, path)
        
        if self.vfs.mkdir(path):
            self._print_output(f"✓ Created directory: {args[0]}", SUCCESS)
    
    def _cmd_touch(self, args):
        """Create empty file"""
        if not args:
            self._print_output("touch: missing operand", ERROR)
            return
        
        path = args[0]
        if not path.startswith('/'):
            path = os.path.join(self.current_dir, path)
        
        if self.vfs.create_file(path, ""):
            self._print_output(f"✓ Created file: {args[0]}", SUCCESS)
    
    def _cmd_rm(self, args):
        """Remove file/directory"""
        if not args:
            self._print_output("rm: missing operand", ERROR)
            return
        
        path = args[0]
        if not path.startswith('/'):
            path = os.path.join(self.current_dir, path)
        
        if self.vfs.delete_file(path):
            self._print_output(f"✓ Removed: {args[0]}", SUCCESS)
    
    def _cmd_whoami(self, args):
        """Show current user"""
        session = get_session_manager().get_current_session()
        if session:
            self._print_output(session.username)
        else:
            self._print_output("aurora")
    
    def _cmd_date(self, args):
        """Show current date/time"""
        from datetime import datetime
        self._print_output(datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p"))
    
    def _cmd_uptime(self, args):
        """Show system uptime"""
        self._print_output("System uptime: <simulated>")
    
    def _cmd_sysinfo(self, args):
        """Show system information"""
        self._print_output("\n🌌 AuroraOS System Information")
        self._print_output("─" * 40)
        self._print_output("OS Name:      AuroraOS")
        self._print_output("Version:      1.0.0 Northern Lights")
        self._print_output("Kernel:       Aurora Kernel 1.0")
        self._print_output("Architecture: x86_64 (simulated)")
        self._print_output("Memory:       128 MB")
        
        # Disk usage
        usage = self.vfs.get_disk_usage()
        self._print_output(f"Disk Usage:   {usage['percent']:.1f}% used")
    
    def _cmd_exit(self, args):
        """Exit terminal"""
        self.window.destroy()


def main():
    """Main entry point"""
    app = TerminalApp()
    app.window.mainloop()


if __name__ == "__main__":
    main()
