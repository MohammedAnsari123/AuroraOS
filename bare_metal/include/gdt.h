#ifndef GDT_H
#define GDT_H

#include <types.h>

// Initialize the GDT
void gdt_init(void);

// Used to define a GDT entry
struct gdt_entry {
    uint16_t limit_low;     // Lower 16 bits of the limit.
    uint16_t base_low;      // Lower 16 bits of the base.
    uint8_t  base_middle;   // Next 8 bits of the base.
    uint8_t  access;        // Access flags, ring level, etc.
    uint8_t  granularity;   // Granularity and limit remaining bits.
    uint8_t  base_high;     // Last 8 bits of the base.
} __attribute__((packed));

// Pointer to the GDT, passed to the `lgdt` instruction
struct gdt_ptr {
    uint16_t limit;         // The upper 16 bits of all selector limits.
    uint32_t base;          // The address of the first gdt_entry_t struct.
} __attribute__((packed));

#endif // GDT_H
