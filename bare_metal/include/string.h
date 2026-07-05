#ifndef STRING_H
#define STRING_H

#include <types.h>

size_t strlen(const char* str);
char* strcpy(char* dest, const char* src);
int strcmp(const char* s1, const char* s2);
void* memset(void* dest, int val, size_t len);
void* memcpy(void* dest, const void* src, size_t len);

#endif
