# 🖥️ AuroraOS Bare-Metal Kernel Guide

This guide describes how to compile, link, and run the real 32-bit x86 Operating System kernel located in the `bare_metal/` folder.

---

## 1. Prerequisites

To build and run the bare-metal kernel on your Windows host machine, you will need the following tools:

### A. Compiler & Assembler
- **GCC Compiler**: MinGW-w64 or standard MinGW GCC (with support for 32-bit compilation `-m32`).
- **NASM**: Netwide Assembler to compile x86 assembly bootloader files.
  - Can be installed on Windows via **Chocolatey**:
    ```bash
    choco install nasm
    ```
  - Or via **Winget**:
    ```bash
    winget install NASM.NASM
    ```

### B. Emulator
- **QEMU**: CPU emulator to execute the multiboot-compliant kernel image.
  - Can be installed on Windows via **Chocolatey**:
    ```bash
    choco install qemu
    ```
  - Or via **Winget**:
    ```bash
    winget install SoftwareCollab.QEMU
    ```

---

## 2. Compilation and Linkage

1. Open your terminal in the project root folder.
2. Run the make command to invoke compilation:
   ```bash
   make baremetal
   ```
   This will assemble, compile, and link the assembly entry points (`boot.asm`, descriptor tables) and the C files (`kernel.c`, drivers, libc) into a final multiboot-compliant binary: `bare_metal/myos.bin`.

---

## 3. Running the Bare-Metal OS

To boot the bare-metal kernel in the QEMU emulator:
```bash
make run-baremetal
```

This launches QEMU in x86 mode (`qemu-system-i386`) using the Multiboot specification to direct-load the kernel.

### What is Running inside QEMU?
Once booted, you will see a graphical retro teal screen featuring:
1. **Window GUI**: A custom window displaying OS information drawn pixel-by-pixel.
2. **Taskbar**: A Start bar at the bottom.
3. **Interrupt-driven Input**:
   - **Keyboard**: Read raw scancodes converted to ASCII.
   - **Mouse**: A retro crosshair mouse cursor that moves as you move your physical mouse. Right-clicking or left-clicking shows a yellow `CLICK!` reactive notification!
4. **Hardware initialization**: Setting up GDT (Global Descriptor Table), IDT (Interrupt Descriptor Table), PIC (Programmable Interrupt Controller), PIT (Timer).
