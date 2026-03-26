"""
Directive Handler
This module handles assembler directives like .data, .text, .word, .byte, .org, .end
"""

class DirectiveHandler:
    """Handles assembler directives"""
    
    def __init__(self):
        """Initialize directive handler"""
        self.current_section = None  # 'data' or 'text'
        self.org_address = None  # Current origin address
        self.data_segment = []  # Data segment content
        self.text_segment = []  # Text segment content
    
    def handle_directive(self, directive, args, current_address):
        """
        Handle an assembler directive
        
        Args:
            directive: Directive name (string)
            args: Directive arguments (list)
            current_address: Current address in memory
            
        Returns:
            Dictionary with directive information:
            {
                'type': directive type,
                'address': address after directive,
                'data': data bytes (for .word, .byte),
                'section': current section
            }
        """
        directive = directive.lower()
        
        if directive == 'data':
            self.current_section = 'data'
            return {'type': 'section', 'section': 'data', 'address': current_address}
        
        elif directive == 'text':
            self.current_section = 'text'
            return {'type': 'section', 'section': 'text', 'address': current_address}
        
        elif directive == 'org':
            if not args:
                raise ValueError(".org directive requires an address argument")
            self.org_address = args[0]
            return {'type': 'org', 'address': args[0]}
        
        elif directive == 'word':
            if not args:
                raise ValueError(".word directive requires at least one value")
            
            words = []
            for arg in args:
                if isinstance(arg, int):
                    words.append(arg & 0xFFFFFFFF)
                else:
                    raise ValueError(f"Invalid value for .word: {arg}")
            
            # Each word is 4 bytes
            return {'type': 'data', 'data': words, 'size': len(words) * 4, 'address': current_address}
        
        elif directive == 'byte':
            if not args:
                raise ValueError(".byte directive requires at least one value")
            
            bytes_list = []
            for arg in args:
                if isinstance(arg, int):
                    bytes_list.append(arg & 0xFF)
                else:
                    raise ValueError(f"Invalid value for .byte: {arg}")
            
            return {'type': 'data', 'data': bytes_list, 'size': len(bytes_list), 'address': current_address}
        
        elif directive == 'end':
            return {'type': 'end', 'address': current_address}
        
        else:
            raise ValueError(f"Unknown directive: .{directive}")
    
    def get_current_section(self):
        """Get current section"""
        return self.current_section
    
    def get_org_address(self):
        """Get current origin address"""
        return self.org_address
    
    def reset(self):
        """Reset directive handler state"""
        self.current_section = None
        self.org_address = None
        self.data_segment = []
        self.text_segment = []
