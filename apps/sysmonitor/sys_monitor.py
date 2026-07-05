"""
AuroraOS System Monitor
Live system resource statistics, process manager, and memory heap visualizer
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import random
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

from system.core.filesystem import get_filesystem
from system.core.kernel_connector import get_kernel_connector

class SystemMonitorApp:
    """System resource monitor with process manager and C-heap visualizer"""
    
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("System Diagnostics Manager")
        self.window.geometry("720x580")
        self.window.configure(bg=Theme.BG_PRIMARY)
        self.window.resizable(True, True)
        
        self.vfs = get_filesystem()
        self.conn = get_kernel_connector()
        
        self.selected_block_addr = None
        self.selected_block_size = 0
        self.drawn_blocks = []
        
        self._setup_styles()
        self._create_ui()
        
        # Start background polling loops
        self._update_stats_loop()
        self._update_processes_loop()
        self._update_heap_loop()
        
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        # Notebook (Tabs) Style
        style.configure('TNotebook', background=Theme.BG_PRIMARY, borderwidth=0)
        style.configure('TNotebook.Tab', 
            background=Theme.BG_SECONDARY, 
            foreground=Theme.TEXT_SECONDARY, 
            padding=[15, 6], 
            font=('Segoe UI', 10, 'bold')
        )
        style.map('TNotebook.Tab',
            background=[('selected', Theme.BG_PRIMARY)],
            foreground=[('selected', Theme.ACCENT)]
        )
        
        # Treeview (Process List) Style
        style.configure('Treeview',
            background=Theme.BG_SECONDARY,
            foreground=Theme.TEXT_PRIMARY,
            fieldbackground=Theme.BG_SECONDARY,
            rowheight=25,
            font=('Segoe UI', 9)
        )
        style.map('Treeview', 
            background=[('selected', Theme.ACCENT)], 
            foreground=[('selected', '#000000')]
        )
        style.configure('Treeview.Heading',
            background=Theme.BG_PRIMARY,
            foreground=Theme.ACCENT,
            font=('Segoe UI', 9, 'bold'),
            relief='flat'
        )
        
    def _create_ui(self):
        """Create diagnostics UI with tabs"""
        # Header Panel
        header = tk.Frame(self.window, bg=Theme.BG_SECONDARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header, text="🌌 Diagnostics & System Manager", font=('Segoe UI', 14, 'bold'),
            bg=Theme.BG_SECONDARY, fg=Theme.ACCENT, pady=15
        ).pack(side=tk.LEFT, padx=20)
        
        self.uptime_lbl = tk.Label(
            header, text="Uptime: 0 ms", font=('Segoe UI', 10),
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY
        )
        self.uptime_lbl.pack(side=tk.RIGHT, padx=20)
        
        # Tab Notebook
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: System Resources (CPU/Memory/Disk)
        self.resources_tab = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.notebook.add(self.resources_tab, text="Resources")
        self._build_resources_tab()
        
        # Tab 2: C-Kernel Process Manager
        self.process_tab = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.notebook.add(self.process_tab, text="Process Manager")
        self._build_process_tab()
        
        # Tab 3: C-Kernel Heap Visualizer
        self.heap_tab = tk.Frame(self.notebook, bg=Theme.BG_PRIMARY)
        self.notebook.add(self.heap_tab, text="Heap Visualizer")
        self._build_heap_tab()
        
    # =========================================================================
    # TAB 1: RESOURCES BUILDER
    # =========================================================================
    
    def _build_resources_tab(self):
        container = tk.Frame(self.resources_tab, bg=Theme.BG_PRIMARY)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.cpu_row = self._create_stat_row(container, "CPU Scheduler Load")
        self.mem_row = self._create_stat_row(container, "C Kernel Heap Memory")
        self.disk_row = self._create_stat_row(container, "Virtual VFS Disk Usage")
        
    def _create_stat_row(self, parent, title):
        row = tk.Frame(parent, bg=Theme.BG_PRIMARY)
        row.pack(fill=tk.X, pady=15)
        
        lbl_frame = tk.Frame(row, bg=Theme.BG_PRIMARY)
        lbl_frame.pack(fill=tk.X)
        
        tk.Label(
            lbl_frame, text=title, font=('Segoe UI', 11, 'bold'),
            bg=Theme.BG_PRIMARY, fg=Theme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        percent_label = tk.Label(
            lbl_frame, text="0%", font=('Segoe UI', 10),
            bg=Theme.BG_PRIMARY, fg=Theme.TEXT_SECONDARY
        )
        percent_label.pack(side=tk.RIGHT)
        
        canvas = tk.Canvas(
            row, height=20, bg=Theme.BG_SECONDARY,
            highlightthickness=0
        )
        canvas.pack(fill=tk.X, pady=5)
        
        bar = canvas.create_rectangle(0, 0, 0, 20, fill=Theme.ACCENT, outline="")
        
        return {'label': percent_label, 'canvas': canvas, 'bar': bar}
        
    def _update_stats_loop(self):
        """Update system statistics gauges"""
        try:
            # Uptime
            uptime = self.conn.get_uptime()
            self.uptime_lbl.config(text=f"Kernel Uptime: {uptime} ms")
            
            # CPU (simulated variations)
            cpu = random.randint(3, 12) + len(self.conn.get_process_list()) * 2
            cpu = min(cpu, 100)
            
            # Memory (Calculated from C-kernel or fallback simulator)
            mem_stats = self.conn.memory_get_info()
            total_mem = mem_stats.get('total_memory', 128 * 1024)
            used_mem = mem_stats.get('used_memory', 0)
            mem_percent = int((used_mem / total_mem) * 100) if total_mem > 0 else 0
            
            # Disk (Real VFS disk usage percentage)
            disk_stats = self.vfs.get_disk_usage()
            disk_percent = int(disk_stats['percent'])
            
            # Animate Gauges
            self._update_bar(self.cpu_row, cpu)
            self._update_bar(self.mem_row, mem_percent)
            self._update_bar(self.disk_row, disk_percent)
            
        except Exception as e:
            print(f"[MONITOR] Error updating stats: {e}")
            
        self.window.after(2000, self._update_stats_loop)
        
    def _update_bar(self, row, percent):
        row['label'].config(text=f"{percent}%")
        width = row['canvas'].winfo_width()
        if width > 1:
            target_x = (percent / 100) * width
            row['canvas'].coords(row['bar'], 0, 0, target_x, 20)
            
            # Change color based on thresholds
            color = Theme.ACCENT
            if percent > 85:
                color = Theme.ERROR
            elif percent > 65:
                color = "#F59E0B" # yellow/warning
            row['canvas'].itemconfig(row['bar'], fill=color)
            
    # =========================================================================
    # TAB 2: PROCESS MANAGER BUILDER
    # =========================================================================
    
    def _build_process_tab(self):
        # Table Scrollable Frame
        table_frame = tk.Frame(self.process_tab, bg=Theme.BG_PRIMARY)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        scroll = ttk.Scrollbar(table_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("pid", "name", "priority", "state", "cpu_time")
        self.proc_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=scroll.set
        )
        self.proc_tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.proc_tree.yview)
        
        # Configure columns
        self.proc_tree.heading("pid", text="PID")
        self.proc_tree.heading("name", text="Process Name")
        self.proc_tree.heading("priority", text="Priority")
        self.proc_tree.heading("state", text="Scheduler State")
        self.proc_tree.heading("cpu_time", text="CPU Time (ms)")
        
        self.proc_tree.column("pid", width=60, anchor=tk.CENTER)
        self.proc_tree.column("name", width=180, anchor=tk.W)
        self.proc_tree.column("priority", width=80, anchor=tk.CENTER)
        self.proc_tree.column("state", width=120, anchor=tk.CENTER)
        self.proc_tree.column("cpu_time", width=100, anchor=tk.E)
        
        # Controls Frame
        controls = tk.Frame(self.process_tab, bg=Theme.BG_PRIMARY)
        controls.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Button(
            controls, text="Spawn New Task", command=self._on_spawn_process,
            bg=Theme.BG_SECONDARY, fg=Theme.ACCENT, font=('Segoe UI', 10, 'bold'),
            activebackground=Theme.ACCENT, activeforeground="#000000",
            relief='flat', borderwidth=0, padx=15, pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls, text="Kill Process", command=self._on_kill_process,
            bg="#3B1A1A", fg=Theme.ERROR, font=('Segoe UI', 10, 'bold'),
            activebackground=Theme.ERROR, activeforeground="#FFFFFF",
            relief='flat', borderwidth=0, padx=15, pady=5
        ).pack(side=tk.LEFT, padx=5)
        
    def _update_processes_loop(self):
        """Poll C-kernel processes"""
        try:
            procs = self.conn.get_process_list()
            
            # Map state enum to text representation
            state_map = {
                0: "NEW",
                1: "READY",
                2: "RUNNING",
                3: "WAITING",
                4: "TERMINATED"
            }
            
            # Store selected item to restore selection after refresh
            selected = self.proc_tree.selection()
            selected_pid = None
            if selected:
                selected_pid = self.proc_tree.item(selected[0])['values'][0]
                
            # Clear old rows
            for item in self.proc_tree.get_children():
                self.proc_tree.delete(item)
                
            # Insert fresh records
            for p in procs:
                state_str = state_map.get(p['state'], "UNKNOWN")
                item_id = self.proc_tree.insert("", tk.END, values=(
                    p['pid'], p['name'], p['priority'], state_str, p['cpu_time']
                ))
                if selected_pid == p['pid']:
                    self.proc_tree.selection_set(item_id)
                    
        except Exception as e:
            print(f"[MONITOR] Error updating process grid: {e}")
            
        self.window.after(2000, self._update_processes_loop)
        
    def _on_spawn_process(self):
        name = simpledialog.askstring("Spawn Task", "Enter process name:")
        if not name:
            return
        priority = simpledialog.askinteger("Priority", "Enter priority (1-255):", initialvalue=100, minvalue=1, maxvalue=255)
        if priority is None:
            return
            
        self.conn.process_create(name, priority=priority)
        self._update_processes_loop()
        
    def _on_kill_process(self):
        selected = self.proc_tree.selection()
        if not selected:
            messagebox.showwarning("Select Process", "Please select a process from the list first.")
            return
            
        pid, name = self.proc_tree.item(selected[0])['values'][0:2]
        if pid in (1, 2):
            messagebox.showerror("Access Denied", f"Cannot kill system protected process '{name}' (PID {pid}).")
            return
            
        confirm = messagebox.askyesno("Kill Process", f"Are you sure you want to terminate process '{name}' (PID {pid})?")
        if confirm:
            res = self.conn.process_kill(pid)
            if res == 0:
                self._update_processes_loop()
            else:
                messagebox.showerror("Error", f"Failed to kill process PID {pid}.")

    # =========================================================================
    # TAB 3: HEAP VISUALIZER BUILDER
    # =========================================================================
    
    def _build_heap_tab(self):
        # Top explanation row
        info_bar = tk.Frame(self.heap_tab, bg=Theme.BG_SECONDARY, height=35)
        info_bar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            info_bar, text="🟢 Free C-Heap Blocks  |  🟣 Allocated Blocks (Purple)  |  🟡 Click to Select",
            font=('Segoe UI', 9, 'bold'), bg=Theme.BG_SECONDARY, fg=Theme.TEXT_SECONDARY
        ).pack(side=tk.LEFT, padx=15, pady=8)
        
        # Scrollable Canvas Frame
        canvas_container = tk.Frame(self.heap_tab, bg=Theme.BG_PRIMARY)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.heap_canvas = tk.Canvas(
            canvas_container, bg="#060919", highlightthickness=1,
            highlightbackground=Theme.BG_SECONDARY, yscrollcommand=v_scroll.set
        )
        self.heap_canvas.pack(fill=tk.BOTH, expand=True)
        v_scroll.config(command=self.heap_canvas.yview)
        
        # Click binding
        self.heap_canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Bottom Details and Allocation Controls
        details_panel = tk.Frame(self.heap_tab, bg=Theme.BG_SECONDARY, pady=10)
        details_panel.pack(fill=tk.X, padx=10, pady=10)
        
        self.block_info_lbl = tk.Label(
            details_panel, text="Click a block to view details or free it",
            font=('Segoe UI', 10, 'italic'), bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY
        )
        self.block_info_lbl.pack(fill=tk.X, padx=10, pady=5)
        
        controls = tk.Frame(details_panel, bg=Theme.BG_SECONDARY)
        controls.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            controls, text="Size (Bytes):", font=('Segoe UI', 9),
            bg=Theme.BG_SECONDARY, fg=Theme.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=5)
        
        self.alloc_size_entry = tk.Entry(
            controls, width=10, bg=Theme.BG_PRIMARY, fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY, borderwidth=1, relief='solid'
        )
        self.alloc_size_entry.pack(side=tk.LEFT, padx=5)
        self.alloc_size_entry.insert(0, "4096")
        
        tk.Button(
            controls, text="Allocate (kmalloc)", command=self._on_kmalloc,
            bg=Theme.BG_PRIMARY, fg=Theme.ACCENT, font=('Segoe UI', 9, 'bold'),
            activebackground=Theme.ACCENT, activeforeground="#000000",
            relief='flat', borderwidth=0, padx=10, pady=3
        ).pack(side=tk.LEFT, padx=10)
        
        self.kfree_btn = tk.Button(
            controls, text="Free Block (kfree)", command=self._on_kfree,
            bg="#3B1A1A", fg=Theme.ERROR, font=('Segoe UI', 9, 'bold'),
            activebackground=Theme.ERROR, activeforeground="#FFFFFF",
            relief='flat', borderwidth=0, padx=10, pady=3, state=tk.DISABLED
        )
        self.kfree_btn.pack(side=tk.LEFT, padx=5)
        
    def _update_heap_loop(self):
        """Refresh Heap Visualizer Blocks"""
        try:
            self._draw_heap_canvas()
        except Exception as e:
            print(f"[MONITOR] Error updating Heap Visualizer: {e}")
            
        self.window.after(3000, self._update_heap_loop)
        
    def _draw_heap_canvas(self):
        blocks = self.conn.get_heap_blocks()
        self.heap_canvas.delete("all")
        self.drawn_blocks = []
        
        x_margin = 15
        y_margin = 15
        x = x_margin
        y = y_margin
        row_height = 32
        max_width = self.heap_canvas.winfo_width()
        if max_width <= 1:
            max_width = 660 # Fallback default
            
        for b in blocks:
            # Display width based on block size in KB
            # Normalized display block widths
            size_kb = b['size'] / 1024
            box_width = int(max(50, min(200, size_kb * 2)))
            
            # Wrap to next row
            if x + box_width > max_width - x_margin:
                x = x_margin
                y += row_height + 15
                
            x1, y1 = x, y
            x2, y2 = x + box_width, y + row_height
            
            if b['is_free']:
                bg_color = "#122A20"
                outline_color = "#10B981"
                text_color = "#10B981"
                label = f"{b['size']} B" if b['size'] < 1024 else f"{b['size']/1024:.0f}K (F)"
            else:
                bg_color = "#2E1452"
                outline_color = "#9F7AEA"
                text_color = "#E9D8FD"
                label = f"{b['size']} B" if b['size'] < 1024 else f"{b['size']/1024:.0f}K (A)"
                
            rect_id = self.heap_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=bg_color,
                outline=outline_color,
                width=1
            )
            
            self.heap_canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=label,
                fill=text_color,
                font=('Segoe UI', 8, 'bold')
            )
            
            # Highlight border if selected
            if self.selected_block_addr == b['address']:
                self.heap_canvas.itemconfig(rect_id, outline='#FFFF00', width=2)
                
            self.drawn_blocks.append((rect_id, b, x1, y1, x2, y2))
            x += box_width + 10
            
        self.heap_canvas.config(scrollregion=(0, 0, max_width, y + row_height + 30))
        
    def _on_canvas_click(self, event):
        clicked_x = self.heap_canvas.canvasx(event.x)
        clicked_y = self.heap_canvas.canvasy(event.y)
        
        self.selected_block_addr = None
        for rect_id, block, x1, y1, x2, y2 in self.drawn_blocks:
            if x1 <= clicked_x <= x2 and y1 <= clicked_y <= y2:
                self.selected_block_addr = block['address']
                self.selected_block_size = block['size']
                status = "Free" if block['is_free'] else "Allocated"
                
                # Highlight in yellow
                self.heap_canvas.itemconfig(rect_id, outline='#FFFF00', width=2)
                self.block_info_lbl.config(
                    text=f"Selected: Addr 0x{block['address']:X} | Size: {block['size']} Bytes | Status: {status}"
                )
                
                # Active kfree button if block is allocated
                if not block['is_free']:
                    self.kfree_btn.config(state=tk.NORMAL)
                else:
                    self.kfree_btn.config(state=tk.DISABLED)
                break
            else:
                self.heap_canvas.itemconfig(
                    rect_id, outline='#10B981' if block['is_free'] else '#9F7AEA', width=1
                )
                
        if not self.selected_block_addr:
            self.block_info_lbl.config(text="Click a block to view details or free it")
            self.kfree_btn.config(state=tk.DISABLED)
            
    def _on_kmalloc(self):
        try:
            size_str = self.alloc_size_entry.get().strip()
            size = int(size_str)
            if size <= 0:
                raise ValueError("Size must be positive")
        except ValueError:
            messagebox.showerror("Invalid Size", "Please enter a valid positive integer size.")
            return
            
        addr = self.conn.kmalloc(size)
        if addr > 0:
            self._draw_heap_canvas()
            # Select the newly allocated block
            self.selected_block_addr = addr
            self.block_info_lbl.config(
                text=f"Mallocated: Addr 0x{addr:X} | Size: {size} Bytes | Status: Allocated"
            )
            self.kfree_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Out Of Memory", "C-Kernel failed to allocate heap memory block.")
            
    def _on_kfree(self):
        if not self.selected_block_addr:
            return
            
        self.conn.kfree(self.selected_block_addr)
        self.selected_block_addr = None
        self.block_info_lbl.config(text="Block freed successfully. Adjacent blocks coalesced!")
        self.kfree_btn.config(state=tk.DISABLED)
        self._draw_heap_canvas()

def main():
    app = SystemMonitorApp()
    app.window.mainloop()

if __name__ == "__main__":
    main()
