# Simple test program for RISC-V assembler
# This program demonstrates basic arithmetic operations

.text
.org 0x0000

start:
    addi x1, x0, 10      # x1 = 10
    addi x6, x0, 20      # x6 = 20 (x2 is sp, avoid changing stack pointer)
    add  x3, x1, x6      # x3 = x1 + x6 = 30
    sub  x4, x6, x1      # x4 = x6 - x1 = 10
    
    # Store result
    sw   x3, 256(x0)     # Store x3 to a safe data address (not over code)
    
    # Branch example
    beq  x1, x6, end     # If x1 == x6, jump to end
    addi x5, x0, 1       # x5 = 1
    
end:
    ebreak               # End of program
