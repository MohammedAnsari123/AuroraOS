"""
AuroraOS Calendar
Simple monthly calendar view with system theme
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime
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

class CalendarApp:
    """Calendar application"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Calendar")
        self.window.geometry("500x550")
        self.window.configure(bg=Theme.BG_PRIMARY)
        self.window.resizable(False, False)
        
        self.now = datetime.now()
        self.year = self.now.year
        self.month = self.now.month
        
        self._create_ui()
        self._draw_calendar()
        
    def _create_ui(self):
        """Create calendar UI"""
        # Header
        header = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Navigation
        self.prev_btn = tk.Button(
            header, text="◀", font=('Segoe UI', 14),
            bg=Theme.BG_SECONDARY, fg=Theme.ACCENT, border=0,
            command=self._prev_month, cursor='hand2'
        )
        self.prev_btn.pack(side=tk.LEFT, padx=20)
        
        self.month_year_label = tk.Label(
            header, text="", font=('Segoe UI', 18, 'bold'),
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY
        )
        self.month_year_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.next_btn = tk.Button(
            header, text="▶", font=('Segoe UI', 14),
            bg=Theme.BG_SECONDARY, fg=Theme.ACCENT, border=0,
            command=self._next_month, cursor='hand2'
        )
        self.next_btn.pack(side=tk.RIGHT, padx=20)
        
        # Days of week header
        days_frame = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        days_frame.pack(fill=tk.X, pady=10)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            tk.Label(
                days_frame, text=day, font=('Segoe UI', 10, 'bold'),
                bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY, width=8
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
        # Calendar grid
        self.grid_frame = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def _draw_calendar(self):
        """Draw calendar grid for current month/year"""
        # Clear grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        # Update header
        self.month_year_label.config(text=f"{calendar.month_name[self.month]} {self.year}")
        
        # Get calendar data
        cal = calendar.monthcalendar(self.year, self.month)
        
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    # Empty day
                    lbl = tk.Label(self.grid_frame, bg=Theme.BG_PRIMARY)
                else:
                    # Active day
                    is_today = (day == self.now.day and 
                               self.month == self.now.month and 
                               self.year == self.now.year)
                    
                    bg_color = Theme.ACCENT if is_today else Theme.BG_SECONDARY
                    fg_color = Theme.TEXT_PRIMARY
                    
                    lbl = tk.Label(
                        self.grid_frame, text=str(day),
                        font=('Segoe UI', 12, 'bold' if is_today else 'normal'),
                        bg=bg_color, fg=fg_color,
                        width=4, height=3, relief=tk.FLAT
                    )
                    
                lbl.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        
        # Configure grid expansion
        for i in range(7):
            self.grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(cal)):
            self.grid_frame.grid_rowconfigure(i, weight=1)
            
    def _prev_month(self):
        """Go to previous month"""
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self._draw_calendar()
        
    def _next_month(self):
        """Go to next month"""
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self._draw_calendar()

def main():
    app = CalendarApp()
    app.window.mainloop()

if __name__ == "__main__":
    main()
