#!/usr/bin/env python3
"""
LARS File Validator and Repair Tool - Command Line Interface
===========================================================

Command-line interface for validating and repairing LARS files.
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    LARSValidator, LARSFile, LARSVersion, ValidationError, ErrorSeverity
)


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


def print_error(error: ValidationError):
    """Print a validation error with appropriate formatting"""
    severity_colors = {
        ErrorSeverity.CRITICAL: 'red',
        ErrorSeverity.ERROR: 'red',
        ErrorSeverity.WARNING: 'yellow',
        ErrorSeverity.INFO: 'blue'
    }
    
    color = severity_colors.get(error.severity, None)
    
    fixable = " [AUTO-FIX]" if error.can_auto_fix else ""
    
    print_colored(
        f"  Line {error.line_number:4d} | {error.severity.value.upper():8s} | {error.error_type:20s} | {error.field_name:15s} | {error.message}{fixable}",
        color
    )
    
    if error.expected_value:
        print_colored(f"           | Expected: {error.expected_value}", color)
    if error.actual_value:
        print_colored(f"           | Actual:   {error.actual_value}", color)
    if error.can_auto_fix and error.suggested_fix:
        print_colored(f"           | Fix:      {error.suggested_fix}", color)


def print_summary(summary: Dict[str, Any]):
    """Print validation summary"""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"File Version:       {summary.get('version', 'Unknown')}")
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


def cmd_validate(args):
    """Handle validate command"""
    validator = LARSValidator()
    
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
        
        # Print errors if any
        if errors:
            print_colored("VALIDATION ERRORS:", 'red')
            print("-" * 60)
            print(f"{'Line':>6} | {'Severity':<8} | {'Type':<20} | {'Field':<15} | Message")
            print("-" * 60)
            
            for error in errors:
                print_error(error)
        
        # Print record details if verbose
        if args.verbose:
            print(f"\nRECORD DETAILS:")
            print("-" * 60)
            for record in lars_file.records:
                status = "VALID" if record.is_valid else "INVALID"
                print(f"Line {record.line_number:4d} | Type {record.record_type:2s} | {status:7s} | {record.original_line[:50]}")
        
        return 0 if summary.get('total_errors', 0) == 0 else 1
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_repair(args):
    """Handle repair command"""
    validator = LARSValidator()
    
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
    validator = LARSValidator()
    
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
        output_path = args.output or (os.path.splitext(args.file)[0] + "_validated.txt")
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
    validator = LARSValidator()
    
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
        print(f"Detected Version: {summary.get('version', 'Unknown')}")
        print(f"Total Records: {summary.get('total_records', 0)}")
        
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
        
        # Show record types
        record_types = {}
        for record in lars_file.records:
            record_type = record.record_type
            record_types[record_type] = record_types.get(record_type, 0) + 1
        
        print(f"\nRecord Types:")
        for record_type, count in sorted(record_types.items()):
            print(f"  Type {record_type}: {count} records")
        
        # Show sample records if verbose
        if args.verbose:
            print(f"\nSample Records:")
            for i, record in enumerate(lars_file.records[:5]):
                print(f"  Line {record.line_number}: Type {record.record_type} - {record.original_line[:60]}")
        
        return 0
        
    except Exception as e:
        print_colored(f"Error: {str(e)}", 'red')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='LARS File Validator and Repair Tool - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lars-validator validate myfile.txt
  lars-validator validate myfile.txt --verbose
  lars-validator repair myfile.txt --output fixed.txt
  lars-validator info myfile.txt
  lars-validator export myfile.txt --output validated.txt
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a LARS file')
    validate_parser.add_argument('file', help='LARS file to validate')
    validate_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Repair command
    repair_parser = subparsers.add_parser('repair', help='Repair a LARS file')
    repair_parser.add_argument('file', help='LARS file to repair')
    repair_parser.add_argument('-o', '--output', help='Output file path')
    repair_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export a LARS file')
    export_parser.add_argument('file', help='LARS file to export')
    export_parser.add_argument('-o', '--output', help='Output file path')
    export_parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show information about a LARS file')
    info_parser.add_argument('file', help='LARS file to analyze')
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
