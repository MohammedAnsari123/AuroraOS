#include <idt.h>
#include <string.h>

struct idt_entry idt[256];
struct idt_ptr idtp;

// Implemented in idt_load.asm
extern void idt_load(uint32_t);

// Set entry in IDT
void idt_set_gate(uint8_t num, uint32_t base, uint16_t sel, uint8_t flags) {
    idt[num].base_lo = base & 0xFFFF;
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel     = sel;
    idt[num].always0 = 0;
    idt[num].flags   = flags /* | 0x60 */; // Use OR 0x60 for user-mode (Ring 3) calling
}

// Installs the IDT
void idt_init(void) {
    idtp.limit = (sizeof (struct idt_entry) * 256) - 1;
    idtp.base = (uint32_t)&idt;

    // Clear out the entire IDT, initializing it to zeros
    memset(&idt, 0, sizeof(struct idt_entry) * 256);

    // Points the processor's internal register to the new IDT
    idt_load((uint32_t)&idtp);
}
