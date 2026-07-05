/**
 * AuroraOS Memory Management Header
 * Virtual memory and physical memory management
 */

#ifndef MEMORY_H
#define MEMORY_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// ============================================================================
// MEMORY CONSTANTS
// ============================================================================

#define PAGE_SIZE 4096
#define KERNEL_HEAP_START 0xC0000000
#define KERNEL_HEAP_SIZE 0x10000000  // 256 MB
#define USER_SPACE_START 0x00400000
#define USER_SPACE_END 0xBFFFFFFF

// ============================================================================
// MEMORY BLOCK STRUCTURE
// ============================================================================

typedef struct memory_block {
    size_t size;                     // Size of the block
    bool is_free;                    // Block allocation status
    struct memory_block *next;       // Next block in list
    struct memory_block *prev;       // Previous block in list
} memory_block_t;

// ============================================================================
// PAGE TABLE STRUCTURES
// ============================================================================

typedef struct {
    uint32_t present    : 1;
    uint32_t rw         : 1;
    uint32_t user       : 1;
    uint32_t accessed   : 1;
    uint32_t dirty      : 1;
    uint32_t unused     : 7;
    uint32_t frame      : 20;
} page_entry_t;

typedef struct {
    page_entry_t pages[1024];
} page_table_t;

typedef struct {
    page_table_t *tables[1024];
    uint32_t physical_tables[1024];
} page_directory_t;

// ============================================================================
// MEMORY FUNCTIONS
// ============================================================================

void* malloc_impl(size_t size);
void free_impl(void *ptr);
void* realloc_impl(void *ptr, size_t size);
void memory_dump_stats(void);

// ============================================================================
// HEAP BLOCK TRAVERSAL (For CTypes connector)
// ============================================================================

typedef struct {
    uint32_t address;
    uint32_t size;
    uint32_t is_free;
} heap_block_info_t;

int get_heap_block_count(void);
int get_heap_blocks(heap_block_info_t *blocks_array, int max_count);

#endif // MEMORY_H
