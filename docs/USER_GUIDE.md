# AuroraOS User Guide

Welcome to **AuroraOS** - an educational lightweight operating system with a beautiful Aurora theme!

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [System Overview](#system-overview)
3. [Login & Authentication](#login--authentication)
4. [Using the Aurora Shell](#using-the-aurora-shell)
5. [Built-in Applications](#built-in-applications)
6. [Terminal Commands](#terminal-commands)
7. [File System](#file-system)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements
- **Python:** 3.8 or higher
- **Operating System:** Windows, Linux, or macOS
- **RAM:** Minimum 2 GB (for host system)
- **Display:** 1024x768 minimum resolution

### First Time Setup

1. **Navigate to the AuroraOS directory:**
   ```bash
   cd "AuroraOS"
   ```

2. **Launch AuroraOS:**
   ```bash
   python launcher.py
   ```

3. **Login with default credentials:**
   - **Username:** `aurora`
   - **Password:** `admin123`

---

## System Overview

AuroraOS is structured with multiple layers:

### 🔹 Kernel Layer (C)
- Memory management
- Process scheduling
- Interrupt handling
- System calls

### 🔹 System Services (Python)
- Virtual file system
- User authentication
- Session management
- Device simulation

### 🔹 User Interface (Python/Tkinter)
- Aurora Shell (desktop environment)
- Built-in applications
- Window management

---

## Login & Authentication

### Default Accounts

AuroraOS comes with two pre-configured accounts:

| Username | Password  | Type          |
|----------|-----------|---------------|
| aurora   | admin123  | Administrator |
| guest    | guest     | Standard User |

### Creating New Users

1. Log in as administrator
2. Open **Settings** → **User Account**
3. Click **Manage Users**
4. Follow the prompts to create a new user

### Changing Password

1. Open **Settings** → **User Account**
2. Click **Change Password**
3. Enter current and new password
4. Confirm changes

---

## Using the Aurora Shell

The Aurora Shell is the main desktop environment featuring a northern lights-inspired theme.

### Desktop Features

#### 🖥️ Desktop Icons
- **My Computer:** View system information
- **Files:** Open file manager
- **Recycle Bin:** View deleted files

#### 📊 Taskbar
Located at the bottom of the screen:
- **Start Menu:** Access applications and system functions
- **Quick Launch:** Fast access to common apps
- **System Tray:** Network, volume, power status
- **Clock:** Current time and date

### Start Menu Options

Access the start menu by clicking **⚡ Start** button:

- **Applications:**
  - 📁 File Manager
  - ⌨️ Terminal
  - 📝 Text Editor
  - 💻 System Info

- **System:**
  - ⚙️ Settings
  - 🔒 Lock
  - 🔄 Restart
  - ⚠️ Shutdown

---

## Built-in Applications

### 📁 File Manager

Navigate and manage files in the virtual file system.

**Features:**
- Browse directories
- Create/delete files and folders
- View file contents
- Navigation history (back/forward)
- Address bar navigation

**Keyboard Shortcuts:**
- Press **Enter** to open selected item
- Use arrow keys to navigate

### ⌨️ Terminal

Command-line interface for advanced users.

**Features:**
- Execute system commands
- File operations (ls, cd, cat, etc.)
- Command history (up/down arrows)
- Tab completion support

See [Terminal Commands](#terminal-commands) for available commands.

### 📝 Text Editor

Simple text editor for creating and editing files.

**Features:**
- Open/save files from VFS
- Cut, copy, paste
- Word wrap toggle
- Undo/redo support

**Keyboard Shortcuts:**
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+A` - Select all

### ⚙️ Settings

System configuration and customization.

**Sections:**
- **👤 User Account:** View user info, manage accounts
- **🎨 Appearance:** Theme selection and colors
- **🖥️ System Info:** View system details
- **ℹ️ About:** AuroraOS information

---

## Terminal Commands

### File System Commands

```bash
# List directory contents
ls [directory]

# Change directory
cd <directory>
cd ..           # Go to parent directory
cd              # Go to home directory

# Print working directory
pwd

# Display file contents
cat <file>

# Create directory
mkdir <directory_name>

# Create empty file
touch <file_name>

# Remove file or directory
rm <path>
```

### System Commands

```bash
# Show current user
whoami

# Show current date and time
date

# Show system uptime
uptime

# Show system information
sysinfo

# Clear terminal screen
clear

# Show help
help

# Exit terminal
exit
```

### Example Usage

```bash
# Create a new directory
mkdir my_projects

# Navigate to it
cd my_projects

# Create a file
touch hello.txt

# List contents
ls

# Go back to home
cd
```

---

## File System

AuroraOS uses a virtual FAT-like file system.

### Directory Structure

```
/                       # Root directory
├── home/              # User home directories
│   └── aurora/        # Default user home
│       ├── Documents/
│       ├── Downloads/
│       ├── Pictures/
│       └── welcome.txt
├── bin/               # System binaries
├── etc/               # Configuration files
├── tmp/               # Temporary files
├── usr/               # User programs
│   └── local/
└── var/               # Variable data
```

### File Paths

- **Absolute paths** start with `/`: `/home/aurora/Documents`
- **Relative paths** are relative to current directory: `Documents/file.txt`
- **Home directory** shortcut: `~` (Terminal only)

### Storage

- **Total Capacity:** 100 MB (virtual)
- **Block Size:** 4 KB
- **File System Type:** Virtual FAT-like

### File Operations

#### Create File
```python
# Via Terminal
touch /home/aurora/myfile.txt

# Via File Manager
Click "📄 New File" button
```

#### Create Folder
```python
# Via Terminal
mkdir /home/aurora/myfolder

# Via File Manager
Click "➕ New Folder" button
```

#### Delete File/Folder
```python
# Via Terminal
rm /home/aurora/myfile.txt

# Via File Manager
Select item → Click "🗑️ Delete"
```

---

## Troubleshooting

### Common Issues

#### 🔴 Problem: Login screen doesn't appear
**Solution:**
- Ensure Python 3.8+ is installed
- Check that tkinter is available: `python -c "import tkinter"`
- On Linux, install: `sudo apt-get install python3-tk`

#### 🔴 Problem: "File not found" errors
**Solution:**
- Check file paths are correct
- Use absolute paths starting with `/`
- Verify file exists with `ls` command

#### 🔴 Problem: Applications won't launch
**Solution:**
- Check console for error messages
- Ensure all files are in correct directories
- Verify Python path is set correctly

#### 🔴 Problem: Cannot save files
**Solution:**
- Check disk space with File Manager
- Ensure you have write permissions
- Verify file path is valid

### Getting Help

If you encounter issues:

1. **Check console output** for error messages
2. **Review log files** in the AuroraOS directory
3. **Verify file structure** matches documentation
4. **Check Python version:** `python --version`

### Resetting the System

To reset AuroraOS to defaults:

1. Close AuroraOS
2. Delete these files:
   - `config/system/virtual_disk.img`
   - `config/system/filesystem_metadata.json`
   - `config/user/users.json`
   - `config/user/session.json`
3. Restart AuroraOS

**Note:** This will delete all user data and files!

---

## Tips & Tricks

### Keyboard Shortcuts

**Shell:**
- `Alt+F4` - Close window
- `F11` - Toggle fullscreen (if supported)

**Terminal:**
- `Up/Down Arrow` - Navigate command history
- `Ctrl+C` - Cancel current input
- `Tab` - Command completion (planned feature)

**Text Editor:**
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save as

### Best Practices

1. **Regular saves:** Save your work frequently in Text Editor
2. **Organized files:** Keep files organized in dedicated folders
3. **Use Terminal:** Learn terminal commands for faster operations
4. **Explore safely:** The system is sandboxed - experiment freely!

### Advanced Features

- Create symbolic links (planned)
- Schedule tasks (planned)
- Custom themes (planned)
- Package management (planned)

---

## Additional Resources

- **Developer Guide:** See `docs/DEVELOPER_GUIDE.md`
- **Architecture Overview:** See `docs/architecture/OVERVIEW.md`
- **API Reference:** See `docs/api/KERNEL_API.md`

---

**Enjoy using AuroraOS! 🌌**

*Where education meets innovation*


---

## 📖 Systems Theory for the Everyday User

Operating systems seem magical, but they follow strict deterministic logic. Here is how your actions translate to under-the-hood events:

### 1. When you Create a File in File Manager
1. **User Request**: You click "New File" and enter `notes.txt`.
2. **System Service Call**: The File Manager app makes a call to the Virtual File System (VFS): `vfs.create_file("/home/aurora/notes.txt")`.
3. **Inode Allocation**: The VFS finds an unused Inode slot, registers `notes.txt` as a child of `/home/aurora/`, and sets the size to `0`.
4. **Disk Write**: VFS writes the updated Inode structure to `virtual_disk.img` and updates `filesystem_metadata.json`.
5. **UI Update**: The File Manager refreshes, reading the Inode table to show the new icon.

### 2. When you Delete a Folder
1. **Recursion**: The VFS checks if the folder contains files.
2. **Block Deallocation**: If files exist, the VFS marks all data blocks associated with those files as "free" in the Superblock bitmap.
3. **Inode Clearing**: The Inode entries for the files and the folder itself are wiped clean.
4. **No Crash Safety**: In older versions, deleting closed the application due to standard stream errors. Now, the File Manager updates live and stays open safely.
