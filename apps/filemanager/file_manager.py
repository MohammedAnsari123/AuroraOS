"""
AuroraOS File Manager
Graphical file browser with Aurora theme
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from system.core.filesystem import get_filesystem

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
        SUCCESS = "#10B981"
        ERROR = "#EF4444"


class FileManagerApp:
    """File manager application"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("File Manager - AuroraOS")
        self.window.geometry("1000x700")
        self.window.configure(bg=Theme.BG_PRIMARY)
        
        self.vfs = get_filesystem()
        self.current_path = "/home/aurora"
        self.history = []
        self.history_index = -1
        
        self._create_ui()
        self._refresh_view()
        
    def _create_ui(self):
        """Create file manager UI"""
        # Toolbar
        toolbar = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=50)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        toolbar.pack_propagate(False)
        
        # Navigation buttons
        self.back_btn = self._create_toolbar_btn(toolbar, "◀", self.go_back)
        self.forward_btn = self._create_toolbar_btn(toolbar, "▶", self.go_forward)
        self.up_btn = self._create_toolbar_btn(toolbar, "⬆", self.go_up)
        self.home_btn = self._create_toolbar_btn(toolbar, "🏠", self.go_home)
        
        # Separator
        sep = tk.Frame(toolbar, bg=Theme.ACCENT, width=2)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Action buttons
        self._create_toolbar_btn(toolbar, "➕ New Folder", self.create_folder)
        self._create_toolbar_btn(toolbar, "📄 New File", self.create_file)
        self._create_toolbar_btn(toolbar, "🗑️ Delete", self.delete_item)
        
        # Separator
        sep2 = tk.Frame(toolbar, bg=Theme.ACCENT, width=2)
        sep2.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        self._create_toolbar_btn(toolbar, "🔄 Refresh", self._refresh_view)
        
        # Address bar
        addr_frame = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=40)
        addr_frame.pack(fill=tk.X, padx=5, pady=5)
        addr_frame.pack_propagate(False)
        
        tk.Label(
            addr_frame,
            text="📍",
            bg=Theme.BG_SECONDARY,
            fg=Theme.ACCENT,
            font=('Segoe UI', 14)
        ).pack(side=tk.LEFT, padx=5)
        
        self.address_bar = tk.Entry(
            addr_frame,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.ACCENT,
            font=('Segoe UI', 11),
            border=0
        )
        self.address_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.address_bar.bind('<Return>', self._on_address_enter)
        
        go_btn = tk.Button(
            addr_frame,
            text="Go",
            bg=Theme.ACCENT,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.BG_TERTIARY,
            border=0,
            padx=15,
            font=('Segoe UI', 10),
            command=self._navigate_to_address
        )
        go_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area
        content_frame = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File list with scrollbar
        list_frame = tk.Frame(content_frame, bg=Theme.BG_PRIMARY)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, bg=Theme.BG_SECONDARY)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_list = tk.Listbox(
            list_frame,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            selectbackground=Theme.ACCENT,
            selectforeground=Theme.TEXT_PRIMARY,
            font=('Consolas', 10),
            border=0,
            yscrollcommand=scrollbar.set,
            activestyle='none'
        )
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_list.yview)
        
        self.file_list.bind('<Double-Button-1>', self._on_item_double_click)
        self.file_list.bind('<Return>', self._on_item_double_click)
        
        # Status bar
        self.status_bar = tk.Label(
            self.window,
            text="Ready",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            anchor=tk.W,
            padx=10,
            font=('Segoe UI', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_toolbar_btn(self, parent, text, command):
        """Create toolbar button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT,
            border=0,
            padx=12,
            pady=5,
            cursor='hand2',
            font=('Segoe UI', 9)
        )
        btn.pack(side=tk.LEFT, padx=2)
        
        btn.bind('<Enter>', lambda e: btn.configure(bg=Theme.BG_TERTIARY))
        btn.bind('<Leave>', lambda e: btn.configure(bg=Theme.BG_SECONDARY))
        
        return btn
    
    def _update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.window.after(3000, lambda: self.status_bar.config(text="Ready"))
    
    def _refresh_view(self):
        """Refresh file list"""
        # Update address bar
        self.address_bar.delete(0, tk.END)
        self.address_bar.insert(0, self.current_path)
        
        # Clear list
        self.file_list.delete(0, tk.END)
        
        # Get files
        files = self.vfs.list_dir(self.current_path)
        
        # Add parent directory link if not at root
        if self.current_path != "/":
            self.file_list.insert(tk.END, "📁 ..")
        
        # Add directories first
        for f in files:
            if f['type'] == 'dir':
                self.file_list.insert(tk.END, f"📁 {f['name']}")
        
        # Add files
        for f in files:
            if f['type'] == 'file':
                size_str = self._format_size(f['size'])
                self.file_list.insert(tk.END, f"📄 {f['name']} ({size_str})")
        
        # Update status
        item_count = len(files)
        self._update_status(f"{item_count} item(s)")
    
    def _format_size(self, size):
        """Format file size"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def _on_item_double_click(self, event):
        """Handle item double click"""
        selection = self.file_list.curselection()
        if not selection:
            return
        
        item = self.file_list.get(selection[0])
        
        if item.startswith("📁"):
            # Directory
            name = item[2:].split(" (")[0]
            
            if name == "..":
                self.go_up()
            else:
                new_path = os.path.join(self.current_path, name).replace("\\", "/")
                self._navigate_to(new_path)
        elif item.startswith("📄"):
            # Open file in Text Editor for full editing capabilities
            name = item[2:].split(" (")[0]
            file_path = os.path.join(self.current_path, name).replace("\\", "/")
            try:
                from apps.editor.text_editor import TextEditorApp
                TextEditorApp(self.window, file_path=file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch Text Editor: {e}")
    
    def _navigate_to(self, path):
        """Navigate to path"""
        path = self.vfs._normalize_path(path)
        
        if path not in self.vfs.inodes:
            messagebox.showerror("Error", f"Path not found: {path}")
            return
        
        # Add to history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(path)
        self.history_index = len(self.history) - 1
        
        self.current_path = path
        self._refresh_view()
    
    def _on_address_enter(self, event):
        """Handle address bar enter key"""
        self._navigate_to_address()
    
    def _navigate_to_address(self):
        """Navigate to address bar path"""
        path = self.address_bar.get().strip()
        if path:
            self._navigate_to(path)
    
    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self._refresh_view()
    
    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self._refresh_view()
    
    def go_up(self):
        """Go to parent directory"""
        if self.current_path != "/":
            parent = os.path.dirname(self.current_path) or "/"
            self._navigate_to(parent)
    
    def go_home(self):
        """Go to home directory"""
        self._navigate_to("/home/aurora")
    
    def create_folder(self):
        """Create new folder"""
        name = simpledialog.askstring("New Folder", "Folder name:")
        if name:
            path = os.path.join(self.current_path, name).replace("\\", "/")
            if self.vfs.mkdir(path):
                self._update_status(f"Created folder: {name}")
                self._refresh_view()
            else:
                messagebox.showerror("Error", "Could not create folder")
    
    def create_file(self):
        """Create new file"""
        name = simpledialog.askstring("New File", "File name:")
        if name:
            path = os.path.join(self.current_path, name).replace("\\", "/")
            if self.vfs.create_file(path, ""):
                self._update_status(f"Created file: {name}")
                self._refresh_view()
            else:
                messagebox.showerror("Error", "Could not create file")
    
    def delete_item(self):
        """Delete selected item"""
        selection = self.file_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item = self.file_list.get(selection[0])
        if item.startswith("📁"):
            name = item[2:].split(" (")[0]
        elif item.startswith("📄"):
            name = item[2:].split(" (")[0]
        else:
            return
        
        if name == "..":
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete '{name}'?"):
            path = os.path.join(self.current_path, name).replace("\\", "/")
            if self.vfs.delete_file(path):
                self._update_status(f"Deleted: {name}")
                self._refresh_view()
            else:
                messagebox.showerror("Error", "Could not delete item")


def main():
    """Main entry point"""
    app = FileManagerApp()
    app.window.mainloop()


if __name__ == "__main__":
    main()

