"""
Parser for Assembly Instructions
This module parses assembly source code into structured components.
"""

import re

class Parser:
    """Parser for RISC-V assembly instructions"""
    
    def __init__(self):
        """Initialize the parser"""
        # Regular expressions for parsing
        self.label_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:')
        self.directive_pattern = re.compile(r'^\s*\.(\w+)')
        self.instruction_pattern = re.compile(
            r'^\s*([a-zA-Z]+)(?:\s+(.+))?$'
        )
        self.register_pattern = re.compile(r'\b([a-z0-9]+)\b')
        self.comment_pattern = re.compile(r'#.*$')
        
    def parse_line(self, line):
        """
        Parse a single line of assembly code
        
        Args:
            line: Line of assembly code (string)
            
        Returns:
            Dictionary with parsed components:
            {
                'type': 'label', 'instruction', 'directive', 'comment', 'empty',
                'label': label name (if type is 'label'),
                'mnemonic': instruction mnemonic (if type is 'instruction'),
                'operands': list of operands (if type is 'instruction'),
                'directive': directive name (if type is 'directive'),
                'args': directive arguments (if type is 'directive'),
                'original': original line
            }
        """
        # Remove comments
        line = self.comment_pattern.sub('', line).strip()
        
        if not line:
            return {'type': 'empty', 'original': line}
        
        result = {'original': line}
        
        # Check for label
        label_match = self.label_pattern.match(line)
        if label_match:
            result['type'] = 'label'
            result['label'] = label_match.group(1)
            # Remove label from line for further parsing
            line = self.label_pattern.sub('', line).strip()
            if not line:
                return result
        
        # Check for directive
        directive_match = self.directive_pattern.match(line)
        if directive_match:
            result['type'] = 'directive'
            result['directive'] = directive_match.group(1)
            # Extract directive arguments
            args_str = line[directive_match.end():].strip()
            result['args'] = self._parse_directive_args(args_str)
            return result
        
        # Parse instruction
        inst_match = self.instruction_pattern.match(line)
        if inst_match:
            # If we had a label, keep it in result but type is 'instruction'
            if 'label' in result:
                result['type'] = 'instruction'  # Label + instruction on same line
            else:
                result['type'] = 'instruction'
            result['mnemonic'] = inst_match.group(1).lower()
            operands_str = inst_match.group(2)
            if operands_str:
                result['operands'] = self._parse_operands(operands_str.strip())
            else:
                result['operands'] = []  # No operands (e.g., ebreak, ecall)
            return result
        
        # If we have a label but nothing else, return label
        if 'label' in result:
            return result
        
        # Unknown line type
        result['type'] = 'unknown'
        return result
    
    def _parse_operands(self, operands_str):
        """
        Parse instruction operands
        
        Args:
            operands_str: String containing operands
            
        Returns:
            List of parsed operands
        """
        if not operands_str:
            return []
        
        # Split by comma, but handle parentheses for load/store
        operands = []
        current = ""
        paren_depth = 0
        
        for char in operands_str:
            if char == '(':
                paren_depth += 1
                current += char
            elif char == ')':
                paren_depth -= 1
                current += char
            elif char == ',' and paren_depth == 0:
                operands.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            operands.append(current.strip())
        
        # Parse each operand
        parsed_operands = []
        for op in operands:
            parsed_operands.append(self._parse_single_operand(op.strip()))
        
        return parsed_operands
    
    def _parse_single_operand(self, operand):
        """
        Parse a single operand (register, immediate, or label)
        
        Args:
            operand: Operand string
            
        Returns:
            Dictionary with operand information:
            {
                'type': 'register', 'immediate', 'label', 'register_offset',
                'value': register number, immediate value, or label name,
                'offset': offset value (for register_offset type),
                'register': register name (for register_offset type)
            }
        """
        # Check for register with offset: offset(register) or (register)
        offset_match = re.match(r'^(-?\d+)?\(([a-z0-9]+)\)$', operand)
        if offset_match:
            offset_str = offset_match.group(1)
            reg_name = offset_match.group(2)
            offset = int(offset_str) if offset_str else 0
            return {
                'type': 'register_offset',
                'register': reg_name,
                'offset': offset
            }
        
        # Check for immediate value (decimal or hex)
        if operand.startswith('0x') or operand.startswith('0X'):
            try:
                value = int(operand, 16)
                return {'type': 'immediate', 'value': value}
            except ValueError:
                pass
        elif operand.startswith('-') or operand[0].isdigit():
            try:
                value = int(operand, 10)
                return {'type': 'immediate', 'value': value}
            except ValueError:
                pass
        
        # Check if it's a register
        if operand.startswith('x') or operand in ['zero', 'ra', 'sp', 'gp', 'tp', 
                                                   't0', 't1', 't2', 's0', 's1',
                                                   'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7',
                                                   's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11',
                                                   't3', 't4', 't5', 't6', 'fp']:
            return {'type': 'register', 'value': operand}
        
        # Otherwise, assume it's a label
        return {'type': 'label', 'value': operand}
    
    def _parse_directive_args(self, args_str):
        """
        Parse directive arguments
        
        Args:
            args_str: String containing directive arguments
            
        Returns:
            List of parsed arguments
        """
        if not args_str:
            return []
        
        # For .word, .byte: parse comma-separated values
        # For .org: parse single address
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            if arg.startswith('0x') or arg.startswith('0X'):
                try:
                    args.append(int(arg, 16))
                except ValueError:
                    args.append(arg)
            elif arg.startswith('-') or arg[0].isdigit():
                try:
                    args.append(int(arg, 10))
                except ValueError:
                    args.append(arg)
            else:
                args.append(arg)
        
        return args
