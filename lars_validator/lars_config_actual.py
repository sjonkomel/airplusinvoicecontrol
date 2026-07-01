#!/usr/bin/env python3
"""
Actual LARS File Configuration
===============================

This file contains the field definitions for your ACTUAL LARS file format
based on the sample file you provided.

Record Types in your file:
- 20000: Header record (File header)
- 20001: Header continuation (Company info line 1)
- 20002: Header continuation (Company info line 2)
- 30000: Transaction record (Main transaction data)
- 30001: Transaction continuation (Customer info)
- 40000: Flight/ticket information
- 59000: Additional transaction details
- 70000: Footer record (File summary)

Note: Positions in this configuration are 0-based (Python indexing).
Your file appears to use variable-length records with fixed starting positions.
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


# Field definitions for your actual LARS format
# Based on analysis of your sample file
ACTUAL_FIELD_DEFINITIONS = {
    LARSRecordType.HEADER: {
        # 200008330024025000      A20250818DTB2951                  LASG                     122089xxxxx7461    9782J           978100000006R                                           V03.00.000 DE83ZZZ00000309554                 AIRPLUS0000000159647
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (20000)'},
        'FILE_ID': {'start': 5, 'length': 8, 'type': 'string', 'required': True, 'description': 'File identification'},
        'CREATION_DATE': {'start': 13, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Creation date'},
        'FILE_TYPE': {'start': 21, 'length': 4, 'type': 'string', 'required': True, 'description': 'File type (DTB2)'},
        'COMPANY_CODE': {'start': 25, 'length': 20, 'type': 'string', 'required': True, 'description': 'Company code'},
        'SYSTEM_ID': {'start': 45, 'length': 10, 'type': 'string', 'required': True, 'description': 'System identifier (LASG)'},
        'CARD_NUMBER': {'start': 55, 'length': 20, 'type': 'string', 'required': False, 'description': 'Card number'},
        'TRANSACTION_REF': {'start': 75, 'length': 10, 'type': 'string', 'required': False, 'description': 'Transaction reference'},
        'AMOUNT1': {'start': 85, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Amount field 1'},
        'CURRENCY1': {'start': 100, 'length': 3, 'type': 'string', 'required': False, 'description': 'Currency code 1'},
        'AMOUNT2': {'start': 103, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Amount field 2'},
        'VERSION': {'start': 118, 'length': 11, 'type': 'string', 'required': False, 'description': 'Version (V03.00.000)'},
        'COUNTRY_CODE': {'start': 129, 'length': 2, 'type': 'string', 'required': False, 'description': 'Country code (DE)'},
        'BANK_CODE': {'start': 131, 'length': 15, 'type': 'string', 'required': False, 'description': 'Bank code'},
        'COMPANY_ACCOUNT': {'start': 146, 'length': 20, 'type': 'string', 'required': False, 'description': 'Company account number'},
        'FILLER': {'start': 166, 'length': 74, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.HEADER_LINE1: {
        # 20001International Criminal Court       Oude Waalsdorperweg 10             2597 AK 'S-GRAVENHAGE              NETHERLANDS                        2597 AK   'S-Gravenhage                      NETHERLANDS
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (20001)'},
        'COMPANY_NAME': {'start': 5, 'length': 40, 'type': 'string', 'required': False, 'description': 'Company name'},
        'ADDRESS_LINE1': {'start': 45, 'length': 40, 'type': 'string', 'required': False, 'description': 'Address line 1'},
        'POSTAL_CODE1': {'start': 85, 'length': 10, 'type': 'string', 'required': False, 'description': 'Postal code 1'},
        'CITY1': {'start': 95, 'length': 20, 'type': 'string', 'required': False, 'description': 'City 1'},
        'COUNTRY1': {'start': 115, 'length': 20, 'type': 'string', 'required': False, 'description': 'Country 1'},
        'POSTAL_CODE2': {'start': 135, 'length': 10, 'type': 'string', 'required': False, 'description': 'Postal code 2'},
        'CITY2': {'start': 145, 'length': 20, 'type': 'string', 'required': False, 'description': 'City 2'},
        'COUNTRY2': {'start': 165, 'length': 20, 'type': 'string', 'required': False, 'description': 'Country 2'},
        'FILLER': {'start': 185, 'length': 16, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.HEADER_LINE2: {
        # 20002AirPlus International GmbH                                            Dornhofstrasse 10                                                     63263     Neu-Isenburg                       GERMANY                            DEDE811163358                   DE81505700180337777712                                                                                   DEUTDEFF505
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (20002)'},
        'COMPANY_NAME2': {'start': 5, 'length': 40, 'type': 'string', 'required': False, 'description': 'Company name continuation'},
        'ADDRESS_LINE2': {'start': 45, 'length': 40, 'type': 'string', 'required': False, 'description': 'Address line 2'},
        'POSTAL_CODE': {'start': 85, 'length': 10, 'type': 'string', 'required': False, 'description': 'Postal code'},
        'CITY': {'start': 95, 'length': 20, 'type': 'string', 'required': False, 'description': 'City'},
        'COUNTRY': {'start': 115, 'length': 20, 'type': 'string', 'required': False, 'description': 'Country'},
        'BANK_CODE1': {'start': 135, 'length': 20, 'type': 'string', 'required': False, 'description': 'Bank code 1'},
        'BANK_CODE2': {'start': 155, 'length': 20, 'type': 'string', 'required': False, 'description': 'Bank code 2'},
        'BANK_CODE3': {'start': 175, 'length': 20, 'type': 'string', 'required': False, 'description': 'Bank code 3'},
        'FILLER': {'start': 195, 'length': 178, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TRANSACTION: {
        # 30000001312025081320250814122089xxxxx7461    SB9782000000000000400000000000000000000100000006000000000000400000000000000000000000400Amole/Graceolapeju Ms           A801045756707020100
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (30000)'},
        'SEQUENCE_NUMBER': {'start': 5, 'length': 3, 'type': 'string', 'required': True, 'description': 'Sequence number'},
        'ITEM_NUMBER': {'start': 8, 'length': 5, 'type': 'string', 'required': True, 'description': 'Item number'},
        'SALES_DATE': {'start': 13, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Sales date'},
        'PROCESSING_DATE': {'start': 21, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Processing date'},
        'CARD_NUMBER': {'start': 29, 'length': 19, 'type': 'string', 'required': True, 'description': 'Card number'},
        'TRANSACTION_TYPE': {'start': 48, 'length': 2, 'type': 'string', 'required': True, 'description': 'Transaction type (SB)'},
        'AMOUNT_TYPE': {'start': 50, 'length': 1, 'type': 'string', 'required': False, 'description': 'Amount type'},
        'NET_AMOUNT': {'start': 51, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Net amount'},
        'VAT_RATE': {'start': 66, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 4, 'description': 'VAT rate'},
        'VAT_AMOUNT': {'start': 75, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'VAT amount'},
        'CONVERSION_RATE': {'start': 84, 'length': 7, 'type': 'decimal', 'required': False, 'precision': 5, 'description': 'Conversion rate'},
        'CONVERSION_DECIMALS': {'start': 91, 'length': 2, 'type': 'integer', 'required': False, 'description': 'Conversion decimals'},
        'GROSS_AMOUNT': {'start': 93, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Gross amount'},
        'INSURANCE_AMOUNT': {'start': 108, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Insurance amount'},
        'TOTAL_AMOUNT': {'start': 117, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Total amount'},
        'CUSTOMER_NAME': {'start': 132, 'length': 30, 'type': 'string', 'required': False, 'description': 'Customer name'},
        'TRANSACTION_ORIGIN': {'start': 162, 'length': 2, 'type': 'string', 'required': False, 'description': 'Transaction origin'},
        'REFERENCE_NUMBER': {'start': 164, 'length': 13, 'type': 'string', 'required': False, 'description': 'Reference number'},
        'FILLER': {'start': 177, 'length': 63, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TRANSACTION_LINE1: {
        # 30001Schiphol Travel B.V.          Schiphol Boulevard 235        1118 BH Schiphol                                                                      01          000    NN0742884051567
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (30001)'},
        'CUSTOMER_NAME_FULL': {'start': 5, 'length': 40, 'type': 'string', 'required': False, 'description': 'Full customer name'},
        'CUSTOMER_ADDRESS': {'start': 45, 'length': 40, 'type': 'string', 'required': False, 'description': 'Customer address'},
        'CUSTOMER_POSTAL': {'start': 85, 'length': 10, 'type': 'string', 'required': False, 'description': 'Customer postal code'},
        'CUSTOMER_CITY': {'start': 95, 'length': 20, 'type': 'string', 'required': False, 'description': 'Customer city'},
        'COUNTRY_CODE': {'start': 115, 'length': 3, 'type': 'string', 'required': False, 'description': 'Country code'},
        'CUSTOMER_REF': {'start': 118, 'length': 10, 'type': 'string', 'required': False, 'description': 'Customer reference'},
        'INVOICE_NUMBER': {'start': 128, 'length': 13, 'type': 'string', 'required': False, 'description': 'Invoice number'},
        'FILLER': {'start': 141, 'length': 44, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.FLIGHT_INFO: {
        # 40000206861                                                      3220TF                        R                             T303-FRA                      20250910         54369                                                       Y                             AMSTERDAM
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (40000)'},
        'FLIGHT_NUMBER': {'start': 5, 'length': 10, 'type': 'string', 'required': False, 'description': 'Flight number'},
        'AIRLINE_CODE': {'start': 15, 'length': 5, 'type': 'string', 'required': False, 'description': 'Airline code'},
        'TICKET_TYPE': {'start': 20, 'length': 1, 'type': 'string', 'required': False, 'description': 'Ticket type'},
        'ROUTE': {'start': 21, 'length': 20, 'type': 'string', 'required': False, 'description': 'Route'},
        'FLIGHT_DATE': {'start': 41, 'length': 10, 'type': 'date', 'format': '%Y%m%d', 'required': False, 'description': 'Flight date'},
        'TICKET_NUMBER': {'start': 51, 'length': 15, 'type': 'string', 'required': False, 'description': 'Ticket number'},
        'DEPARTURE_AIRPORT': {'start': 66, 'length': 3, 'type': 'string', 'required': False, 'description': 'Departure airport'},
        'ARRIVAL_AIRPORT': {'start': 69, 'length': 3, 'type': 'string', 'required': False, 'description': 'Arrival airport'},
        'CLASS': {'start': 72, 'length': 1, 'type': 'string', 'required': False, 'description': 'Class'},
        'FILLER': {'start': 73, 'length': 222, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.TICKET_DETAIL: {
        # 59000Schiphol Travel B.V.                         KL0742884051567 Class Q on 10.09.2025        TICKET 07428840515670                        A                                        472320250910000000000000000000000000000400S000000000000000000TS000000000000400
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (59000)'},
        'CUSTOMER_NAME_DETAIL': {'start': 5, 'length': 40, 'type': 'string', 'required': False, 'description': 'Customer name for detail'},
        'TICKET_REFERENCE': {'start': 45, 'length': 20, 'type': 'string', 'required': False, 'description': 'Ticket reference'},
        'TICKET_DESCRIPTION': {'start': 65, 'length': 30, 'type': 'string', 'required': False, 'description': 'Ticket description'},
        'TICKET_NUMBER_DETAIL': {'start': 95, 'length': 20, 'type': 'string', 'required': False, 'description': 'Ticket number detail'},
        'TICKET_TYPE': {'start': 115, 'length': 1, 'type': 'string', 'required': False, 'description': 'Ticket type'},
        'TRANSACTION_DATE': {'start': 116, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': False, 'description': 'Transaction date'},
        'AMOUNT_DETAIL': {'start': 124, 'length': 30, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Amount detail'},
        'CURRENCY_DETAIL': {'start': 154, 'length': 3, 'type': 'string', 'required': False, 'description': 'Currency detail'},
        'FILLER': {'start': 157, 'length': 143, 'type': 'string', 'required': False, 'description': 'Filler'},
    },
    
    LARSRecordType.FOOTER: {
        # 700000013500000671000000003396949000000000000000000000000293605700000000000000000000000000000293605720250901000000002936057000000000000000002936057NNSS000000000000000000000000    000000000000000000000000    000000000000000000000000    000000000000000000000000    000000000000000000000000    000000000000000000000000
        'RECORD_TYPE': {'start': 0, 'length': 5, 'type': 'string', 'required': True, 'description': 'Record type (70000)'},
        'TOTAL_RECORDS': {'start': 5, 'length': 8, 'type': 'integer', 'required': True, 'description': 'Total number of records'},
        'TOTAL_AMOUNT1': {'start': 13, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 1'},
        'TOTAL_AMOUNT2': {'start': 28, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 2'},
        'TOTAL_AMOUNT3': {'start': 43, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 3'},
        'TOTAL_AMOUNT4': {'start': 58, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 4'},
        'TOTAL_AMOUNT5': {'start': 73, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 5'},
        'TOTAL_AMOUNT6': {'start': 88, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 6'},
        'TOTAL_AMOUNT7': {'start': 103, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 7'},
        'TOTAL_AMOUNT8': {'start': 118, 'length': 15, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'Total amount 8'},
        'CURRENCY_CODE': {'start': 133, 'length': 3, 'type': 'string', 'required': False, 'description': 'Currency code'},
        'FILLER': {'start': 136, 'length': 264, 'type': 'string', 'required': False, 'description': 'Filler'},
    }
}


# Validation rules for your actual format
ACTUAL_VALIDATION_RULES = {
    'date_format': r'^\d{8}$',  # YYYYMMDD
    'amount_format': r'^-?\d+\.?\d*$',
    'currency_code': r'^[A-Z]{3}$',
    'card_number': r'^\d{13,19}$',
    'record_type': r'^\d{5}$',  # 5-digit record types
}


def get_record_type_from_line(line: str) -> str:
    """Extract record type from a line (first 5 characters)"""
    if len(line) >= 5:
        return line[:5]
    return "UNKNOWN"


def get_field_definitions(record_type: str) -> Dict:
    """Get field definitions for a specific record type"""
    for enum_type, definitions in ACTUAL_FIELD_DEFINITIONS.items():
        if enum_type.value == record_type:
            return definitions
    return {}


if __name__ == "__main__":
    # Print the field definitions for reference
    print("Actual LARS Field Definitions:")
    print("=" * 80)
    
    for record_type_enum, fields in ACTUAL_FIELD_DEFINITIONS.items():
        print(f"\nRecord Type: {record_type_enum.value}")
        print("-" * 60)
        for field_name, field_def in sorted(fields.items(), key=lambda x: x[1]['start']):
            start = field_def['start']
            length = field_def['length']
            field_type = field_def['type']
            required = field_def.get('required', False)
            description = field_def.get('description', field_name)
            
            print(f"  {start:3d}-{start+length:3d}: {field_name:25s} ({field_type:8s}, {'REQ' if required else 'OPT'}) - {description}")
