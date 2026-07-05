#include <keyboard.h>
#include <isr.h>
#include <io.h>
#include <stdio.h>

char keyboard_buffer[KBD_BUFFER_SIZE];
volatile int kbd_buffer_head = 0;
volatile int kbd_buffer_tail = 0;
bool shift_pressed = false;

// Basic US QWERTY Scancode mapping (Setup 1)
const char kbdus[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', /* 9 */
  '9', '0', '-', '=', '\b', /* Backspace */
  '\t',         /* Tab */
  'q', 'w', 'e', 'r',   /* 19 */
  't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n', /* Enter key */
    0,          /* 29   - Control */
  'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', /* 39 */
 '\'', '`',   0,        /* Left shift */
 '\\', 'z', 'x', 'c', 'v', 'b', 'n',            /* 49 */
  'm', ',', '.', '/',   0,              /* Right shift */
  '*',
    0,  /* Alt */
  ' ',  /* Space bar */
    0,  /* Caps lock */
    0,  /* 59 - F1 key ... > */
    0,   0,   0,   0,   0,   0,   0,   0,
    0,  /* < ... F10 */
    0,  /* 69 - Num lock*/
    0,  /* Scroll Lock */
    0,  /* Home key */
    0,  /* Up Arrow */
    0,  /* Page Up */
  '-',
    0,  /* Left Arrow */
    0,
    0,  /* Right Arrow */
  '+',
    0,  /* 79 - End key*/
    0,  /* Down Arrow */
    0,  /* Page Down */
    0,  /* Insert Key */
    0,  /* Delete Key */
    0,   0,   0,
    0,  /* F11 Key */
    0,  /* F12 Key */
    0,  /* All other keys are undefined */
};

const char kbdus_shift[128] = {
    0,  27, '!', '@', '#', '$', '%', '^', '&', '*',
  '(', ')', '_', '+', '\b',
  '\t',
  'Q', 'W', 'E', 'R',
  'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n',
    0,
  'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':',
 '\"', '~',   0,
 '|', 'Z', 'X', 'C', 'V', 'B', 'N',
  'M', '<', '>', '?',   0,
  '*',
    0,
  ' ',
    0,
    // ... rest undefined for now
};

static void keyboard_callback(struct registers* regs) {
    (void)regs; // Unused
    // Read the scancode from the keyboard data port (0x60)
    uint8_t scancode = inb(0x60);

    // If the top bit is set, it means a key was released.
    if (scancode & 0x80) {
        // Did we release shift?
        if (scancode == 0xAA || scancode == 0xB6) {
            shift_pressed = false;
        }
    } else {
        // Key was pressed down
        if (scancode == 0x2A || scancode == 0x36) { // Left or right shift
            shift_pressed = true;
            return;
        }

        char c = 0;
        if (shift_pressed) {
            c = kbdus_shift[scancode];
        } else {
            c = kbdus[scancode];
        }

        if (c != 0) {
            // Echo char to screen! (But we also need to store it in the buffer for the shell)
            if (c == '\b') {
                // We handle backspace echo here to feel immediate
                printf("\b \b");
            } else {
                printf("%c", c);
            }
            
            int next_head = (kbd_buffer_head + 1) % KBD_BUFFER_SIZE;
            if (next_head != kbd_buffer_tail) {
                keyboard_buffer[kbd_buffer_head] = c;
                kbd_buffer_head = next_head;
            }
        }
    }
}

void keyboard_init(void) {
    // IRQ1 belongs to the keyboard!
    register_interrupt_handler(33, keyboard_callback);
}

char keyboard_getchar(void) {
    if (kbd_buffer_head == kbd_buffer_tail) {
        return 0; // Buffer is empty
    }
    char c = keyboard_buffer[kbd_buffer_tail];
    kbd_buffer_tail = (kbd_buffer_tail + 1) % KBD_BUFFER_SIZE;
    return c;
}
