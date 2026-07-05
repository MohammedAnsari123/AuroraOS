#ifndef MOUSE_H
#define MOUSE_H

#include <types.h>

void mouse_init(void);

// Global mouse state accessible by the window manager
extern volatile int mouse_x;
extern volatile int mouse_y;
extern volatile bool mouse_left_pressed;
extern volatile bool mouse_right_pressed;

#define MOUSE_PORT   0x60
#define MOUSE_STATUS 0x64
#define MOUSE_ABIT   0x02
#define MOUSE_BBIT   0x01
#define MOUSE_WRITE  0xD4
#define MOUSE_F_BIT  0x20
#define MOUSE_V_BIT  0x08

#endif // MOUSE_H
