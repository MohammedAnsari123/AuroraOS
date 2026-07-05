"""
AuroraOS Settings
System settings and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from user.auth.authentication import get_auth_manager
from user.session.session_manager import get_session_manager

try:
    from ui.themes.colors import CURRENT_THEME as Theme
except ImportError:
    class Theme:
        BG_PRIMARY = "#0A0E27"
        BG_SECONDARY = "#1A1F3A"
        BG_TERTIARY = "#151934"
        TEXT_PRIMARY = "#FFFFFF"
        TEXT_SECONDARY = "#B8C1EC"
        ACCENT = "#00D9FF"
        ACCENT_SECONDARY = "#9D4EDD"
        SUCCESS = "#10B981"


class SettingsApp:
    """System settings application"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Settings - AuroraOS")
        self.window.geometry("900x650")
        self.window.configure(bg=Theme.BG_PRIMARY)
        
        self.auth_manager = get_auth_manager()
        self.session = get_session_manager().get_current_session()
        
        self._create_ui()
        
    def _create_ui(self):
        """Create settings UI"""
        # Header
        header = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚙️ System Settings",
            font=('Segoe UI', 24, 'bold'),
            bg=Theme.BG_SECONDARY,
            fg=Theme.ACCENT,
            pady=20
        ).pack()
        
        # Main content
        content = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left sidebar - categories
        sidebar = tk.Frame(content, bg=Theme.BG_SECONDARY, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)
        
        tk.Label(
            sidebar,
            text="Categories",
            font=('Segoe UI', 12, 'bold'),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            pady=15
        ).pack()
        
        # Category buttons
        self._create_category_btn(sidebar, "👤 User Account", self._show_user_settings)
        self._create_category_btn(sidebar, "🎨 Appearance", self._show_appearance_settings)
        self._create_category_btn(sidebar, "🖥️ System Info", self._show_system_info)
        self._create_category_btn(sidebar, "ℹ️ About", self._show_about)
        
        # Right panel - settings content
        self.content_panel = tk.Frame(content, bg=Theme.BG_PRIMARY)
        self.content_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Show default panel
        self._show_user_settings()
    
    def _create_category_btn(self, parent, text, command):
        """Create category button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT,
            activeforeground=Theme.TEXT_PRIMARY,
            border=0,
            anchor=tk.W,
            padx=20,
            pady=12,
            font=('Segoe UI', 10),
            cursor='hand2'
        )
        btn.pack(fill=tk.X, pady=2)
        
        btn.bind('<Enter>', lambda e: btn.configure(bg=Theme.BG_TERTIARY))
        btn.bind('<Leave>', lambda e: btn.configure(bg=Theme.BG_SECONDARY))
    
    def _clear_content_panel(self):
        """Clear content panel"""
        for widget in self.content_panel.winfo_children():
            widget.destroy()
    
    def _create_section_title(self, parent, text):
        """Create section title"""
        tk.Label(
            parent,
            text=text,
            font=('Segoe UI', 16, 'bold'),
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT,
            anchor=tk.W,
            pady=10
        ).pack(fill=tk.X)
    
    def _create_setting_row(self, parent, label, widget):
        """Create a setting row"""
        row = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(
            row,
            text=label,
            font=('Segoe UI', 11),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        widget.pack(side=tk.LEFT)
    
    def _show_user_settings(self):
        """Show user account settings"""
        self._clear_content_panel()
        
        self._create_section_title(self.content_panel, "👤 User Account")
        
        # User info
        info_frame = tk.Frame(self.content_panel, bg=Theme.BG_SECONDARY, relief=tk.FLAT)
        info_frame.pack(fill=tk.X, pady=10, padx=10, ipady=15)
        
        if self.session:
            username = self.session.username
            full_name = self.session.full_name
            is_admin = "Yes" if self.session.is_admin else "No"
        else:
            username = "Unknown"
            full_name = "Unknown"
            is_admin = "No"
        
        tk.Label(
            info_frame,
            text=f"Username: {username}",
            font=('Segoe UI', 11),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            anchor=tk.W,
            padx=20
        ).pack(fill=tk.X, pady=5)
        
        tk.Label(
            info_frame,
            text=f"Full Name: {full_name}",
            font=('Segoe UI', 11),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            anchor=tk.W,
            padx=20
        ).pack(fill=tk.X, pady=5)
        
        tk.Label(
            info_frame,
            text=f"Administrator: {is_admin}",
            font=('Segoe UI', 11),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            anchor=tk.W,
            padx=20
        ).pack(fill=tk.X, pady=5)
        
        # Actions
        actions_frame = tk.Frame(self.content_panel, bg=Theme.BG_PRIMARY)
        actions_frame.pack(fill=tk.X, pady=20)
        
        self._create_action_btn(actions_frame, "🔑 Change Password", self._change_password)
        self._create_action_btn(actions_frame, "👥 Manage Users", self._manage_users)
    
    def _show_appearance_settings(self):
        """Show appearance settings"""
        self._clear_content_panel()
        
        self._create_section_title(self.content_panel, "🎨 Appearance")
        
        # Theme selection
        theme_frame = tk.Frame(self.content_panel, bg=Theme.BG_PRIMARY)
        theme_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            theme_frame,
            text="Theme:",
            font=('Segoe UI', 11),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=5)
        
        # Theme buttons
        theme_btn_frame = tk.Frame(theme_frame, bg=Theme.BG_PRIMARY)
        theme_btn_frame.pack(fill=tk.X, pady=10)
        
        # Aurora Dark (active)
        dark_btn = tk.Button(
            theme_btn_frame,
            text="🌌 Aurora Dark (Active)",
            bg=Theme.ACCENT,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_SECONDARY,
            border=0,
            padx=20,
            pady=15,
            font=('Segoe UI', 11),
            cursor='hand2'
        )
        dark_btn.pack(fill=tk.X, pady=5)
        
        # Aurora Light (coming soon)
        light_btn = tk.Button(
            theme_btn_frame,
            text="☀️ Aurora Light (Coming Soon)",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            border=0,
            padx=20,
            pady=15,
            font=('Segoe UI', 11),
            state=tk.DISABLED
        )
        light_btn.pack(fill=tk.X, pady=5)
        
        # Color info
        tk.Label(
            self.content_panel,
            text="Aurora theme features northern lights-inspired colors:",
            font=('Segoe UI', 10),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            anchor=tk.W,
            pady=20
        ).pack(fill=tk.X)
        
        colors_frame = tk.Frame(self.content_panel, bg=Theme.BG_PRIMARY)
        colors_frame.pack(fill=tk.X, pady=10)
        
        self._create_color_swatch(colors_frame, "Teal", "#00D9FF")
        self._create_color_swatch(colors_frame, "Purple", "#9D4EDD")
        self._create_color_swatch(colors_frame, "Neon Blue", "#5E60CE")
    
    def _create_color_swatch(self, parent, name, color):
        """Create color swatch"""
        swatch_frame = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        swatch_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            swatch_frame,
            text="  ",
            bg=color,
            relief=tk.RAISED,
            borderwidth=2,
            width=4,
            height=2
        ).pack()
        
        tk.Label(
            swatch_frame,
            text=name,
            font=('Segoe UI', 9),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY
        ).pack(pady=5)
    
    def _show_system_info(self):
        """Show system information"""
        self._clear_content_panel()
        
        self._create_section_title(self.content_panel, "🖥️ System Information")
        
        # System info display
        info_frame = tk.Frame(self.content_panel, bg=Theme.BG_SECONDARY, relief=tk.FLAT)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        info_text = """
