/**
 * AuroraOS Kernel Implementation
 * Main kernel initialization and core functions
 */

#include "../include/kernel.h"
#include "../include/memory.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// ============================================================================
// GLOBAL KERNEL STATE
// ============================================================================

static pcb_t *process_list = NULL;
static pcb_t *current_process = NULL;
static uint32_t next_pid = 1;
static uint64_t system_uptime = 0;
static bool kernel_running = false;
static interrupt_handler_t interrupt_handlers[256];

// ============================================================================
// KERNEL INITIALIZATION
// ============================================================================

/**
 * Initialize the AuroraOS kernel
 * Sets up all core subsystems
 */
void kernel_init(void) {
    printf("\n");
    printf("  ╔═══════════════════════════════════════════════════════╗\n");
    printf("  ║         🌌 AuroraOS Kernel v%s 🌌               ║\n", AURORA_VERSION);
    printf("  ║              %s                  ║\n", AURORA_CODENAME);
    printf("  ╚═══════════════════════════════════════════════════════╝\n");
    printf("\n");
    
    kprintf("[KERNEL] Initializing AuroraOS Kernel...\n");
    
    // Initialize memory management
    kprintf("[KERNEL] Initializing memory management...\n");
    memory_init(128 * 1024); // 128 MB simulated RAM
    
    // Initialize interrupt system
    kprintf("[KERNEL] Setting up interrupt handlers...\n");
    interrupts_init();
    
    // Initialize process scheduler
    kprintf("[KERNEL] Initializing process scheduler...\n");
    process_list = NULL;
    current_process = NULL;
    
    // Create init process (PID 1)
    kprintf("[KERNEL] Creating init process...\n");
    // process_create("init", init_process, 100);
    
    kernel_running = true;
    kprintf("[KERNEL] ✓ Kernel initialization complete!\n");
    printf("\n");
}

/**
 * Main kernel loop
 */
void kernel_main(void) {
    kprintf("[KERNEL] Entering main kernel loop...\n");
    
    while (kernel_running) {
        // Update system uptime
        system_uptime++;
        
        // Run scheduler
        scheduler_run();
        
        // Small delay to prevent busy-wait
        // In real OS, this would be handled by timer interrupts
        // usleep(1000); // 1ms
    }
}

/**
 * Shutdown the kernel
 */
void kernel_shutdown(void) {
    kprintf("[KERNEL] Shutting down AuroraOS...\n");
    
    // Terminate all processes
    pcb_t *current = process_list;
    while (current != NULL) {
        pcb_t *next = current->next;
        kprintf("[KERNEL] Terminating process %d (%s)\n", current->pid, current->name);
        kfree(current);
        current = next;
    }
    
    kernel_running = false;
    kprintf("[KERNEL] ✓ Shutdown complete. Goodbye!\n");
}

// ============================================================================
// PROCESS MANAGEMENT
// ============================================================================

/**
 * Create a new process
 */
int32_t process_create(const char *name, void (*entry_point)(void), uint32_t priority) {
    // Allocate PCB
    pcb_t *pcb = (pcb_t*)kmalloc(sizeof(pcb_t));
    if (pcb == NULL) {
        kprintf("[KERNEL] ERROR: Failed to allocate PCB for %s\n", name);
        return -1;
    }
    
    // Initialize PCB
    pcb->pid = next_pid++;
    pcb->parent_pid = current_process ? current_process->pid : 0;
    pcb->state = PROCESS_NEW;
    pcb->priority = priority;
    pcb->cpu_time = 0;
    pcb->stack_pointer = kmalloc(KERNEL_STACK_SIZE);
    pcb->instruction_pointer = (void*)entry_point;
    strncpy(pcb->name, name, 63);
    pcb->name[63] = '\0';
    pcb->next = NULL;
    
    // Add to process list
    if (process_list == NULL) {
        process_list = pcb;
    } else {
        pcb_t *current = process_list;
        while (current->next != NULL) {
            current = current->next;
        }
        current->next = pcb;
    }
    
    pcb->state = PROCESS_READY;
    kprintf("[KERNEL] Created process %d: %s (priority=%d)\n", pcb->pid, name, priority);
    
    return pcb->pid;
}

/**
 * Kill a process
 */
int32_t process_kill(uint32_t pid) {
    pcb_t *prev = NULL;
    pcb_t *current = process_list;
    
    while (current != NULL) {
        if (current->pid == pid) {
            kprintf("[KERNEL] Killing process %d (%s)\n", pid, current->name);
            
            // Update state
            current->state = PROCESS_TERMINATED;
            
            // Remove from list
            if (prev == NULL) {
                process_list = current->next;
            } else {
                prev->next = current->next;
            }
            
            // Free resources
            kfree(current->stack_pointer);
            kfree(current);
            
            return 0;
        }
        prev = current;
        current = current->next;
    }
    
    kprintf("[KERNEL] ERROR: Process %d not found\n", pid);
    return -1;
}

