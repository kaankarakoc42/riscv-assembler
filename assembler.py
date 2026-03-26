"""
Main Assembler Class
This module orchestrates all components to assemble RISC-V assembly code.
"""

import struct

from opcode_table import OpcodeTable
from symbol_table import SymbolTable
from parser import Parser
from code_generator import CodeGenerator
from directive_handler import DirectiveHandler

class Assembler:
    """Main assembler class for RISC-V RV32I"""
    
    def __init__(self):
        """Initialize the assembler with all components"""
        self.opcode_table = OpcodeTable()
        self.symbol_table = SymbolTable()
        self.parser = Parser()
        self.directive_handler = DirectiveHandler()
        self.code_generator = CodeGenerator(self.opcode_table, self.symbol_table)
        
        # Assembly state
        self.current_address = 0
        self.data_address = 0x1000  # Default data segment start
        self.text_address = 0x0000  # Default text segment start
        self.output = []  # List of (address, value) tuples
        self.errors = []
        self.warnings = []
    
    def assemble(self, source_code):
        """
        Assemble source code into machine code
        
        Args:
            source_code: Assembly source code as string or list of lines
            
        Returns:
            Dictionary with assembly results:
            {
                'success': bool,
                'output': list of (address, value) tuples,
                'errors': list of error messages,
                'warnings': list of warning messages,
                'symbol_table': symbol table
            }
        """
        # Reset state
        self.symbol_table.clear()
        self.directive_handler.reset()
        self.output = []
        self.errors = []
        self.warnings = []
        self.current_address = self.text_address
        
        # Convert source to lines if needed
        if isinstance(source_code, str):
            lines = source_code.split('\n')
        else:
            lines = source_code
        
        # First pass: collect labels and directives
        try:
            self._first_pass(lines)
        except Exception as e:
            self.errors.append(f"First pass error: {str(e)}")
            return self._get_result()
        
        # Second pass: generate machine code
        try:
            self._second_pass(lines)
        except Exception as e:
            self.errors.append(f"Second pass error: {str(e)}")
            return self._get_result()
        
        return self._get_result()
    
    def assemble_file(self, filename):
        """
        Assemble a file
        
        Args:
            filename: Path to assembly source file
            
        Returns:
            Dictionary with assembly results
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source_code = f.read()
            return self.assemble(source_code)
        except FileNotFoundError:
            return {
                'success': False,
                'output': [],
                'errors': [f"File not found: {filename}"],
                'warnings': [],
                'symbol_table': self.symbol_table
            }
        except Exception as e:
            return {
                'success': False,
                'output': [],
                'errors': [f"Error reading file: {str(e)}"],
                'warnings': [],
                'symbol_table': self.symbol_table
            }
    
    def _first_pass(self, lines):
        """First pass: collect labels and resolve directives"""
        self.current_address = self.text_address
        line_number = 0
        
        for line in lines:
            line_number += 1
            parsed = self.parser.parse_line(line)
            
            if parsed['type'] == 'empty' or parsed['type'] == 'comment':
                continue
            
            # Handle directives
            if parsed['type'] == 'directive':
                directive = parsed['directive']
                args = parsed.get('args', [])
                
                if directive == 'org':
                    if args:
                        self.current_address = args[0]
                elif directive == 'data':
                    self.current_address = self.data_address
                elif directive == 'text':
                    self.current_address = self.text_address
                elif directive == 'word':
                    # Each word is 4 bytes
                    word_count = len(args)
                    self.current_address += word_count * 4
                elif directive == 'byte':
                    # Each byte is 1 byte
                    byte_count = len(args)
                    self.current_address += byte_count
                continue
            
            # Handle labels
            if 'label' in parsed:
                label = parsed['label']
                self.symbol_table.add_symbol(label, self.current_address)
            
            # Handle instructions
            if parsed['type'] == 'instruction' or 'mnemonic' in parsed:
                # Each instruction is 4 bytes
                self.current_address += 4
    
    def _second_pass(self, lines):
        """Second pass: generate machine code"""
        self.current_address = self.text_address
        line_number = 0
        
        for line in lines:
            line_number += 1
            parsed = self.parser.parse_line(line)
            
            if parsed['type'] == 'empty' or parsed['type'] == 'comment':
                continue
            
            # Handle directives
            if parsed['type'] == 'directive':
                directive = parsed['directive']
                args = parsed.get('args', [])
                
                try:
                    result = self.directive_handler.handle_directive(
                        directive, args, self.current_address
                    )
                    
                    if directive == 'org':
                        self.current_address = args[0]
                    elif directive == 'data':
                        self.current_address = self.data_address
                    elif directive == 'text':
                        self.current_address = self.text_address
                    elif directive == 'word':
                        # Add word data to output
                        for word in result['data']:
                            self.output.append((self.current_address, word))
                            self.current_address += 4
                    elif directive == 'byte':
                        # Add byte data to output
                        for byte_val in result['data']:
                            self.output.append((self.current_address, byte_val))
                            self.current_address += 1
                    elif directive == 'end':
                        break
                except Exception as e:
                    self.errors.append(f"Line {line_number}: {str(e)}")
                continue
            
            # Handle labels on same line as instruction
            # Handle labels (already processed in first pass, but check for instruction)
            if 'label' in parsed and parsed['type'] == 'label' and 'mnemonic' not in parsed:
                continue
            
            # Handle instructions
            if parsed['type'] == 'instruction' or 'mnemonic' in parsed:
                try:
                    machine_code = self.code_generator.generate_instruction(
                        parsed, self.current_address
                    )
                    self.output.append((self.current_address, machine_code))
                    self.current_address += 4
                except Exception as e:
                    self.errors.append(f"Line {line_number}: {str(e)}")
    
    def _get_result(self):
        """Get assembly result dictionary"""
        success = len(self.errors) == 0
        return {
            'success': success,
            'output': self.output,
            'errors': self.errors,
            'warnings': self.warnings,
            'symbol_table': self.symbol_table
        }
    
    def _build_memory_image(self):
        """Build a contiguous memory image from sparse assembler output."""
        if not self.output:
            return 0, b""

        sorted_output = sorted(self.output, key=lambda item: item[0])
        starts = []
        ends = []
        entries = []

        for idx, (address, value) in enumerate(sorted_output):
            prev_addr = sorted_output[idx - 1][0] if idx > 0 else None
            next_addr = (
                sorted_output[idx + 1][0] if idx + 1 < len(sorted_output) else None
            )

            # Heuristic: values emitted inside contiguous byte runs are bytes.
            is_byte_run = (
                value <= 0xFF and
                ((prev_addr is not None and prev_addr == address - 1) or
                 (next_addr is not None and next_addr == address + 1))
            )
            size = 1 if is_byte_run else 4
            payload = value.to_bytes(size, byteorder='little', signed=False)

            starts.append(address)
            ends.append(address + size)
            entries.append((address, payload))

        base_address = min(starts)
        image_size = max(ends) - base_address
        image = bytearray(image_size)

        for address, payload in entries:
            start = address - base_address
            image[start:start + len(payload)] = payload

        return base_address, bytes(image)

    def _write_elf32_riscv(self, filename):
        """Write output as an ELF32 little-endian RISC-V executable."""
        base_address, image = self._build_memory_image()
        if not image:
            raise ValueError("No output to write. Run assemble() first.")

        # ELF layout
        elf_header_size = 52
        program_header_size = 32
        section_header_size = 40
        p_offset = elf_header_size + program_header_size
        text_offset = p_offset
        text_size = len(image)

        shstrtab = b"\x00.text\x00.shstrtab\x00"
        shstrtab_offset = text_offset + text_size
        shoff = shstrtab_offset + len(shstrtab)
        section_count = 3

        # e_ident
        e_ident = bytearray(16)
        e_ident[0:4] = b"\x7fELF"  # Magic
        e_ident[4] = 1  # ELFCLASS32
        e_ident[5] = 1  # ELFDATA2LSB
        e_ident[6] = 1  # EV_CURRENT
        e_ident[7] = 0  # ELFOSABI_NONE

        # ELF header (ELF32)
        elf_header = struct.pack(
            "<16sHHIIIIIHHHHHH",
            bytes(e_ident),
            2,                  # e_type = ET_EXEC
            243,                # e_machine = EM_RISCV
            1,                  # e_version = EV_CURRENT
            self.text_address,  # e_entry
            elf_header_size,    # e_phoff
            shoff,              # e_shoff
            0,                  # e_flags
            elf_header_size,    # e_ehsize
            program_header_size,  # e_phentsize
            1,                  # e_phnum
            section_header_size,  # e_shentsize
            section_count,      # e_shnum
            2,                  # e_shstrndx (.shstrtab)
        )

        # Program header (PT_LOAD)
        # Note: p_vaddr must be congruent to p_offset modulo p_align.
        # Using 4 keeps the file compact and satisfies loader checks.
        program_header = struct.pack(
            "<IIIIIIII",
            1,                  # p_type = PT_LOAD
            text_offset,        # p_offset
            base_address,       # p_vaddr
            base_address,       # p_paddr
            text_size,          # p_filesz
            text_size,          # p_memsz
            0x7,                # p_flags = PF_R | PF_W | PF_X
            0x4,                # p_align
        )

        # Section headers: NULL, .text, .shstrtab
        sh_null = struct.pack("<IIIIIIIIII", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        sh_text = struct.pack(
            "<IIIIIIIIII",
            1,              # sh_name = ".text"
            1,              # sh_type = SHT_PROGBITS
            0x6,            # sh_flags = SHF_ALLOC | SHF_EXECINSTR
            base_address,   # sh_addr
            text_offset,    # sh_offset
            text_size,      # sh_size
            0,              # sh_link
            0,              # sh_info
            4,              # sh_addralign
            0,              # sh_entsize
        )
        sh_shstrtab = struct.pack(
            "<IIIIIIIIII",
            7,                  # sh_name = ".shstrtab"
            3,                  # sh_type = SHT_STRTAB
            0,                  # sh_flags
            0,                  # sh_addr
            shstrtab_offset,    # sh_offset
            len(shstrtab),      # sh_size
            0,                  # sh_link
            0,                  # sh_info
            1,                  # sh_addralign
            0,                  # sh_entsize
        )

        with open(filename, "wb") as f:
            f.write(elf_header)
            f.write(program_header)
            f.write(image)
            f.write(shstrtab)
            f.write(sh_null)
            f.write(sh_text)
            f.write(sh_shstrtab)

    def write_object_file(self, filename, format='hex'):
        """
        Write object code to file
        
        Args:
            filename: Output filename
            format: Output format ('hex', 'binary', 'verilog', 'elf')
        """
        if not self.output:
            raise ValueError("No output to write. Run assemble() first.")

        if format == 'elf':
            self._write_elf32_riscv(filename)
            return

        file_mode = 'wb' if format == 'binary' else 'w'
        with open(filename, file_mode) as f:
            if format == 'hex':
                for address, value in self.output:
                    f.write(f"{address:08X}: {value:08X}\n")
            elif format == 'verilog':
                f.write("// Machine code output\n")
                f.write("// Format: address: instruction\n")
                for address, value in self.output:
                    f.write(f"32'h{value:08X}, // 0x{address:08X}\n")
            elif format == 'binary':
                # Write as binary (little-endian)
                for address, value in self.output:
                    bytes_val = value.to_bytes(4, byteorder='little')
                    f.write(bytes_val)
    
    def print_symbol_table(self):
        """Print symbol table"""
        print(self.symbol_table)
    
    def print_output(self):
        """Print assembled output"""
        print("Assembled Output:")
        print("-" * 50)
        print(f"{'Address':<12} {'Machine Code':<12} {'Binary'}")
        print("-" * 50)
        for address, value in self.output:
            binary = format(value, '032b')
            print(f"0x{address:08X}   0x{value:08X}   {binary}")
