"""
AuroraOS Command Palette
Global search and command execution with system theme
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

class CommandPalette:
    """Global command palette and app launcher"""
    
    def __init__(self, parent=None, callback=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Command Palette")
        self.window.geometry("600x400")
        self.window.overrideredirect(True) # Remove boarder
        self.window.configure(bg=Theme.BG_PRIMARY)
        
        # Center on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 4)
        self.window.geometry(f"600x400+{x}+{y}")
        
        self.callback = callback
        self.commands = [
            {"name": "Terminal", "desc": "Launch system terminal", "icon": "📟", "cmd": "terminal"},
            {"name": "File Manager", "desc": "Browse files and folders", "icon": "📁", "cmd": "filemanager"},
            {"name": "Text Editor", "desc": "Edit text files", "icon": "📝", "cmd": "editor"},
            {"name": "Settings", "desc": "Configure system settings", "icon": "⚙️", "cmd": "settings"},
            {"name": "Calculator", "desc": "Arithmetic calculations", "icon": "➕", "cmd": "calculator"},
            {"name": "Calendar", "desc": "View monthly calendar", "icon": "📅", "cmd": "calendar"},
            {"name": "System Monitor", "desc": "View resource usage", "icon": "📊", "cmd": "monitor"},
            {"name": "Tic-Tac-Toe", "desc": "Classic board game", "icon": "🎮", "cmd": "tictactoe"},
            {"name": "Logout", "desc": "End current session", "icon": "🚪", "cmd": "logout"},
            {"name": "Restart", "desc": "Reboot AuroraOS", "icon": "🔄", "cmd": "restart"},
            {"name": "Shutdown", "desc": "Power off AuroraOS", "icon": "🔌", "cmd": "shutdown"},
        ]
        
        self.filtered_commands = self.commands.copy()
        self.selected_idx = 0
        
        self._create_ui()
        self.window.bind("<Escape>", lambda e: self.close())
        self.window.bind("<Up>", self._on_up)
        self.window.bind("<Down>", self._on_down)
        self.window.bind("<Return>", self._on_select)
        
        self.search_entry.focus_set()
        
    def _create_ui(self):
        """Create palette UI"""
        # Search container
        search_frame = tk.Frame(self.window, bg=Theme.ACCENT, pady=2)
        search_frame.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 16),
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.ACCENT,
            border=10,
            relief=tk.FLAT
        )
        self.search_entry.pack(fill=tk.X)
        
        # Results frame
        self.results_frame = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self._render_results()
        
    def _render_results(self):
        """Render filtered command list"""
        # Clear previous
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not self.filtered_commands:
            tk.Label(
                self.results_frame, text="No commands found",
                font=('Segoe UI', 12), bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY
            ).pack(pady=20)
            return
            
        for i, cmd in enumerate(self.filtered_commands):
            is_selected = (i == self.selected_idx)
            bg = Theme.BG_SECONDARY if is_selected else Theme.BG_PRIMARY
            
            row = tk.Frame(self.results_frame, bg=bg, padx=20, pady=8)
            row.pack(fill=tk.X)
            
            # Icon
            tk.Label(
                row, text=cmd["icon"], font=('Segoe UI', 16),
                bg=bg, fg=Theme.TEXT_PRIMARY
            ).pack(side=tk.LEFT, padx=(0, 15))
            
            # Text container
            texts = tk.Frame(row, bg=bg)
            texts.pack(side=tk.LEFT, fill=tk.Y)
            
            tk.Label(
                texts, text=cmd["name"], font=('Segoe UI', 11, 'bold'),
                bg=bg, fg=Theme.ACCENT if is_selected else Theme.TEXT_PRIMARY
            ).pack(anchor=tk.W)
            
            tk.Label(
                texts, text=cmd["desc"], font=('Segoe UI', 9),
                bg=bg, fg=Theme.TEXT_SECONDARY
            ).pack(anchor=tk.W)
            
            # Bind click
            row.bind("<Button-1>", lambda e, idx=i: self._select_by_idx(idx))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._select_by_idx(idx))
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        grandchild.bind("<Button-1>", lambda e, idx=i: self._select_by_idx(idx))

    def _on_search_change(self, *args):
        """Handle search input update"""
        query = self.search_var.get().lower()
        if not query:
            self.filtered_commands = self.commands.copy()
        else:
            self.filtered_commands = [
                c for c in self.commands 
                if query in c["name"].lower() or query in c["desc"].lower()
            ]
        
        self.selected_idx = 0
        self._render_results()
        
    def _on_up(self, e):
        if self.filtered_commands:
            self.selected_idx = (self.selected_idx - 1) % len(self.filtered_commands)
            self._render_results()
            
    def _on_down(self, e):
        if self.filtered_commands:
            self.selected_idx = (self.selected_idx + 1) % len(self.filtered_commands)
            self._render_results()
            
    def _on_select(self, e=None):
        if self.filtered_commands and self.selected_idx < len(self.filtered_commands):
            cmd = self.filtered_commands[self.selected_idx]
            if self.callback:
                self.callback(cmd["cmd"])
            self.close()
            
    def _select_by_idx(self, idx):
        self.selected_idx = idx
        self._on_select()
        
    def close(self):
        self.window.destroy()

def main():
    def dummy_callback(cmd):
        print(f"Executing: {cmd}")
    app = CommandPalette(callback=dummy_callback)
    app.window.mainloop()

if __name__ == "__main__":
    main()
