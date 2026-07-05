; boot.asm - Minimal Multiboot bootloader

; Multiboot header constants
MBALIGN     equ  1 << 0                   ; align loaded modules on page boundaries
MEMINFO     equ  1 << 1                   ; provide memory map
FLAGS       equ  MBALIGN | MEMINFO        ; this is the Multiboot 'flag' field
MAGIC       equ  0x1BADB002               ; 'magic number' lets bootloader find the header
CHECKSUM    equ -(MAGIC + FLAGS)          ; checksum of above, to prove we are multiboot

; The Multiboot header
section .multiboot
align 4
    dd MAGIC
    dd FLAGS
    dd CHECKSUM


; Allocate space for the stack
section .bss
align 16
stack_bottom:
resb 16384 ; 16 KiB
stack_top:

; The entry point
section .text
global _start
extern kernel_main

_start:
    ; Set up the stack pointer
    mov esp, stack_top

    ; Push the magic value and multiboot info structure pointer
    ; They are passed in eax and ebx respectively by the multiboot bootloader
    push eax
    push ebx

    ; Call the high-level C kernel
    call kernel_main

    ; If kernel_main returns, halt the system
    cli
.hang:
    hlt
    jmp .hang
