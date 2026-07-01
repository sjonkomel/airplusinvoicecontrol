#!/usr/bin/env python3
"""
Final LARS File Configuration
==============================

This file contains the FINAL CORRECTED field definitions for your actual LARS file format.
Based on the user's clarification that record types are 3 digits, not 5.

Record Types in your file:
- 200: File header
- 201: Header continuation line 1
- 202: Header continuation line 2
- 300: Main transaction record
- 301: Transaction continuation (customer info)
- 400: Flight/ticket information
- 590: Additional transaction details
- 700: File footer

Note: All positions are 0-based (Python indexing).
Record types are 3 digits (positions 0-3).
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


# FINAL CORRECTED Field definitions for your actual LARS format
# Record types are 3 digits (0-3), not 5 digits
FINAL_FIELD_DEFINITIONS = {
    LARSRecordType.HEADER: {
        # 2008330024025000      A20250818DTB2951                  LASG                     122089xxxxx7461
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (200)'},
        'FILE_ID': {'start': 3, 'length': 8, 'type': 'string', 'required': False, 'description': 'File identification'},
        'UNKNOWN1': {'start': 11, 'length': 8, 'type': 'string', 'required': False, 'description': 'Unknown field 1'},
        'COMPANY_CODE': {'start': 19, 'length': 10, 'type': 'string', 'required': False, 'description': 'Company code'},
        'SYSTEM_ID': {'start': 29, 'length': 10, 'type': 'string', 'required': False, 'description': 'System identifier'},
        'CARD_NUMBER': {'start': 39, 'length': 20, 'type': 'string', 'required': False, 'description': 'Card number'},
        'TRANSACTION_REF': {'start': 59, 'length': 10, 'type': 'string', 'required': False, 'description': 'Transaction reference'},
        'AMOUNT1': {'start': 69, 'length': 15, 'type': 'string', 'required': False, 'description': 'Amount field 1'},
        'CURRENCY1': {'start': 84, 'length': 3, 'type': 'string', 'required': False, 'description': 'Currency code 1'},
        'AMOUNT2': {'start': 87, 'length': 15, 'type': 'string', 'required': False, 'description': 'Amount field 2'},
        'VERSION': {'start': 102, 'length': 11, 'type': 'string', 'required': False, 'description': 'Version'},
        'COUNTRY_CODE': {'start': 113, 'length': 2, 'type': 'string', 'required': False, 'description': 'Country code'},
        'BANK_CODE': {'start': 115, 'length': 15, 'type': 'string', 'required': False, 'description': 'Bank code'},
        'COMPANY_ACCOUNT': {'start': 130, 'length': 20, 'type': 'string', 'required': False, 'description': 'Company account number'},
        'FILLER': {'start': 150, 'length': 90, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.HEADER_LINE1: {
        # 201International Criminal Court       Oude Waalsdorperweg 10             2597 AK 'S-GRAVENHAGE
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (201)'},
        'COMPANY_NAME': {'start': 3, 'length': 40, 'type': 'string', 'required': False, 'description': 'Company name'},
        'ADDRESS_LINE1': {'start': 43, 'length': 40, 'type': 'string', 'required': False, 'description': 'Address line 1'},
        'POSTAL_CODE1': {'start': 83, 'length': 10, 'type': 'string', 'required': False, 'description': 'Postal code 1'},
        'CITY1': {'start': 93, 'length': 20, 'type': 'string', 'required': False, 'description': 'City 1'},
        'COUNTRY1': {'start': 113, 'length': 20, 'type': 'string', 'required': False, 'description': 'Country 1'},
        'POSTAL_CODE2': {'start': 133, 'length': 10, 'type': 'string', 'required': False, 'description': 'Postal code 2'},
        'CITY2': {'start': 143, 'length': 20, 'type': 'string', 'required': False, 'description': 'City 2'},
        'COUNTRY2': {'start': 163, 'length': 20, 'type': 'string', 'required': False, 'description': 'Country 2'},
        'FILLER': {'start': 183, 'length': 17, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.HEADER_LINE2: {
        # 202AirPlus International GmbH                                            Dornhofstrasse 10
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (202)'},
        'COMPANY_NAME2': {'start': 3, 'length': 40, 'type': 'string', 'required': False, 'description': 'Company name continuation'},
        'ADDRESS_LINE2': {'start': 43, 'length': 40, 'type': 'string', 'required': False, 'description': 'Address line 2'},
        'POSTAL_CODE': {'start': 83, 'length': 10, 'type': 'string', 'required': False, 'description': 'Postal code'},
        'CITY': {'start': 93, 'length': 20, 'type': 'string', 'required': False, 'description': 'City'},
        'COUNTRY': {'start': 113, 'length': 20, 'type': 'string', 'required': False, 'description': 'Country'},
        'BANK_CODE1': {'start': 133, 'length': 20, 'type': 'string', 'required': False, 'description': 'Bank code 1'},
        'BANK_CODE2': {'start': 153, 'length': 20, 'type': 'string', 'required': False, 'description': 'Bank code 2'},
        'BANK_CODE3': {'start': 173, 'length': 20, 'type': 'string', 'required': False, 'description': 'Bank code 3'},
        'FILLER': {'start': 193, 'length': 177, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TRANSACTION: {
        # 300001312025081320250814122089xxxxx7461    SB97820000000000004000000000000000000001000000060000000
        # Based on user's breakdown:
        # 0-10: '3000000131' -> Record type (300) + Sequence (001) + Item (31202)
        # But user says first column is record type of length 3
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (300)'},
        'SEQUENCE_NUMBER': {'start': 3, 'length': 3, 'type': 'string', 'required': True, 'description': 'Sequence number'},
        'ITEM_NUMBER': {'start': 6, 'length': 5, 'type': 'string', 'required': True, 'description': 'Item number'},
        'SALES_DATE': {'start': 11, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Sales date (YYYYMMDD)'},
        'PROCESSING_DATE': {'start': 19, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Processing date (YYYYMMDD)'},
        'CARD_NUMBER': {'start': 27, 'length': 19, 'type': 'string', 'required': True, 'description': 'Card number'},
        'CARD_TYPE': {'start': 46, 'length': 2, 'type': 'string', 'required': False, 'description': 'Card type (SB, HB, etc.)'},
        'NET_AMOUNT': {'start': 48, 'length': 15, 'type': 'string', 'required': False, 'description': 'Net amount'},
        'VAT_RATE': {'start': 63, 'length': 8, 'type': 'string', 'required': False, 'description': 'VAT rate'},
        'VAT_AMOUNT': {'start': 71, 'length': 8, 'type': 'string', 'required': False, 'description': 'VAT amount'},
        'CONVERSION_RATE': {'start': 79, 'length': 8, 'type': 'string', 'required': False, 'description': 'Conversion rate'},
        'CONVERSION_DECIMALS': {'start': 87, 'length': 2, 'type': 'string', 'required': False, 'description': 'Conversion decimals'},
        'GROSS_AMOUNT': {'start': 89, 'length': 15, 'type': 'string', 'required': False, 'description': 'Gross amount'},
        'INSURANCE_AMOUNT': {'start': 104, 'length': 9, 'type': 'string', 'required': False, 'description': 'Insurance amount'},
        'TOTAL_AMOUNT': {'start': 113, 'length': 15, 'type': 'string', 'required': False, 'description': 'Total amount'},
        'CUSTOMER_NAME': {'start': 128, 'length': 50, 'type': 'string', 'required': False, 'description': 'Customer name'},
        'FILLER': {'start': 178, 'length': 62, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TRANSACTION_LINE1: {
        # 301Schiphol Travel B.V.          Schiphol Boulevard 235        1118 BH Schiphol
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (301)'},
        'CUSTOMER_NAME_FULL': {'start': 3, 'length': 40, 'type': 'string', 'required': False, 'description': 'Full customer name'},
        'CUSTOMER_ADDRESS': {'start': 43, 'length': 40, 'type': 'string', 'required': False, 'description': 'Customer address'},
        'CUSTOMER_POSTAL': {'start': 83, 'length': 10, 'type': 'string', 'required': False, 'description': 'Customer postal code'},
        'CUSTOMER_CITY': {'start': 93, 'length': 20, 'type': 'string', 'required': False, 'description': 'Customer city'},
        'COUNTRY_CODE': {'start': 113, 'length': 3, 'type': 'string', 'required': False, 'description': 'Country code'},
        'CUSTOMER_REF': {'start': 116, 'length': 10, 'type': 'string', 'required': False, 'description': 'Customer reference'},
        'INVOICE_NUMBER': {'start': 126, 'length': 13, 'type': 'string', 'required': False, 'description': 'Invoice number'},
        'FILLER': {'start': 139, 'length': 61, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.FLIGHT_INFO: {
        # 400206861                                                      3220TF
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (400)'},
        'FLIGHT_NUMBER': {'start': 3, 'length': 10, 'type': 'string', 'required': False, 'description': 'Flight number'},
        'FILLER': {'start': 13, 'length': 287, 'type': 'string', 'required': False, 'description': 'Flight/ticket information'},
    },
    
    LARSRecordType.TICKET_DETAIL: {
        # 590Schiphol Travel B.V.                         KL0742884051567 Class Q on 10.09.2025
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (590)'},
        'FILLER': {'start': 3, 'length': 312, 'type': 'string', 'required': False, 'description': 'Ticket detail information'},
    },
    
    LARSRecordType.FOOTER: {
        # 7000013500000671000000003396949000000000000000000000000002936057000000000000000000000000000002936057
        'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type (700)'},
        'TOTAL_RECORDS': {'start': 3, 'length': 8, 'type': 'string', 'required': False, 'description': 'Total number of records'},
        'FILLER': {'start': 11, 'length': 389, 'type': 'string', 'required': False, 'description': 'Footer filler'},
    }
}


# Validation rules for your format
FINAL_VALIDATION_RULES = {
    'date_format': r'^\d{8}$',  # YYYYMMDD
    'amount_format': r'^-?\d+\.?\d*$',
    'currency_code': r'^[A-Z]{3}$',
    'record_type': r'^\d{3}$',  # 3-digit record types
}


def get_record_type_from_line(line: str) -> str:
    """Extract record type from a line (first 3 characters)"""
    if len(line) >= 3:
        return line[:3]
    return "UNKNOWN"


def get_field_definitions(record_type: str) -> Dict:
    """Get field definitions for a specific record type"""
    for enum_type, definitions in FINAL_FIELD_DEFINITIONS.items():
        if enum_type.value == record_type:
            return definitions
    return {}


if __name__ == "__main__":
    # Print the field definitions for reference
    print("Final LARS Field Definitions (3-digit record types):")
    print("=" * 80)
    
    for record_type_enum, fields in FINAL_FIELD_DEFINITIONS.items():
        print(f"\nRecord Type: {record_type_enum.value}")
        print("-" * 60)
        for field_name, field_def in sorted(fields.items(), key=lambda x: x[1]['start']):
            start = field_def['start']
            length = field_def['length']
            field_type = field_def['type']
            required = field_def.get('required', False)
            description = field_def.get('description', field_name)
            
            print(f"  {start:3d}-{start+length:3d}: {field_name:25s} ({field_type:8s}, {'REQ' if required else 'OPT'}) - {description}")