/**
 * Get current process ID
 */
uint32_t process_get_current_pid(void) {
    return current_process ? current_process->pid : 0;
}

/**
 * Yield CPU to next process
 */
void process_yield(void) {
    scheduler_run();
}

/**
 * Simple round-robin scheduler
 */
void scheduler_run(void) {
    if (process_list == NULL) {
        return;
    }
    
    // Find next ready process
    static pcb_t *last_scheduled = NULL;
    pcb_t *start = last_scheduled ? last_scheduled->next : process_list;
    if (start == NULL) {
        start = process_list;
    }
    
    pcb_t *current = start;
    do {
        if (current->state == PROCESS_READY) {
            // Context switch
            if (current_process && current_process->state == PROCESS_RUNNING) {
                current_process->state = PROCESS_READY;
            }
            
            current_process = current;
            current_process->state = PROCESS_RUNNING;
            current_process->cpu_time++;
            last_scheduled = current;
            return;
        }
        
        current = current->next;
        if (current == NULL) {
            current = process_list;
        }
    } while (current != start);
}

// ============================================================================
// MEMORY MANAGEMENT
// ============================================================================

static memory_info_t mem_info;

void memory_init(uint32_t total_mem) {
    mem_info.total_memory = total_mem;
    mem_info.used_memory = 0;
    mem_info.free_memory = total_mem;
    mem_info.cached_memory = 0;
    
    kprintf("[MEMORY] Initialized %d KB of system memory\n", total_mem);
}

void* kmalloc(size_t size) {
    void *ptr = malloc_impl(size);
    if (ptr != NULL) {
        mem_info.used_memory += size / 1024;
        mem_info.free_memory -= size / 1024;
    }
    return ptr;
}

void kfree(void *ptr) {
    if (ptr != NULL) {
        free_impl(ptr);
    }
}

memory_info_t* memory_get_info(void) {
    return &mem_info;
}

// ============================================================================
// INTERRUPT HANDLING
// ============================================================================

void interrupts_init(void) {
    // Clear all interrupt handlers
    for (int i = 0; i < 256; i++) {
        interrupt_handlers[i] = NULL;
    }
    kprintf("[INTERRUPTS] Initialized interrupt descriptor table\n");
}

void interrupt_register_handler(uint8_t num, interrupt_handler_t handler) {
    interrupt_handlers[num] = handler;
    kprintf("[INTERRUPTS] Registered handler for interrupt %d\n", num);
}

void interrupts_enable(void) {
    // In real OS: asm volatile("sti");
    kprintf("[INTERRUPTS] Interrupts enabled\n");
}

void interrupts_disable(void) {
    // In real OS: asm volatile("cli");
    kprintf("[INTERRUPTS] Interrupts disabled\n");
}

// ============================================================================
// SYSTEM CALLS
// ============================================================================

void syscall_handler(registers_t *regs) {
    // System call implementation would go here
    uint32_t syscall_num = regs->eax;
    kprintf("[SYSCALL] System call %d from process %d\n", syscall_num, process_get_current_pid());
}

void syscall_register(uint32_t num, void* handler) {
    kprintf("[SYSCALL] Registered system call %d\n", num);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

void kernel_panic(const char *message) {
    printf("\n");
    printf("╔═══════════════════════════════════════════════════════╗\n");
    printf("║                  ⚠️  KERNEL PANIC ⚠️                    ║\n");
    printf("╚═══════════════════════════════════════════════════════╝\n");
    printf("\n");
    printf("FATAL ERROR: %s\n", message);
    printf("\n");
    printf("System halted. Please restart.\n");
    exit(1);
}

void kprintf(const char *format, ...) {
    printf("%s", format);
}

uint64_t get_uptime(void) {
    return system_uptime;
}

int get_process_count(void) {
    int count = 0;
    pcb_t *current = process_list;
    while (current != NULL) {
        count++;
        current = current->next;
    }
    return count;
}

int get_process_list(process_info_t *info_array, int max_count) {
    int count = 0;
    pcb_t *current = process_list;
    while (current != NULL && count < max_count) {
        info_array[count].pid = current->pid;
        info_array[count].parent_pid = current->parent_pid;
        info_array[count].state = (uint32_t)current->state;
        info_array[count].priority = current->priority;
        info_array[count].cpu_time = current->cpu_time;
        strncpy(info_array[count].name, current->name, 63);
        info_array[count].name[63] = '\0';
        
        count++;
        current = current->next;
    }
    return count;
}

