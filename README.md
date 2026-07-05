# 🌌 AuroraOS - Unified Hybrid Operating System

Welcome to **AuroraOS**, a highly modular, lightweight, and visual hybrid operating system designed for educational and experimental systems development. 

AuroraOS is structured as a **Dual-Architecture OS**:
1. **Simulated GUI/CLI Environment (Hybrid)**: A Tkinter-based desktop environment that connects directly to a compiled low-level C Kernel DLL using dynamic binary linking (`ctypes`). If a C compiler is not present, it features a complete Python-based Kernel Simulator fallback.
2. **Bare-Metal Operating System (x86)**: A real, bootable 32-bit x86 operating system featuring an interrupt-driven GDT/IDT, PS/2 mouse and keyboard drivers, and a pixel-addressable VGA graphics kernel that boots inside QEMU.

---

## 🎯 Architectural Overview

AuroraOS operates as a **hybrid system** to demonstrate both low-level OS design and modern desktop application layer interactions:

```mermaid
graph TD
    subgraph User Space (Python GUI)
        A[Aurora Shell Desktop] --> B[System Diagnostics Manager]
        A --> C[Terminal Emulator]
        A --> D[File Manager]
    end

    subgraph System Services Layer (Python)
        E[Virtual File System VFS] --> F[VFS Inode DB]
        G[Session & User Manager] --> H[JSON Auth DB]
    end

    subgraph Dynamic Linking Interface
        I[Kernel Connector ctypes]
    end

    subgraph Low-Level Kernel (C DLL)
        J[C Process Scheduler] --> K[Linked-List Memory Heap Allocator]
        K --> L[Simulated Physical Memory]
    end

    B & C --> I
    I --> J
    D --> E
```

---

## 📂 Directory Layout

```
AuroraOS/
├── apps/                   # Built-in Desktop Applications
│   ├── calculator/         # Standard Calculator GUI app
│   ├── editor/             # Text Editor app with VFS save/load
│   ├── filemanager/        # Graphical directory/file browser
│   ├── settings/           # Customizer for user data and themes
│   ├── sysmonitor/         # Diagnostics, Task Manager, & Heap Visualizer
│   └── terminal/           # Shell emulator with command routing
├── bare_metal/             # Bootable x86 C/Assembly OS Kernel
│   ├── boot/               # boot.asm Multiboot x86 entry point
│   ├── arch/               # GDT, IDT, ISR descriptors and loader scripts
│   ├── drivers/            # VGA graphics, keyboard, and PS/2 mouse drivers
│   ├── kernel/             # Bare-metal kernel entry point
│   └── libc/               # Standard library overrides (string, stdio)
├── config/                 # System Registry and User DB
│   ├── system/             # VFS virtual_disk.img and metadata
│   └── user/               # Persistent users and sessions data
├── docs/                   # Developer guides & API references
├── drivers/                # Simulated storage and display drivers
├── kernel/                 # Shared C Kernel library code (ctypes target)
│   ├── include/            # C headers (kernel.h, memory.h)
│   └── src/                # C implementation (kernel.c, memory.c)
├── system/                 # System services
│   └── core/               # File system (VFS) and C-Kernel Connector
├── ui/                     # Tkinter graphics components
│   ├── shell/              # Desktop environment, Start Menu, & Taskbar
│   └── themes/             # Color tokens, styles, and asset catalogs
├── user/                   # User Profile and Session Management
├── launcher.py             # Main GUI OS startup script
├── Makefile                # Root builder automating C DLL and bare-metal compilation
└── requirements.txt        # Python external dependency declarations
```

---

## ✨ Features and Enhancements

### 1. Interactive Heap Memory Visualizer (New!)
A real-time graphical debugger of the C-Kernel dynamic heap allocator.
* **Live Block Map**: Displays all memory blocks (metadata headers + payload) sequentially.
* **Color-Coded Status**: Free blocks are drawn in **green**, and allocated blocks are in **purple**.
* **Splitting & Coalescing**: Watch blocks split when `kmalloc` is called, and watch adjacent free blocks merge (coalesce) back together when `kfree` is triggered!
* **Diagnostics Panel**: Clicking any block highlights it and shows its exact memory address (hex), size, and allocation state.

