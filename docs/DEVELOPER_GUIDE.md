# AuroraOS Developer Guide

Complete technical documentation for developers working on AuroraOS.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Adding Features](#adding-features)
6. [Testing](#testing)
7. [Contributing](#contributing)

---

## Architecture Overview

AuroraOS uses a **hybrid architecture** combining C (kernel) and Python (system services & UI).

### System Layers

```
┌─────────────────────────────────────────┐
│         User Applications               │
│    (Terminal, Editor, File Manager)     │
├─────────────────────────────────────────┤
│          Aurora Shell (GUI)             │
│         (Tkinter-based Desktop)         │
├─────────────────────────────────────────┤
│        System Services (Python)         │
│  (File System, Auth, Session Manager)   │
├─────────────────────────────────────────┤
│        Kernel Layer (C/Python)          │
│   (Memory, Process, Interrupt Mgmt)     │
├─────────────────────────────────────────┤
│       Hardware Abstraction Layer        │
│          (Simulated Devices)            │
└─────────────────────────────────────────┘
```

### Design Principles

1. **Modularity:** Each component is self-contained
2. **Simplicity:** Easy to understand and modify
3. **Educational:** Clear code with extensive comments
4. **Extensibility:** Easy to add new features

---

## Development Setup

### Prerequisites

```bash
# Python 3.8+
python --version

# Git (optional)
git --version

# GCC (for C kernel compilation)
gcc --version
```

### Setting Up Development Environment

1. **Clone/Download the project:**
   ```bash
   cd "AuroraOS"
   ```

2. **Install development tools (optional):**
   ```bash
   pip install pylint black mypy
   ```

3. **Verify structure:**
   ```bash
   python launcher.py
   ```

### IDE Recommendations

- **VS Code** with Python extension
- **PyCharm** Community Edition
- **Sublime Text** with Python plugins

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-vscode.cpptools"
  ]
}
```

---

## Project Structure

### Directory Layout

```
AuroraOS/
├── boot/                   # Bootloader (future implementation)
├── kernel/                 # C-based kernel
│   ├── include/           # Header files
│   │   ├── kernel.h
│   │   └── memory.h
│   └── src/               # C source files
│       ├── kernel.c
│       └── memory.c
├── system/                # System services (Python)
│   ├── core/
│   │   └── filesystem.py  # Virtual file system
│   └── services/          # Background services
├── drivers/               # Device drivers (simulated)
│   ├── display/
│   └── disk/
├── user/                  # User management
│   ├── auth/
│   │   └── authentication.py
│   └── session/
│       └── session_manager.py
├── apps/                  # Built-in applications
│   ├── terminal/
│   │   └── terminal.py
│   ├── editor/
│   │   └── text_editor.py
│   ├── filemanager/
│   │   └── file_manager.py
│   └── settings/
│       └── settings.py
├── ui/                    # User interface
│   ├── shell/
│   │   └── aurora_shell.py
│   ├── themes/            # Theme files
│   └── assets/            # Icons, images
├── config/                # Configuration
│   ├── system/            # System config
│   └── user/              # User data
├── docs/                  # Documentation
│   ├── api/
│   ├── architecture/
│   ├── USER_GUIDE.md
│   └── DEVELOPER_GUIDE.md
├── launcher.py            # Main entry point
├── requirements.txt       # Dependencies
└── README.md             # Project README
```

### Key Files

| File | Purpose |
|------|---------|
| `launcher.py` | Main system launcher and boot sequence |
| `kernel/src/kernel.c` | Core kernel implementation |
| `system/core/filesystem.py` | Virtual file system |
| `user/auth/authentication.py` | User authentication |
| `ui/shell/aurora_shell.py` | Desktop environment |

---

## Core Components

### 1. Kernel Layer

**Location:** `kernel/src/kernel.c`

**Key Functions:**
```c
// Initialization
void kernel_init(void);
void kernel_main(void);
void kernel_shutdown(void);

// Process Management
int32_t process_create(const char *name, void (*entry_point)(void), uint32_t priority);
int32_t process_kill(uint32_t pid);
void scheduler_run(void);

// Memory Management
void memory_init(uint32_t total_mem);
void* kmalloc(size_t size);
void kfree(void *ptr);

// Interrupts
void interrupts_init(void);
void interrupt_register_handler(uint8_t num, interrupt_handler_t handler);
```

**To modify the kernel:**
```c
// 1. Edit kernel/src/kernel.c
// 2. Implement your function
void my_kernel_function() {
    kprintf("[KERNEL] My custom function\n");
}

// 3. Add declaration to kernel/include/kernel.h
void my_kernel_function(void);
```

### 2. File System

**Location:** `system/core/filesystem.py`

**Key Classes:**
```python
class FileNode:
    """Represents a file or directory"""
    pass

class VirtualFileSystem:
    """Main VFS implementation"""
    
    def create_file(self, path: str, content: str) -> bool:
        """Create a new file"""
        
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        
    def write_file(self, path: str, content: str) -> bool:
        """Write to file"""
        
    def delete_file(self, path: str) -> bool:
        """Delete file"""
        
    def mkdir(self, path: str) -> bool:
        """Create directory"""
        
    def list_dir(self, path: str) -> List[Dict]:
        """List directory contents"""
```

**To add file system features:**
```python
# 1. Add method to VirtualFileSystem class
def my_new_feature(self, path: str) -> bool:
    """My new feature description"""
    # Implementation here
    pass

# 2. Update metadata structure if needed
# 3. Test with terminal commands
```

### 3. Authentication System

**Location:** `user/auth/authentication.py`

**Key Classes:**
```python
class User:
    """User account representation"""
    def __init__(self, username, password_hash, full_name, is_admin):
        pass

class AuthenticationManager:
    """Handles user authentication"""
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        
    def create_user(self, username: str, password: str) -> bool:
        """Create new user"""
        
    def change_password(self, username: str, old: str, new: str) -> bool:
        """Change user password"""
```

### 4. Aurora Shell

**Location:** `ui/shell/aurora_shell.py`

**Key Components:**
```python
class AuroraShell:
    """Main desktop shell"""
    
    def __init__(self):
        """Initialize shell"""
        
    def _create_desktop(self):
        """Create desktop area"""
        
    def _create_taskbar(self):
        """Create taskbar"""
        
    def open_file_manager(self):
        """Launch file manager"""
        
    def open_terminal(self):
        """Launch terminal"""
```

**Theme Colors:**
```python
class AuroraTheme:
    DEEP_BLACK = "#0A0E27"
    NEON_BLUE = "#5E60CE"
    PURPLE = "#9D4EDD"
    TEAL = "#00D9FF"
    CYAN = "#00F5FF"
```

---

## Adding Features

### Adding a New Application

1. **Create app directory:**
   ```bash
   mkdir apps/myapp
   ```

2. **Create main file:**
   ```python
   # apps/myapp/myapp.py
   import tkinter as tk
   
   class MyApp:
       def __init__(self, parent=None):
           self.window = tk.Toplevel(parent) if parent else tk.Tk()
           self.window.title("My App - AuroraOS")
           self._create_ui()
       
       def _create_ui(self):
           # UI code here
           pass
   
   def main():
       app = MyApp()
       app.window.mainloop()
   
   if __name__ == "__main__":
       main()
   ```

3. **Add to shell:**
   ```python
   # In ui/shell/aurora_shell.py
   
   def open_my_app(self):
       """Launch my app"""
       try:
           from apps.myapp.myapp import MyApp
           MyApp(self.root)
       except Exception as e:
           messagebox.showinfo("My App", "My App will open here")
   
   # Add to start menu or taskbar
   ```

### Adding Terminal Commands

1. **Edit terminal.py:**
   ```python
   # In apps/terminal/terminal.py
   
   def _cmd_mycommand(self, args):
       """My custom command"""
       self._print_output("Executing my command...")
       # Command implementation
   
   # Add to command routing
   commands = {
       # ... existing commands ...
       'mycommand': self._cmd_mycommand,
   }
   ```

2. **Update help:**
   ```python
   def _cmd_help(self, args):
       # ... existing help ...
       self._print_output("  mycommand - Description of my command")
   ```

### Adding System Services

1. **Create service file:**
   ```python
   # system/services/my_service.py
   
   class MyService:
       def __init__(self):
           self.running = False
       
       def start(self):
           """Start service"""
           self.running = True
           print("[MyService] Started")
       
       def stop(self):
           """Stop service"""
           self.running = False
           print("[MyService] Stopped")
   
   # Global instance
   my_service = None
   
   def get_my_service():
       global my_service
       if my_service is None:
           my_service = MyService()
       return my_service
   ```

2. **Initialize in launcher:**
   ```python
   # In launcher.py
   
   def initialize_system():
       # ... existing initialization ...
       
       from system.services.my_service import get_my_service
       service = get_my_service()
       service.start()
   ```

---

## Testing

### Manual Testing

1. **Test file system:**
   ```bash
   python launcher.py
   # Login → Open Terminal
   # Run: mkdir test_dir
   # Run: cd test_dir
   # Run: touch test.txt
   # Run: ls
   ```

2. **Test authentication:**
   ```bash
   # Try logging in with wrong password
   # Verify lockout after 3 attempts
   # Test password change in Settings
   ```

3. **Test applications:**
   ```bash
   # Launch each app from start menu
   # Verify all features work
   # Test keyboard shortcuts
   ```

### Automated Testing (Future)

```python
# tests/test_filesystem.py
import unittest
from system.core.filesystem import VirtualFileSystem

class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.vfs = VirtualFileSystem()
    
    def test_create_file(self):
        result = self.vfs.create_file("/test.txt", "content")
        self.assertTrue(result)
    
    def test_read_file(self):
        self.vfs.create_file("/test.txt", "hello")
        content = self.vfs.read_file("/test.txt")
        self.assertEqual(content, "hello")

if __name__ == '__main__':
    unittest.main()
```

---

## Contributing

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings
- Maximum line length: 100

**C:**
- K&R style bracing
- 4-space indentation
- Descriptive variable names
- Comment complex logic

### Commit Guidelines

```bash
# Format: [Component] Brief description

git commit -m "[Kernel] Add process priority support"
git commit -m "[FileSystem] Fix directory deletion bug"
git commit -m "[UI] Improve theme colors"
```

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Implement feature with tests
4. Update documentation
5. Submit pull request

---

## Debugging Tips

### Enable Debug Mode

```python
# In launcher.py, add at top:
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")
```

### Common Debugging Scenarios

**File system issues:**
```python
# Check disk image
import os
print(os.path.exists("config/system/virtual_disk.img"))

# View metadata
import json
with open("config/system/filesystem_metadata.json") as f:
    print(json.dumps(json.load(f), indent=2))
```

**Authentication issues:**
```python
# Check users file
import json
with open("config/user/users.json") as f:
    print(json.dumps(json.load(f), indent=2))
```

### Logging

Add comprehensive logging:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('auroraos.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

---

## Advanced Topics

### Performance Optimization

- Use lazy loading for large data
- Implement caching where appropriate
- Profile code with `cProfile`
- Optimize file system block allocation

### Security Considerations

- Hash passwords with SHA-256 (currently)
- Consider bcrypt for production
- Implement session timeouts
- Add file permission checks

### Future Enhancements

- [ ] Real bootloader with GRUB
- [ ] Actual assembly code for kernel
- [ ] Hardware device drivers
- [ ] Network stack implementation
- [ ] Package manager
- [ ] Multi-user concurrent sessions
- [ ] Scripting language support

---

## Resources

### Learning Materials

- **OS Development:**
  - OSDev Wiki: https://wiki.osdev.org
  - Operating Systems: Three Easy Pieces (book)
  
- **Python GUI:**
  - Tkinter documentation
  - Real Python Tkinter tutorials

- **C Programming:**
  - K&R C Programming Language
  - Learn C the Hard Way

### Reference Projects

- **Minix:** Educational OS
- **xv6:** MIT teaching OS
- **ToaruOS:** Hobby OS with GUI

---

**Happy coding! 🌌**

*Building operating systems, one line at a time*


---

## 🧪 Developer Architecture & API References

### 1. Writing a New Custom C-Kernel Function
To add a new routine to the C Kernel:
1. Open [kernel/include/kernel.h](file:///c:/Users/ANSARI%20MOHAMMED/OneDrive/Desktop/Software/AuroraOS/kernel/include/kernel.h) or the appropriate header and declare your function:
   ```c
   __declspec(dllexport) int get_system_uptime_ticks(void);
   ```
2. Implement your function in the source file:
   ```c
   int get_system_uptime_ticks(void) {
       return scheduler_ticks; // Global tick counter
   }
   ```
3. Recompile the library using the Makefile:
   ```bash
   make clean && make
   ```
4. Bind the function in the Python connector [system/core/kernel_connector.py](file:///c:/Users/ANSARI%20MOHAMMED/OneDrive/Desktop/Software/AuroraOS/system/core/kernel_connector.py):
   ```python
   self.lib.get_system_uptime_ticks.argtypes = []
   self.lib.get_system_uptime_ticks.restype = ctypes.c_int
   ```
5. Implement the simulation fallback inside `PythonKernelSimulator` to prevent crashes when the C library is compiled as a mismatch.

### 2. Debugging Memory Violations
If a memory violation occurs (segmentation fault) in the DLL, Windows will terminate the Python process instantly. To debug this:
* Compile with debugging symbols enabled by adding `-g` to the compiler flags in the [Makefile](file:///c:/Users/ANSARI%20MOHAMMED/OneDrive/Desktop/Software/AuroraOS/Makefile).
* Run the Python script using a native debugger like GDB:
  ```bash
  gdb --args python launcher.py
  ```
