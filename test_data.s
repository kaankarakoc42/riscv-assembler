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
    # Base of .data is 0x1000; LUI places imm in bits [31:12], so use 0x1 -> 0x1000
    lui  x1, 0x1         # x1 = 0x00001000
    lw   x2, 0(x1)       # Load value1
    lw   x3, 4(x1)       # Load value2
    
    # Arithmetic
    add  x4, x2, x3      # x4 = value1 + value2
    
    # Store result safely after array bytes (array is at 0x1008..0x100C)
    sw   x4, 16(x1)      # Store result at 0x1010
    
    ebreak
