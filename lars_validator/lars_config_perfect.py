#!/usr/bin/env python3
"""
Perfect LARS File Configuration
===============================

This file contains the PERFECT field definitions for your actual LARS file format
based on your exact specifications for Record Type 300.

Record Type 300 (SN00) Field Specifications:
- Record type: 3 digits (300)
- Sequence No: 2 digits (always "00")
- Item no.: 5 digits
- Sales date: 8 digits (YYYYMMDD)
- Processing date: 8 digits (YYYYMMDD)
- Card no.: 19 digits
- Debit/credit booking: 1 digit
- Billing/charging item: 1 digit
- Sales currency: 3 digits
- Decimal places: 1 digit
- Sales amount Net: 15 digits
- VAT rate: 9 digits
- VAT amount: 9 digits
- Conversion rate: 7 digits
- Decimal places for conversion rate: 2 digits
- Gross invoice amount: 15 digits
- Amount for addnl. insurance: 9 digits
- Total amount for item: 15 digits
- Customer: 30 characters
- Transaction type: 2 characters
- Reference number: 13 characters
- 400 counter: 2 digits
- 5xx counter: 2 digits
- 600 counter: 2 digits
- FAKTURA check identifier: 1 digit
- User check identifier: 1 digit
- Filler: 215 characters

Total line length: ~400 characters

Note: All positions are 0-based (Python indexing).
"""

from enum import Enum
from typing import Dict, Any


class LARSRecordType(Enum):
    """Record types in your LARS file - 3 digits"""
    HEADER = "200"           # File header
    HEADER_LINE1 = "201"     # Company info line 1
    HEADER_LINE2 = "202"     # Company info line 2
    TRANSACTION = "300"      # Main transaction record
    TRANSACTION_LINE1 = "301" # Transaction continuation
    FLIGHT_INFO = "400"       # Flight/ticket information
    TICKET_DETAIL = "590"    # Additional transaction details
    FOOTER = "700"           # File footer


