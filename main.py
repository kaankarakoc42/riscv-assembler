"""
Main entry point for the RISC-V Assembler
"""

import sys
import argparse
from assembler import Assembler

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='RISC-V RV32I Assembler for PicoRV processor'
    )
    parser.add_argument('input_file', help='Input assembly file')
    parser.add_argument('-o', '--output', help='Output file (default depends on format)')
    parser.add_argument('-f', '--format', choices=['hex', 'verilog', 'binary', 'elf'],
                       default='elf', help='Output format (default: elf)')
    parser.add_argument('-s', '--symbols', action='store_true',
                       help='Print symbol table')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Create assembler
    assembler = Assembler()
    
    # Assemble file
    if args.verbose:
        print(f"Assembling {args.input_file}...")
    
    result = assembler.assemble_file(args.input_file)
    
    # Check for errors
    if not result['success']:
        print("Assembly failed with errors:")
        for error in result['errors']:
            print(f"  ERROR: {error}")
        sys.exit(1)
    
    # Print warnings
    if result['warnings']:
        print("Warnings:")
        for warning in result['warnings']:
            print(f"  WARNING: {warning}")
    
    # Print symbol table if requested
    if args.symbols:
        assembler.print_symbol_table()
        print()
    
    # Print output if verbose
    if args.verbose:
        assembler.print_output()
        print()
    
    # Write output file
    if args.output:
        output_file = args.output
    else:
        ext_map = {
            'hex': '.hex',
            'verilog': '.v',
            'binary': '.bin',
            'elf': '.elf',
        }
        output_file = args.input_file.rsplit('.', 1)[0] + ext_map[args.format]
    
    try:
        assembler.write_object_file(output_file, format=args.format)
        print(f"Assembly successful! Output written to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
