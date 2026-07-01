#!/usr/bin/env python3
"""
Simple CLI for Analyzing Your LARS File Structure
==================================================

This CLI helps you analyze the structure of your LARS files
so we can create the correct field definitions.

Usage:
    python cli_simple.py analyze yourfile.lrs
    python cli_simple.py info yourfile.lrs
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from validator_simple import SimpleLARSValidator, analyze_lrs_file


def print_colored(text: str, color: str = None):
    """Print colored text to console"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
    }
    
    reset = '\033[0m'
    
    if color and color in colors:
        print(f"{colors[color]}{text}{reset}")
    else:
        print(text)


def cmd_analyze(args):
    """Analyze file structure"""
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        analyze_lrs_file(args.file, args.lines)
        return 0
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_info(args):
    """Show basic file info"""
    validator = SimpleLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        lars_file = validator.parse_file(args.file)
        errors = validator.validate_file(lars_file)
        summary = validator.get_summary(lars_file)
        
        print(f"File: {args.file}")
        print(f"Total Records: {summary.get('total_records', 0)}")
        print(f"Has Header (20000): {'Yes' if summary.get('has_header') else 'No'}")
        print(f"Has Footer (70000): {'Yes' if summary.get('has_footer') else 'No'}")
        
        print(f"\nRecord Types:")
        for record_type, count in sorted(summary.get('record_types', {}).items()):
            print(f"  Type {record_type}: {count} records")
        
        if args.verbose:
            print(f"\nValidation Errors: {summary.get('total_errors', 0)}")
            for error in lars_file.validation_errors:
                print(f"  Line {error.line_number}: {error.message}")
        
        return 0
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Simple LARS File Analyzer - Analyze file structure to determine field positions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cli_simple.py analyze yourfile.lrs
  cli_simple.py analyze yourfile.lrs --lines 5
  cli_simple.py info yourfile.lrs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze file structure')
    analyze_parser.add_argument('file', help='LRS file to analyze')
    analyze_parser.add_argument('-l', '--lines', type=int, default=10, help='Number of lines to analyze')
    analyze_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show file information')
    info_parser.add_argument('file', help='LRS file to analyze')
    info_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'info':
        return cmd_info(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
