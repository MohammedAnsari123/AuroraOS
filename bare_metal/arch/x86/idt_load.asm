global idt_load

; Loads the IDT
idt_load:
    mov eax, [esp+4]    ; Get the pointer to the IDT, passed as a parameter
    lidt [eax]          ; Load the IDT pointer
    ret                 ; Return to C
