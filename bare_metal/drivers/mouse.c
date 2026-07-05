#include <mouse.h>
#include <isr.h>
#include <io.h>
#include <vga_graphics.h> // For clamping to screen dimensions

volatile int mouse_x = SCREEN_WIDTH / 2;
volatile int mouse_y = SCREEN_HEIGHT / 2;
volatile bool mouse_left_pressed = false;
volatile bool mouse_right_pressed = false;

uint8_t mouse_cycle = 0;
int8_t mouse_byte[3];

// Helper to wait until the mouse is ready to receive commands
void mouse_wait(uint8_t a_type) {
    uint32_t _time_out = 100000;
    if (a_type == 0) {
        while (_time_out--) {
            if ((inb(MOUSE_STATUS) & 1) == 1) {
                return;
            }
        }
        return;
    } else {
        while (_time_out--) {
            if ((inb(MOUSE_STATUS) & 2) == 0) {
                return;
            }
        }
        return;
    }
}

// Write to the mouse
void mouse_write(uint8_t a_write) {
    // Wait to be able to send a command
    mouse_wait(1);
    // Tell the mouse we are sending a command
    outb(MOUSE_STATUS, MOUSE_WRITE);
    // Wait for the final part
    mouse_wait(1);
    // Finally write
    outb(MOUSE_PORT, a_write);
}

// Read from the mouse
uint8_t mouse_read() {
    // Get response from mouse
    mouse_wait(0);
    return inb(MOUSE_PORT);
}

// Handle mouse interrupts (IRQ 12 / INT 44)
static void mouse_callback(struct registers* regs) {
    (void)regs;
    
    // Read the status byte structure from port 64h
    uint8_t status = inb(MOUSE_STATUS);
    while (status & MOUSE_BBIT) {
        int8_t mouse_in = inb(MOUSE_PORT);
        
        // Ensure that the bit for "mouse packet" vs keyboard packet is set
        if (status & MOUSE_F_BIT) {
            
            // Build the 3-byte mouse packet
            switch(mouse_cycle) {
                case 0:
                    mouse_byte[0] = mouse_in;
                    // Bit 3 MUST be set in a valid PS/2 packet. If not, we are misaligned.
                    if (!(mouse_in & MOUSE_V_BIT)) return;
                    mouse_cycle++;
                    break;
                case 1:
                    mouse_byte[1] = mouse_in;
                    mouse_cycle++;
                    break;
                case 2:
                    mouse_byte[2] = mouse_in;
                    mouse_cycle = 0;
                    
                    // Decode the packet!
                    mouse_left_pressed = (mouse_byte[0] & 0x01);
                    mouse_right_pressed = (mouse_byte[0] & 0x02);
                    
                    // Decode movement.
                    // mouse_byte[1] is X movement. mouse_byte[2] is Y movement.
                    // We must sign-extend them based on bits in byte 0.
                    int dx = mouse_byte[1];
                    int dy = mouse_byte[2];

                    if (mouse_byte[0] & 0x10) dx |= 0xFFFFFF00; // Sign extend X (negative)
                    if (mouse_byte[0] & 0x20) dy |= 0xFFFFFF00; // Sign extend Y (negative)

                    // Y is inverted on screen vs mouse hardware
                    dy = -dy;

                    mouse_x += dx;
                    mouse_y += dy;

                    // Clamping to screen bounds
                    if (mouse_x < 0) mouse_x = 0;
                    if (mouse_y < 0) mouse_y = 0;
                    if (mouse_x >= SCREEN_WIDTH) mouse_x = SCREEN_WIDTH - 1;
                    if (mouse_y >= SCREEN_HEIGHT) mouse_y = SCREEN_HEIGHT - 1;

                    break;
            }
        }
        status = inb(MOUSE_STATUS);
    }
}

void mouse_init(void) {
    uint8_t _status;

    // Enable the auxiliary mouse device
    mouse_wait(1);
    outb(MOUSE_STATUS, 0xA8);

    // Enable the interrupts
    mouse_wait(1);
    outb(MOUSE_STATUS, 0x20);
    mouse_wait(0);
    _status = (inb(MOUSE_PORT) | 2);
    mouse_wait(1);
    outb(MOUSE_STATUS, 0x60);
    mouse_wait(1);
    outb(MOUSE_PORT, _status);

    // Tell the mouse to use default settings
    mouse_write(0xF6);
    mouse_read();  // Acknowledge

    // Enable the mouse
    mouse_write(0xF4);
    mouse_read();  // Acknowledge

    // Setup the IRQ12 handler
    register_interrupt_handler(44, mouse_callback);
}
