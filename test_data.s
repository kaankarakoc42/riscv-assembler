# Test program demonstrating data directives

.data
.org 0x1000

# Data segment
value1: .word 0x12345678
value2: .word 0xABCDEF00
array:  .byte 1, 2, 3, 4, 5

.text
.org 0x0000

main:
    # Load data
    lui  x1, 0x10000     # Load upper immediate
    lw   x2, 0(x1)       # Load value1
    lw   x3, 4(x1)       # Load value2
    
    # Arithmetic
    add  x4, x2, x3      # x4 = value1 + value2
    
    # Store result
    sw   x4, 8(x1)       # Store result
    
    ebreak
