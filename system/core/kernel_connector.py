"""
AuroraOS C-Kernel Connector
Bridges the Python shell/GUI to the compiled C kernel using ctypes,
with a seamless pure Python fallback if the C library is not available.
"""

import ctypes
import os
import sys
import platform
import time
from typing import List, Dict, Optional

# ============================================================================
# CTYPES STRUCTURES
# ============================================================================

class MemoryInfo(ctypes.Structure):
    _fields_ = [
        ("total_memory", ctypes.c_uint32),
        ("used_memory", ctypes.c_uint32),
        ("free_memory", ctypes.c_uint32),
        ("cached_memory", ctypes.c_uint32),
    ]

class ProcessInfo(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_uint32),
        ("parent_pid", ctypes.c_uint32),
        ("state", ctypes.c_uint32),
        ("priority", ctypes.c_uint32),
        ("cpu_time", ctypes.c_uint32),
        ("name", ctypes.c_char * 64),
    ]

class HeapBlockInfo(ctypes.Structure):
    _fields_ = [
        ("address", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("is_free", ctypes.c_uint32),
    ]

# ============================================================================
# PURE PYTHON FALLBACK SIMULATOR
# ============================================================================

class SimulatedPCB:
    def __init__(self, pid: int, parent_pid: int, name: str, priority: int):
        self.pid = pid
        self.parent_pid = parent_pid
        self.name = name
        self.priority = priority
        self.state = 1  # READY
        self.cpu_time = 0
        self.created_time = time.time()

class SimulatedBlock:
    def __init__(self, address: int, size: int, is_free: bool):
        self.address = address
        self.size = size
        self.is_free = is_free

class PythonKernelSimulator:
    """Simulates the C kernel completely in Python if C DLL is missing"""
    def __init__(self):
        self.total_memory = 128 * 1024  # 128 MB in KB
        self.used_memory = 12400  # simulated base system usage (KB)
        self.processes: Dict[int, SimulatedPCB] = {
            1: SimulatedPCB(1, 0, "init", 100),
            2: SimulatedPCB(2, 1, "kthreadd", 120),
            3: SimulatedPCB(3, 1, "sys_monitor", 80),
        }
        self.processes[1].state = 2  # RUNNING
        self.next_pid = 4
        self.start_time = time.time()
        
        # Initialize mock memory blocks list
        self.blocks = [
            SimulatedBlock(0x10000, 12400 * 1024, False), # Base kernel usage
            SimulatedBlock(0x10000 + 12400 * 1024, (128 * 1024 - 12400) * 1024, True) # Free space
        ]
        
    def kernel_init(self):
        print("[CONNECTOR] Initialized Python kernel simulator (fallback)")
        
    def kernel_shutdown(self):
        print("[CONNECTOR] Shutting down Python kernel simulator")
        self.processes.clear()
        
    def process_create(self, name: str, entry_point=None, priority: int = 100) -> int:
        pid = self.next_pid
        self.next_pid += 1
        self.processes[pid] = SimulatedPCB(pid, 1, name, priority)
        print(f"[SIM-KERNEL] Created process {pid}: {name}")
        return pid
        
    def process_kill(self, pid: int) -> int:
        if pid in self.processes:
            name = self.processes[pid].name
            del self.processes[pid]
            print(f"[SIM-KERNEL] Terminated process {pid}: {name}")
            return 0
        return -1
        
    def get_uptime(self) -> int:
        return int((time.time() - self.start_time) * 1000)
        
    def memory_get_info(self) -> dict:
        free = self.total_memory - self.used_memory
        return {
            "total_memory": self.total_memory,
            "used_memory": self.used_memory,
            "free_memory": free,
            "cached_memory": 4096
        }
        
    def kmalloc(self, size: int) -> int:
        # Align size to 8 bytes
        size = (size + 7) & ~7
        
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                # Split if block is larger than needed
                if block.size > size + 1024:
                    new_block = SimulatedBlock(block.address + size, block.size - size, True)
                    block.size = size
                    block.is_free = False
                    self.blocks.insert(i + 1, new_block)
                else:
                    block.is_free = False
                
                self.used_memory = sum(b.size for b in self.blocks if not b.is_free) // 1024
                return block.address
        return 0
        
    def kfree(self, addr: int):
        for i, block in enumerate(self.blocks):
            if block.address == addr:
                block.is_free = True
                
                # Coalesce right
                if i + 1 < len(self.blocks) and self.blocks[i + 1].is_free:
                    block.size += self.blocks[i + 1].size
                    self.blocks.pop(i + 1)
                
                # Coalesce left
                if i - 1 >= 0 and self.blocks[i - 1].is_free:
                    self.blocks[i - 1].size += block.size
                    self.blocks.pop(i)
                
                self.used_memory = sum(b.size for b in self.blocks if not b.is_free) // 1024
                break
                
    def get_heap_block_count(self) -> int:
        return len(self.blocks)
        
    def get_heap_blocks(self) -> List[dict]:
        return [
            {
                "address": b.address,
                "size": b.size,
                "is_free": 1 if b.is_free else 0
            }
            for b in self.blocks
        ]
            
    def get_process_count(self) -> int:
        return len(self.processes)
        
    def get_process_list(self) -> List[dict]:
        # Simulate scheduler progress
        for proc in self.processes.values():
            if proc.state == 2:  # RUNNING
                proc.cpu_time += int(time.time() - proc.created_time) % 5 + 1
                
        return [
            {
                "pid": p.pid,
                "parent_pid": p.parent_pid,
                "state": p.state,
                "priority": p.priority,
                "cpu_time": p.cpu_time,
                "name": p.name
            }
            for p in self.processes.values()
        ]

# ============================================================================
# KERNEL CONNECTOR
# ============================================================================

class KernelConnector:
    """Manages the C-Kernel dynamic linking connection"""
    
    def __init__(self):
        self.lib = None
        self.simulator = None
        self.use_simulator = True
        self._load_library()
        
    def _load_library(self):
        """Try to load the compiled C kernel shared library"""
        # Determine library extension based on OS
        sys_os = platform.system()
        if sys_os == "Windows":
            lib_name = "kernel.dll"
        elif sys_os == "Darwin":
            lib_name = "kernel.dylib"
        else:
            lib_name = "kernel.so"
            
        # Search paths
        paths = [
            os.path.join(os.getcwd(), lib_name),
            os.path.join(os.getcwd(), "kernel", "src", lib_name),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), lib_name),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "kernel", "src", lib_name)
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    print(f"[CONNECTOR] Attempting to load C kernel library: {path}")
                    self.lib = ctypes.CDLL(path)
                    self._bind_functions()
                    self.use_simulator = False
                    print("[CONNECTOR] ✓ Successfully linked C kernel library!")
                    break
                except Exception as e:
                    print(f"[CONNECTOR] Warning: Failed to load C library at {path}: {e}")
                    
        if self.use_simulator:
            self.simulator = PythonKernelSimulator()
            
    def _bind_functions(self):
        """Bind types to C functions"""
        # void kernel_init(void)
        self.lib.kernel_init.argtypes = []
        self.lib.kernel_init.restype = None
        
        # void kernel_shutdown(void)
        self.lib.kernel_shutdown.argtypes = []
        self.lib.kernel_shutdown.restype = None
        
        # int32_t process_create(const char*, void (*entry)(void), uint32_t)
        self.lib.process_create.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_uint32]
        self.lib.process_create.restype = ctypes.c_int32
        
        # int32_t process_kill(uint32_t)
        self.lib.process_kill.argtypes = [ctypes.c_uint32]
        self.lib.process_kill.restype = ctypes.c_int32
        
        # uint64_t get_uptime(void)
        self.lib.get_uptime.argtypes = []
        self.lib.get_uptime.restype = ctypes.c_uint64
        
        # memory_info_t* memory_get_info(void)
        self.lib.memory_get_info.argtypes = []
        self.lib.memory_get_info.restype = ctypes.POINTER(MemoryInfo)
        
        # void* kmalloc(size_t)
        self.lib.kmalloc.argtypes = [ctypes.c_size_t]
        self.lib.kmalloc.restype = ctypes.c_void_p
        
        # void kfree(void*)
        self.lib.kfree.argtypes = [ctypes.c_void_p]
        self.lib.kfree.restype = None
        
        # int get_process_count(void)
        try:
            self.lib.get_process_count.argtypes = []
            self.lib.get_process_count.restype = ctypes.c_int
            
            # int get_process_list(process_info_t*, int)
            self.lib.get_process_list.argtypes = [ctypes.POINTER(ProcessInfo), ctypes.c_int]
            self.lib.get_process_list.restype = ctypes.c_int
            
            # int get_heap_block_count(void)
            self.lib.get_heap_block_count.argtypes = []
            self.lib.get_heap_block_count.restype = ctypes.c_int
            
            # int get_heap_blocks(heap_block_info_t*, int)
            self.lib.get_heap_blocks.argtypes = [ctypes.POINTER(HeapBlockInfo), ctypes.c_int]
            self.lib.get_heap_blocks.restype = ctypes.c_int
        except AttributeError:
            print("[CONNECTOR] Warning: Process/Memory traversal functions not exported by C kernel. Using fallback simulator.")
            self.use_simulator = True
            self.simulator = PythonKernelSimulator()
            
    # ========================================================================
    # PUBLIC API BRIDGE
    # ========================================================================
    
    def kernel_init(self):
        if not self.use_simulator:
            self.lib.kernel_init()
        else:
            self.simulator.kernel_init()
            
    def kernel_shutdown(self):
        if not self.use_simulator:
            self.lib.kernel_shutdown()
        else:
            self.simulator.kernel_shutdown()
            
    def process_create(self, name: str, priority: int = 100) -> int:
        if not self.use_simulator:
            return self.lib.process_create(name.encode('utf-8'), None, priority)
        else:
            return self.simulator.process_create(name, priority=priority)
            
    def process_kill(self, pid: int) -> int:
        if not self.use_simulator:
            return self.lib.process_kill(pid)
        else:
            return self.simulator.process_kill(pid)
            
    def get_uptime(self) -> int:
        if not self.use_simulator:
            return self.lib.get_uptime()
        else:
            return self.simulator.get_uptime()
            
    def memory_get_info(self) -> dict:
        if not self.use_simulator:
            mem_ptr = self.lib.memory_get_info()
            if mem_ptr:
                info = mem_ptr.contents
                return {
                    "total_memory": info.total_memory,
                    "used_memory": info.used_memory,
                    "free_memory": info.free_memory,
                    "cached_memory": info.cached_memory
                }
            return {"total_memory": 0, "used_memory": 0, "free_memory": 0, "cached_memory": 0}
        else:
            return self.simulator.memory_get_info()
            
    def kmalloc(self, size: int) -> int:
        if not self.use_simulator:
            ptr = self.lib.kmalloc(size)
            return ptr or 0
        else:
            return self.simulator.kmalloc(size)
            
    def kfree(self, addr: int):
        if not self.use_simulator:
            self.lib.kfree(ctypes.c_void_p(addr))
        else:
            self.simulator.kfree(addr)
            
    def get_process_list(self) -> List[dict]:
        if not self.use_simulator:
            try:
                count = self.lib.get_process_count()
                if count <= 0:
                    return []
                
                # Allocate array
                arr_type = ProcessInfo * count
                arr = arr_type()
                
                ret_count = self.lib.get_process_list(arr, count)
                result = []
                for i in range(ret_count):
                    p = arr[i]
                    result.append({
                        "pid": p.pid,
                        "parent_pid": p.parent_pid,
                        "state": p.state,
                        "priority": p.priority,
                        "cpu_time": p.cpu_time,
                        "name": p.name.decode('utf-8', errors='replace')
                    })
                return result
            except Exception as e:
                print(f"[CONNECTOR] Error getting C process list: {e}")
                return []
        else:
            return self.simulator.get_process_list()
            
    def get_heap_blocks(self) -> List[dict]:
        if not self.use_simulator:
            try:
                count = self.lib.get_heap_block_count()
                if count <= 0:
                    return []
                
                arr_type = HeapBlockInfo * count
                arr = arr_type()
                
                ret_count = self.lib.get_heap_blocks(arr, count)
                result = []
                for i in range(ret_count):
                    b = arr[i]
                    result.append({
                        "address": b.address,
                        "size": b.size,
                        "is_free": b.is_free
                    })
                return result
            except Exception as e:
                print(f"[CONNECTOR] Error getting C heap block list: {e}")
                return []
        else:
            return self.simulator.get_heap_blocks()

# ============================================================================
# GLOBAL CONNECTOR INSTANCE
# ============================================================================

_connector = None

def get_kernel_connector() -> KernelConnector:
    """Get global kernel connector instance"""
    global _connector
    if _connector is None:
        _connector = KernelConnector()
    return _connector
