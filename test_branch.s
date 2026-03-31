# Test program demonstrating branch and jump instructions

.text
.org 0x0000

main:
    addi x5, x0, 5       # x5 = 5
    addi x6, x0, 10      # x6 = 10
    
loop:
    addi x5, x5, 1       # x5 = x5 + 1
    blt  x5, x6, loop    # If x5 < x6, branch to loop
    
    # Jump example
    jal  x1, subroutine  # Jump and link
    
done:
    ebreak

subroutine:
    addi x3, x0, 42      # x3 = 42
    jalr x0, 0(x1)       # Return (jump to return address in x1)
