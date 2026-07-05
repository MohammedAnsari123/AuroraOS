"""
AuroraOS Virtual File System
FAT-like file system implementation with full CRUD operations

This module implements a simple virtual file system that stores files
in a binary image file, supporting directories, files, and metadata.
"""

import os
import json
import time
import struct
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ============================================================================
# FILE SYSTEM CONSTANTS
# ============================================================================

BLOCK_SIZE = 4096  # 4KB blocks
MAX_FILENAME_LENGTH = 255
MAX_PATH_LENGTH = 4096
DISK_IMAGE_PATH = "config/system/virtual_disk.img"
METADATA_PATH = "config/system/filesystem_metadata.json"

# File types
FILE_TYPE_REGULAR = 0
FILE_TYPE_DIRECTORY = 1
FILE_TYPE_SYMLINK = 2

# File permissions
PERM_READ = 0o444
PERM_WRITE = 0o222
PERM_EXECUTE = 0o111
PERM_DEFAULT = 0o644

# ============================================================================
# FILE SYSTEM CLASSES
# ============================================================================

class FileNode:
    """Represents a file or directory in the file system"""
    
    def __init__(self, name: str, file_type: int = FILE_TYPE_REGULAR,
                 parent: Optional[str] = None):
        self.name = name
        self.file_type = file_type
        self.parent = parent
        self.size = 0
        self.created = time.time()
        self.modified = time.time()
        self.accessed = time.time()
        self.permissions = PERM_DEFAULT
        self.owner = "aurora"
        self.data_blocks = []  # List of block indices
        self.children = {} if file_type == FILE_TYPE_DIRECTORY else None
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'type': self.file_type,
            'parent': self.parent,
            'size': self.size,
            'created': self.created,
            'modified': self.modified,
            'accessed': self.accessed,
            'permissions': self.permissions,
            'owner': self.owner,
            'data_blocks': self.data_blocks,
            'children': list(self.children.keys()) if self.children else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileNode':
        """Create FileNode from dictionary"""
        node = cls(data['name'], data['type'], data.get('parent'))
        node.size = data['size']
        node.created = data['created']
        node.modified = data['modified']
        node.accessed = data['accessed']
        node.permissions = data['permissions']
        node.owner = data['owner']
        node.data_blocks = data['data_blocks']
        if data['children'] is not None:
            node.children = {child: None for child in data['children']}
        return node


