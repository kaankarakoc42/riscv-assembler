"""
Symbol Table for Assembler
This module implements the symbol table data structure to store labels and their addresses.
"""

class SymbolTable:
    """Symbol table to store labels and their addresses"""
    
    def __init__(self):
        """Initialize an empty symbol table"""
        self.symbols = {}  # Dictionary: label -> address
        self.forward_refs = {}  # Dictionary: label -> list of (address, instruction_type)
    
    def add_symbol(self, label, address):
        """
        Add a symbol (label) with its address
        
        Args:
            label: Label name (string)
            address: Address of the label (integer)
        """
        if label in self.symbols:
            raise ValueError(f"Duplicate label definition: {label}")
        self.symbols[label] = address
        
        # Resolve forward references if any
        if label in self.forward_refs:
            for ref_addr, inst_type in self.forward_refs[label]:
                # Store reference for later resolution
                pass
            del self.forward_refs[label]
    
    def get_address(self, label):
        """
        Get the address of a label
        
        Args:
            label: Label name (string)
            
        Returns:
            Address (integer) if found, None otherwise
        """
        return self.symbols.get(label)
    
    def has_symbol(self, label):
        """Check if symbol exists in table"""
        return label in self.symbols
    
    def add_forward_ref(self, label, address, inst_type):
        """
        Add a forward reference (label used before definition)
        
        Args:
            label: Label name (string)
            address: Address where label is referenced (integer)
            inst_type: Type of instruction using the label (string)
        """
        if label not in self.forward_refs:
            self.forward_refs[label] = []
        self.forward_refs[label].append((address, inst_type))
    
    def get_forward_refs(self):
        """Get all unresolved forward references"""
        return self.forward_refs
    
    def get_all_symbols(self):
        """Get all symbols in the table"""
        return self.symbols.copy()
    
    def clear(self):
        """Clear the symbol table"""
        self.symbols.clear()
        self.forward_refs.clear()
    
    def __str__(self):
        """String representation of symbol table"""
        result = "Symbol Table:\n"
        result += "-" * 40 + "\n"
        result += f"{'Label':<20} {'Address':<10}\n"
        result += "-" * 40 + "\n"
        for label, addr in sorted(self.symbols.items()):
            result += f"{label:<20} 0x{addr:08X}\n"
        if self.forward_refs:
            result += "\nUnresolved Forward References:\n"
            for label, refs in self.forward_refs.items():
                result += f"  {label}: {len(refs)} references\n"
        return result
