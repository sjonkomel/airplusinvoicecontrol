#!/usr/bin/env python3
"""
CLI for Corrected LARS Validator
=================================

Command-line interface using the corrected field definitions for your actual LARS format.

Usage:
    python cli_corrected.py validate yourfile.lrs
    python cli_corrected.py info yourfile.lrs
    python cli_corrected.py analyze300 yourfile.lrs
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from validator_corrected import CorrectedLARSValidator, validate_corrected_lrs_file


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


def cmd_validate(args):
    """Handle validate command"""
    validator = CorrectedLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        # Parse the file
        print(f"Parsing {args.file}...")
        lars_file = validator.parse_file(args.file)
        
        # Validate the file
        print(f"Validating {args.file}...")
        errors = validator.validate_file(lars_file)
        
        # Print summary
        summary = validator.get_summary(lars_file)
        print_summary(summary)
        
        # Print record type breakdown
        print(f"\nRecord Type Breakdown:")
        for record_type, count in sorted(summary.get('record_types', {}).items()):
            print(f"  Type {record_type}: {count} records")
        
        # Print errors if any
        if errors:
            print_colored(f"\nVALIDATION ERRORS ({len(errors)} total):", 'red')
            print("-" * 80)
            print(f"{'Line':>6} | {'Severity':<8} | {'Type':<20} | {'Field':<25} | Message")
            print("-" * 80)
            
            for error in errors:
                severity_colors = {
                    'critical': 'red',
                    'error': 'red', 
                    'warning': 'yellow',
                    'info': 'blue'
                }
                color = severity_colors.get(error.severity.value, None)
                fixable = " [AUTO-FIX]" if error.can_auto_fix else ""
                
                print_colored(
                    f"  Line {error.line_number:4d} | {error.severity.value.upper():8s} | {error.error_type:20s} | {error.field_name:25s} | {error.message}{fixable}",
                    color
                )
        else:
            print_colored("\nNo validation errors found!", 'green')
        
        # Print 30000 analysis if verbose
        if args.verbose:
            validator.print_30000_analysis(lars_file)
        
        return 0 if summary.get('total_errors', 0) == 0 else 1
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_info(args):
    """Handle info command"""
    validator = CorrectedLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        # Parse the file
        print(f"Parsing {args.file}...")
        lars_file = validator.parse_file(args.file)
        
        # Validate
        errors = validator.validate_file(lars_file)
        summary = validator.get_summary(lars_file)
        
        print(f"File: {args.file}")
        print(f"Total Records: {summary.get('total_records', 0)}")
        print(f"Valid Records: {summary.get('valid_records', 0)}")
        print(f"Invalid Records: {summary.get('invalid_records', 0)}")
        print(f"Has Header (20000): {'Yes' if summary.get('has_header') else 'No'}")
        print(f"Has Footer (70000): {'Yes' if summary.get('has_footer') else 'No'}")
        
        print(f"\nRecord Types:")
        for record_type, count in sorted(summary.get('record_types', {}).items()):
            print(f"  Type {record_type}: {count} records")
        
        # Show header info
        if lars_file.header:
            print(f"\nHeader Information:")
            for key, value in lars_file.header.items():
                print(f"  {key}: {value}")
        
        # Show footer info
        if lars_file.footer:
            print(f"\nFooter Information:")
            for key, value in lars_file.footer.items():
                print(f"  {key}: {value}")
        
        # Show sample 30000 records
        if args.verbose:
            print(f"\nSample 30000 Records:")
            validator.print_30000_analysis(lars_file)
        
        return 0
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_analyze300(args):
    """Analyze 30000 records specifically"""
    validator = CorrectedLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        lars_file = validator.parse_file(args.file)
        validator.validate_file(lars_file)
        validator.print_30000_analysis(lars_file)
        
        return 0
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        return 1


def print_summary(summary: dict):
    """Print validation summary"""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"Total Records:     {summary.get('total_records', 0)}")
    print(f"Valid Records:     {summary.get('valid_records', 0)}")
    print(f"Invalid Records:   {summary.get('invalid_records', 0)}")
    print(f"Total Errors:      {summary.get('total_errors', 0)}")
    
    errors_by_severity = summary.get('errors_by_severity', {})
    print(f"  Critical:        {errors_by_severity.get('critical', 0)}")
    print(f"  Errors:          {errors_by_severity.get('error', 0)}")
    print(f"  Warnings:        {errors_by_severity.get('warning', 0)}")
    print(f"  Info:            {errors_by_severity.get('info', 0)}")
    
    print(f"Auto-fixable:     {summary.get('auto_fixable_errors', 0)}")
    print(f"Has Header:       {'Yes' if summary.get('has_header') else 'No'}")
    print(f"Has Footer:       {'Yes' if summary.get('has_footer') else 'No'}")
    
    total_errors = summary.get('total_errors', 0)
    if total_errors == 0:
        print_colored("\nFile Status: PASS", 'green')
    else:
        print_colored("\nFile Status: FAIL", 'red')
    
    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Corrected LARS File Validator - CLI for your actual format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cli_corrected.py validate yourfile.lrs
  cli_corrected.py validate yourfile.lrs --verbose
  cli_corrected.py info yourfile.lrs
  cli_corrected.py analyze300 yourfile.lrs

Supported Record Types:
  20000 - File header
  20001 - Header line 1
  20002 - Header line 2
  30000 - Main transaction record (CORRECTED)
  30001 - Transaction continuation
  40000 - Flight/ticket information
  59000 - Additional transaction details
  70000 - File footer

Field Positions for 30000:
  0-5:   RECORD_TYPE
  5-8:   SEQUENCE_NUMBER
  8-13:  ITEM_NUMBER
  13-21: SALES_DATE (YYYYMMDD)
  21-29: PROCESSING_DATE (YYYYMMDD)
  29-48: CARD_NUMBER
  48-50: CARD_TYPE
  50-65: NET_AMOUNT
  65-73: VAT_RATE
  73-81: VAT_AMOUNT
  81-89: CONVERSION_RATE
  89-91: CONVERSION_DECIMALS
  91-106: GROSS_AMOUNT
  106-115: INSURANCE_AMOUNT
  115-130: TOTAL_AMOUNT
  130+:  CUSTOMER_NAME
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a LRS file')
    validate_parser.add_argument('file', help='LRS file to validate')
    validate_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show file information')
    info_parser.add_argument('file', help='LRS file to analyze')
    info_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Analyze 30000 records
    analyze_parser = subparsers.add_parser('analyze300', help='Analyze 30000 records')
    analyze_parser.add_argument('file', help='LRS file to analyze')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'info':
        return cmd_info(args)
    elif args.command == 'analyze300':
        return cmd_analyze300(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
