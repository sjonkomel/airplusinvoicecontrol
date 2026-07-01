#!/usr/bin/env python3
"""
Corrected LARS File Configuration
==================================

This file contains the CORRECTED field definitions for your actual LARS file format.
Based on the analysis of your 30000 record type.

Record Types in your file:
- 20000: File header
- 20001: Header continuation line 1
- 20002: Header continuation line 2
- 30000: Main transaction record (CORRECTED)
- 30001: Transaction continuation (customer info)
- 40000: Flight/ticket information
- 59000: Additional transaction details
- 70000: File footer

Note: All positions are 0-based (Python indexing).
"""

from enum import Enum
from typing import Dict, Any


class LARSRecordType(Enum):
    """Record types in your LARS file"""
    HEADER = "20000"           # File header
    HEADER_LINE1 = "20001"     # Company info line 1
    HEADER_LINE2 = "20002"     # Company info line 2
    TRANSACTION = "30000"      # Main transaction record
    TRANSACTION_LINE1 = "30001" # Transaction continuation
    FLIGHT_INFO = "40000"       # Flight/ticket information
    TICKET_DETAIL = "59000"    # Additional transaction details
    FOOTER = "70000"           # File footer


# CORRECTED Field definitions for your actual LARS format
CORRECTED_FIELD_DEFINITIONS = {
    LARSRecordType.HEADER: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (20000)'},
        # Add other header fields as needed
        'FILLER': {'start': 5, 'length': 235, 'type': 'string', 'required': False, 'description': 'Rest of header line'},
    },
    
    LARSRecordType.HEADER_LINE1: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (20001)'},
        'FILLER': {'start': 5, 'length': 196, 'type': 'string', 'required': False, 'description': 'Company info line 1'},
    },
    
    LARSRecordType.HEADER_LINE2: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (20002)'},
        'FILLER': {'start': 5, 'length': 368, 'type': 'string', 'required': False, 'description': 'Company info line 2'},
    },
    
    LARSRecordType.TRANSACTION: {
        # CORRECTED based on your analysis:
        # '30000001312025081320250814122089xxxxx7461    SB97820000000000004000000000000000000001000000060000000'
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (30000)'},
        'SEQUENCE_NUMBER': {'start': 5, 'length': 3, 'type': 'string', 'required': True, 'description': 'Sequence number'},
        'ITEM_NUMBER': {'start': 8, 'length': 5, 'type': 'string', 'required': True, 'description': 'Item number'},
        'SALES_DATE': {'start': 13, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Sales date (YYYYMMDD)'},
        'PROCESSING_DATE': {'start': 21, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Processing date (YYYYMMDD)'},
        'CARD_NUMBER': {'start': 29, 'length': 19, 'type': 'string', 'required': True, 'description': 'Card number'},
        'CARD_TYPE': {'start': 48, 'length': 2, 'type': 'string', 'required': False, 'description': 'Card type (SB, HB, etc.)'},
        'NET_AMOUNT': {'start': 50, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Net amount'},
        'VAT_RATE': {'start': 65, 'length': 8, 'type': 'decimal', 'required': False, 'precision': 4, 'description': 'VAT rate'},
        'VAT_AMOUNT': {'start': 73, 'length': 8, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'VAT amount'},
        'CONVERSION_RATE': {'start': 81, 'length': 8, 'type': 'decimal', 'required': False, 'precision': 5, 'description': 'Conversion rate'},
        'CONVERSION_DECIMALS': {'start': 89, 'length': 2, 'type': 'integer', 'required': False, 'description': 'Conversion decimals'},
        'GROSS_AMOUNT': {'start': 91, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Gross amount'},
        'INSURANCE_AMOUNT': {'start': 106, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Insurance amount'},
        'TOTAL_AMOUNT': {'start': 115, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Total amount'},
        'CUSTOMER_NAME': {'start': 130, 'length': 50, 'type': 'string', 'required': False, 'description': 'Customer name'},
        'FILLER': {'start': 180, 'length': 60, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TRANSACTION_LINE1: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (30001)'},
        'FILLER': {'start': 5, 'length': 180, 'type': 'string', 'required': False, 'description': 'Customer info continuation'},
    },
    
    LARSRecordType.FLIGHT_INFO: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (40000)'},
        'FILLER': {'start': 5, 'length': 290, 'type': 'string', 'required': False, 'description': 'Flight/ticket information'},
    },
    
    LARSRecordType.TICKET_DETAIL: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (59000)'},
        'FILLER': {'start': 5, 'length': 310, 'type': 'string', 'required': False, 'description': 'Ticket detail information'},
    },
    
    LARSRecordType.FOOTER: {
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (70000)'},
        'TOTAL_RECORDS': {'start': 5, 'length': 8, 'type': 'integer', 'required': True, 'description': 'Total number of records'},
        'FILLER': {'start': 13, 'length': 387, 'type': 'string', 'required': False, 'description': 'Footer filler'},
    }
}


# Validation rules for your format
CORRECTED_VALIDATION_RULES = {
    'date_format': r'^\d{8}$',  # YYYYMMDD
    'amount_format': r'^-?\d+\.?\d*$',
    'currency_code': r'^[A-Z]{3}$',
    'record_type': r'^\d{5}$',  # 5-digit record types
}


def get_record_type_from_line(line: str) -> str:
    """Extract record type from a line (first 5 characters)"""
    if len(line) >= 5:
        return line[:5]
    return "UNKNOWN"


def get_field_definitions(record_type: str) -> Dict:
    """Get field definitions for a specific record type"""
    for enum_type, definitions in CORRECTED_FIELD_DEFINITIONS.items():
        if enum_type.value == record_type:
            return definitions
    return {}


if __name__ == "__main__":
    # Print the field definitions for reference
    print("Corrected LARS Field Definitions:")
    print("=" * 80)
    
    for record_type_enum, fields in CORRECTED_FIELD_DEFINITIONS.items():
        print(f"\nRecord Type: {record_type_enum.value}")
        print("-" * 60)
        for field_name, field_def in sorted(fields.items(), key=lambda x: x[1]['start']):
            start = field_def['start']
            length = field_def['length']
            field_type = field_def['type']
            required = field_def.get('required', False)
            description = field_def.get('description', field_name)
            
            print(f"  {start:3d}-{start+length:3d}: {field_name:25s} ({field_type:8s}, {'REQ' if required else 'OPT'}) - {description}")
