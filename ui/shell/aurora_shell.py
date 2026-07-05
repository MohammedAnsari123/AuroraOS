"""
AuroraOS Shell - Main GUI
Modern, futuristic desktop interface with Aurora theme
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# AURORA THEME COLORS
# ============================================================================

try:
    from ui.themes.colors import CURRENT_THEME as AuroraTheme
except ImportError:
    # Fallback if colors.py is not available
    class AuroraTheme:
        DEEP_BLACK = "#0A0E27"
        DARK_BLUE = "#1A1F3A"
        MIDNIGHT = "#151934"
        NEON_BLUE = "#5E60CE"
        PURPLE = "#9D4EDD"
        TEAL = "#00D9FF"
        CYAN = "#00F5FF"
        PINK = "#FF006E"
        BG_PRIMARY = DEEP_BLACK
        BG_SECONDARY = DARK_BLUE
        BG_TERTIARY = MIDNIGHT
        TEXT_PRIMARY = "#FFFFFF"
        TEXT_SECONDARY = "#B8C1EC"
        TEXT_TERTIARY = "#6B7280"
        ACCENT = TEAL
        ACCENT_SECONDARY = PURPLE
        SUCCESS = "#10B981"
        WARNING = "#F59E0B"
        ERROR = "#EF4444"
        GLOW_ACCENT = "#00D9FF40"


# ============================================================================
# AURORA SHELL
# ============================================================================

class AuroraShell:
    """Main AuroraOS desktop shell"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AuroraOS")
        self.root.geometry("1200x800")
        self.root.configure(bg=AuroraTheme.BG_PRIMARY)
        
        # Session data
        self.username = "aurora"
        self.is_fullscreen = False
        self.exit_status = "shutdown" # default
        
        # Configure styles
        self._configure_styles()
        
        # Create UI components
        self._create_desktop()
        self._create_taskbar()
        
        # Start clock update
        self._update_clock()
        
    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure(
            'Aurora.TButton',
            background=AuroraTheme.BG_SECONDARY,
            foreground=AuroraTheme.TEXT_PRIMARY,
            borderwidth=0,
            focuscolor=AuroraTheme.ACCENT,
            padding=10
        )
        
        style.map('Aurora.TButton',
            background=[('active', AuroraTheme.ACCENT)],
            foreground=[('active', AuroraTheme.TEXT_PRIMARY)]
        )
        
        # Configure label style
        style.configure(
            'Aurora.TLabel',
            background=AuroraTheme.BG_PRIMARY,
            foreground=AuroraTheme.TEXT_PRIMARY,
            font=('Segoe UI', 10)
        )
        
    def _create_desktop(self):
        """Create desktop area"""
        # Desktop frame
        self.desktop = tk.Frame(
            self.root,
            bg=AuroraTheme.BG_PRIMARY
        )
        self.desktop.pack(fill=tk.BOTH, expand=True)
        
        # Welcome widget
        self._create_welcome_widget()
        
        # Desktop icons area
        self.icons_frame = tk.Frame(
            self.desktop,
            bg=AuroraTheme.BG_PRIMARY
        )
        self.icons_frame.place(x=20, y=20)
        
        # Create desktop shortcuts
        self._create_desktop_icons()
    
    def _create_welcome_widget(self):
        """Create welcome widget in center"""
        welcome_frame = tk.Frame(
            self.desktop,
            bg=AuroraTheme.BG_SECONDARY,
            highlightbackground=AuroraTheme.ACCENT,
            highlightthickness=2
        )
        welcome_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            welcome_frame,
            text="🌌 Welcome to AuroraOS",
            font=('Segoe UI', 32, 'bold'),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.ACCENT,
            pady=20,
            padx=40
        )
        title_label.pack()
        
        # Subtitle
        subtitle = tk.Label(
            welcome_frame,
            text="Northern Lights • Educational OS",
            font=('Segoe UI', 14),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.TEXT_SECONDARY,
            pady=10
        )
        subtitle.pack()
        
        # User info
        user_info = tk.Label(
            welcome_frame,
            text=f"Logged in as: {self.username}",
            font=('Segoe UI', 11),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.TEXT_TERTIARY,
            pady=10,
            padx=40
        )
        user_info.pack()
        
        # Quick action buttons
        actions_frame = tk.Frame(welcome_frame, bg=AuroraTheme.BG_SECONDARY, pady=20)
        actions_frame.pack()
        
        self._create_action_button(actions_frame, "📁 File Manager", self.open_file_manager)
        self._create_action_button(actions_frame, "📟 Terminal", self.open_terminal)
        self._create_action_button(actions_frame, "⚙️ Settings", self.open_settings)
        
        # Second row of quick actions
        actions_frame2 = tk.Frame(welcome_frame, bg=AuroraTheme.BG_SECONDARY, pady=5)
        actions_frame2.pack()
        
        self._create_action_button(actions_frame2, "➕ Calculator", self.open_calculator)
        self._create_action_button(actions_frame2, "📅 Calendar", self.open_calendar)
        self._create_action_button(actions_frame2, "📊 Monitor", self.open_monitor)
    
    def _create_action_button(self, parent, text, command):
        """Create styled action button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 11),
            bg=AuroraTheme.ACCENT,
            fg=AuroraTheme.TEXT_PRIMARY,
            activebackground=AuroraTheme.ACCENT_SECONDARY,
            activeforeground=AuroraTheme.TEXT_PRIMARY,
            border=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=command
        )
        btn.pack(side=tk.LEFT, padx=10)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=AuroraTheme.ACCENT_SECONDARY))
        btn.bind('<Leave>', lambda e: btn.configure(bg=AuroraTheme.ACCENT))
    
    def _create_desktop_icons(self):
        """Create desktop shortcut icons"""
        icons = [
            ("💻 My Computer", self.open_system_info),
            ("📁 Files", self.open_file_manager),
            ("➕ Calculator", self.open_calculator),
            ("📅 Calendar", self.open_calendar),
            ("📊 Monitor", self.open_monitor),
            ("🎮 Tic-Tac-Toe", self.open_tictactoe),
            ("🗑️ Recycle Bin", self.open_recycle_bin),
        ]
        
        for i, (label, command) in enumerate(icons):
            self._create_desktop_icon(label, command, i)
    
    def _create_desktop_icon(self, text, command, index):
        """Create a single desktop icon"""
        icon_frame = tk.Frame(
            self.icons_frame,
            bg=AuroraTheme.BG_PRIMARY,
            cursor='hand2'
        )
        icon_frame.grid(row=index, column=0, pady=10)
        
        # Icon button
        btn = tk.Label(
            icon_frame,
            text=text.split()[0],  # Just the emoji
            font=('Segoe UI', 32),
            bg=AuroraTheme.BG_PRIMARY,
            fg=AuroraTheme.TEXT_PRIMARY,
            cursor='hand2'
        )
        btn.pack()
        
        # Label
        label = tk.Label(
            icon_frame,
            text=" ".join(text.split()[1:]),  # Text without emoji
            font=('Segoe UI', 9),
            bg=AuroraTheme.BG_PRIMARY,
            fg=AuroraTheme.TEXT_SECONDARY,
            cursor='hand2'
        )
        label.pack()
        
        # Bind click events
        for widget in [btn, label, icon_frame]:
            widget.bind('<Button-1>', lambda e, cmd=command: cmd())
            widget.bind('<Enter>', lambda e: label.configure(fg=AuroraTheme.ACCENT))
            widget.bind('<Leave>', lambda e: label.configure(fg=AuroraTheme.TEXT_SECONDARY))
    
    def _create_taskbar(self):
        """Create bottom taskbar"""
        self.taskbar = tk.Frame(
            self.root,
            bg=AuroraTheme.BG_SECONDARY,
            height=50,
            highlightbackground=AuroraTheme.ACCENT,
            highlightthickness=1
        )
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.taskbar.pack_propagate(False)
        
        # Start menu button
        self.start_btn = tk.Button(
            self.taskbar,
            text="⚡ Start",
            font=('Segoe UI', 11, 'bold'),
            bg=AuroraTheme.ACCENT,
            fg=AuroraTheme.TEXT_PRIMARY,
            activebackground=AuroraTheme.ACCENT_SECONDARY,
            border=0,
            padx=20,
            cursor='hand2',
            command=self.show_start_menu
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Quick launch icons
        self._create_taskbar_button("📁", self.open_file_manager, "File Manager")
        self._create_taskbar_button("📟", self.open_terminal, "Terminal")
        self._create_taskbar_button("📝", self.open_text_editor, "Text Editor")
        self._create_taskbar_button("➕", self.open_calculator, "Calculator")
        self._create_taskbar_button("📊", self.open_monitor, "System Monitor")
        
        # Spacer
        spacer = tk.Frame(self.taskbar, bg=AuroraTheme.BG_SECONDARY)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Shortcuts
        self.root.bind('<Control-space>', lambda e: self.open_command_palette())
        
        # System tray area
        self._create_system_tray()
        
        # Clock
        self.clock_label = tk.Label(
            self.taskbar,
            text="",
            font=('Segoe UI', 10),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.TEXT_PRIMARY,
            padx=15
        )
        self.clock_label.pack(side=tk.RIGHT, pady=5)
    
    def _create_taskbar_button(self, icon, command, tooltip):
        """Create taskbar quick launch button"""
        btn = tk.Button(
            self.taskbar,
            text=icon,
            font=('Segoe UI', 16),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.TEXT_PRIMARY,
            activebackground=AuroraTheme.ACCENT,
            border=0,
            width=3,
            cursor='hand2',
            command=command
        )
        btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Hover effect
        btn.bind('<Enter>', lambda e: btn.configure(bg=AuroraTheme.BG_TERTIARY))
        btn.bind('<Leave>', lambda e: btn.configure(bg=AuroraTheme.BG_SECONDARY))
    
    def _create_system_tray(self):
        """Create system tray with status icons"""
        tray_frame = tk.Frame(self.taskbar, bg=AuroraTheme.BG_SECONDARY)
        tray_frame.pack(side=tk.RIGHT, padx=10)
        
        # Network icon
        network_icon = tk.Label(
            tray_frame,
            text="📶",
            font=('Segoe UI', 12),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.SUCCESS,
            cursor='hand2'
        )
        network_icon.pack(side=tk.LEFT, padx=5)
        
        # Volume icon
        volume_icon = tk.Label(
            tray_frame,
            text="🔊",
            font=('Segoe UI', 12),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.TEXT_PRIMARY,
            cursor='hand2'
        )
        volume_icon.pack(side=tk.LEFT, padx=5)
        
        # Power icon
        power_icon = tk.Label(
            tray_frame,
            text="⚡",
            font=('Segoe UI', 12),
            bg=AuroraTheme.BG_SECONDARY,
            fg=AuroraTheme.SUCCESS,
            cursor='hand2'
        )
        power_icon.pack(side=tk.LEFT, padx=5)
    
    def _update_clock(self):
        """Update clock display"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%a, %b %d")
        
        self.clock_label.configure(text=f"{time_str}\n{date_str}")
        self.root.after(1000, self._update_clock)
    
    def show_start_menu(self):
        """Show start menu"""
        menu = tk.Menu(self.root, tearoff=0, bg=AuroraTheme.BG_SECONDARY,
                      fg=AuroraTheme.TEXT_PRIMARY, activebackground=AuroraTheme.ACCENT)
        
        menu.add_command(label="📁 File Manager", command=self.open_file_manager)
        menu.add_command(label="📟 Terminal", command=self.open_terminal)
        menu.add_command(label="📝 Text Editor", command=self.open_text_editor)
        menu.add_separator()
        menu.add_command(label="➕ Calculator", command=self.open_calculator)
        menu.add_command(label="📅 Calendar", command=self.open_calendar)
        menu.add_command(label="📊 System Monitor", command=self.open_monitor)
        menu.add_command(label="🎮 Tic-Tac-Toe", command=self.open_tictactoe)
        menu.add_separator()
        menu.add_command(label="💻 System Info", command=self.open_system_info)
        menu.add_command(label="⚙️ Settings", command=self.open_settings)
        menu.add_separator()
        menu.add_command(label="🔒 Lock", command=self.lock_system)
        menu.add_command(label="🔄 Restart", command=self.restart_system)
        menu.add_command(label="🔌 Shutdown", command=self.shutdown_system)
        
        # Display menu at start button
        x = self.start_btn.winfo_rootx()
        y = self.start_btn.winfo_rooty() - 200
        menu.post(x, y)
    
    # ========================================================================
    # APPLICATION LAUNCHERS
    # ========================================================================
    
    def open_file_manager(self):
        """Launch file manager"""
        print("[SHELL] Launching File Manager...")
        # This will be implemented in a separate file
        try:
            from apps.filemanager.file_manager import FileManagerApp
            FileManagerApp(self.root)
        except Exception as e:
            messagebox.showinfo("File Manager", "File Manager will open here")
    
    def open_terminal(self):
        """Launch terminal"""
        print("[SHELL] Launching Terminal...")
        try:
            from apps.terminal.terminal import TerminalApp
            TerminalApp(self.root)
        except Exception as e:
            messagebox.showinfo("Terminal", "Terminal will open here")
    
    def open_text_editor(self):
        """Launch text editor"""
        print("[SHELL] Launching Text Editor...")
        try:
            from apps.editor.text_editor import TextEditorApp
            TextEditorApp(self.root)
        except Exception as e:
            messagebox.showinfo("Text Editor", "Text Editor will open here")
    
    def open_settings(self):
        """Launch settings"""
        print("[SHELL] Launching Settings...")
        try:
            from apps.settings.settings import SettingsApp
            SettingsApp(self.root)
        except Exception as e:
            messagebox.showinfo("Settings", "Settings will open here")
    
    def open_calculator(self):
        """Launch calculator"""
        print("[SHELL] Launching Calculator...")
        try:
            from apps.calculator.calculator import CalculatorApp
            CalculatorApp(self.root)
        except Exception as e:
            messagebox.showinfo("Calculator", f"Could not launch Calculator: {e}")

    def open_calendar(self):
        """Launch calendar"""
        print("[SHELL] Launching Calendar...")
        try:
            from apps.calendar.calendar_app import CalendarApp
            CalendarApp(self.root)
        except Exception as e:
            messagebox.showinfo("Calendar", f"Could not launch Calendar: {e}")

    def open_monitor(self):
        """Launch system monitor"""
        print("[SHELL] Launching System Monitor...")
        try:
            from apps.sysmonitor.sys_monitor import SystemMonitorApp
            SystemMonitorApp(self.root)
        except Exception as e:
            messagebox.showinfo("System Monitor", f"Could not launch System Monitor: {e}")

    def open_tictactoe(self):
        """Launch Tic-Tac-Toe"""
        print("[SHELL] Launching Tic-Tac-Toe...")
        try:
            from apps.games.tictactoe import TicTacToeApp
            TicTacToeApp(self.root)
        except Exception as e:
            messagebox.showinfo("Tic-Tac-Toe", f"Could not launch Tic-Tac-Toe: {e}")

    def open_command_palette(self):
        """Open command palette"""
        print("[SHELL] Opening Command Palette...")
        try:
            from ui.shell.command_palette import CommandPalette
            CommandPalette(self.root, callback=self._handle_command)
        except Exception as e:
            print(f"[SHELL] Error opening command palette: {e}")

    def _handle_command(self, cmd):
        """Handle command from palette"""
        commands = {
            "terminal": self.open_terminal,
            "filemanager": self.open_file_manager,
            "editor": self.open_text_editor,
            "settings": self.open_settings,
            "calculator": self.open_calculator,
            "calendar": self.open_calendar,
            "monitor": self.open_monitor,
            "tictactoe": self.open_tictactoe,
            "logout": self.lock_system,
            "restart": self.restart_system,
            "shutdown": self.shutdown_system
        }
        if cmd in commands:
            commands[cmd]()

    def open_system_info(self):
        """Show system information"""
        print("[SHELL] Opening System Info...")
        info_win = tk.Toplevel(self.root)
        info_win.title("System Information")
        info_win.geometry("500x450")
        info_win.configure(bg=AuroraTheme.BG_PRIMARY)
        info_win.resizable(False, False)
        
        # Center on screen
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        info_win.geometry(f"500x450+{x}+{y}")
        
        # UI
        tk.Label(
            info_win, text="🌌 AuroraOS", font=('Segoe UI', 28, 'bold'),
            bg=AuroraTheme.BG_PRIMARY, fg=AuroraTheme.ACCENT, pady=20
        ).pack()
        
        info_frame = tk.Frame(info_win, bg=AuroraTheme.BG_SECONDARY, padx=20, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        info_text = (
            f"Version: 1.0.0 (Northern Lights)\n"
            f"Kernel: Aurora Kernel 1.0\n"
            f"Architecture: x86_64 (simulated)\n"
            f"Memory: 128 MB\n"
            f"User: {self.username}\n\n"
            f"© 2025 AuroraOS Project\n"
            f"Educational Edition"
        )
        
        tk.Label(
            info_frame, text=info_text, font=('Segoe UI', 11),
            bg=AuroraTheme.BG_SECONDARY, fg=AuroraTheme.TEXT_PRIMARY,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        tk.Button(
            info_win, text="Close", font=('Segoe UI', 10),
            bg=AuroraTheme.ACCENT, fg=AuroraTheme.TEXT_PRIMARY,
            padx=20, pady=8, border=0, command=info_win.destroy,
            cursor='hand2'
        ).pack(pady=10)
    
    def open_recycle_bin(self):
        """Open recycle bin"""
        messagebox.showinfo("Recycle Bin", "Recycle Bin is empty")
    
    def lock_system(self):
        """Lock the system (Logout)"""
        if messagebox.askyesno("Lock System", "Logout of AuroraOS?"):
            print("[SHELL] Logging out...")
            self.exit_status = "logout"
            self.root.destroy()
    
    def restart_system(self):
        """Restart the system"""
        if messagebox.askyesno("Restart", "Restart AuroraOS?"):
            print("[SHELL] Restarting system...")
            self.exit_status = "restart"
            self.root.destroy()
    
    def shutdown_system(self):
        """Shutdown the system"""
        if messagebox.askyesno("Shutdown", "Shutdown AuroraOS?"):
            print("[SHELL] Shutting down...")
            self.exit_status = "shutdown"
            self.root.destroy()
    
    def run(self):
        """Start the shell"""
        self.root.mainloop()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for Aurora Shell"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║              🌌 AuroraOS Shell v1.0 🌌                 ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print("\n")
    
    shell = AuroraShell()
    shell.run()


if __name__ == "__main__":
    main()
