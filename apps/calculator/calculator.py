"""
AuroraOS Calculator
Functional calculator with system theme
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from ui.themes.colors import CURRENT_THEME as Theme
except ImportError:
    class Theme:
        BG_PRIMARY = "#0A0E27"
        BG_SECONDARY = "#1A1F3A"
        TEXT_PRIMARY = "#FFFFFF"
        ACCENT = "#00D9FF"
        ERROR = "#EF4444"
        SUCCESS = "#10B981"

class CalculatorApp:
    """Simple calculator application"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Calculator")
        self.window.geometry("350x500")
        self.window.configure(bg=Theme.BG_PRIMARY)
        self.window.resizable(False, False)
        
        self.equation = ""
        self.clear_on_next = False
        
        self._create_ui()
        
    def _create_ui(self):
        """Create calculator UI"""
        # Display
        self.display_var = tk.StringVar(value="0")
        display = tk.Entry(
            self.window,
            textvariable=self.display_var,
            font=('Segoe UI', 24),
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            border=0,
            justify='right',
            insertbackground=Theme.ACCENT
        )
        display.pack(fill=tk.X, padx=10, pady=20, ipady=15)
        
        # Buttons frame
        btn_frame = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        buttons = [
            ('C', 0, 0, Theme.ERROR), ('(', 0, 1), (')', 0, 2), ('/', 0, 3, Theme.ACCENT),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3, Theme.ACCENT),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3, Theme.ACCENT),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3, Theme.ACCENT),
            ('0', 4, 0, None, 2), ('.', 4, 2), ('=', 4, 3, Theme.SUCCESS)
        ]
        
        for btn_data in buttons:
            text = btn_data[0]
            row = btn_data[1]
            col = btn_data[2]
            color = btn_data[3] if len(btn_data) > 3 else Theme.BG_SECONDARY
            colspan = btn_data[4] if len(btn_data) > 4 else 1
            
            self._create_button(btn_frame, text, row, col, color, colspan)
            
    def _create_button(self, parent, text, row, col, color, colspan):
        """Create calculator button"""
        bg_color = color or Theme.BG_SECONDARY
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 12, 'bold'),
            bg=bg_color,
            fg=Theme.TEXT_PRIMARY,
            activebackground=Theme.ACCENT,
            activeforeground=Theme.TEXT_PRIMARY,
            border=0,
            cursor='hand2',
            command=lambda: self._on_btn_click(text)
        )
        btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)
        
        # Configure grid expansion
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        # Hover effect
        btn.bind('<Enter>', lambda e: btn.configure(bg=Theme.ACCENT if color != Theme.ERROR else color))
        btn.bind('<Leave>', lambda e: btn.configure(bg=bg_color))
        
    def _on_btn_click(self, char):
        """Handle button click"""
        if char == 'C':
            self.equation = ""
            self.display_var.set("0")
            self.clear_on_next = False
        elif char == '=':
            try:
                # Basic validation for safety
                allowed = "0123456789+-*/(). "
                if all(c in allowed for c in self.equation):
                    # Replace -- with + for eval
                    clean_eq = self.equation.replace('--', '+')
                    result = str(eval(clean_eq))
                    # Handle float integers
                    if result.endswith('.0'):
                        result = result[:-2]
                    self.display_var.set(result)
                    self.equation = result
                    self.clear_on_next = True
                else:
                    self.display_var.set("Error")
                    self.equation = ""
            except Exception:
                self.display_var.set("Error")
                self.equation = ""
        else:
            operators = "+-*/()."
            if self.clear_on_next and char not in operators:
                self.equation = char
                self.clear_on_next = False
            elif self.display_var.get() == "0" or self.display_var.get() == "Error":
                self.equation = char
                self.clear_on_next = False
            else:
                self.equation += str(char)
                self.clear_on_next = False
            self.display_var.set(self.equation)

def main():
    app = CalculatorApp()
    app.window.mainloop()

if __name__ == "__main__":
    main()
