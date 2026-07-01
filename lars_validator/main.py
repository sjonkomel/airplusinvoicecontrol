#!/usr/bin/env python3
"""
LARS File Validator and Repair Tool
===================================

A desktop application for validating and repairing AIRPLUS LARS invoice files
before uploading to ERP systems.

Features:
- Upload and parse LARS files
- Automatic error detection
- Interactive error repair
- Export corrected files
- Local execution for travel assistants
"""

import os
import sys
import re
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LARSVersion(Enum):
    """Supported LARS file versions"""
    V2_0 = "2.0"
    V3_0 = "3.0"


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
    version: LARSVersion
    records: List[LARSRecord] = field(default_factory=list)
    header: Optional[Dict[str, str]] = None
    footer: Optional[Dict[str, str]] = None
    validation_errors: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LARSValidator:
    """
    Main validator class for LARS files
    
    LARS (Lufthansa AirPlus Invoice Record System) files typically have:
    - Header record (type 01)
    - Transaction records (type 02, 03, etc.)
    - Footer record (type 99)
    
    Common field patterns:
    - Fixed width fields
    - Specific data types (dates, amounts, codes)
    - Mandatory fields
    - Cross-field validations
    """
    
    # Field definitions for LARS format (based on typical structure)
    FIELD_DEFINITIONS = {
        LARSVersion.V3_0: {
            '01': {  # Header record
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'VERSION': {'start': 2, 'length': 4, 'type': 'string', 'required': True},
                'COMPANY_CODE': {'start': 6, 'length': 10, 'type': 'string', 'required': True},
                'CREATION_DATE': {'start': 16, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True},
                'FILE_REFERENCE': {'start': 24, 'length': 20, 'type': 'string', 'required': True},
                'CURRENCY': {'start': 44, 'length': 3, 'type': 'string', 'required': True},
                'FILLER': {'start': 47, 'length': 53, 'type': 'string', 'required': False},
            },
            '02': {  # Transaction record
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'TRANSACTION_TYPE': {'start': 2, 'length': 2, 'type': 'string', 'required': True},
                'CARD_NUMBER': {'start': 4, 'length': 16, 'type': 'string', 'required': True},
                'TRANSACTION_DATE': {'start': 20, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True},
                'POSTING_DATE': {'start': 28, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True},
                'AMOUNT': {'start': 36, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2},
                'CURRENCY': {'start': 51, 'length': 3, 'type': 'string', 'required': True},
                'MERCHANT_CODE': {'start': 54, 'length': 10, 'type': 'string', 'required': True},
                'MERCHANT_NAME': {'start': 64, 'length': 30, 'type': 'string', 'required': False},
                'INVOICE_NUMBER': {'start': 94, 'length': 20, 'type': 'string', 'required': False},
                'COST_CENTER': {'start': 114, 'length': 10, 'type': 'string', 'required': False},
                'DESCRIPTION': {'start': 124, 'length': 50, 'type': 'string', 'required': False},
            },
            '03': {  # Additional transaction details
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'CARD_NUMBER': {'start': 2, 'length': 16, 'type': 'string', 'required': True},
                'TRANSACTION_REFERENCE': {'start': 18, 'length': 20, 'type': 'string', 'required': True},
                'TAX_AMOUNT': {'start': 38, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2},
                'TAX_CODE': {'start': 53, 'length': 5, 'type': 'string', 'required': False},
                'FILLER': {'start': 58, 'length': 142, 'type': 'string', 'required': False},
            },
            '99': {  # Footer record
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'TOTAL_RECORDS': {'start': 2, 'length': 6, 'type': 'integer', 'required': True},
                'TOTAL_AMOUNT': {'start': 8, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2},
                'TOTAL_CURRENCY': {'start': 23, 'length': 3, 'type': 'string', 'required': True},
                'FILLER': {'start': 26, 'length': 174, 'type': 'string', 'required': False},
            }
        },
        LARSVersion.V2_0: {
            # Similar structure but with some differences
            '01': {
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'VERSION': {'start': 2, 'length': 4, 'type': 'string', 'required': True},
                'COMPANY_CODE': {'start': 6, 'length': 10, 'type': 'string', 'required': True},
                'CREATION_DATE': {'start': 16, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True},
                'FILE_REFERENCE': {'start': 24, 'length': 15, 'type': 'string', 'required': True},
                'CURRENCY': {'start': 39, 'length': 3, 'type': 'string', 'required': True},
            },
            '02': {
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'TRANSACTION_TYPE': {'start': 2, 'length': 2, 'type': 'string', 'required': True},
                'CARD_NUMBER': {'start': 4, 'length': 16, 'type': 'string', 'required': True},
                'TRANSACTION_DATE': {'start': 20, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True},
                'AMOUNT': {'start': 28, 'length': 12, 'type': 'decimal', 'required': True, 'precision': 2},
                'CURRENCY': {'start': 40, 'length': 3, 'type': 'string', 'required': True},
                'MERCHANT_CODE': {'start': 43, 'length': 10, 'type': 'string', 'required': True},
                'MERCHANT_NAME': {'start': 53, 'length': 25, 'type': 'string', 'required': False},
            },
            '99': {
                'RECORD_TYPE': {'start': 0, 'length': 2, 'type': 'string', 'required': True},
                'TOTAL_RECORDS': {'start': 2, 'length': 6, 'type': 'integer', 'required': True},
                'TOTAL_AMOUNT': {'start': 8, 'length': 12, 'type': 'decimal', 'required': True, 'precision': 2},
                'TOTAL_CURRENCY': {'start': 20, 'length': 3, 'type': 'string', 'required': True},
            }
        }
    }
    
    # Common validation rules
    VALIDATION_RULES = {
        'date_format': r'^\d{8}$',  # YYYYMMDD
        'amount_format': r'^-?\d+\.?\d*$',  # Allows for decimal amounts
        'card_number': r'^\d{13,19}$',  # Standard credit card number length
        'currency_code': r'^[A-Z]{3}$',  # ISO currency codes
        'transaction_type': r'^\d{2}$',
        'record_type': r'^\d{2}$',
    }
    
    def __init__(self):
        self.detected_version = None
        self.file_path = None
        self.lars_file = None
    
    def detect_version(self, file_path: str) -> LARSVersion:
        """Detect the LARS file version from the file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                
            if len(first_line) >= 6:
                version_str = first_line[2:6].strip()
                if version_str == '3.0' or version_str == '30':
                    return LARSVersion.V3_0
                elif version_str == '2.0' or version_str == '20':
                    return LARSVersion.V2_0
            
            # Default to V3.0 as it's the most recent
            return LARSVersion.V3_0
            
        except Exception as e:
            logger.error(f"Error detecting version: {e}")
            return LARSVersion.V3_0
    
    def parse_file(self, file_path: str) -> LARSFile:
        """Parse a LARS file and return a LARSFile object"""
        self.file_path = file_path
        self.detected_version = self.detect_version(file_path)
        
        lars_file = LARSFile(version=self.detected_version)
        field_defs = self.FIELD_DEFINITIONS[self.detected_version]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip('\n\r')
                
                if not line.strip():
                    continue
                
                # Extract record type (first 2 characters)
                if len(line) < 2:
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
                
                record_type = line[:2]
                
                # Get field definitions for this record type
                if record_type not in field_defs:
                    error = ValidationError(
                        line_number=line_num,
                        field_name="RECORD_TYPE",
                        error_type="unknown_record_type",
                        severity=ErrorSeverity.ERROR,
                        message=f"Unknown record type: {record_type}",
                        actual_value=record_type
                    )
                    lars_file.validation_errors.append(error)
                    continue
                
                # Parse the record
                record_data = {}
                record_errors = []
                
                for field_name, field_def in field_defs[record_type].items():
                    start = field_def['start']
                    length = field_def['length']
                    
                    # Check if line is long enough
                    if len(line) < start + length:
                        error = ValidationError(
                            line_number=line_num,
                            field_name=field_name,
                            error_type="field_truncated",
                            severity=ErrorSeverity.ERROR,
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
                if record_type == '01':
                    lars_file.header = record_data
                elif record_type == '99':
                    lars_file.footer = record_data
                
                lars_file.records.append(record)
            
            self.lars_file = lars_file
            return lars_file
            
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            raise
    
    def validate_file(self, lars_file: Optional[LARSFile] = None) -> List[ValidationError]:
        """Validate the parsed LARS file and return all validation errors"""
        if lars_file is None:
            if self.lars_file is None:
                raise ValueError("No LARS file to validate")
            lars_file = self.lars_file
        
        all_errors = []
        field_defs = self.FIELD_DEFINITIONS[lars_file.version]
        
        # Validate each record
        for record in lars_file.records:
            record_type = record.record_type
            
            if record_type not in field_defs:
                continue  # Already handled during parsing
            
            record_errors = self._validate_record(record, field_defs[record_type])
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
            
            elif field_type == 'decimal':
                if not self._validate_decimal(field_value):
                    errors.append(ValidationError(
                        line_number=record.line_number,
                        field_name=field_name,
                        error_type="invalid_decimal_format",
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid decimal format for {field_name}",
                        expected_value="Valid decimal number",
                        actual_value=field_value,
                        can_auto_fix=True,
                        suggested_fix=self._suggest_decimal_fix(field_value)
                    ))
                else:
                    # Check precision if specified
                    precision = field_def.get('precision', 2)
                    if not self._validate_decimal_precision(field_value, precision):
                        errors.append(ValidationError(
                            line_number=record.line_number,
                            field_name=field_name,
                            error_type="decimal_precision",
                            severity=ErrorSeverity.WARNING,
                            message=f"Decimal precision exceeds {precision} places for {field_name}",
                            expected_value=f"Max {precision} decimal places",
                            actual_value=field_value,
                            can_auto_fix=True,
                            suggested_fix=self._suggest_decimal_precision_fix(field_value, precision)
                        ))
            
            elif field_type == 'integer':
                if not self._validate_integer(field_value):
                    errors.append(ValidationError(
                        line_number=record.line_number,
                        field_name=field_name,
                        error_type="invalid_integer_format",
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid integer format for {field_name}",
                        expected_value="Valid integer",
                        actual_value=field_value,
                        can_auto_fix=True,
                        suggested_fix=self._suggest_integer_fix(field_value)
                    ))
            
            # Field-specific validations
            if field_name == 'CURRENCY' and field_value:
                if not re.match(self.VALIDATION_RULES['currency_code'], field_value):
                    errors.append(ValidationError(
                        line_number=record.line_number,
                        field_name=field_name,
                        error_type="invalid_currency_code",
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid currency code: {field_value}",
                        expected_value="3-letter ISO currency code",
                        actual_value=field_value,
                        can_auto_fix=False
                    ))
            
            elif field_name == 'CARD_NUMBER' and field_value:
                if not re.match(self.VALIDATION_RULES['card_number'], field_value):
                    errors.append(ValidationError(
                        line_number=record.line_number,
                        field_name=field_name,
                        error_type="invalid_card_number",
                        severity=ErrorSeverity.WARNING,
                        message=f"Card number format may be invalid: {field_value}",
                        expected_value="13-19 digit number",
                        actual_value=field_value,
                        can_auto_fix=False
                    ))
            
            elif field_name == 'RECORD_TYPE' and field_value:
                if not re.match(self.VALIDATION_RULES['record_type'], field_value):
                    errors.append(ValidationError(
                        line_number=record.line_number,
                        field_name=field_name,
                        error_type="invalid_record_type",
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid record type: {field_value}",
                        expected_value="2-digit number",
                        actual_value=field_value,
                        can_auto_fix=False
                    ))
        
        return errors
    
    def _validate_cross_records(self, lars_file: LARSFile) -> List[ValidationError]:
        """Perform cross-record validations"""
        errors = []
        
        # Check if header exists
        if not lars_file.header:
            errors.append(ValidationError(
                line_number=0,
                field_name="HEADER",
                error_type="missing_header",
                severity=ErrorSeverity.CRITICAL,
                message="LARS file is missing header record (type 01)",
                can_auto_fix=False
            ))
        
        # Check if footer exists
        if not lars_file.footer:
            errors.append(ValidationError(
                line_number=0,
                field_name="FOOTER",
                error_type="missing_footer",
                severity=ErrorSeverity.CRITICAL,
                message="LARS file is missing footer record (type 99)",
                can_auto_fix=False
            ))
        
        # Check record count in footer matches actual count
        if lars_file.footer and 'TOTAL_RECORDS' in lars_file.footer:
            try:
                expected_count = int(lars_file.footer['TOTAL_RECORDS'])
                # Exclude header and footer from count
                actual_count = len([r for r in lars_file.records if r.record_type not in ['01', '99']])
                
                if expected_count != actual_count:
                    errors.append(ValidationError(
                        line_number=0,
                        field_name="TOTAL_RECORDS",
                        error_type="record_count_mismatch",
                        severity=ErrorSeverity.ERROR,
                        message=f"Record count mismatch: expected {expected_count}, found {actual_count}",
                        expected_value=str(expected_count),
                        actual_value=str(actual_count),
                        can_auto_fix=True,
                        suggested_fix=str(actual_count)
                    ))
            except ValueError:
                errors.append(ValidationError(
                    line_number=0,
                    field_name="TOTAL_RECORDS",
                    error_type="invalid_record_count",
                    severity=ErrorSeverity.ERROR,
                    message=f"Invalid record count in footer: {lars_file.footer['TOTAL_RECORDS']}",
                    expected_value="Valid integer",
                    actual_value=lars_file.footer['TOTAL_RECORDS'],
                    can_auto_fix=True,
                    suggested_fix=str(len([r for r in lars_file.records if r.record_type not in ['01', '99']]))
                ))
        
        # Check currency consistency
        currencies = set()
        for record in lars_file.records:
            if 'CURRENCY' in record.data and record.data['CURRENCY']:
                currencies.add(record.data['CURRENCY'])
        
        if len(currencies) > 1:
            errors.append(ValidationError(
                line_number=0,
                field_name="CURRENCY",
                error_type="multiple_currencies",
                severity=ErrorSeverity.WARNING,
                message=f"Multiple currencies found: {', '.join(currencies)}",
                expected_value="Single currency",
                actual_value=', '.join(currencies),
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
    
    def _validate_decimal(self, value: str) -> bool:
        """Validate a decimal number string"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _validate_decimal_precision(self, value: str, precision: int) -> bool:
        """Check if decimal has correct precision"""
        try:
            if '.' in value:
                decimal_part = value.split('.')[1]
                return len(decimal_part) <= precision
            return True
        except:
            return False
    
    def _validate_integer(self, value: str) -> bool:
        """Validate an integer string"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _suggest_date_fix(self, date_str: str) -> str:
        """Suggest a fix for invalid date format"""
        # Try to detect common date formats and convert to YYYYMMDD
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
    
    def _suggest_decimal_fix(self, value: str) -> str:
        """Suggest a fix for invalid decimal format"""
        # Remove all non-numeric characters except minus and decimal point
        clean_value = re.sub(r'[^\d.-]', '', value)
        
        # Ensure only one decimal point
        if clean_value.count('.') > 1:
            parts = clean_value.split('.')
            clean_value = parts[0] + '.' + ''.join(parts[1:])
        
        # Ensure it's a valid number
        try:
            float(clean_value)
            return clean_value
        except ValueError:
            # Remove decimal point if still invalid
            clean_value = re.sub(r'[^\d-]', '', value)
            try:
                float(clean_value)
                return clean_value
            except ValueError:
                return "0.00"
    
    def _suggest_decimal_precision_fix(self, value: str, precision: int) -> str:
        """Suggest a fix for decimal precision"""
        try:
            num = float(value)
            return f"{num:.{precision}f}"
        except ValueError:
            return value
    
    def _suggest_integer_fix(self, value: str) -> str:
        """Suggest a fix for invalid integer format"""
        clean_value = re.sub(r'[^\d-]', '', value)
        try:
            int(clean_value)
            return clean_value
        except ValueError:
            return "0"
    
    def apply_auto_fixes(self, lars_file: Optional[LARSFile] = None) -> Tuple[LARSFile, List[str]]:
        """Apply automatic fixes to the LARS file and return fixed file and list of fixes applied"""
        if lars_file is None:
            if self.lars_file is None:
                raise ValueError("No LARS file to fix")
            lars_file = self.lars_file
        
        fixes_applied = []
        field_defs = self.FIELD_DEFINITIONS[lars_file.version]
        
        # Create a deep copy to avoid modifying original
        import copy
        fixed_file = copy.deepcopy(lars_file)
        
        # Fix each record
        for record in fixed_file.records:
            record_type = record.record_type
            
            if record_type not in field_defs:
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
        
        # Fix cross-record issues
        for error in fixed_file.validation_errors:
            if error.can_auto_fix and error.suggested_fix:
                if error.field_name == "TOTAL_RECORDS" and fixed_file.footer:
                    old_value = fixed_file.footer.get('TOTAL_RECORDS', '')
                    fixed_file.footer['TOTAL_RECORDS'] = error.suggested_fix
                    fixes_applied.append(
                        f"Footer: Fixed TOTAL_RECORDS from '{old_value}' to '{error.suggested_fix}'"
                    )
        
        # Re-validate to update error status
        self._rebuild_lines(fixed_file)
        self.validate_file(fixed_file)
        
        return fixed_file, fixes_applied
    
    def _rebuild_lines(self, lars_file: LARSFile):
        """Rebuild the original lines from the parsed data"""
        field_defs = self.FIELD_DEFINITIONS[lars_file.version]
        
        for record in lars_file.records:
            record_type = record.record_type
            
            if record_type not in field_defs:
                continue
            
            # Create a new line with the current data
            line_parts = [' '] * 200  # Initialize with spaces
            
            for field_name, field_def in field_defs[record_type].items():
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
            logger.error(f"Error exporting file: {e}")
            return False
    
    def get_summary(self, lars_file: Optional[LARSFile] = None) -> Dict[str, Any]:
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
        
        return {
            'version': lars_file.version.value,
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'total_errors': len(lars_file.validation_errors),
            'errors_by_severity': errors_by_severity,
            'auto_fixable_errors': auto_fixable,
            'has_header': lars_file.header is not None,
            'has_footer': lars_file.footer is not None,
            'file_path': getattr(lars_file, 'file_path', self.file_path)
        }