Operating System:    AuroraOS v1.0.0
Codename:           Northern Lights
Kernel:             Aurora Kernel 1.0
Architecture:       x86_64 (simulated)

Memory:             128 MB (simulated)
Storage:            100 MB virtual disk
File System:        Virtual FAT-like FS

CPU:                Simulated
Graphics:           Software Rendering
Network:            Simulated Interface

Build Date:         2025
Purpose:            Educational & Experimental
        """
        
        tk.Label(
            info_frame,
            text=info_text,
            font=('Consolas', 10),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            anchor=tk.W,
            justify=tk.LEFT,
            padx=20,
            pady=20
        ).pack(fill=tk.BOTH, expand=True)
    
    def _show_about(self):
        """Show about page"""
        self._clear_content_panel()
        
        # Logo and title
        tk.Label(
            self.content_panel,
            text="🌌",
            font=('Segoe UI', 48),
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT,
            pady=20
        ).pack()
        
        tk.Label(
            self.content_panel,
            text="AuroraOS",
            font=('Segoe UI', 28, 'bold'),
            bg=Theme.BG_PRIMARY,
            fg=Theme.ACCENT
        ).pack()
        
        tk.Label(
            self.content_panel,
            text="Northern Lights Edition",
            font=('Segoe UI', 14),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            pady=5
        ).pack()
        
        tk.Label(
            self.content_panel,
            text="Version 1.0.0",
            font=('Segoe UI', 11),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            pady=20
        ).pack()
        
        # Description
        about_text = """
AuroraOS is a complete, functional, and modular lightweight
operating system designed for educational and experimental purposes.

Built with a hybrid architecture combining C (kernel) and Python
(system services & UI), AuroraOS demonstrates core OS concepts
including process management, memory handling, file systems,
user authentication, and graphical interfaces.

© 2025 AuroraOS Project
Created for educational purposes
        """
        
        tk.Label(
            self.content_panel,
            text=about_text,
            font=('Segoe UI', 10),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            justify=tk.CENTER,
            pady=20
        ).pack()
    
    def _create_action_btn(self, parent, text, command):
        """Create action button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=Theme.ACCENT,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT_SECONDARY,
            border=0,
            padx=25,
            pady=12,
            font=('Segoe UI', 11),
            cursor='hand2'
        )
        btn.pack(pady=5)
        
        btn.bind('<Enter>', lambda e: btn.configure(bg=Theme.ACCENT_SECONDARY))
        btn.bind('<Leave>', lambda e: btn.configure(bg=Theme.ACCENT))
    
    def _change_password(self):
        """Change user password"""
        messagebox.showinfo("Change Password", "Password change functionality would be implemented here")
    
    def _manage_users(self):
        """Manage users"""
        users = self.auth_manager.list_users()
        
        user_list = "\n".join([
            f"• {u['username']} ({u['full_name']}) - Admin: {u['is_admin']}"
            for u in users
        ])
        
        messagebox.showinfo("User Management", f"Registered Users:\n\n{user_list}")


def main():
    """Main entry point"""
    app = SettingsApp()
    app.window.mainloop()


if __name__ == "__main__":
    main()
