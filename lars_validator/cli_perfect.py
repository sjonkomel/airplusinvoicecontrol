#!/usr/bin/env python3
"""
Perfect CLI for Your LARS File Format
======================================

Command-line interface using the perfect configuration based on your exact specifications.

Usage:
    python cli_perfect.py validate yourfile.lrs
    python cli_perfect.py info yourfile.lrs
    python cli_perfect.py analyze300 yourfile.lrs
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from validator_perfect import PerfectLARSValidator, validate_perfect_lrs_file


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
    validator = PerfectLARSValidator()
    
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
        
        # Print 300 analysis if verbose
        if args.verbose:
            validator.print_300_analysis(lars_file)
        
        return 0 if summary.get('total_errors', 0) == 0 else 1
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_info(args):
    """Handle info command"""
    validator = PerfectLARSValidator()
    
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
        print(f"Has Header (200): {'Yes' if summary.get('has_header') else 'No'}")
        print(f"Has Footer (700): {'Yes' if summary.get('has_footer') else 'No'}")
        
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
        
        # Show sample 300 records
        if args.verbose:
            print(f"\nSample 300 Records:")
            validator.print_300_analysis(lars_file)
        
        return 0
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_analyze300(args):
    """Analyze 300 records specifically"""
    validator = PerfectLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        lars_file = validator.parse_file(args.file)
        validator.validate_file(lars_file)
        validator.print_300_analysis(lars_file)
        
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
        description='Perfect LARS File Validator - CLI based on your exact specifications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cli_perfect.py validate yourfile.lrs
  cli_perfect.py validate yourfile.lrs --verbose
  cli_perfect.py info yourfile.lrs
  cli_perfect.py analyze300 yourfile.lrs

Supported Record Types (3 digits):
  200 - File header
  201 - Header line 1
  202 - Header line 2
  300 - Main transaction record (PERFECT CONFIGURATION)
  301 - Transaction continuation
  400 - Flight/ticket information
  590 - Additional transaction details
  700 - File footer

Field Positions for 300 (Based on Your Specifications):
  0-3:   LARS-SATZ-ART (Record type - 300)
  3-5:   LARS-POS-SN (Sequence No - 2 digits, always "00")
  5-10:  LARS-LFD-POS (Item no. - 5 digits)
  10-18: LARS-VERK-DAT (Sales date - 8 digits, YYYYMMDD)
  18-26: LARS-VERARB-DAT (Processing date - 8 digits, YYYYMMDD)
  26-45: LARS-KA-NR (Card no. - 19 digits)
  45-46: LARS-S-H-POS (Debit/credit booking - 1 digit)
  46-47: LARS-POS-ART (Billing/charging item - 1 digit)
  47-50: LARS-VERK-WAEHR (Sales currency - 3 digits)
  50-51: LARS-VERK-NK (Decimal places - 1 digit)
  51-66: LARS-NETTO-BETRAG (Sales amount Net - 15 digits)
  66-75: LARS-MWST-SATZ (VAT rate - 9 digits)
  75-84: LARS-MWST-BETRAG (VAT amount - 9 digits)
  84-91: LARS-VERK-ABR-KURS (Conversion rate - 7 digits)
  91-93: LARS-VERK-ABR-KURS-NK (Decimal places for conversion rate - 2 digits)
  93-108: LARS-BRUTTO-BETRAG (Gross invoice amount - 15 digits)
  108-117: LARS-ZV-BETRAG (Amount for addnl. insurance - 9 digits)
  117-132: LARS-POS-BETRAG (Total amount for item - 15 digits)
  132-162: LARS-NAME (Customer - 30 characters)
  162-164: LARS-HK (Transaction type - 2 characters)
  164-177: LARS-TC-NR (Reference number - 13 characters)
  177-179: LARS-400-COUNT (400 counter - 2 digits)
  179-181: LARS-5XX-COUNT (5xx counter - 2 digits)
  181-183: LARS-600-COUNT (600 counter - 2 digits)
  183-184: LARS-FAKTURA (FAKTURA check identifier - 1 digit)
  184-185: LARS-BENUTZER (User check identifier - 1 digit)
  185-400: LARS-FILLER-300-00 (Filler - 215 characters)
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
    
    # Analyze 300 records
    analyze_parser = subparsers.add_parser('analyze300', help='Analyze 300 records')
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
