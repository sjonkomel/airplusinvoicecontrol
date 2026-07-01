#!/usr/bin/env python3
"""
CLI for Your Actual LARS File Format
====================================

Command-line interface for your actual LARS files with record types:
20000, 20001, 20002, 30000, 30001, 40000, 59000, 70000.

Usage:
    python cli_actual.py validate yourfile.lrs
    python cli_actual.py info yourfile.lrs
    python cli_actual.py export yourfile.lrs --output fixed.lrs
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from validator_actual import ActualLARSValidator, validate_actual_lrs_file


def print_colored(text: str, color: str = None):
    """Print colored text to console"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'underline': '\033[4m',
    }
    
    reset = '\033[0m'
    
    if color and color in colors:
        print(f"{colors[color]}{text}{reset}")
    else:
        print(text)


def cmd_validate(args):
    """Handle validate command"""
    validator = ActualLARSValidator()
    
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
            print_colored("\nVALIDATION ERRORS:", 'red')
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
                
                if error.expected_value:
                    print_colored(f"           | Expected: {error.expected_value}", color)
                if error.actual_value:
                    print_colored(f"           | Actual:   {error.actual_value}", color)
                if error.can_auto_fix and error.suggested_fix:
                    print_colored(f"           | Fix:      {error.suggested_fix}", color)
        
        # Print record details if verbose
        if args.verbose:
            print(f"\nRECORD DETAILS:")
            print("-" * 80)
            for record in lars_file.records:
                status = "VALID" if record.is_valid else "INVALID"
                print(f"Line {record.line_number:4d} | Type {record.record_type:5s} | {status:7s} | {record.original_line[:60]}")
        
        return 0 if summary.get('total_errors', 0) == 0 else 1
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_repair(args):
    """Handle repair command"""
    validator = ActualLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        # Parse the file
        print(f"Parsing {args.file}...")
        lars_file = validator.parse_file(args.file)
        
        # Validate first
        print(f"Validating {args.file}...")
        errors = validator.validate_file(lars_file)
        summary = validator.get_summary(lars_file)
        
        if summary.get('total_errors', 0) == 0:
            print_colored("No errors found. File is already valid.", 'green')
            return 0
        
        print_summary(summary)
        
        # Apply auto-fixes
        print(f"Applying automatic fixes...")
        fixed_file, fixes_applied = validator.apply_auto_fixes(lars_file)
        
        if fixes_applied:
            print_colored(f"\nApplied {len(fixes_applied)} automatic fixes:", 'green')
            for fix in fixes_applied:
                print(f"  {fix}")
        else:
            print_colored("\nNo automatic fixes were applied.", 'yellow')
        
        # Re-validate
        print(f"\nRe-validating...")
        new_errors = validator.validate_file(fixed_file)
        new_summary = validator.get_summary(fixed_file)
        print_summary(new_summary)
        
        # Export if output file specified
        if args.output:
            print(f"Exporting to {args.output}...")
            success = validator.export_file(fixed_file, args.output)
            if success:
                print_colored(f"File exported successfully to {args.output}", 'green')
            else:
                print_colored(f"Failed to export file to {args.output}", 'red')
                return 1
        
        return 0 if new_summary.get('total_errors', 0) == 0 else 1
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_export(args):
    """Handle export command"""
    validator = ActualLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        # Parse the file
        print(f"Parsing {args.file}...")
        lars_file = validator.parse_file(args.file)
        
        # Validate
        print(f"Validating {args.file}...")
        errors = validator.validate_file(lars_file)
        summary = validator.get_summary(lars_file)
        
        print_summary(summary)
        
        # Export
        output_path = args.output or (os.path.splitext(args.file)[0] + "_validated.lrs")
        print(f"Exporting to {output_path}...")
        success = validator.export_file(lars_file, output_path)
        
        if success:
            print_colored(f"File exported successfully to {output_path}", 'green')
            return 0
        else:
            print_colored(f"Failed to export file to {output_path}", 'red')
            return 1
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_info(args):
    """Handle info command"""
    validator = ActualLARSValidator()
    
    if not os.path.exists(args.file):
        print_colored(f"Error: File not found: {args.file}", 'red')
        return 1
    
    try:
        # Parse the file
        print(f"Parsing {args.file}...")
        lars_file = validator.parse_file(args.file)
        
        # Get summary
        summary = validator.get_summary(lars_file)
        
        print(f"File: {args.file}")
        print(f"Total Records: {summary.get('total_records', 0)}")
        print(f"Valid Records: {summary.get('valid_records', 0)}")
        print(f"Invalid Records: {summary.get('invalid_records', 0)}")
        
        # Show record type breakdown
        print(f"\nRecord Types:")
        for record_type, count in sorted(summary.get('record_types', {}).items()):
            print(f"  Type {record_type}: {count} records")
        
        # Show sample records if verbose
        if args.verbose:
            print(f"\nSample Records:")
            for i, record in enumerate(lars_file.records[:5]):
                print(f"  Line {record.line_number}: Type {record.record_type} - {record.original_line[:80]}")
        
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
        
        return 0
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
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
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Actual LARS File Validator - Command Line Interface for your specific format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cli_actual.py validate myfile.lrs
  cli_actual.py validate myfile.lrs --verbose
  cli_actual.py repair myfile.lrs --output fixed.lrs
  cli_actual.py info myfile.lrs
  cli_actual.py export myfile.lrs --output validated.lrs

Supported Record Types:
  20000 - File header
  20001 - Header line 1 (Company info)
  20002 - Header line 2 (Company info)
  30000 - Main transaction record
  30001 - Transaction continuation (Customer info)
  40000 - Flight/ticket information
  59000 - Additional transaction details
  70000 - File footer
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a LRS file')
    validate_parser.add_argument('file', help='LRS file to validate')
    validate_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Repair command
    repair_parser = subparsers.add_parser('repair', help='Repair a LRS file')
    repair_parser.add_argument('file', help='LRS file to repair')
    repair_parser.add_argument('-o', '--output', help='Output file path')
    repair_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export a LRS file')
    export_parser.add_argument('file', help='LRS file to export')
    export_parser.add_argument('-o', '--output', help='Output file path')
    export_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show information about a LRS file')
    info_parser.add_argument('file', help='LRS file to analyze')
    info_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Handle commands
    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'repair':
        return cmd_repair(args)
    elif args.command == 'export':
        return cmd_export(args)
    elif args.command == 'info':
        return cmd_info(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
