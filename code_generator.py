"""
Machine Code Generator
This module generates machine code from parsed assembly instructions.
"""

class CodeGenerator:
    """Generates machine code from parsed instructions"""
    
    def __init__(self, opcode_table, symbol_table):
        """
        Initialize code generator
        
        Args:
            opcode_table: OpcodeTable instance
            symbol_table: SymbolTable instance
        """
        self.opcode_table = opcode_table
        self.symbol_table = symbol_table
    
    def generate_instruction(self, parsed_line, current_address):
        """
        Generate machine code for an instruction
        
        Args:
            parsed_line: Parsed instruction line (from parser)
            current_address: Current address in memory
            
        Returns:
            Machine code as integer (32-bit)
        """
        mnemonic = parsed_line['mnemonic']
        operands = parsed_line.get('operands', [])
        inst_info = self.opcode_table.get_instruction_info(mnemonic)
        
        # Store mnemonic in inst_info for system instructions
        if inst_info:
            inst_info['mnemonic'] = mnemonic
        
        if not inst_info:
            raise ValueError(f"Unknown instruction: {mnemonic}")
        
        inst_type = inst_info['type']
        
        if inst_type == 'R':
            return self._generate_r_type(inst_info, operands)
        elif inst_type == 'I':
            return self._generate_i_type(inst_info, operands, current_address, mnemonic)
        elif inst_type == 'S':
            return self._generate_s_type(inst_info, operands)
        elif inst_type == 'B':
            return self._generate_b_type(inst_info, operands, current_address)
        elif inst_type == 'U':
            return self._generate_u_type(inst_info, operands)
        elif inst_type == 'J':
            return self._generate_j_type(inst_info, operands, current_address)
        else:
            raise ValueError(f"Unsupported instruction type: {inst_type}")
    
    def _generate_r_type(self, inst_info, operands):
        """Generate R-type instruction encoding"""
        if len(operands) != 3:
            raise ValueError(f"R-type instruction requires 3 operands, got {len(operands)}")
        
        rd = self._get_register_number(operands[0])
        rs1 = self._get_register_number(operands[1])
        rs2 = self._get_register_number(operands[2])
        
        opcode = inst_info['opcode']
        funct3 = inst_info['funct3']
        funct7 = inst_info.get('funct7', 0)
        
        # R-type format: funct7(7) | rs2(5) | rs1(5) | funct3(3) | rd(5) | opcode(7)
        instruction = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        
        return instruction & 0xFFFFFFFF
    
    def _generate_i_type(self, inst_info, operands, current_address, mnemonic=''):
        """Generate I-type instruction encoding"""
        opcode = inst_info['opcode']
        funct3 = inst_info['funct3']
        
        # Handle different I-type instructions
        if inst_info['opcode'] == 0x03:  # Load instructions
            if len(operands) != 2:
                raise ValueError(f"Load instruction requires 2 operands, got {len(operands)}")
            
            rd = self._get_register_number(operands[0])
            offset_op = operands[1]
            
            if offset_op['type'] == 'register_offset':
                reg_op = {'type': 'register', 'value': offset_op['register']}
                rs1 = self._get_register_number(reg_op)
                imm = self._sign_extend(offset_op['offset'], 12)
            else:
                raise ValueError("Load instruction requires offset(register) format")
        
        elif inst_info['opcode'] == 0x67:  # JALR
            if len(operands) != 2:
                raise ValueError(f"JALR requires 2 operands, got {len(operands)}")
            
            rd = self._get_register_number(operands[0])
            offset_op = operands[1]
            
            if offset_op['type'] == 'register_offset':
                reg_op = {'type': 'register', 'value': offset_op['register']}
                rs1 = self._get_register_number(reg_op)
                imm = self._sign_extend(offset_op['offset'], 12)
            elif offset_op['type'] == 'register':
                rs1 = self._get_register_number(offset_op)
                imm = 0
            else:
                raise ValueError("JALR requires register or offset(register) format")
        
        elif inst_info['opcode'] == 0x73:  # System instructions (ecall, ebreak)
            # System instructions: imm=0 for ecall, imm=1 for ebreak
            # rs1=0, funct3=0, rd=0
            if mnemonic.lower() == 'ebreak':
                imm = 1  # ebreak
            else:
                imm = 0  # ecall (default)
            rs1 = 0
            rd = 0
        
        else:  # Arithmetic/logic immediate instructions
            if len(operands) != 3:
                raise ValueError(f"I-type instruction requires 3 operands, got {len(operands)}")
            
            rd = self._get_register_number(operands[0])
            rs1 = self._get_register_number(operands[1])
            imm_op = operands[2]
            
            if imm_op['type'] == 'immediate':
                imm = self._sign_extend(imm_op['value'], 12)
            elif imm_op['type'] == 'label':
                # Forward reference - will be resolved in second pass
                target_addr = self.symbol_table.get_address(imm_op['value'])
                if target_addr is None:
                    raise ValueError(f"Undefined label: {imm_op['value']}")
                imm = self._sign_extend(target_addr - current_address, 12)
            else:
                raise ValueError(f"Expected immediate or label, got {imm_op['type']}")
        
        # I-type format: imm[11:0](12) | rs1(5) | funct3(3) | rd(5) | opcode(7)
        instruction = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        
        # Special handling for shift instructions (slli, srli, srai)
        if inst_info.get('funct7') is not None:
            funct7 = inst_info['funct7']
            instruction = (funct7 << 25) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
            # For shift, imm is in rs2 field (lower 5 bits)
            shamt = imm & 0x1F
            instruction = (funct7 << 25) | (shamt << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
        
        return instruction & 0xFFFFFFFF
    
    def _generate_s_type(self, inst_info, operands):
        """Generate S-type instruction encoding"""
        if len(operands) != 2:
            raise ValueError(f"S-type instruction requires 2 operands, got {len(operands)}")
        
        rs2 = self._get_register_number(operands[0])
        offset_op = operands[1]
        
        if offset_op['type'] == 'register_offset':
            reg_op = {'type': 'register', 'value': offset_op['register']}
            rs1 = self._get_register_number(reg_op)
            imm = self._sign_extend(offset_op['offset'], 12)
        else:
            raise ValueError("Store instruction requires offset(register) format")
        
        opcode = inst_info['opcode']
        funct3 = inst_info['funct3']
        
        # S-type format: imm[11:5](7) | rs2(5) | rs1(5) | funct3(3) | imm[4:0](5) | opcode(7)
        imm_11_5 = (imm >> 5) & 0x7F
        imm_4_0 = imm & 0x1F
        
        instruction = (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode
        
        return instruction & 0xFFFFFFFF
    
    def _generate_b_type(self, inst_info, operands, current_address):
        """Generate B-type instruction encoding"""
        if len(operands) != 3:
            raise ValueError(f"B-type instruction requires 3 operands, got {len(operands)}")
        
        rs1 = self._get_register_number(operands[0])
        rs2 = self._get_register_number(operands[1])
        target_op = operands[2]
        
        if target_op['type'] == 'immediate':
            offset = target_op['value']
        elif target_op['type'] == 'label':
            target_addr = self.symbol_table.get_address(target_op['value'])
            if target_addr is None:
                raise ValueError(f"Undefined label: {target_op['value']}")
            offset = target_addr - current_address
        else:
            raise ValueError(f"Expected immediate or label, got {target_op['type']}")
        
        # Check if offset fits in 13-bit signed range
        if offset < -4096 or offset > 4094 or offset % 2 != 0:
            raise ValueError(f"Branch offset out of range or not aligned: {offset}")
        
        opcode = inst_info['opcode']
        funct3 = inst_info['funct3']
        
        # B-type format: imm[12|10:5](7) | rs2(5) | rs1(5) | funct3(3) | imm[4:1|11](5) | opcode(7)
        imm = self._sign_extend(offset, 13)
        imm_12 = (imm >> 12) & 0x1
        imm_11 = (imm >> 11) & 0x1
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0xF
        
        instruction = (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_11 << 11) | (imm_4_1 << 7) | opcode
        
        return instruction & 0xFFFFFFFF
    
    def _generate_u_type(self, inst_info, operands):
        """Generate U-type instruction encoding"""
        if len(operands) != 2:
            raise ValueError(f"U-type instruction requires 2 operands, got {len(operands)}")
        
        rd = self._get_register_number(operands[0])
        imm_op = operands[1]
        
        if imm_op['type'] == 'immediate':
            imm = imm_op['value']
        elif imm_op['type'] == 'label':
            target_addr = self.symbol_table.get_address(imm_op['value'])
            if target_addr is None:
                raise ValueError(f"Undefined label: {imm_op['value']}")
            imm = target_addr
        else:
            raise ValueError(f"Expected immediate or label, got {imm_op['type']}")
        
        # U-type uses upper 20 bits
        imm_31_12 = (imm >> 12) & 0xFFFFF
        
        opcode = inst_info['opcode']
        
        # U-type format: imm[31:12](20) | rd(5) | opcode(7)
        instruction = (imm_31_12 << 12) | (rd << 7) | opcode
        
        return instruction & 0xFFFFFFFF
    
    def _generate_j_type(self, inst_info, operands, current_address):
        """Generate J-type instruction encoding"""
        # JAL can have 1 or 2 operands: jal label or jal rd, label
        if len(operands) == 1:
            # Only label specified, use ra (x1) as default
            rd = 1  # ra register
            target_op = operands[0]
        elif len(operands) == 2:
            # Register and label specified
            rd = self._get_register_number(operands[0])
            target_op = operands[1]
        else:
            raise ValueError(f"J-type instruction requires 1 or 2 operands, got {len(operands)}")
        
        if target_op['type'] == 'immediate':
            offset = target_op['value']
        elif target_op['type'] == 'label':
            target_addr = self.symbol_table.get_address(target_op['value'])
            if target_addr is None:
                raise ValueError(f"Undefined label: {target_op['value']}")
            offset = target_addr - current_address
        else:
            raise ValueError(f"Expected immediate or label, got {target_op['type']}")
        
        # Check if offset fits in 21-bit signed range
        if offset < -1048576 or offset > 1048574 or offset % 2 != 0:
            raise ValueError(f"Jump offset out of range or not aligned: {offset}")
        
        opcode = inst_info['opcode']
        
        # J-type format: imm[20|10:1|11|19:12](20) | rd(5) | opcode(7)
        imm = self._sign_extend(offset, 21)
        imm_20 = (imm >> 20) & 0x1
        imm_19_12 = (imm >> 12) & 0xFF
        imm_11 = (imm >> 11) & 0x1
        imm_10_1 = (imm >> 1) & 0x3FF
        
        instruction = (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12) | (rd << 7) | opcode
        
        return instruction & 0xFFFFFFFF
    
    def _get_register_number(self, operand):
        """Get register number from operand"""
        if operand['type'] == 'register':
            reg_num = self.opcode_table.get_register_number(operand['value'])
            if reg_num is None:
                raise ValueError(f"Invalid register: {operand['value']}")
            return reg_num
        else:
            raise ValueError(f"Expected register, got {operand['type']}")
    
    def _sign_extend(self, value, bits):
        """Sign extend a value to specified number of bits"""
        sign_bit = 1 << (bits - 1)
        mask = (1 << bits) - 1
        value = value & mask  # Keep only lower bits
        if value & sign_bit:
            # Negative number - extend sign bit
            return value | (~mask)
        return value
