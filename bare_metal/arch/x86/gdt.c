#include <gdt.h>

struct gdt_entry gdt[3]; // Null, Kernel Code, Kernel Data
struct gdt_ptr gp;

// Implemented in gdt_load.asm
extern void gdt_flush(uint32_t);

// Set up a descriptor in the Global Descriptor Table
void gdt_set_gate(int num, uint32_t base, uint32_t limit, uint8_t access, uint8_t gran) {
    // Base Address
    gdt[num].base_low = (base & 0xFFFF);
    gdt[num].base_middle = (base >> 16) & 0xFF;
    gdt[num].base_high = (base >> 24) & 0xFF;

    // Limit
    gdt[num].limit_low = (limit & 0xFFFF);
    gdt[num].granularity = ((limit >> 16) & 0x0F);

    // Flags & Access
    gdt[num].granularity |= (gran & 0xF0);
    gdt[num].access = access;
}

// Function to initialize and set up the GDT
void gdt_init(void) {
    gp.limit = (sizeof(struct gdt_entry) * 3) - 1;
    gp.base = (uint32_t)&gdt;

    gdt_set_gate(0, 0, 0, 0, 0);                // Null segment
    gdt_set_gate(1, 0, 0xFFFFFFFF, 0x9A, 0xCF); // Code segment (Ring 0, Executable/Read)
    gdt_set_gate(2, 0, 0xFFFFFFFF, 0x92, 0xCF); // Data segment (Ring 0, Read/Write)

    gdt_flush((uint32_t)&gp);
}
