#!/usr/bin/env python3
"""
Simple LARS Validator - Minimal Configuration
==============================================

This is a minimal validator that focuses on correctly identifying
record types and parsing the basic structure of your LARS files.

It will:
1. Correctly identify all record types (20000, 20001, 20002, 30000, 30001, 40000, 59000, 70000)
2. Parse each line without validation errors
3. Show you the raw data so we can refine the field positions

Usage:
    from validator_simple import SimpleLARSValidator
    validator = SimpleLARSValidator()
    lars_file = validator.parse_file("yourfile.lrs")
    print(validator.get_summary(lars_file))
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for validation errors"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error in a LARS file"""
    line_number: int
    field_name: str
    error_type: str
    severity: ErrorSeverity
    message: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    can_auto_fix: bool = False
    suggested_fix: Optional[str] = None


@dataclass
class LARSRecord:
    """Represents a single record in a LARS file"""
    record_type: str
    data: Dict[str, str]
    original_line: str
    line_number: int
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)


@dataclass
class LARSFile:
    """Represents a complete LARS file"""
    records: List[LARSRecord] = field(default_factory=list)
    header: Optional[Dict[str, str]] = None
    footer: Optional[Dict[str, str]] = None
    validation_errors: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimpleLARSValidator:
    """
    Simple validator that focuses on record type identification
    and basic parsing without strict validation.
    """
    
    def __init__(self):
        self.file_path = None
        self.lars_file = None
        # Minimal field definitions - just record type
        self.field_definitions = {
            '20000': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '20001': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '20002': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '30000': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '30001': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '40000': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '59000': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
            '70000': {'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True}},
        }
    
    def parse_file(self, file_path: str) -> LARSFile:
        """Parse a LARS file and return a LARSFile object"""
        self.file_path = file_path
        
        lars_file = LARSFile()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip('\n\r')
                
                if not line.strip():
                    continue
                
                # Extract record type (first 5 characters)
                if len(line) < 5:
                    error = ValidationError(
                        line_number=line_num,
                        field_name="RECORD_TYPE",
                        error_type="missing_record_type",
                        severity=ErrorSeverity.ERROR,
                        message=f"Line too short to contain record type",
                        actual_value=line
                    )
                    lars_file.validation_errors.append(error)
                    continue
                
                record_type = line[:5]
                
                # Create basic record data
                record_data = {
                    'RECORD_TYPE': record_type,
                    'FULL_LINE': line,  # Store the full line for analysis
                    'LINE_LENGTH': len(line)
                }
                
                # Create record
                record = LARSRecord(
                    record_type=record_type,
                    data=record_data,
                    original_line=line,
                    line_number=line_num,
                    is_valid=True,
                    errors=[]
                )
                
                # Store header and footer
                if record_type == '20000':
                    lars_file.header = record_data
                elif record_type == '70000':
                    lars_file.footer = record_data
                
                lars_file.records.append(record)
            
            self.lars_file = lars_file
            return lars_file
            
        except Exception as e:
            print(f"Error parsing file: {e}")
            raise
    
    def validate_file(self, lars_file: LARSFile = None) -> List[ValidationError]:
        """Minimal validation - just check for header and footer"""
        if lars_file is None:
            if self.lars_file is None:
                raise ValueError("No LARS file to validate")
            lars_file = self.lars_file
        
        all_errors = []
        
        # Check for header record (20000)
        has_header = any(r.record_type == '20000' for r in lars_file.records)
        if not has_header:
            all_errors.append(ValidationError(
                line_number=0,
                field_name="HEADER",
                error_type="missing_header",
                severity=ErrorSeverity.CRITICAL,
                message="LARS file is missing header record (type 20000)",
                can_auto_fix=False
            ))
        else:
            print("✓ Header record (20000) found")
        
        # Check for footer record (70000)
        has_footer = any(r.record_type == '70000' for r in lars_file.records)
        if not has_footer:
            all_errors.append(ValidationError(
                line_number=0,
                field_name="FOOTER",
                error_type="missing_footer",
                severity=ErrorSeverity.CRITICAL,
                message="LARS file is missing footer record (type 70000)",
                can_auto_fix=False
            ))
        else:
            print("✓ Footer record (70000) found")
        
        # Count record types
        record_types = {}
        for record in lars_file.records:
            record_type = record.record_type
            record_types[record_type] = record_types.get(record_type, 0) + 1
        
        print(f"Record type breakdown: {record_types}")
        
        lars_file.validation_errors = all_errors
        return all_errors
    
    def get_summary(self, lars_file: LARSFile = None) -> Dict[str, Any]:
        """Get a summary of the LARS file"""
        if lars_file is None:
            if self.lars_file is None:
                return {}
            lars_file = self.lars_file
        
        total_records = len(lars_file.records)
        valid_records = len([r for r in lars_file.records if r.is_valid])
        invalid_records = total_records - valid_records
        
        errors_by_severity = {
            'critical': len([e for e in lars_file.validation_errors if e.severity == ErrorSeverity.CRITICAL]),
            'error': len([e for e in lars_file.validation_errors if e.severity == ErrorSeverity.ERROR]),
            'warning': len([e for e in lars_file.validation_errors if e.severity == ErrorSeverity.WARNING]),
            'info': len([e for e in lars_file.validation_errors if e.severity == ErrorSeverity.INFO]),
        }
        
        # Count record types
        record_types = {}
        for record in lars_file.records:
            record_type = record.record_type
            record_types[record_type] = record_types.get(record_type, 0) + 1
        
        return {
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'total_errors': len(lars_file.validation_errors),
            'errors_by_severity': errors_by_severity,
            'auto_fixable_errors': 0,
            'has_header': lars_file.header is not None,
            'has_footer': lars_file.footer is not None,
            'record_types': record_types,
            'file_path': self.file_path
        }
    
    def export_file(self, lars_file: LARSFile, output_path: str) -> bool:
        """Export the LARS file to a new file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for record in lars_file.records:
                    f.write(record.original_line + '\n')
            return True
        except Exception as e:
            print(f"Error exporting file: {e}")
            return False
    
    def print_line_analysis(self, lars_file: LARSFile = None, max_lines: int = 10):
        """Print analysis of each line to help determine field positions"""
        if lars_file is None:
            if self.lars_file is None:
                print("No file loaded")
                return
            lars_file = self.lars_file
        
        print("\n" + "=" * 80)
        print("LINE ANALYSIS - For determining field positions")
        print("=" * 80)
        
        for i, record in enumerate(lars_file.records[:max_lines]):
            line = record.original_line
            print(f"\nLine {record.line_number} | Type {record.record_type} | Length: {len(line)}")
            print("-" * 60)
            print(f"Full: {repr(line[:100])}")
            
            # Show position breakdown
            print("Position breakdown:")
            for pos in range(0, min(len(line), 100), 10):
                segment = line[pos:pos+10]
                print(f"  {pos:3d}-{pos+10:3d}: {repr(segment)}")


# Convenience function
def analyze_lrs_file(file_path: str, max_lines: int = 10):
    """Analyze a LRS file and print line structure"""
    validator = SimpleLARSValidator()
    lars_file = validator.parse_file(file_path)
    validator.validate_file(lars_file)
    validator.print_line_analysis(lars_file, max_lines)
    
    summary = validator.get_summary(lars_file)
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_lrs_file(sys.argv[1])
    else:
        print("Usage: python validator_simple.py <path_to_lrs_file>")
