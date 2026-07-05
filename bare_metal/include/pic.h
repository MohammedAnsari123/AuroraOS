#ifndef PIC_H
#define PIC_H

#include <types.h>
#include <io.h>

void pic_remap(int offset1, int offset2);
void pic_unmask(int irq);

#endif // PIC_H
