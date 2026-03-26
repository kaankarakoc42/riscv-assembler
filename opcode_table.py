"""
Opcode Table for RV32I Instruction Set
This module contains the opcode definitions and instruction encoding information
for the RISC-V RV32I base instruction set.
"""

class OpcodeTable:
    """Opcode table for RV32I instruction set"""
    
    # RISC-V instruction formats
    R_TYPE = "R"
    I_TYPE = "I"
    S_TYPE = "S"
    B_TYPE = "B"
    U_TYPE = "U"
    J_TYPE = "J"
    
    def __init__(self):
        """Initialize the opcode table with RV32I instructions"""
        self.instructions = {
            # Arithmetic and Logic Instructions (R-type)
            'add': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x0, 'funct7': 0x00},
            'sub': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x0, 'funct7': 0x20},
            'sll': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x1, 'funct7': 0x00},
            'slt': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x2, 'funct7': 0x00},
            'sltu': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x3, 'funct7': 0x00},
            'xor': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x4, 'funct7': 0x00},
            'srl': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x5, 'funct7': 0x00},
            'sra': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x5, 'funct7': 0x20},
            'or': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x6, 'funct7': 0x00},
            'and': {'type': self.R_TYPE, 'opcode': 0x33, 'funct3': 0x7, 'funct7': 0x00},
            
            # Immediate Arithmetic Instructions (I-type)
            'addi': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x0},
            'slti': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x2},
            'sltiu': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x3},
            'xori': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x4},
            'ori': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x6},
            'andi': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x7},
            'slli': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x1, 'funct7': 0x00},
            'srli': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x5, 'funct7': 0x00},
            'srai': {'type': self.I_TYPE, 'opcode': 0x13, 'funct3': 0x5, 'funct7': 0x20},
            
            # Load Instructions (I-type)
            'lb': {'type': self.I_TYPE, 'opcode': 0x03, 'funct3': 0x0},
            'lh': {'type': self.I_TYPE, 'opcode': 0x03, 'funct3': 0x1},
            'lw': {'type': self.I_TYPE, 'opcode': 0x03, 'funct3': 0x2},
            'lbu': {'type': self.I_TYPE, 'opcode': 0x03, 'funct3': 0x4},
            'lhu': {'type': self.I_TYPE, 'opcode': 0x03, 'funct3': 0x5},
            
            # Store Instructions (S-type)
            'sb': {'type': self.S_TYPE, 'opcode': 0x23, 'funct3': 0x0},
            'sh': {'type': self.S_TYPE, 'opcode': 0x23, 'funct3': 0x1},
            'sw': {'type': self.S_TYPE, 'opcode': 0x23, 'funct3': 0x2},
            
            # Branch Instructions (B-type)
            'beq': {'type': self.B_TYPE, 'opcode': 0x63, 'funct3': 0x0},
            'bne': {'type': self.B_TYPE, 'opcode': 0x63, 'funct3': 0x1},
            'blt': {'type': self.B_TYPE, 'opcode': 0x63, 'funct3': 0x4},
            'bge': {'type': self.B_TYPE, 'opcode': 0x63, 'funct3': 0x5},
            'bltu': {'type': self.B_TYPE, 'opcode': 0x63, 'funct3': 0x6},
            'bgeu': {'type': self.B_TYPE, 'opcode': 0x63, 'funct3': 0x7},
            
            # Jump Instructions
            'jal': {'type': self.J_TYPE, 'opcode': 0x6f},
            'jalr': {'type': self.I_TYPE, 'opcode': 0x67, 'funct3': 0x0},
            
            # Upper Immediate Instructions (U-type)
            'lui': {'type': self.U_TYPE, 'opcode': 0x37},
            'auipc': {'type': self.U_TYPE, 'opcode': 0x17},
            
            # System Instructions (I-type)
            'ecall': {'type': self.I_TYPE, 'opcode': 0x73, 'funct3': 0x0},
            'ebreak': {'type': self.I_TYPE, 'opcode': 0x73, 'funct3': 0x0},
        }
        
        # Register name to number mapping
        self.registers = {
            'zero': 0, 'x0': 0,
            'ra': 1, 'x1': 1,
            'sp': 2, 'x2': 2,
            'gp': 3, 'x3': 3,
            'tp': 4, 'x4': 4,
            't0': 5, 'x5': 5,
            't1': 6, 'x6': 6,
            't2': 7, 'x7': 7,
            's0': 8, 'fp': 8, 'x8': 8,
            's1': 9, 'x9': 9,
            'a0': 10, 'x10': 10,
            'a1': 11, 'x11': 11,
            'a2': 12, 'x12': 12,
            'a3': 13, 'x13': 13,
            'a4': 14, 'x14': 14,
            'a5': 15, 'x15': 15,
            'a6': 16, 'x16': 16,
            'a7': 17, 'x17': 17,
            's2': 18, 'x18': 18,
            's3': 19, 'x19': 19,
            's4': 20, 'x20': 20,
            's5': 21, 'x21': 21,
            's6': 22, 'x22': 22,
            's7': 23, 'x23': 23,
            's8': 24, 'x24': 24,
            's9': 25, 'x25': 25,
            's10': 26, 'x26': 26,
            's11': 27, 'x27': 27,
            't3': 28, 'x28': 28,
            't4': 29, 'x29': 29,
            't5': 30, 'x30': 30,
            't6': 31, 'x31': 31,
        }
    
    def get_instruction_info(self, mnemonic):
        """Get instruction encoding information"""
        return self.instructions.get(mnemonic.lower())
    
    def is_valid_instruction(self, mnemonic):
        """Check if instruction is valid"""
        return mnemonic.lower() in self.instructions
    
    def get_register_number(self, reg_name):
        """Convert register name to register number"""
        return self.registers.get(reg_name.lower())
    
    def is_valid_register(self, reg_name):
        """Check if register name is valid"""
        return reg_name.lower() in self.registers
