# RISC-V RV32I Assembler for PicoRV Processor

A complete assembler implementation for the RISC-V RV32I instruction set, designed for the PicoRV processor subset.

## Features

- **Complete RV32I Instruction Support**: Supports all base RISC-V RV32I instructions including:
  - Arithmetic and logic operations (R-type, I-type)
  - Load/Store instructions
  - Branch and jump instructions
  - System instructions (ecall, ebreak)
  - Upper immediate instructions (lui, auipc)

- **Assembler Directives**: Supports common assembler directives:
  - `.data` - Data segment
  - `.text` - Text (code) segment
  - `.word` - Define word (32-bit) values
  - `.byte` - Define byte values
  - `.org` - Set origin address
  - `.end` - End of assembly

- **Symbol Table**: Complete symbol table implementation for labels
- **Two-Pass Assembly**: Proper two-pass assembly process for forward reference resolution
- **Multiple Output Formats**: Supports ELF (default), hex, Verilog, and binary output formats

## Project Structure

```
riscv-assembler/
├── opcode_table.py      # Opcode table and instruction encoding
├── symbol_table.py      # Symbol table data structure
├── parser.py            # Assembly code parser
├── code_generator.py    # Machine code generator
├── directive_handler.py # Assembler directive handler
├── assembler.py         # Main assembler class
├── main.py              # Command-line interface
├── test_simple.s        # Simple test program
├── test_data.s          # Test with data directives
├── test_branch.s        # Test with branches and jumps
└── README.md            # This file
```

## Installation

No external dependencies required. The assembler is written in pure Python 3.

## Usage

### Command Line

```bash
# Basic usage
python main.py input.s

# Specify output file
python main.py input.s -o output.elf

# Choose output format
python main.py input.s -o output.v -f verilog
python main.py input.s -o output.elf -f elf

# Print symbol table
python main.py input.s -s

# Verbose output
python main.py input.s -v
```

### Programmatic Usage

```python
from assembler import Assembler

# Create assembler instance
asm = Assembler()

# Assemble from file
result = asm.assemble_file('program.s')

# Or assemble from string
source_code = """
.text
    addi x1, x0, 10
    add  x2, x1, x1
"""
result = asm.assemble(source_code)

# Check result
if result['success']:
    # Print output
    asm.print_output()
    
    # Print symbol table
    asm.print_symbol_table()
    
    # Write object file
    asm.write_object_file('output.elf', format='elf')
else:
    # Print errors
    for error in result['errors']:
        print(f"Error: {error}")
```

## Assembly Language Syntax

### Instructions

Instructions follow the standard RISC-V assembly syntax:

```assembly
# R-type: add rd, rs1, rs2
add x1, x2, x3

# I-type: addi rd, rs1, imm
addi x1, x2, 10

# Load: lw rd, offset(rs1)
lw x1, 4(x2)

# Store: sw rs2, offset(rs1)
sw x1, 8(x2)

# Branch: beq rs1, rs2, label
beq x1, x2, loop

# Jump: jal rd, label
jal x1, subroutine
```

### Directives

```assembly
.data                    # Start data segment
.org 0x1000              # Set origin to 0x1000
value: .word 0x12345678  # Define word value
array: .byte 1, 2, 3     # Define byte array

.text                    # Start text segment
.org 0x0000              # Set code origin
main:                    # Label definition
    addi x1, x0, 10
    ebreak
.end                     # End of assembly
```

### Labels

Labels can be defined on their own line or on the same line as an instruction:

```assembly
loop:
    addi x1, x1, 1
    blt x1, x2, loop

# Or on same line
start: addi x1, x0, 10
```

### Comments

Comments start with `#` and extend to the end of the line:

```assembly
addi x1, x0, 10  # Load immediate value 10
```

## Register Names

The assembler supports both standard RISC-V register names and numeric names:

- `x0` - `x31` or `zero`, `ra`, `sp`, `gp`, `tp`, `t0`-`t6`, `s0`-`s11`, `a0`-`a7`
- `fp` is an alias for `s0`

## Output Formats

### ELF Format (default)
Produces a minimal ELF32 little-endian RISC-V executable image.

### Hex Format
```
00000000: 00A00093
00000004: 01400113
00000008: 002081B3
```

### Verilog Format
```
// Machine code output
// Format: address: instruction
32'h00A00093, // 0x00000000
32'h01400113, // 0x00000004
32'h002081B3, // 0x00000008
```

### Binary Format
Raw binary output (little-endian, 32-bit words)

## Testing

Test programs are included:

```bash
# Test simple arithmetic
python main.py test_simple.s -v -s

# Test data directives
python main.py test_data.s -v -s

# Test branches and jumps
python main.py test_branch.s -v -s
```

## Architecture

The assembler uses a modular architecture:

1. **OpcodeTable**: Stores instruction encodings and register mappings
2. **SymbolTable**: Manages labels and their addresses
3. **Parser**: Parses assembly source into structured components
4. **CodeGenerator**: Generates machine code from parsed instructions
5. **DirectiveHandler**: Processes assembler directives
6. **Assembler**: Orchestrates the two-pass assembly process

### Two-Pass Assembly

1. **First Pass**: 
   - Collects all labels and their addresses
   - Processes directives to determine memory layout
   - Builds symbol table

2. **Second Pass**:
   - Generates machine code using resolved labels
   - Handles data directives
   - Produces final output

## Algorithm Complexity

- **Time Complexity**: O(n) where n is the number of lines
  - First pass: O(n) - single scan
  - Second pass: O(n) - single scan
  - Total: O(n)

- **Space Complexity**: O(m) where m is the number of symbols
  - Symbol table: O(m)
  - Output: O(n) for n instructions
  - Total: O(n + m)

## Limitations

- Currently supports RV32I base instruction set only
- No macro support
- No expression evaluation in directives (only immediate values)
- Forward references must be resolvable within the same file

## Future Enhancements

- Support for additional RISC-V extensions (M, A, F, D)
- Macro support
- Expression evaluation
- Linker support
- Object file format output (ELF)

## License

This project is developed for educational purposes as part of a computer architecture course.

## Author

Developed for PicoRV processor assembler project.

## References

- RISC-V Instruction Set Manual, Volume I: User-Level ISA
- RISC-V Specification v2.2
- PicoRV32 Processor Documentation
