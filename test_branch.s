# Test program demonstrating branch and jump instructions

.text
.org 0x0000

main:
    addi x1, x0, 5       # x1 = 5
    addi x2, x0, 10      # x2 = 10
    
loop:
    addi x1, x1, 1       # x1 = x1 + 1
    blt  x1, x2, loop    # If x1 < x2, branch to loop
    
    # Jump example
    jal  x1, subroutine  # Jump and link
    
done:
    ebreak

subroutine:
    addi x3, x0, 42      # x3 = 42
    jalr x0, 0(x1)       # Return (jump to return address in x1)
