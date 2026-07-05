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


---

## 📐 Intel x86 Architecture Details: Theory & Low-Level Routines

The bare-metal kernel in `bare_metal/` runs in 32-bit x86 Protected Mode. Below are the key hardware descriptors initialized:

### 1. Global Descriptor Table (GDT)
The GDT defines the memory segments (Privilege levels or Rings). We set up 5 descriptors:
1. **Null Descriptor**: Required by the CPU.
2. **Kernel Code Segment**: Base `0x0`, Limit `0xFFFFFFFF`, Ring 0 (highest privilege), Executable/Read.
3. **Kernel Data Segment**: Base `0x0`, Limit `0xFFFFFFFF`, Ring 0, Read/Write.
4. **User Code Segment**: Base `0x0`, Limit `0xFFFFFFFF`, Ring 3 (user space applications), Executable/Read.
5. **User Data Segment**: Base `0x0`, Limit `0xFFFFFFFF`, Ring 3, Read/Write.

### 2. Interrupt Descriptor Table (IDT) & PIC
The IDT routes hardware interrupts (IRQs) and software exceptions to ISR routines.
* **PIC Remapping**: The standard Intel 8259 Programmable Interrupt Controller (PIC) maps hardware interrupts to vector slots 0-7. However, these conflict with default CPU exceptions. We remap the Master PIC to use vectors `0x20 - 0x27` and the Slave PIC to `0x28 - 0x2F`.
* **Keyboard Interrupt (IRQ 1)**: Tied to Interrupt vector `0x21`. When a key is pressed, the CPU halts execution, saves registers, calls the keyboard handler in `vga.c`/`kernel.c`, reads the scancode from port `0x60`, and sends an EOI (End of Interrupt) signal to the PIC (`outb(0x20, 0x20)`).

### 3. VGA Graphics: Mode 13h
The bare-metal graphics driver writes directly to memory address `0xA0000`. By setting VGA controller registers to Mode 13h, we get:
* **Resolution**: 320x200 pixels.
* **Colors**: 256 colors using an 8-bit lookup palette.
* **Plotting a Pixel**: Writing a color byte to index `0xA0000 + (y * 320) + x` paints that pixel instantly.
