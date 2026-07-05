#include <stdio.h>
#include <vga.h>
#include <string.h>
#include <types.h>

// Extremely basic implementation of variable arguments since we don't have <stdarg.h> from the compiler available cleanly without setup
typedef char* va_list;
#define va_start(ap, param) (ap = (va_list)&param + sizeof(param))
#define va_arg(ap, type)    (*(type *)((ap += sizeof(type)) - sizeof(type)))
#define va_end(ap)          (ap = NULL)

void itoa(int value, char* str, int base) {
    char* rc;
    char* ptr;
    char* low;
    // Check for supported base.
    if ( base < 2 || base > 36 ) {
        *str = '\0';
        return;
    }
    rc = ptr = str;
    // Set '-' for negative decimals.
    if ( value < 0 && base == 10 ) {
        *ptr++ = '-';
    }
    // Remember where the numbers start.
    low = ptr;
    // The actual conversion.
    do {
        // Modulo is negative for negative value. This trick makes abs() unnecessary.
        *ptr++ = "zyxwvutsrqponmlkjihgfedcba9876543210123456789abcdefghijklmnopqrstuvwxyz"[35 + value % base];
        value /= base;
    } while ( value );
    // Terminating the string.
    *ptr-- = '\0';
    // Invert the numbers.
    while ( low < ptr ) {
        char tmp = *low;
        *low++ = *ptr;
        *ptr-- = tmp;
    }
}

void printf(const char* format, ...) {
    va_list ap;
    va_start(ap, format);

    while (*format) {
        if (*format == '%') {
            format++;
            switch (*format) {
                case 's': {
                    char* s = va_arg(ap, char*);
                    vga_writestring(s);
                    break;
                }
                case 'd': {
                    int d = va_arg(ap, int);
                    char buf[32];
                    itoa(d, buf, 10);
                    vga_writestring(buf);
                    break;
                }
                case 'x': {
                    int x = va_arg(ap, int);
                    char buf[32];
                    itoa(x, buf, 16);
                    vga_writestring(buf);
                    break;
                }
                case 'c': {
                    char c = (char)va_arg(ap, int);
                    vga_putchar(c);
                    break;
                }
                default:
                    vga_putchar('%');
                    vga_putchar(*format);
                    break;
            }
        } else {
            vga_putchar(*format);
        }
        format++;
    }

    va_end(ap);
}