### 2. C-Kernel Process & Task Manager (New!)
An interactive process controller linked to the kernel scheduler.
* **Active Queue**: Displays PID, Name, Priority, Scheduler State (READY, RUNNING, WAITING), and CPU execution ticks.
* **Graphical Controller**: Create new mock threads or terminate active processes from the GUI. Protected system threads (like `init` and `kthreadd`) have kill-safeguards to prevent system panic.

### 3. FAT-like Virtual File System (VFS)
* **Storage virtualization**: Simulates a physical disk storage by reading/writing blocks to a raw binary disk image (`virtual_disk.img`).
* **Inode-based metadata**: Manages path structures, allocation tables, and file properties dynamically.

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.8+**
* **GCC Compiler** (MinGW for Windows, standard GCC for Linux)
* **NASM** (Required for bare-metal Assembly assembly)
* **QEMU** (Required for bare-metal emulation)

### Setup & Run (GUI Simulator)

1. Open your terminal in the `AuroraOS` directory.
2. Run the system using the root Makefile:
   ```bash
   make run
   ```
   *Note: This command automatically detects your OS, compiles the dynamic C library (`kernel.dll` / `kernel.so`), configures UTF-8 encoding streams, creates the 100MB virtual disk if missing, and boots the launcher GUI.*

3. Log in using the default administrator credentials:
   * **Username**: `aurora`
   * **Password**: `admin123`

---

## 🖥️ Running the Bare-Metal x86 Kernel

To build and run the bootable x86 operating system inside the QEMU emulator:

1. **Install NASM and QEMU**:
   * **Windows** (via Chocolatey):
     ```bash
     choco install nasm qemu
     ```
   * **Windows** (via Winget):
     ```bash
     winget install NASM.NASM SoftwareCollab.QEMU
     ```
   * **Linux/Debian**:
     ```bash
     sudo apt install nasm qemu-system-x86 build-essential
     ```

2. **Compile and Run**:
   ```bash
   make baremetal
   make run-baremetal
   ```

### What boots inside the emulator?
The bare-metal kernel initializes the GDT/IDT descriptors, hooks keyboard/mouse interrupt handlers, boots into a 320x200 256-color VGA mode, and renders:
* A windowed UI showing OS metrics.
* A live taskbar.
* A retro crosshair mouse cursor that moves as you drag your physical mouse, with click notifications on left/right click triggers.

---

## 🛠️ Developer Code Reference

### Dynamic Linking CTypes Schema
The Python [kernel_connector.py](file:///c:/Users/ANSARI%20MOHAMMED/OneDrive/Desktop/Software/AuroraOS/system/core/kernel_connector.py) defines structures that map exactly to the C struct alignments.

```python
# Ctypes Struct representing a C-Memory Block
class HeapBlockInfo(ctypes.Structure):
    _fields_ = [
        ("address", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("is_free", ctypes.c_uint32),
    ]

# Function binding mapping to memory.c exports
def _bind_functions(self):
    self.lib.get_heap_block_count.argtypes = []
    self.lib.get_heap_block_count.restype = ctypes.c_int
    
    self.lib.get_heap_blocks.argtypes = [ctypes.POINTER(HeapBlockInfo), ctypes.c_int]
    self.lib.get_heap_blocks.restype = ctypes.c_int
```

```c
// Matching C structure in memory.h
typedef struct {
    uint32_t address;
    uint32_t size;
    uint32_t is_free;
} heap_block_info_t;
```

---

## 📋 Roadmap & Achievements
- [x] Consolidate project files into a unified structure.
- [x] Link C kernel memory/processes dynamically to Python Tkinter.
- [x] Implement the interactive VFS block filesystem.
- [x] Create the System Diagnostics Task Manager.
- [x] Add the graphical C-Heap Allocator block visualizer.
- [x] Create root Makefiles to build both the GUI and the bare-metal kernel.
- [ ] Add virtual network socket simulations.
- [ ] Implement write-back file caching to VFS blocks.

---

## 📄 License
This project is created for educational purposes. Feel free to copy, modify, and learn from it.
