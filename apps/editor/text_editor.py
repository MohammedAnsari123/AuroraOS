"""
AuroraOS Text Editor
Simple text editor with Aurora theme
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
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
        TEXT_PRIMARY = "#FFFFFF"
        ACCENT = "#00D9FF"
        SUCCESS = "#10B981"


class TextEditorApp:
    """Text editor application"""
    
    def __init__(self, parent=None, file_path=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Untitled - AuroraOS Text Editor")
        self.window.geometry("900x700")
        self.window.configure(bg=Theme.BG_PRIMARY)
        
        self.vfs = get_filesystem()
        self.current_file = file_path
        self.is_modified = False
        
        self._create_ui()
        self._create_menu()
        
        if file_path:
            self.load_file(file_path)
        
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.window, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_editor)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Word Wrap", command=self.toggle_wrap)
        
        # Bind shortcuts
        self.window.bind('<Control-n>', lambda e: self.new_file())
        self.window.bind('<Control-o>', lambda e: self.open_file())
        self.window.bind('<Control-s>', lambda e: self.save_file())
    
    def _create_ui(self):
        """Create editor UI"""
        # Toolbar
        toolbar = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        toolbar.pack_propagate(False)
        
        # Toolbar buttons
        self._create_button(toolbar, "📄 New", self.new_file)
        self._create_button(toolbar, "📁 Open", self.open_file)
        self._create_button(toolbar, "💾 Save", self.save_file)
        
        # Separator
        sep = tk.Frame(toolbar, bg=Theme.ACCENT, width=2)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        self._create_button(toolbar, "✂️ Cut", self.cut_text)
        self._create_button(toolbar, "📋 Copy", self.copy_text)
        self._create_button(toolbar, "📌 Paste", self.paste_text)
        
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
        
        # Text editor
        self.text_area = scrolledtext.ScrolledText(
            self.window,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.ACCENT,
            font=('Consolas', 11),
            wrap=tk.WORD,
            border=0,
            padx=15,
            pady=15,
            undo=True
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_area.bind('<<Modified>>', self._on_text_modified)
        self.text_area.focus()
    
    def _create_button(self, parent, text, command):
        """Create toolbar button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT,
            border=0,
            padx=15,
            pady=5,
            cursor='hand2',
            font=('Segoe UI', 9)
        )
        btn.pack(side=tk.LEFT, padx=2)
        
        btn.bind('<Enter>', lambda e: btn.configure(bg=Theme.ACCENT))
        btn.bind('<Leave>', lambda e: btn.configure(bg=Theme.BG_SECONDARY))
    
    def _on_text_modified(self, event):
        """Handle text modification"""
        if self.text_area.edit_modified():
            self.is_modified = True
            self._update_title()
            self.text_area.edit_modified(False)
    
    def _update_title(self):
        """Update window title"""
        filename = self.current_file or "Untitled"
        modified = "*" if self.is_modified else ""
        self.window.title(f"{filename}{modified} - AuroraOS Text Editor")
    
    def _update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.window.after(3000, lambda: self.status_bar.config(text="Ready"))

    def load_file(self, file_path):
        """Load file from VFS path"""
        content = self.vfs.read_file(file_path)
        if content is not None:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, content)
            self.current_file = file_path
            self.is_modified = False
            self._update_title()
            self._update_status(f"Opened: {file_path}")
        else:
            messagebox.showerror("Error", f"Could not load file: {file_path}")

    def new_file(self):
        """Create new file"""
        if self.is_modified:
            if not messagebox.askyesno("Unsaved Changes", "Save current file?"):
                return
            else:
                self.save_file()
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.is_modified = False
        self._update_title()
        self._update_status("New file created")
    
    def open_file(self):
        """Open file from VFS"""
        # Simple file path dialog
        file_path = simpledialog.askstring("Open File", "Enter file path:")
        if not file_path:
            return
        
        content = self.vfs.read_file(file_path)
        if content is not None:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, content)
            self.current_file = file_path
            self.is_modified = False
            self._update_title()
            self._update_status(f"Opened: {file_path}")
        else:
            messagebox.showerror("Error", f"Could not open file: {file_path}")
    
    def save_file(self):
        """Save current file"""
        if self.current_file is None:
            self.save_file_as()
        else:
            content = self.text_area.get(1.0, tk.END)
            if self.vfs.write_file(self.current_file, content):
                self.is_modified = False
                self._update_title()
                self._update_status(f"Saved: {self.current_file}")
            else:
                messagebox.showerror("Error", "Could not save file")
    
    def save_file_as(self):
        """Save file with new name"""
        file_path = simpledialog.askstring("Save As", "Enter file path:")
        if not file_path:
            return
        
        content = self.text_area.get(1.0, tk.END)
        if self.vfs.write_file(file_path, content):
            self.current_file = file_path
            self.is_modified = False
            self._update_title()
            self._update_status(f"Saved as: {file_path}")
        else:
            messagebox.showerror("Error", "Could not save file")
    
    def cut_text(self):
        """Cut selected text"""
        try:
            self.text_area.event_generate("<<Cut>>")
            self._update_status("Text cut to clipboard")
        except:
            pass
    
    def copy_text(self):
        """Copy selected text"""
        try:
            self.text_area.event_generate("<<Copy>>")
            self._update_status("Text copied to clipboard")
        except:
            pass
    
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.text_area.event_generate("<<Paste>>")
            self._update_status("Text pasted from clipboard")
        except:
            pass
    
    def select_all(self):
        """Select all text"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
    
    def toggle_wrap(self):
        """Toggle word wrap"""
        current = self.text_area.cget('wrap')
        self.text_area.config(wrap=tk.NONE if current == tk.WORD else tk.WORD)
    
    def exit_editor(self):
        """Exit editor"""
        if self.is_modified:
            response = messagebox.askyesnocancel("Unsaved Changes", "Save before closing?")
            if response:  # Yes
                self.save_file()
                self.window.destroy()
            elif response is False:  # No
                self.window.destroy()
            # Cancel - do nothing
        else:
            self.window.destroy()


def main():
    """Main entry point"""
    app = TextEditorApp()
    app.window.mainloop()


if __name__ == "__main__":
    main()
