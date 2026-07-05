# Root Makefile for AuroraOS
# Automates C kernel DLL compilation, system launch, and bare-metal OS operations

# Target library name based on OS (fallback to DLL for Windows)
ifeq ($(OS),Windows_NT)
    LIB_TARGET = kernel.dll
    RM = del /Q /F
    PYTHON = python
    MAKE_BAREMETAL = $(MAKE) -C bare_metal
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        LIB_TARGET = kernel.dylib
    else
        LIB_TARGET = kernel.so
    endif
    RM = rm -f
    PYTHON = python3
    MAKE_BAREMETAL = make -C bare_metal
endif

.PHONY: all dll run clean baremetal run-baremetal help

all: dll

# Compile the C kernel shared library (CTypes bridge)
dll: $(LIB_TARGET)

$(LIB_TARGET): kernel/src/kernel.c kernel/src/memory.c kernel/include/kernel.h kernel/include/memory.h
	gcc -shared -o $(LIB_TARGET) -Ikernel/include kernel/src/kernel.c kernel/src/memory.c

# Run the Python simulated GUI operating system
run: dll
	$(PYTHON) launcher.py

# Build the 32-bit x86 bare-metal kernel
baremetal:
	$(MAKE_BAREMETAL) all

# Run the bare-metal kernel inside QEMU
run-baremetal:
	$(MAKE_BAREMETAL) run

# Clean up all build and generated artifacts
clean:
	-$(RM) $(LIB_TARGET)
	-$(RM) config\system\virtual_disk.img
	-$(RM) config\system\filesystem_metadata.json
	-$(RM) config\user\users.json
	-$(RM) config\user\session.json
	$(MAKE_BAREMETAL) clean

# Help instructions
help:
	@echo ====================================================================
	@echo "                   AURORAOS BUILD SYSTEM HELP"
	@echo ====================================================================
	@echo "  make dll            - Compile C kernel dynamic shared library"
	@echo "  make run            - Launch AuroraOS Tkinter GUI (auto-builds DLL)"
	@echo "  make clean          - Reset OS data and remove build artifacts"
	@echo "  make baremetal      - Build 32-bit x86 baremetal kernel (C/ASM)"
	@echo "  make run-baremetal  - Launch baremetal kernel in QEMU"
	@echo ====================================================================
