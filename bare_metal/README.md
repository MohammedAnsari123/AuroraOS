# Building Operating System

This project is a minimal, Multiboot-compliant 32-bit x86 Operating System kernel written in C and Assembly. It's designed as a learning resource and foundation for building a more complex OS.

## 1. Folder Structure
- `boot/`: Contains the Assembly bootloader (`boot.asm`) which acts as the entry point and sets up the environment before calling the C kernel.
- `kernel/`: Contains the main C code for the kernel, starting with `kernel_main`.
- `drivers/`: Contains hardware drivers. Currently includes a VGA text mode driver (`vga.c`) to print text to the screen.
- `include/`: Contains C header files (`.h`), such as custom standard types (`types.h`) and driver interfaces (`vga.h`).
- `scripts/`: Contains build scripts, notably the linker script (`linker.ld`) which defines how the compiled files are combined and where they reside in memory.
- `Makefile`: Automates the build process using `make`.

## 2. Prerequisites
To build and run this OS, you will need a cross-compiler and an emulator.
- **nasm**: The Netwide Assembler to compile `boot.asm`.
- **i686-elf-gcc**: A GCC cross-compiler targeting the `i686-elf` architecture. (Building a cross-compiler is highly recommended for OS development to avoid relying on host OS libraries).
- **make**: Build automation tool.
- **qemu-system-i386**: QEMU emulator to run the compiled OS binary.

## 3. Building and Running
1. Open your terminal.
2. Run `make` to assemble, compile, and link the OS into `myos.bin`.
3. Run `make run` to launch QEMU and boot the OS.

## 4. How the Linux Kernel is Structured Internally
For reference as you expand this minimal OS into something bigger, here is a high-level view of how a real-world, monolithic kernel like Linux is structured:
- **`arch/`**: Architecture-specific code (x86, arm, mips). Each architecture has its own boot code, CPU initialization, and memory management specifics.
- **`block/`**: Block storage device drivers and scheduling algorithms.
- **`crypto/`**: Cryptographic API and algorithms.
- **`drivers/`**: The largest directory! Contains drivers for every conceivable piece of hardware (PCI, USB, network cards, graphics cards).
- **`fs/`**: Virtual File System (VFS) and implementations of specific filesystems (ext4, fat, btrfs).
- **`include/`**: Kernel headers. `include/linux/` contains generic headers, while `include/asm/` points to architecture-specific headers.
- **`init/`**: Kernel initialization code. The famous `start_kernel()` function lives here.
- **`ipc/`**: Inter-Process Communication (shared memory, semaphores, message queues).
- **`kernel/`**: Core monolithic kernel subsystems: process scheduler, timers, interrupt handling, etc.
- **`mm/`**: Memory Management (page tables, virtual memory, memory swapping).
- **`net/`**: Networking stack (TCP/IP, sockets, packet filtering).
- **`security/`**: Security frameworks like SELinux or AppArmor.

## 5. 60-Day OS Development Roadmap
Here is a structured path to take this starter OS to a functional, modern-ish toy operating system.

### Phase 1: The Foundation (Days 1 - 10)
- **Day 1-2**: Understand the boot sequence, Multiboot specification, and VGA text mode. (You are here!)
- **Day 3-4**: Implement `printf` and better string formatting (`libk`).
- **Day 5-7**: Implement the Global Descriptor Table (GDT) to define memory segments.
- **Day 8-10**: Implement Interrupt Descriptor Table (IDT) and Interrupt Service Routines (ISRs). Handle a custom software interrupt.

### Phase 2: Hardware Interrupts & Timing (Days 11 - 20)
- **Day 11-13**: Program the Programmable Interrupt Controller (PIC) to handle hardware interrupts.
- **Day 14-16**: Write a keyboard driver. Read scancodes and convert them to ASCII.
- **Day 17-20**: Program the Programmable Interval Timer (PIT). Create `sleep()` and `ticks` functions. 

### Phase 3: Memory Management (Days 21 - 35)
- **Day 21-25**: Physical Memory Management (PMM). Implement a bitmap or stack physical page allocator.
- **Day 26-30**: Virtual Memory and Paging. Set up page directories and page tables. Enable paging.
- **Day 31-35**: Kernel heap allocator (e.g., implementing `kmalloc` and `kfree`).

### Phase 4: Processes & Multitasking (Days 36 - 45)
- **Day 36-39**: Define a Process Control Block (PCB).
- **Day 40-42**: Implement context switching (saving/restoring registers).
- **Day 43-45**: Implement a round-robin process scheduler. Run two kernel threads concurrently.

### Phase 5: User Mode & File Systems (Days 46 - 60)
- **Day 46-48**: Switch to Ring 3 (User space). Create User Mode GDT entries and Set up the Task State Segment (TSS).
- **Day 49-51**: Implement basic System Calls (syscalls) allowing user programs to request kernel services (like printing on screen).
- **Day 52-55**: Write a basic ATA/IDE disk driver to read/write sectors.
- **Day 56-60**: Design and implement a simple Virtual File System (VFS) and an elementary filesystem (like FAT16 or a custom one) to read and load external programs.


---

## 📟 Assembly Bootstrap & Linker Internals

This section describes the assembly structure and compiler configurations for the bootable image.

### 1. Linker Script (`linker.ld`)
The linker script is crucial for x86 bootable OS binaries. It specifies the exact order of section placing:
* **`ENTRY(_start)`**: Sets the binary entry point to the `_start` label in `boot.asm`.
* **`. = 1M` (1 Megabyte)**: The kernel is loaded at physical memory address `1MB`. Memory below 1MB is reserved for BIOS variables, VGA graphics buffer, and legacy hardware.
* **`.multiboot`**: Places the multiboot header at the very beginning of the binary, satisfying the GRUB loader specification.

### 2. Multiboot Header Structure
The multiboot header consists of:
* **Magic Number**: `0x1BADB002` (expected by GRUB/QEMU).
* **Flags**: Specifies if the kernel requires page alignment or memory information.
* **Checksum**: Must satisfy `(magic + flags + checksum) == 0`.
