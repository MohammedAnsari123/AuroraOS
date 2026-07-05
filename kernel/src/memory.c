/**
 * AuroraOS Memory Management Implementation
 * Simulated memory allocation using linked list
 */

#include "../include/memory.h"
#include "../include/kernel.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// ============================================================================
// MEMORY HEAP MANAGEMENT
// ============================================================================

static memory_block_t *heap_start = NULL;
static size_t total_allocated = 0;
static size_t total_freed = 0;

/**
 * Initialize memory block
 */
static memory_block_t* init_memory_block(size_t size) {
    memory_block_t *block = (memory_block_t*)malloc(sizeof(memory_block_t) + size);
    if (block == NULL) {
        return NULL;
    }
    
    block->size = size;
    block->is_free = false;
    block->next = NULL;
    block->prev = NULL;
    
    return block;
}

/**
 * Find free block that fits the requested size
 */
static memory_block_t* find_free_block(size_t size) {
    memory_block_t *current = heap_start;
    
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            return current;
        }
        current = current->next;
    }
    
    return NULL;
}

/**
 * Memory allocation implementation
 */
void* malloc_impl(size_t size) {
    if (size == 0) {
        return NULL;
    }
    
    // Align size to 8 bytes
    size = (size + 7) & ~7;
    
    // Try to find free block
    memory_block_t *block = find_free_block(size);
    
    if (block != NULL) {
        // Reuse existing block
        block->is_free = false;
        total_allocated += size;
        return (void*)(block + 1);
    }
    
    // Allocate new block
    block = init_memory_block(size);
    if (block == NULL) {
        printf("[MEMORY] ERROR: Failed to allocate %zu bytes\n", size);
        return NULL;
    }
    
    // Add to linked list
    if (heap_start == NULL) {
        heap_start = block;
    } else {
        memory_block_t *current = heap_start;
        while (current->next != NULL) {
            current = current->next;
        }
        current->next = block;
        block->prev = current;
    }
    
    total_allocated += size;
    return (void*)(block + 1);
}

/**
 * Memory free implementation
 */
void free_impl(void *ptr) {
    if (ptr == NULL) {
        return;
    }
    
    // Get block header
    memory_block_t *block = (memory_block_t*)ptr - 1;
    
    if (block->is_free) {
        printf("[MEMORY] WARNING: Double free detected at %p\n", ptr);
        return;
    }
    
    block->is_free = true;
    total_freed += block->size;
    
    // Coalesce with next block if free
    if (block->next != NULL && block->next->is_free) {
        block->size += sizeof(memory_block_t) + block->next->size;
        block->next = block->next->next;
        if (block->next != NULL) {
            block->next->prev = block;
        }
    }
    
    // Coalesce with previous block if free
    if (block->prev != NULL && block->prev->is_free) {
        block->prev->size += sizeof(memory_block_t) + block->size;
        block->prev->next = block->next;
        if (block->next != NULL) {
            block->next->prev = block->prev;
        }
    }
}

/**
 * Memory reallocation implementation
 */
void* realloc_impl(void *ptr, size_t size) {
    if (ptr == NULL) {
        return malloc_impl(size);
    }
    
    if (size == 0) {
        free_impl(ptr);
        return NULL;
    }
    
    // Get current block
    memory_block_t *block = (memory_block_t*)ptr - 1;
    
    // If new size fits in current block, just return it
    if (block->size >= size) {
        return ptr;
    }
    
    // Allocate new block
    void *new_ptr = malloc_impl(size);
    if (new_ptr == NULL) {
        return NULL;
    }
    
    // Copy old data
    memcpy(new_ptr, ptr, block->size);
    
    // Free old block
    free_impl(ptr);
    
    return new_ptr;
}

/**
 * Dump memory statistics
 */
void memory_dump_stats(void) {
    printf("\n");
    printf("╔═══════════════════════════════════════════════════════╗\n");
    printf("║              MEMORY ALLOCATION STATISTICS             ║\n");
    printf("╚═══════════════════════════════════════════════════════╝\n");
    printf("\n");
    printf("  Total Allocated: %zu bytes\n", total_allocated);
    printf("  Total Freed:     %zu bytes\n", total_freed);
    printf("  Currently Used:  %zu bytes\n", total_allocated - total_freed);
    printf("\n");
    
    // Count blocks
    int total_blocks = 0;
    int free_blocks = 0;
    memory_block_t *current = heap_start;
    
    while (current != NULL) {
        total_blocks++;
        if (current->is_free) {
            free_blocks++;
        }
        current = current->next;
    }
    
    printf("  Total Blocks:    %d\n", total_blocks);
    printf("  Free Blocks:     %d\n", free_blocks);
    printf("  Used Blocks:     %d\n", total_blocks - free_blocks);
    printf("\n");
}

int get_heap_block_count(void) {
    int count = 0;
    memory_block_t *current = heap_start;
    while (current != NULL) {
        count++;
        current = current->next;
    }
    return count;
}

int get_heap_blocks(heap_block_info_t *blocks_array, int max_count) {
    int count = 0;
    memory_block_t *current = heap_start;
    while (current != NULL && count < max_count) {
        blocks_array[count].address = (uint32_t)(uintptr_t)(current + 1); // User pointer address
        blocks_array[count].size = (uint32_t)current->size;
        blocks_array[count].is_free = (uint32_t)current->is_free;
        
        count++;
        current = current->next;
    }
    return count;
}
