"""
AuroraOS Tic-Tac-Toe
Classic game with system theme
"""

import tkinter as tk
from tkinter import messagebox
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
        SUCCESS = "#10B981"
        ERROR = "#EF4444"

class TicTacToeApp:
    """Tic-Tac-Toe game implementation"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Tic-Tac-Toe")
        self.window.geometry("400x500")
        self.window.configure(bg=Theme.BG_PRIMARY)
        self.window.resizable(False, False)
        
        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []
        
        self._create_ui()
        
    def _create_ui(self):
        """Create game UI"""
        # Status Label
        self.status_label = tk.Label(
            self.window, text="Player X's Turn", font=('Segoe UI', 16, 'bold'),
            bg=Theme.BG_PRIMARY, fg=Theme.ACCENT, pady=20
        )
        self.status_label.pack()
        
        # Grid frame
        grid_frame = tk.Frame(self.window, bg=Theme.BG_PRIMARY)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for i in range(9):
            btn = tk.Button(
                grid_frame, text="", font=('Segoe UI', 24, 'bold'),
                bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY,
                activebackground=Theme.ACCENT, border=0,
                width=3, height=1, cursor='hand2',
                command=lambda idx=i: self._on_click(idx)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="nsew")
            self.buttons.append(btn)
            
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1)
            grid_frame.grid_rowconfigure(i, weight=1)
            
        # Reset Button
        reset_btn = tk.Button(
            self.window, text="Reset Game", font=('Segoe UI', 12),
            bg=Theme.ACCENT, fg=Theme.TEXT_PRIMARY, border=0,
            padx=20, pady=10, command=self.reset_game, cursor='hand2'
        )
        reset_btn.pack(pady=20)
        
    def _on_click(self, idx):
        """Handle cell click"""
        if self.board[idx] == "" and not self._check_winner():
            self.board[idx] = self.current_player
            self.buttons[idx].config(
                text=self.current_player,
                fg=Theme.ACCENT if self.current_player == "X" else Theme.ACCENT_SECONDARY if hasattr(Theme, 'ACCENT_SECONDARY') else "#FF006E"
            )
            
            winner = self._check_winner()
            if winner:
                if winner == "Tie":
                    self.status_label.config(text="It's a Tie!", fg=Theme.TEXT_SECONDARY)
                    messagebox.showinfo("Game Over", "It's a Tie!")
                else:
                    self.status_label.config(text=f"Player {winner} Wins!", fg=Theme.SUCCESS)
                    messagebox.showinfo("Game Over", f"Player {winner} wins!")
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.status_label.config(text=f"Player {self.current_player}'s Turn")
                
    def _check_winner(self):
        """Check for winner or tie"""
        win_combos = [
            (0,1,2), (3,4,5), (6,7,8), # Rows
            (0,3,6), (1,4,7), (2,5,8), # Cols
            (0,4,8), (2,4,6)           # Diagonals
        ]
        
        for combo in win_combos:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != "":
                return self.board[combo[0]]
                
        if "" not in self.board:
            return "Tie"
            
        return None
        
    def reset_game(self):
        """Reset game state"""
        self.current_player = "X"
        self.board = [""] * 9
        for btn in self.buttons:
            btn.config(text="", fg=Theme.TEXT_PRIMARY)
        self.status_label.config(text="Player X's Turn", fg=Theme.ACCENT)

def main():
    app = TicTacToeApp()
    app.window.mainloop()

if __name__ == "__main__":
    main()
