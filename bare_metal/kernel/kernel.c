#include <vga.h>
#include <vga_graphics.h>
#include <stdio.h>
#include <string.h>
#include <gdt.h>
#include <idt.h>
#include <pic.h>
#include <isr.h>
#include <keyboard.h>
#include <mouse.h>

// Some useful VGA Mode 13h colors
#define COLOR_BLACK       0
#define COLOR_BLUE        1
#define COLOR_GREEN       2
#define COLOR_CYAN        3
#define COLOR_RED         4
#define COLOR_MAGENTA     5
#define COLOR_BROWN       6
#define COLOR_LIGHTGRAY   7
#define COLOR_DARKGRAY    8
#define COLOR_LIGHTBLUE   9
#define COLOR_LIGHTGREEN  10
#define COLOR_LIGHTCYAN   11
#define COLOR_LIGHTRED    12
#define COLOR_LIGHTMAGENTA 13
#define COLOR_YELLOW      14
#define COLOR_WHITE       15

void draw_desktop(void) {
    // Background color (A nice retro teal)
    clear_screen(COLOR_CYAN);

    // Draw the "Taskbar" at the bottom
    draw_rect(0, SCREEN_HEIGHT - 12, SCREEN_WIDTH, 12, COLOR_LIGHTGRAY);
    draw_line(0, SCREEN_HEIGHT - 12, SCREEN_WIDTH, SCREEN_HEIGHT - 12, COLOR_WHITE); // highlight
    
    // Start button text
    draw_string("START", 4, SCREEN_HEIGHT - 10, COLOR_BLACK);

    // A mock "Window"
    int win_x = 40;
    int win_y = 30;
    int win_w = 200;
    int win_h = 100;

    // Window shadow
    draw_rect(win_x + 2, win_y + 2, win_w, win_h, COLOR_DARKGRAY);
    // Window base
    draw_rect(win_x, win_y, win_w, win_h, COLOR_LIGHTGRAY);
    // Window Title Bar
    draw_rect(win_x, win_y, win_w, 10, COLOR_BLUE);
    draw_string("Antigravity OS Info", win_x + 4, win_y + 2, COLOR_WHITE);

    // Window Content
    draw_rect(win_x + 2, win_y + 12, win_w - 4, win_h - 14, COLOR_WHITE);
    draw_string("Welcome to UI Mode!", win_x + 10, win_y + 20, COLOR_BLACK);
    draw_string("Mouse works!", win_x + 10, win_y + 40, COLOR_BLACK);
}

void draw_mouse_cursor(int x, int y, bool clicking) {   
    // A simple crosshair cursor
    uint8_t color = clicking ? COLOR_RED : COLOR_BLACK;

    put_pixel(x, y, color);
    draw_line(x - 3, y, x + 3, y, color);
    draw_line(x, y - 3, x, y + 3, color);
}

void kernel_main(uint32_t magic, uint32_t multiboot_info_addr) {
    (void)magic;
    (void)multiboot_info_addr;

    // Initialize core hardware (Memory, Interrupts)
    gdt_init();
    idt_init();
    isr_init();

    // Initialize input devices
    keyboard_init();
    pic_unmask(1);  // IRQ 1 Keyboard
    
    mouse_init();
    pic_unmask(12); // IRQ 12 Mouse

    // Enable Graphics Mode! 
    // This turns off standard vga_putchar terminal printing and swaps to pixel drawing
    vga_graphics_init();

    int last_mouse_x = -1;
    int last_mouse_y = -1;
    bool last_mouse_clicked = false;

    // The Graphical "Desktop" Loop
    while(1) {
        
        // We only redraw if the mouse actually moved or clicked state changed to stop the screen from flickering terribly
        if (mouse_x != last_mouse_x || mouse_y != last_mouse_y || mouse_left_pressed != last_mouse_clicked) {
            
            // 1. Draw the static background and windows
            draw_desktop();

            // 2. Draw dynamic UI components (like a click reaction)
            if (mouse_left_pressed) {
                draw_rect(200, 10, 80, 10, COLOR_CYAN); // clear old
                draw_string("CLICK!", 200, 10, COLOR_YELLOW);
            } else {
                draw_rect(200, 10, 80, 10, COLOR_CYAN); // clear old
            }

            // 3. Draw the mouse cursor over everything else
            draw_mouse_cursor(mouse_x, mouse_y, mouse_left_pressed);

            // Update tracked state
            last_mouse_x = mouse_x;
            last_mouse_y = mouse_y;
            last_mouse_clicked = mouse_left_pressed;
        }

        // Suspend CPU until the next interrupt (usually a mouse movement or timer tick) to save extreme CPU usage
        __asm__ volatile ("hlt");
    }
}
