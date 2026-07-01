#!/usr/bin/env python3
"""
Custom LARS File Configuration
===============================

This file contains the field definitions for your specific LARS file format.
Based on the provided structure for Record Type 300 (SN00).

To use this configuration:
1. Import it in your main.py or create a custom validator
2. Use LARSConfig.FIELD_DEFINITIONS instead of the default ones

Record Type 300 (SN00) Structure:
- Fixed width fields
- Positions are 1-based in the documentation, converted to 0-based for Python
- All fields are strings unless specified otherwise
"""

from enum import Enum
from typing import Dict, Any


class LARSVersion(Enum):
    """Supported LARS file versions"""
    V3_0 = "3.0"
    SN00 = "SN00"  # Your specific version


# Custom field definitions for your LARS format
# Note: Positions in the documentation are 1-based, we convert to 0-based for Python
# Example: Position 1 in docs = index 0 in Python
CUSTOM_FIELD_DEFINITIONS = {
    LARSVersion.SN00: {
        '300': {  # Record Type 300 - SN00 (Transaction Record)
            # Field definitions based on your provided structure
            'LARS-SATZ-ART': {'start': 0, 'length': 3, 'type': 'string', 'required': True, 'description': 'Record type'},
            'LARS-POS-SN': {'start': 3, 'length': 2, 'type': 'string', 'required': True, 'description': 'Sequence No (always "00")'},
            'LARS-LFD-POS': {'start': 5, 'length': 5, 'type': 'string', 'required': True, 'description': 'Item no.'},
            'LARS-VERK-DAT': {'start': 10, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Sales date'},
            'LARS-VERARB-DAT': {'start': 18, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True, 'description': 'Processing date'},
            'LARS-KA-NR': {'start': 26, 'length': 19, 'type': 'string', 'required': True, 'description': 'Card no.'},
            'LARS-S-H-POS': {'start': 45, 'length': 1, 'type': 'string', 'required': True, 'description': 'Debit/credit booking'},
            'LARS-POS-ART': {'start': 46, 'length': 1, 'type': 'string', 'required': True, 'description': 'Billing/charging item'},
            'LARS-VERK-WAEHR': {'start': 47, 'length': 3, 'type': 'string', 'required': True, 'description': 'Sales currency'},
            'LARS-VERK-NK': {'start': 50, 'length': 1, 'type': 'integer', 'required': True, 'description': 'Decimal places'},
            'LARS-NETTO-BETRAG': {'start': 51, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Sales amount Net'},
            'LARS-MWST-SATZ': {'start': 66, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 4, 'description': 'VAT rate'},
            'LARS-MWST-BETRAG': {'start': 75, 'length': 9, 'type': 'decimal', 'required': False, 'precision': 2, 'description': 'VAT amount'},
            'LARS-VERK-ABR-KURS': {'start': 84, 'length': 7, 'type': 'decimal', 'required': False, 'precision': 5, 'description': 'Conversion rate: sales to billing currency'},
            'LARS-VERK-ABR-KURS-NK': {'start': 91, 'length': 2, 'type': 'integer', 'required': False, 'description': 'Decimal places for conversion rate'},
            'LARS-BRUTTO-BETRAG': {'start': 93, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2, 'description': 'Gross invoice amount (exc. amount of addnl. insurance)'},
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
        # Add other record types as needed
        '01': {  # Header record (adjust as needed)
            'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True},
            # Add your header fields here
        },
        '99': {  # Footer record (adjust as needed)
            'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True},
            # Add your footer fields here
        }
    }
}


# Validation rules specific to your format
CUSTOM_VALIDATION_RULES = {
    'date_format': r'^\d{8}$',  # YYYYMMDD
    'amount_format': r'^-?\d+\.?\d*$',
    'currency_code': r'^[A-Z0-9]{3}$',  # Allow numeric currency codes too
    'card_number': r'^\d{13,19}$',
    'record_type': r'^\d{3}$',  # 3-digit record types
}


def get_custom_field_definitions(version=None):
    """
    Get field definitions for your custom LARS format.
    
    Args:
        version: LARSVersion enum or string. If None, returns SN00 definitions.
    
    Returns:
        Dictionary of field definitions
    """
    if version is None:
        return CUSTOM_FIELD_DEFINITIONS[LARSVersion.SN00]
    
    if isinstance(version, str):
        version = LARSVersion(version)
    
    return CUSTOM_FIELD_DEFINITIONS.get(version, CUSTOM_FIELD_DEFINITIONS[LARSVersion.SN00])


if __name__ == "__main__":
    # Print the field definitions for reference
    print("Custom LARS Field Definitions for Record Type 300 (SN00):")
    print("=" * 60)
    
    for record_type, fields in CUSTOM_FIELD_DEFINITIONS[LARSVersion.SN00].items():
        print(f"\nRecord Type: {record_type}")
        print("-" * 40)
        for field_name, field_def in fields.items():
            start = field_def['start']
            length = field_def['length']
            field_type = field_def['type']
            required = field_def.get('required', False)
            description = field_def.get('description', '')
            
            print(f"  {start:3d}-{start+length:3d}: {field_name:20s} ({field_type:8s}, {'REQ' if required else 'OPT'}) - {description}")