# PERFECT Field definitions for your actual LARS format
# Based on your exact specifications
PERFECT_FIELD_DEFINITIONS = {
    LARSRecordType.HEADER: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (200)'},
        'FILLER': {'start': 3, 'length': 397, 'type': 'string', 'required': False, 'description': 'Rest of header line'},
    },
    
    LARSRecordType.HEADER_LINE1: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (201)'},
        'FILLER': {'start': 3, 'length': 397, 'type': 'string', 'required': False, 'description': 'Company info line 1'},
    },
    
    LARSRecordType.HEADER_LINE2: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (202)'},
        'FILLER': {'start': 3, 'length': 397, 'type': 'string', 'required': False, 'description': 'Company info line 2'},
    },
    
    LARSRecordType.TRANSACTION: {
        # PERFECT configuration based on your specifications:
        # Position 0: Record type (300) - 3 digits
        # Position 3: Sequence No - 2 digits (always "00")
        # Position 5: Item no. - 5 digits
        # Position 10: Sales date - 8 digits (YYYYMMDD)
        # Position 18: Processing date - 8 digits (YYYYMMDD)
        # Position 26: Card no. - 19 digits
        # Position 45: Debit/credit booking - 1 digit
        # Position 46: Billing/charging item - 1 digit
        # Position 47: Sales currency - 3 digits
        # Position 50: Decimal places - 1 digit
        # Position 51: Sales amount Net - 15 digits
        # Position 66: VAT rate - 9 digits
        # Position 75: VAT amount - 9 digits
        # Position 84: Conversion rate - 7 digits
        # Position 91: Decimal places for conversion rate - 2 digits
        # Position 93: Gross invoice amount - 15 digits
        # Position 108: Amount for addnl. insurance - 9 digits
        # Position 117: Total amount for item - 15 digits
        # Position 132: Customer - 30 characters
        # Position 162: Transaction type - 2 characters
        # Position 164: Reference number - 13 characters
        # Position 177: 400 counter - 2 digits
        # Position 179: 5xx counter - 2 digits
        # Position 181: 600 counter - 2 digits
        # Position 183: FAKTURA check identifier - 1 digit
        # Position 184: User check identifier - 1 digit
        # Position 185: Filler - 215 characters
        
        'LARS-SATZ-ART': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (300)'},
        'LARS-POS-SN': {'start': 3, 'length': 2, 'type': 'string', 'required': True, 'description': 'Sequence No (always "00")'},
        'LARS-LFD-POS': {'start': 5, 'length': 5, 'type': 'string', 'required': True, 'description': 'Item no.'},
        'LARS-VERK-DAT': {'start': 10, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Sales date (YYYYMMDD)'},
        'LARS-VERARB-DAT': {'start': 18, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Processing date (YYYYMMDD)'},
        'LARS-KA-NR': {'start': 26, 'length': 19, 'type': 'string', 'required': True, 'description': 'Card no.'},
        'LARS-S-H-POS': {'start': 45, 'length': 1, 'type': 'string', 'required': True, 'description': 'Debit/credit booking'},
        'LARS-POS-ART': {'start': 46, 'length': 1, 'type': 'string', 'required': True, 'description': 'Billing/charging item'},
        'LARS-VERK-WAEHR': {'start': 47, 'length': 3, 'type': 'string', 'required': True, 'description': 'Sales currency'},
        'LARS-VERK-NK': {'start': 50, 'length': 1, 'type': 'integer', 'required': True, 'description': 'Decimal places'},
        'LARS-NETTO-BETRAG': {'start': 51, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Sales amount Net'},
        'LARS-MWST-SATZ': {'start': 66, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 4, 'description': 'VAT rate'},
        'LARS-MWST-BETRAG': {'start': 75, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'VAT amount'},
        'LARS-VERK-ABR-KURS': {'start': 84, 'length': 7, 'type': 'decimal', 'required': False, 'precision': 5, 'description': 'Conversion rate'},
        'LARS-VERK-ABR-KURS-NK': {'start': 91, 'length': 2, 'type': 'integer', 'required': False, 'description': 'Decimal places for conversion rate'},
        'LARS-BRUTTO-BETRAG': {'start': 93, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Gross invoice amount'},
        'LARS-ZV-BETRAG': {'start': 108, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Amount for addnl. insurance'},
        'LARS-POS-BETRAG': {'start': 117, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Total amount for item'},
        'LARS-NAME': {'start': 132, 'length': 30, 'type': 'string', 'required': False, 'description': 'Customer'},
        'LARS-HK': {'start': 162, 'length': 2, 'type': 'string', 'required': False, 'description': 'Transaction type/transaction origin'},
        'LARS-TC-NR': {'start': 164, 'length': 13, 'type': 'string', 'required': False, 'description': 'Reference/transaction no.'},
        'LARS-400-COUNT': {'start': 177, 'length': 2, 'type': 'integer', 'required': False, 'description': '400 counter'},
        'LARS-5XX-COUNT': {'start': 179, 'length': 2, 'type': 'integer', 'required': False, 'description': '5xx counter'},
        'LARS-600-COUNT': {'start': 181, 'length': 2, 'type': 'integer', 'required': False, 'description': '600 counter'},
        'LARS-FAKTURA': {'start': 183, 'length': 1, 'type': 'string', 'required': False, 'description': 'FAKTURA check identifier'},
        'LARS-BENUTZER': {'start': 184, 'length': 1, 'type': 'string', 'required': False, 'description': 'User check identifier'},
        'LARS-FILLER-300-00': {'start': 185, 'length': 215, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TRANSACTION_LINE1: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (301)'},
        'FILLER': {'start': 3, 'length': 397, 'type': 'string', 'required': False, 'description': 'Customer info continuation'},
    },
    
    LARSRecordType.FLIGHT_INFO: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (400)'},
        'FILLER': {'start': 3, 'length': 397, 'type': 'string', 'required': False, 'description': 'Flight/ticket information'},
    },
    
    LARSRecordType.TICKET_DETAIL: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (590)'},
        'FILLER': {'start': 3, 'length': 397, 'type': 'string', 'required': False, 'description': 'Ticket detail information'},
    },
    
    LARSRecordType.FOOTER: {
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (700)'},
        'TOTAL_RECORDS': {'start': 3, 'length': 8, 'type': 'integer', 'required': True, 'description': 'Total number of records'},
        'FILLER': {'start': 11, 'length': 389, 'type': 'string', 'required': False, 'description': 'Footer filler'},
    }
}


# Validation rules for your format
PERFECT_VALIDATION_RULES = {
    'date_format': r'^\d{8}$',  # YYYYMMDD
    'amount_format': r'^-?\d+\.?\d*$',
    'currency_code': r'^[A-Z0-9]{3}$',  # Allow numeric currency codes
    'record_type': r'^\d{3}$',  # 3-digit record types
}


def get_record_type_from_line(line: str) -> str:
    """Extract record type from a line (first 3 characters)"""
    if len(line) >= 3:
        return line[:3]
    return "UNKNOWN"


def get_field_definitions(record_type: str) -> Dict:
    """Get field definitions for a specific record type"""
    for enum_type, definitions in PERFECT_FIELD_DEFINITIONS.items():
        if enum_type.value == record_type:
            return definitions
    return {}


if __name__ == "__main__":
    # Print the field definitions for reference
    print("Perfect LARS Field Definitions (Based on Your Specifications):")
    print("=" * 80)
    
    for record_type_enum, fields in PERFECT_FIELD_DEFINITIONS.items():
        print(f"\nRecord Type: {record_type_enum.value}")
        print("-" * 60)
        for field_name, field_def in sorted(fields.items(), key=lambda x: x[1]['start']):
            start = field_def['start']
            length = field_def['length']
            field_type = field_def['type']
            required = field_def.get('required', False)
            description = field_def.get('description', field_name)
            
            print(f"  {start:3d}-{start+length:3d}: {field_name:25s} ({field_type:8s}, {'REQ' if required else 'OPT'}) - {description}")
