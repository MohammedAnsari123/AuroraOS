#ifndef KEYBOARD_H
#define KEYBOARD_H

#include <types.h>

void keyboard_init(void);

// Buffer for keyboard input
#define KBD_BUFFER_SIZE 256
extern char keyboard_buffer[KBD_BUFFER_SIZE];
extern volatile int kbd_buffer_head;
extern volatile int kbd_buffer_tail;

// Fetch a typed character from the buffer. Returns 0 if empty.
char keyboard_getchar(void);

#endif // KEYBOARD_H