class VirtualFileSystem:
    """Virtual File System Implementation"""
    
    def __init__(self, disk_size_mb: int = 100):
        self.disk_size = disk_size_mb * 1024 * 1024  # Convert to bytes
        self.total_blocks = self.disk_size // BLOCK_SIZE
        self.free_blocks = set(range(self.total_blocks))
        self.root = FileNode("/", FILE_TYPE_DIRECTORY)
        self.inodes = {"/": self.root}
        self.current_dir = "/"
        
        # Initialize or load existing file system
        self._initialize_filesystem()
        
    def _initialize_filesystem(self):
        """Initialize or load existing file system"""
        # Create config directory if it doesn't exist
        os.makedirs("config/system", exist_ok=True)
        
        # Load existing file system or create new one
        if os.path.exists(METADATA_PATH):
            self._load_metadata()
        else:
            self._create_default_structure()
            # Save only once after initial structure is created
            self._save_metadata()
        
        # Create or load disk image
        if not os.path.exists(DISK_IMAGE_PATH):
            self._create_disk_image()
    
    def _create_disk_image(self):
        """Create empty disk image file of specified size"""
        try:
            print(f"[VFS] Creating empty disk image: {DISK_IMAGE_PATH} ({self.disk_size // (1024 * 1024)} MB)...")
            with open(DISK_IMAGE_PATH, 'wb') as f:
                # Write in 1MB chunks to be memory-efficient
                chunk = b'\x00' * (1024 * 1024)
                for _ in range(self.disk_size // (1024 * 1024)):
                    f.write(chunk)
            print(f"[VFS] [OK] Created empty disk image: {DISK_IMAGE_PATH}")
        except Exception as e:
            print(f"[VFS] Error creating disk image: {e}")
            
    def _create_default_structure(self):
        """Create default directory structure"""
        directories = [
            "/home",
            "/home/aurora",
            "/home/aurora/Documents",
            "/home/aurora/Downloads",
            "/home/aurora/Pictures",
            "/bin",
            "/etc",
            "/var",
            "/tmp",
            "/usr",
            "/usr/local",
        ]
        
        # Use a version of mkdir that doesn't save metadata on every call
        for dir_path in directories:
            self.mkdir(dir_path, save=False)
        
        # Create welcome file
        welcome_content = """Welcome to AuroraOS!

This is your personal operating system built for educational purposes.

Quick Guide:
- Use the File Manager to browse files
- Open Terminal to run commands
- Check System Settings to customize your experience

Enjoy exploring AuroraOS!
"""
        self.create_file("/home/aurora/welcome.txt", welcome_content, save=False)
    
    def _save_metadata(self):
        """Save file system metadata to JSON"""
        metadata = {
            'disk_size': self.disk_size,
            'total_blocks': self.total_blocks,
            'free_blocks': list(self.free_blocks),
            'inodes': {path: node.to_dict() for path, node in self.inodes.items()}
        }
        
        with open(METADATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self):
        """Load file system metadata from JSON"""
        try:
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.disk_size = metadata['disk_size']
            self.total_blocks = metadata['total_blocks']
            self.free_blocks = set(metadata['free_blocks'])
            
            # Rebuild inode tree
            self.inodes = {}
            for path, node_data in metadata['inodes'].items():
                self.inodes[path] = FileNode.from_dict(node_data)
            
            # Rebuild parent-child relationships
            for path, node in self.inodes.items():
                if node.children is not None:
                    node.children = {
                        child: self.inodes.get(f"{path}/{child}".replace("//", "/"))
                        for child in node.children.keys()
                    }
            
            self.root = self.inodes["/"]
            print("[VFS] [OK] Loaded existing file system")
            
        except Exception as e:
            print(f"[VFS] Warning: Could not load metadata: {e}")
            self._create_default_structure()
    
    def _allocate_blocks(self, num_blocks: int) -> List[int]:
        """Allocate blocks for file storage"""
        if len(self.free_blocks) < num_blocks:
            raise IOError("Not enough disk space")
        
        blocks = []
        for _ in range(num_blocks):
            block = self.free_blocks.pop()
            blocks.append(block)
        
        return blocks
    
    def _free_blocks(self, blocks: List[int]):
        """Free allocated blocks"""
        for block in blocks:
            self.free_blocks.add(block)
    
    def _write_blocks(self, blocks: List[int], data: bytes):
        """Write data to disk blocks"""
        with open(DISK_IMAGE_PATH, 'r+b') as f:
            offset = 0
            for block_idx in blocks:
                f.seek(block_idx * BLOCK_SIZE)
                chunk = data[offset:offset + BLOCK_SIZE]
                f.write(chunk)
                offset += BLOCK_SIZE
    
    def _read_blocks(self, blocks: List[int]) -> bytes:
        """Read data from disk blocks"""
        data = b''
        with open(DISK_IMAGE_PATH, 'rb') as f:
            for block_idx in blocks:
                f.seek(block_idx * BLOCK_SIZE)
                data += f.read(BLOCK_SIZE)
        return data
    
    def _normalize_path(self, path: str) -> str:
        """Normalize file path"""
        if not path.startswith('/'):
            path = os.path.join(self.current_dir, path)
        
        parts = []
        for part in path.split('/'):
            if part == '..':
                if parts:
                    parts.pop()
            elif part and part != '.':
                parts.append(part)
        
        return '/' + '/'.join(parts) if parts else '/'
    
    # ========================================================================
    # PUBLIC FILE OPERATIONS
    # ========================================================================
    
    def create_file(self, path: str, content: str = "", save: bool = True) -> bool:
        """Create a new file"""
        try:
            path = self._normalize_path(path)
            
            if path in self.inodes:
                print(f"[VFS] Error: File already exists: {path}")
                return False
            
            # Get parent directory
            parent_path = os.path.dirname(path) or "/"
            if parent_path not in self.inodes:
                print(f"[VFS] Error: Parent directory doesn't exist: {parent_path}")
                return False
            
            parent = self.inodes[parent_path]
            if parent.file_type != FILE_TYPE_DIRECTORY:
                print(f"[VFS] Error: Parent is not a directory: {parent_path}")
                return False
            
            # Create file node
            filename = os.path.basename(path)
            node = FileNode(filename, FILE_TYPE_REGULAR, parent_path)
            
            # Write content if provided
            if content:
                data = content.encode('utf-8')
                num_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
                blocks = self._allocate_blocks(num_blocks)
                self._write_blocks(blocks, data)
                node.data_blocks = blocks
                node.size = len(data)
            
            # Add to parent directory
            parent.children[filename] = node
            self.inodes[path] = node
            
            self._save_metadata()
            print(f"[VFS] [OK] Created file: {path}")
            return True
            
        except Exception as e:
            print(f"[VFS] Error creating file: {e}")
            return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        try:
            path = self._normalize_path(path)
            
            if path not in self.inodes:
                print(f"[VFS] Error: File not found: {path}")
                return None
            
            node = self.inodes[path]
            if node.file_type != FILE_TYPE_REGULAR:
                print(f"[VFS] Error: Not a regular file: {path}")
                return None
            
            # Update access time
            node.accessed = time.time()
            
            if not node.data_blocks:
                return ""
            
            # Read data from blocks
            data = self._read_blocks(node.data_blocks)
            return data[:node.size].decode('utf-8')
            
        except Exception as e:
            print(f"[VFS] Error reading file: {e}")
            return None
    
    def write_file(self, path: str, content: str, save: bool = True) -> bool:
        """Write content to existing file"""
        try:
            path = self._normalize_path(path)
            
            if path not in self.inodes:
                return self.create_file(path, content, save=save)
            
            node = self.inodes[path]
            if node.file_type != FILE_TYPE_REGULAR:
                print(f"[VFS] Error: Not a regular file: {path}")
                return False
            
            # Free old blocks
            if node.data_blocks:
                self._free_blocks(node.data_blocks)
            
            # Allocate new blocks and write data
            data = content.encode('utf-8')
            num_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
            blocks = self._allocate_blocks(num_blocks)
            self._write_blocks(blocks, data)
            
            node.data_blocks = blocks
            node.size = len(data)
            node.modified = time.time()
            
            self._save_metadata()
            return True
            
        except Exception as e:
            print(f"[VFS] Error writing file: {e}")
            return False
    
    def delete_file(self, path: str, save: bool = True) -> bool:
        """Delete a file"""
        try:
            path = self._normalize_path(path)
            
            if path not in self.inodes:
                print(f"[VFS] Error: File not found: {path}")
                return False
            
            if path == "/":
                print("[VFS] Error: Cannot delete root directory")
                return False
            
            node = self.inodes[path]
            
            # Check if directory is empty
            if node.file_type == FILE_TYPE_DIRECTORY and node.children:
                print(f"[VFS] Error: Directory not empty: {path}")
                return False
            
            # Free data blocks
            if node.data_blocks:
                self._free_blocks(node.data_blocks)
            
            # Remove from parent
            parent = self.inodes[node.parent]
            del parent.children[node.name]
            
            # Remove from inodes
            del self.inodes[path]
            
            self._save_metadata()
            print(f"[VFS] [OK] Deleted: {path}")
            return True
            
        except Exception as e:
            print(f"[VFS] Error deleting file: {e}")
            return False
    
    def mkdir(self, path: str, save: bool = True) -> bool:
        """Create a directory"""
        try:
            path = self._normalize_path(path)
            
            if path in self.inodes:
                return True  # Already exists
            
            # Get parent directory
            parent_path = os.path.dirname(path) or "/"
            if parent_path not in self.inodes:
                # Recursively create parent directories
                self.mkdir(parent_path, save=False)
            
            parent = self.inodes[parent_path]
            
            # Create directory node
            dirname = os.path.basename(path)
            node = FileNode(dirname, FILE_TYPE_DIRECTORY, parent_path)
            
            # Add to parent directory
            parent.children[dirname] = node
            self.inodes[path] = node
            
            self._save_metadata()
            return True
            
        except Exception as e:
            print(f"[VFS] Error creating directory: {e}")
            return False
    
    def list_dir(self, path: str = None) -> List[Dict]:
        """List directory contents"""
        try:
            if path is None:
                path = self.current_dir
            
            path = self._normalize_path(path)
            
            if path not in self.inodes:
                print(f"[VFS] Error: Directory not found: {path}")
                return []
            
            node = self.inodes[path]
            if node.file_type != FILE_TYPE_DIRECTORY:
                print(f"[VFS] Error: Not a directory: {path}")
                return []
            
            # Update access time
            node.accessed = time.time()
            
            # Build file list
            files = []
            for name, child in node.children.items():
                files.append({
                    'name': name,
                    'type': 'dir' if child.file_type == FILE_TYPE_DIRECTORY else 'file',
                    'size': child.size,
                    'modified': datetime.fromtimestamp(child.modified).strftime('%Y-%m-%d %H:%M'),
                    'owner': child.owner,
                    'permissions': oct(child.permissions)
                })
            
            return sorted(files, key=lambda x: (x['type'] != 'dir', x['name']))
            
        except Exception as e:
            print(f"[VFS] Error listing directory: {e}")
            return []
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage statistics"""
        used_blocks = self.total_blocks - len(self.free_blocks)
        used_bytes = used_blocks * BLOCK_SIZE
        total_bytes = self.total_blocks * BLOCK_SIZE
        
        return {
            'total': total_bytes,
            'used': used_bytes,
            'free': total_bytes - used_bytes,
            'percent': (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
        }


# ============================================================================
# GLOBAL FILE SYSTEM INSTANCE
# ============================================================================

vfs = None

def get_filesystem() -> VirtualFileSystem:
    """Get global file system instance"""
    global vfs
    if vfs is None:
        vfs = VirtualFileSystem()
    return vfs

