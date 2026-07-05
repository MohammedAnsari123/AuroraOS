#ifndef ISR_H
#define ISR_H

#include <types.h>

// Struct mapping to the registers pushed by our interrupt_stubs.asm
struct registers {
    uint32_t ds;                                     // Data segment selector
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax; // Pushed by pusha
    uint32_t int_no, err_code;                       // Interrupt number and error code (if applicable)
    uint32_t eip, cs, eflags, useresp, ss;           // Pushed by the processor automatically
};

typedef void (*isr_t)(struct registers*);

// ISR Initialization (Registers all CPU Exceptions in the IDT)
void isr_init(void);

// Register a custom handler for a specific interrupt
void register_interrupt_handler(uint8_t n, isr_t handler);

// The actual C function called by our assembly stub `isr_common_stub`
void isr_handler(struct registers* regs);

// The actual C function called by our assembly stub `irq_common_stub`
void irq_handler(struct registers* regs);

#endif // ISR_H
