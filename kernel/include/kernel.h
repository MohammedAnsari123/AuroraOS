/**
 * AuroraOS Kernel Header
 * Main kernel definitions and system-wide constants
 * 
 * This file defines the core kernel structures, constants, and function
 * prototypes that are used throughout the operating system.
 */

#ifndef KERNEL_H
#define KERNEL_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// ============================================================================
// KERNEL CONSTANTS
// ============================================================================

#define AURORA_VERSION "1.0.0"
#define AURORA_CODENAME "Northern Lights"
#define KERNEL_STACK_SIZE 8192
#define MAX_PROCESSES 256
#define MAX_THREADS 1024
#define PAGE_SIZE 4096

// ============================================================================
// SYSTEM CALL NUMBERS
// ============================================================================

#define SYS_EXIT        1
#define SYS_FORK        2
#define SYS_READ        3
#define SYS_WRITE       4
#define SYS_OPEN        5
#define SYS_CLOSE       6
#define SYS_WAIT        7
#define SYS_EXEC        8
#define SYS_GETPID      9
#define SYS_KILL        10
#define SYS_SLEEP       11

// ============================================================================
// PROCESS STATES
// ============================================================================

typedef enum {
    PROCESS_NEW = 0,
    PROCESS_READY,
    PROCESS_RUNNING,
    PROCESS_WAITING,
    PROCESS_TERMINATED
} process_state_t;

// ============================================================================
// PROCESS CONTROL BLOCK (PCB)
// ============================================================================

typedef struct process_control_block {
    uint32_t pid;                    // Process ID
    uint32_t parent_pid;             // Parent process ID
    process_state_t state;           // Current process state
    uint32_t priority;               // Process priority (0-255)
    uint32_t cpu_time;               // CPU time used (ms)
    void *stack_pointer;             // Stack pointer
    void *instruction_pointer;       // Instruction pointer
    uint32_t page_directory;         // Page directory address
    char name[64];                   // Process name
    struct process_control_block *next; // Next process in queue
} pcb_t;

// ============================================================================
// MEMORY STRUCTURES
// ============================================================================

typedef struct {
    uint32_t present    : 1;   // Page present in memory
    uint32_t rw         : 1;   // Read/write permissions
    uint32_t user       : 1;   // User/supervisor mode
    uint32_t accessed   : 1;   // Has been accessed
    uint32_t dirty      : 1;   // Has been written to
    uint32_t unused     : 7;   // Reserved
    uint32_t frame      : 20;  // Frame address
} page_table_entry_t;

typedef struct {
    uint32_t total_memory;       // Total system memory (KB)
    uint32_t used_memory;        // Used memory (KB)
    uint32_t free_memory;        // Free memory (KB)
    uint32_t cached_memory;      // Cached memory (KB)
} memory_info_t;

// ============================================================================
// INTERRUPT HANDLING
// ============================================================================

typedef struct {
    uint32_t ds;                     // Data segment selector
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax; // Registers
    uint32_t int_no, err_code;       // Interrupt number and error code
    uint32_t eip, cs, eflags, useresp, ss; // Pushed by processor
} registers_t;

typedef void (*interrupt_handler_t)(registers_t*);

// ============================================================================
// KERNEL FUNCTIONS - Initialization
// ============================================================================

/**
 * Initialize the kernel
 * Sets up memory management, process scheduler, and interrupt handlers
 */
void kernel_init(void);

/**
 * Main kernel loop
 * Handles scheduling and system maintenance
 */
void kernel_main(void);

/**
 * Shutdown the kernel
 * Cleanup resources and halt the system
 */
void kernel_shutdown(void);

// ============================================================================
// KERNEL FUNCTIONS - Process Management
// ============================================================================

/**
 * Create a new process
 * @param name Process name
 * @param entry_point Entry function pointer
 * @param priority Process priority (0-255)
 * @return Process ID or -1 on error
 */
int32_t process_create(const char *name, void (*entry_point)(void), uint32_t priority);

/**
 * Kill a process
 * @param pid Process ID to terminate
 * @return 0 on success, -1 on error
 */
int32_t process_kill(uint32_t pid);

/**
 * Get current process ID
 * @return Current process PID
 */
uint32_t process_get_current_pid(void);

/**
 * Yield CPU to next process
 */
void process_yield(void);

/**
 * Schedule next process
 * Called by timer interrupt
 */
void scheduler_run(void);

// ============================================================================
// KERNEL FUNCTIONS - Memory Management
// ============================================================================

/**
 * Initialize memory management
 * @param total_mem Total system memory in KB
 */
void memory_init(uint32_t total_mem);

/**
 * Allocate memory
 * @param size Size in bytes
 * @return Pointer to allocated memory or NULL
 */
void* kmalloc(size_t size);

/**
 * Free allocated memory
 * @param ptr Pointer to memory to free
 */
void kfree(void *ptr);

/**
 * Get memory information
 * @return Pointer to memory_info_t structure
 */
memory_info_t* memory_get_info(void);

// ============================================================================
// KERNEL FUNCTIONS - Interrupt Handling
// ============================================================================

/**
 * Initialize interrupt descriptor table
 */
void interrupts_init(void);

/**
 * Register interrupt handler
 * @param num Interrupt number
 * @param handler Handler function
 */
void interrupt_register_handler(uint8_t num, interrupt_handler_t handler);

/**
 * Enable interrupts
 */
void interrupts_enable(void);

/**
 * Disable interrupts
 */
void interrupts_disable(void);

// ============================================================================
// KERNEL FUNCTIONS - System Calls
// ============================================================================

/**
 * System call handler
 * @param regs Register state
 */
void syscall_handler(registers_t *regs);

/**
 * Register system call
 * @param num System call number
 * @param handler Handler function
 */
void syscall_register(uint32_t num, void* handler);

// ============================================================================
// KERNEL FUNCTIONS - Utilities
// ============================================================================

/**
 * Kernel panic - fatal error handler
 * @param message Error message
 */
void kernel_panic(const char *message);

/**
 * Print kernel message
 * @param message Message to print
 */
void kprintf(const char *format, ...);

/**
 * Get system uptime
 * @return Uptime in milliseconds
 */
uint64_t get_uptime(void);

// ============================================================================
// CONNECTOR HELPERS
// ============================================================================

typedef struct {
    uint32_t pid;
    uint32_t parent_pid;
    uint32_t state;
    uint32_t priority;
    uint32_t cpu_time;
    char name[64];
} process_info_t;

int get_process_count(void);
int get_process_list(process_info_t *info_array, int max_count);

#endif // KERNEL_H
