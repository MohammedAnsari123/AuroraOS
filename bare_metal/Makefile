# Custom OS Makefile

# Toolchain (using native gcc in 32-bit mode instead of cross-compiler)
CC = gcc
AS = nasm
LD = gcc

# Flags
CFLAGS = -m32 -std=gnu99 -ffreestanding -O2 -Wall -Wextra -Iinclude -fno-pie -fno-pic
ASFLAGS = -f elf32
LDFLAGS = -m32 -T scripts/linker.ld -ffreestanding -O2 -nostdlib -lgcc -no-pie -Wl,-z,max-page-size=0x1000 -Wl,--build-id=none

# Sources
ASM_SOURCES = boot/boot.asm arch/x86/gdt_load.asm arch/x86/idt_load.asm arch/x86/interrupt_stubs.asm
C_SOURCES = kernel/kernel.c drivers/vga.c drivers/vga_graphics.c libc/string.c libc/stdio.c arch/x86/gdt.c arch/x86/idt.c arch/x86/isr.c drivers/pic.c drivers/keyboard.c drivers/mouse.c

# Objects
ASM_OBJECTS = $(ASM_SOURCES:.asm=.o)
C_OBJECTS = $(C_SOURCES:.c=.o)
OBJECTS = $(ASM_OBJECTS) $(C_OBJECTS)

# Output binary
TARGET = myos.bin

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $(OBJECTS)

%.o: %.asm
	$(AS) $(ASFLAGS) $< -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(ASM_OBJECTS) $(C_OBJECTS) myos.bin

run: myos.bin
	qemu-system-i386 -kernel myos.bin -d int,cpu_reset -no-reboot
