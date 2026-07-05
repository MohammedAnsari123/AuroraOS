#include <vga_graphics.h>
#include <io.h>

// Register array for VGA Mode 13h (320x200x256 colors)
// This is standard magic to configure the ancient CRTC, Sequencer, Graphics, and Attribute controllers
unsigned char mode_13h_registers[] = {
    // MISC
    0x63,
    // SEQ
    0x03, 0x01, 0x0F, 0x00, 0x0E,
    // CRTC
    0x5F, 0x4F, 0x50, 0x82, 0x54, 0x80, 0xBF, 0x1F,
    0x00, 0x41, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x9C, 0x0E, 0x8F, 0x28,  0x40, 0x96, 0xB9, 0xA3,
    0xFF,
    // GC
    0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x05, 0x0F,
    0xFF,
    // AC
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x41, 0x00, 0x0F, 0x00,  0x00
};

void write_registers(uint8_t *regs) {
    unsigned i;

    // write MISCELLANEOUS reg
    outb(0x3C2, *regs);
    regs++;

    // write SEQUENCER regs
    for(i = 0; i < 5; i++) {
        outb(0x3C4, i);
        outb(0x3C5, *regs);
        regs++;
    }

    // Unlock CRTC registers
    outb(0x3D4, 0x03);
    outb(0x3D5, inb(0x3D5) | 0x80);
    outb(0x3D4, 0x11);
    outb(0x3D5, inb(0x3D5) & ~0x80);

    regs[0x03] |= 0x80;
    regs[0x11] &= ~0x80;

    // write CRTC regs
    for(i = 0; i < 25; i++) {
        outb(0x3D4, i);
        outb(0x3D5, *regs);
        regs++;
    }

    // write GRAPHICS CONTROLLER regs
    for(i = 0; i < 9; i++) {
        outb(0x3CE, i);
        outb(0x3CF, *regs);
        regs++;
    }

    // write ATTRIBUTE CONTROLLER regs
    for(i = 0; i < 21; i++) {
        inb(0x3DA);
        outb(0x3C0, i);
        outb(0x3C0, *regs);
        regs++;
    }

    inb(0x3DA);
    outb(0x3C0, 0x20); // Turn screen ON!
}

void vga_graphics_init(void) {
    write_registers(mode_13h_registers);
}

void put_pixel(int x, int y, uint8_t color) {
    if (x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT) {
        VGA_GRAPHICS_MEMORY[SCREEN_WIDTH * y + x] = color;
    }
}

void draw_rect(int x, int y, int width, int height, uint8_t color) {
    for (int i = y; i < y + height; i++) {
        for (int j = x; j < x + width; j++) {
            put_pixel(j, i, color);
        }
    }
}

// Absolute value helper for line algorithm
static int abs(int n) { return n < 0 ? -n : n; }

// Bresenham's line algorithm
void draw_line(int x0, int y0, int x1, int y1, uint8_t color) {
    int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
    int dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
    int err = dx + dy, e2;

    for (;;) {
        put_pixel(x0, y0, color);
        if (x0 == x1 && y0 == y1) break;
        e2 = 2 * err;
        if (e2 >= dy) { err += dy; x0 += sx; }
        if (e2 <= dx) { err += dx; y0 += sy; }
    }
}

void clear_screen(uint8_t color) {
    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        VGA_GRAPHICS_MEMORY[i] = color;
    }
}

// Simple monochrome 8x8 font. Only implementing a few characters for demo!
// 1 bit = pixel on, 0 bit = pixel off
const uint8_t font8x8[128][8] = {
    // Space
    [32] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
    // 'A'
    [65] = {0x18, 0x24, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42},
    // 'a'
    [97] = {0x00, 0x00, 0x3C, 0x02, 0x3E, 0x42, 0x3E, 0x00},
    // 'n'
    [110]= {0x00, 0x00, 0x5C, 0x62, 0x42, 0x42, 0x42, 0x00},
    // 't'
    [116]= {0x00, 0x10, 0x3E, 0x10, 0x10, 0x10, 0x0C, 0x00},
    // 'i'
    [105]= {0x00, 0x18, 0x00, 0x38, 0x18, 0x18, 0x3C, 0x00},
    // 'g'
    [103]= {0x00, 0x00, 0x3E, 0x42, 0x3E, 0x02, 0x3C, 0x00},
    // 'r'
    [114]= {0x00, 0x00, 0x5C, 0x62, 0x40, 0x40, 0x40, 0x00},
    // 'v'
    [118]= {0x00, 0x00, 0x42, 0x42, 0x24, 0x18, 0x18, 0x00},
    // 'y'
    [121]= {0x00, 0x00, 0x42, 0x42, 0x3E, 0x02, 0x3C, 0x00},
    // 'O'
    [79] = {0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C, 0x00},
    // 'S'
    [83] = {0x3C, 0x42, 0x40, 0x3C, 0x02, 0x42, 0x3C, 0x00},
    // 'W'
    [87] = {0x42, 0x42, 0x42, 0x5A, 0x5A, 0x24, 0x24, 0x00},
    // 'd'
    [100]= {0x02, 0x02, 0x3E, 0x42, 0x42, 0x42, 0x3E, 0x00},
    // 'o'
    [111]= {0x00, 0x00, 0x3C, 0x42, 0x42, 0x42, 0x3C, 0x00},
    // 'w'
    [119]= {0x00, 0x00, 0x42, 0x42, 0x5A, 0x24, 0x24, 0x00},
};

void draw_char(char c, int x, int y, uint8_t color) {
    if ((uint8_t)c >= 128) return; // Unhandled

    for (int row = 0; row < 8; row++) {
        uint8_t row_data = font8x8[(uint8_t)c][row];
        for (int col = 0; col < 8; col++) {
            // Check if the bit is set
            if ((row_data >> (7 - col)) & 1) {
                put_pixel(x + col, y + row, color);
            }
        }
    }
}

// Fallback to simplistic text mapping for demo
void draw_string(const char* str, int x, int y, uint8_t color) {
    int cx = x;
    while (*str) {
        draw_char(*str, cx, y, color);
        cx += 8;
        str++;
    }
}
