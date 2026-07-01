#!/usr/bin/env python3
"""
Final LARS Validator for Your Actual File Format
=================================================

This validator uses the FINAL CORRECTED field definitions with 3-digit record types.

Usage:
    from validator_final import FinalLARSValidator
    validator = FinalLARSValidator()
    lars_file = validator.parse_file("yourfile.lrs")
    errors = validator.validate_file(lars_file)
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from lars_config_final import FINAL_FIELD_DEFINITIONS, FINAL_VALIDATION_RULES, get_record_type_from_line, get_field_definitions


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


class FinalLARSValidator:
    """
    Final validator for your actual LARS file format with 3-digit record types.
    """
    
    def __init__(self):
        self.file_path = None
        self.lars_file = None
        self.field_definitions = FINAL_FIELD_DEFINITIONS
        self.validation_rules = FINAL_VALIDATION_RULES
    
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
                
                # Extract record type (first 3 characters)
                if len(line) < 3:
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
                
                record_type = line[:3]
                
                # Get field definitions for this record type
                field_defs = get_field_definitions(record_type)
                
                if not field_defs:
                    # Unknown record type - try to handle gracefully
                    error = ValidationError(
                        line_number=line_num,
                        field_name="RECORD_TYPE",
                        error_type="unknown_record_type",
                        severity=ErrorSeverity.WARNING,
                        message=f"Unknown record type: {record_type}",
                        actual_value=record_type
                    )
                    lars_file.validation_errors.append(error)
                    
                    # Still create a record with basic info
                    record_data = {'RECORD_TYPE': record_type}
                    record = LARSRecord(
                        record_type=record_type,
                        data=record_data,
                        original_line=line,
                        line_number=line_num,
                        is_valid=False,
                        errors=[error]
                    )
                    lars_file.records.append(record)
                    continue
                
                # Parse the record
                record_data = {}
                record_errors = []
                
                for field_name, field_def in field_defs.items():
                    start = field_def['start']
                    length = field_def['length']
                    
                    # Check if line is long enough
                    if len(line) < start + length:
                        error = ValidationError(
                            line_number=line_num,
                            field_name=field_name,
                            error_type="field_truncated",
                            severity=ErrorSeverity.WARNING,
                            message=f"Field {field_name} truncated at position {start}+{length}",
                            expected_value=f"Length {length}",
                            actual_value=line[start:] if start < len(line) else ""
                        )
                        record_errors.append(error)
                        record_data[field_name] = line[start:] if start < len(line) else ""
                    else:
                        field_value = line[start:start+length].strip()
                        record_data[field_name] = field_value
                
                # Create record
                record = LARSRecord(
                    record_type=record_type,
                    data=record_data,
                    original_line=line,
                    line_number=line_num,
                    is_valid=len(record_errors) == 0,
                    errors=record_errors
                )
                
                # Store header and footer
                if record_type == '200':
                    lars_file.header = record_data
                elif record_type == '700':
                    lars_file.footer = record_data
                
                lars_file.records.append(record)
            
            self.lars_file = lars_file
            return lars_file
            
        except Exception as e:
            print(f"Error parsing file: {e}")
            raise
    
    def validate_file(self, lars_file: LARSFile = None) -> List[ValidationError]:
        """Validate the parsed LARS file and return all validation errors"""
        if lars_file is None:
            if self.lars_file is None:
                raise ValueError("No LARS file to validate")
            lars_file = self.lars_file
        
        all_errors = []
        
        # Validate each record
        for record in lars_file.records:
            record_type = record.record_type
            field_defs = get_field_definitions(record_type)
            
            if not field_defs:
                continue  # Already handled during parsing
            
            record_errors = self._validate_record(record, field_defs)
            all_errors.extend(record_errors)
            record.errors.extend(record_errors)
            record.is_valid = len(record_errors) == 0
        
        # Cross-record validations
        cross_errors = self._validate_cross_records(lars_file)
        all_errors.extend(cross_errors)
        
        lars_file.validation_errors = all_errors
        return all_errors
    
    def _validate_record(self, record: LARSRecord, field_defs: Dict) -> List[ValidationError]:
        """Validate a single record against field definitions"""
        errors = []
        
        for field_name, field_def in field_defs.items():
            if field_name not in record.data:
                continue
            
            field_value = record.data[field_name]
            
            # Check required fields
            if field_def.get('required', False) and not field_value:
                errors.append(ValidationError(
                    line_number=record.line_number,
                    field_name=field_name,
                    error_type="required_field_missing",
                    severity=ErrorSeverity.ERROR,
                    message=f"Required field {field_name} is missing or empty",
                    expected_value="Non-empty value",
                    actual_value=field_value,
                    can_auto_fix=False
                ))
                continue
            
            # Skip empty optional fields
            if not field_value:
                continue
            
            # Validate field type
            field_type = field_def.get('type', 'string')
            
            if field_type == 'date':
                date_format = field_def.get('format', '%Y%m%d')
                if not self._validate_date(field_value, date_format):
                    errors.append(ValidationError(
                        line_number=record.line_number,
                        field_name=field_name,
                        error_type="invalid_date_format",
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid date format for {field_name}. Expected {date_format}",
                        expected_value=date_format,
                        actual_value=field_value,
                        can_auto_fix=True,
                        suggested_fix=self._suggest_date_fix(field_value)
                    ))
        
        return errors
    
    def _validate_cross_records(self, lars_file: LARSFile) -> List[ValidationError]:
        """Perform cross-record validations"""
        errors = []
        
        # Check if we have any records
        if not lars_file.records:
            errors.append(ValidationError(
                line_number=0,
                field_name="RECORDS",
                error_type="no_records",
                severity=ErrorSeverity.CRITICAL,
                message="No records found in file",
                can_auto_fix=False
            ))
            return errors
        
        # Check for header record (200)
        has_header = any(r.record_type == '200' for r in lars_file.records)
        if not has_header:
            errors.append(ValidationError(
                line_number=0,
                field_name="HEADER",
                error_type="missing_header",
                severity=ErrorSeverity.CRITICAL,
                message="LARS file is missing header record (type 200)",
                can_auto_fix=False
            ))
        else:
            print("✓ Header record (200) found")
        
        # Check for footer record (700)
        has_footer = any(r.record_type == '700' for r in lars_file.records)
        if not has_footer:
            errors.append(ValidationError(
                line_number=0,
                field_name="FOOTER",
                error_type="missing_footer",
                severity=ErrorSeverity.CRITICAL,
                message="LARS file is missing footer record (type 700)",
                can_auto_fix=False
            ))
        else:
            print("✓ Footer record (700) found")
        
        # Count record types
        record_types = {}
        for record in lars_file.records:
            record_type = record.record_type
            record_types[record_type] = record_types.get(record_type, 0) + 1
        
        print(f"Record type breakdown: {record_types}")
        
        # Check for transaction records (300)
        transaction_records = [r for r in lars_file.records if r.record_type == '300']
        if not transaction_records:
            errors.append(ValidationError(
                line_number=0,
                field_name="TRANSACTIONS",
                error_type="no_transactions",
                severity=ErrorSeverity.WARNING,
                message="No transaction records (type 300) found",
                can_auto_fix=False
            ))
        
        # Check for continuity of transaction records
        # Each 300 should be followed by a 301
        for i in range(len(lars_file.records) - 1):
            current = lars_file.records[i]
            next_rec = lars_file.records[i + 1]
            
            if current.record_type == '300' and next_rec.record_type != '301':
                errors.append(ValidationError(
                    line_number=current.line_number,
                    field_name="RECORD_SEQUENCE",
                    error_type="missing_continuation",
                    severity=ErrorSeverity.INFO,
                    message=f"Transaction record (300) at line {current.line_number} not followed by continuation (301)",
                    expected_value="301",
                    actual_value=next_rec.record_type,
                    can_auto_fix=False
                ))
        
        return errors
    
    def _validate_date(self, date_str: str, date_format: str) -> bool:
        """Validate a date string against a format"""
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False
    
    def _suggest_date_fix(self, date_str: str) -> str:
        """Suggest a fix for invalid date format"""
        date_str = date_str.strip()
        
        # Remove common separators
        clean_date = re.sub(r'[/-\\.]', '', date_str)
        
        # Try different formats
        formats = ['%Y%m%d', '%d%m%Y', '%m%d%Y', '%Y/%m/%d', '%d/%m/%Y']
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y%m%d')
            except ValueError:
                continue
        
        # Try with clean date
        for fmt in ['%Y%m%d', '%d%m%Y', '%m%d%Y']:
            try:
                dt = datetime.strptime(clean_date, fmt)
                return dt.strftime('%Y%m%d')
            except ValueError:
                continue
        
        # If all else fails, return current date
        return datetime.now().strftime('%Y%m%d')
    
    def apply_auto_fixes(self, lars_file: LARSFile = None) -> Tuple[LARSFile, List[str]]:
        """Apply automatic fixes to the LARS file"""
        if lars_file is None:
            if self.lars_file is None:
                raise ValueError("No LARS file to fix")
            lars_file = self.lars_file
        
        fixes_applied = []
        
        # Create a deep copy to avoid modifying original
        import copy
        fixed_file = copy.deepcopy(lars_file)
        
        # Fix each record
        for record in fixed_file.records:
            record_type = record.record_type
            field_defs = get_field_definitions(record_type)
            
            if not field_defs:
                continue
            
            for error in record.errors:
                if error.can_auto_fix and error.suggested_fix:
                    field_name = error.field_name
                    if field_name in record.data:
                        old_value = record.data[field_name]
                        record.data[field_name] = error.suggested_fix
                        fixes_applied.append(
                            f"Line {error.line_number}: Fixed {field_name} from '{old_value}' to '{error.suggested_fix}'"
                        )
        
        # Re-validate to update error status
        self._rebuild_lines(fixed_file)
        self.validate_file(fixed_file)
        
        return fixed_file, fixes_applied
    
    def _rebuild_lines(self, lars_file: LARSFile):
        """Rebuild the original lines from the parsed data"""
        for record in lars_file.records:
            record_type = record.record_type
            field_defs = get_field_definitions(record_type)
            
            if not field_defs:
                continue
            
            # Find the maximum end position
            max_end = 0
            for field_name, field_def in field_defs.items():
                end_pos = field_def['start'] + field_def['length']
                if end_pos > max_end:
                    max_end = end_pos
            
            # Initialize line with spaces
            line_parts = [' '] * max_end
            
            for field_name, field_def in field_defs.items():
                if field_name in record.data:
                    value = str(record.data[field_name])
                    start = field_def['start']
                    length = field_def['length']
                    
                    # Pad or truncate value to fit
                    if len(value) > length:
                        value = value[:length]
                    else:
                        value = value.ljust(length)
                    
                    # Update line parts
                    for i, char in enumerate(value):
                        if start + i < len(line_parts):
                            line_parts[start + i] = char
            
            record.original_line = ''.join(line_parts).rstrip()
    
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
    
    def get_summary(self, lars_file: LARSFile = None) -> Dict[str, Any]:
        """Get a summary of the LARS file validation"""
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
        
        auto_fixable = len([e for e in lars_file.validation_errors if e.can_auto_fix])
        
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
            'auto_fixable_errors': auto_fixable,
            'has_header': lars_file.header is not None,
            'has_footer': lars_file.footer is not None,
            'record_types': record_types,
            'file_path': self.file_path
        }
    
    def print_300_analysis(self, lars_file: LARSFile = None):
        """Print detailed analysis of 300 records"""
        if lars_file is None:
            if self.lars_file is None:
                print("No file loaded")
                return
            lars_file = self.lars_file
        
        print("\n" + "=" * 80)
        print("300 RECORD ANALYSIS (3-digit record types)")
        print("=" * 80)
        
        transaction_records = [r for r in lars_file.records if r.record_type == '300']
        
        if not transaction_records:
            print("No 300 records found")
            return
        
        print(f"Found {len(transaction_records)} 300 records\n")
        
        for i, record in enumerate(transaction_records[:5]):  # Show first 5
            data = record.data
            print(f"Record {i+1} (Line {record.line_number}):")
            print(f"  Record Type: {data.get('RECORD_TYPE', 'N/A')}")
            print(f"  Sequence: {data.get('SEQUENCE_NUMBER', 'N/A')}")
            print(f"  Item Number: {data.get('ITEM_NUMBER', 'N/A')}")
            print(f"  Sales Date: {data.get('SALES_DATE', 'N/A')}")
            print(f"  Processing Date: {data.get('PROCESSING_DATE', 'N/A')}")
            print(f"  Card Number: {data.get('CARD_NUMBER', 'N/A')}")
            print(f"  Card Type: {data.get('CARD_TYPE', 'N/A')}")
            print(f"  Net Amount: {data.get('NET_AMOUNT', 'N/A')}")
            print(f"  Gross Amount: {data.get('GROSS_AMOUNT', 'N/A')}")
            print(f"  Total Amount: {data.get('TOTAL_AMOUNT', 'N/A')}")
            print(f"  Customer Name: {data.get('CUSTOMER_NAME', 'N/A')}")
            print()


# Convenience function
def validate_final_lrs_file(file_path: str) -> Dict[str, Any]:
    """
    Quick function to validate a LRS file with final configuration.
    
    Args:
        file_path: Path to the .lrs file
    
    Returns:
        Dictionary with validation summary
    """
    validator = FinalLARSValidator()
    lars_file = validator.parse_file(file_path)
    errors = validator.validate_file(lars_file)
    return validator.get_summary(lars_file)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            validator = FinalLARSValidator()
            lars_file = validator.parse_file(file_path)
            errors = validator.validate_file(lars_file)
            summary = validator.get_summary(lars_file)
            
            print("Validation Summary:")
            print("=" * 50)
            for key, value in summary.items():
                print(f"{key}: {value}")
            
            # Print 300 analysis
            validator.print_300_analysis(lars_file)
        else:
            print(f"File not found: {file_path}")
    else:
        print("Usage: python validator_final.py <path_to_lrs_file>")
