#ifndef VGA_GRAPHICS_H
#define VGA_GRAPHICS_H

#include <types.h>

#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 200
#define VGA_GRAPHICS_MEMORY ((uint8_t*)0xA0000)

// Switches the VGA hardware from Text Mode to 320x200 256-color Graphics Mode
void vga_graphics_init(void);

// Drawing primitives
void put_pixel(int x, int y, uint8_t color);
void draw_rect(int x, int y, int width, int height, uint8_t color);
void draw_line(int x0, int y0, int x1, int y1, uint8_t color);
void clear_screen(uint8_t color);

// Very basic 8x8 bitmap font rendering
void draw_char(char c, int x, int y, uint8_t color);
void draw_string(const char* str, int x, int y, uint8_t color);

#endif // VGA_GRAPHICS_H
