# Custom LARS Format Configuration

This directory contains a **custom configuration** specifically for your LARS file format with **Record Type 300 (SN00)**.

## 📁 **Files Included**

| File | Purpose | Usage |
|------|---------|-------|
| `lars_config.py` | Field definitions for your format | Import in custom scripts |
| `validator_custom.py` | Custom validator using your format | `from validator_custom import CustomLARSValidator` |
| `cli_custom.py` | Command line interface for your format | `python cli_custom.py validate file.lrs` |

## 🎯 **Your File Structure (Record Type 300 - SN00)**

Based on the configuration you provided, here's your record structure:

### **Field Definitions**

| Pos. | Field Name | Length | Type | Required | Description |
|------|------------|--------|------|----------|-------------|
| 1-3 | LARS-SATZ-ART | 3 | string | ✅ | Record type (300) |
| 4-5 | LARS-POS-SN | 2 | string | ✅ | Sequence No (always "00") |
| 6-10 | LARS-LFD-POS | 5 | string | ✅ | Item no. |
| 11-18 | LARS-VERK-DAT | 8 | date | ✅ | Sales date (YYYYMMDD) |
| 19-26 | LARS-VERARB-DAT | 8 | date | ✅ | Processing date (YYYYMMDD) |
| 27-45 | LARS-KA-NR | 19 | string | ✅ | Card no. |
| 46 | LARS-S-H-POS | 1 | string | ✅ | Debit/credit booking (D/C/H) |
| 47 | LARS-POS-ART | 1 | string | ✅ | Billing/charging item (1-4) |
| 48-50 | LARS-VERK-WAEHR | 3 | string | ✅ | Sales currency |
| 51 | LARS-VERK-NK | 1 | integer | ✅ | Decimal places |
| 52-66 | LARS-NETTO-BETRAG | 15 | decimal | ✅ | Sales amount Net |
| 67-75 | LARS-MWST-SATZ | 9 | decimal | ❌ | VAT rate |
| 76-84 | LARS-MWST-BETRAG | 9 | decimal | ❌ | VAT amount |
| 85-91 | LARS-VERK-ABR-KURS | 7 | decimal | ❌ | Conversion rate |
| 92-93 | LARS-VERK-ABR-KURS-NK | 2 | integer | ❌ | Decimal places for conversion rate |
| 94-108 | LARS-BRUTTO-BETRAG | 15 | decimal | ✅ | Gross invoice amount |
| 109-117 | LARS-ZV-BETRAG | 9 | decimal | ❌ | Amount for addnl. insurance |
| 118-132 | LARS-POS-BETRAG | 15 | decimal | ✅ | Total amount for item |
| 133-162 | LARS-NAME | 30 | string | ❌ | Customer |
| 163-164 | LARS-HK | 2 | string | ❌ | Transaction type/origin |
| 165-177 | LARS-TC-NR | 13 | string | ❌ | Reference/transaction no. |
| 178-179 | LARS-400-COUNT | 2 | integer | ❌ | 400 counter |
| 180-181 | LARS-5XX-COUNT | 2 | integer | ❌ | 5xx counter |
| 182-183 | LARS-600-COUNT | 2 | integer | ❌ | 600 counter |
| 184 | LARS-FAKTURA | 1 | string | ❌ | FAKTURA check identifier |
| 185 | LARS-BENUTZER | 1 | string | ❌ | User check identifier |
| 186-400 | LARS-FILLER-300-00 | 215 | string | ❌ | Filler |

**Note:** Positions in the table above are **1-based** (as in your documentation). In the code, they are **0-based** (Python uses 0-based indexing).

## 🚀 **How to Use the Custom Configuration**

### **Option 1: Use the Custom CLI (Recommended)**

The easiest way to validate your files:

```bash
# Validate a file
python cli_custom.py validate yourfile.lrs

# Repair a file
python cli_custom.py repair yourfile.lrs --output fixed.lrs

# Show file information
python cli_custom.py info yourfile.lrs

# Export validated file
python cli_custom.py export yourfile.lrs --output validated.lrs
```

### **Option 2: Use the Custom Validator in Python**

```python
from validator_custom import CustomLARSValidator

# Create validator
validator = CustomLARSValidator()

# Parse and validate a file
lars_file = validator.parse_file("yourfile.lrs")
errors = validator.validate_file(lars_file)

# Get summary
summary = validator.get_summary(lars_file)
print(summary)

# Apply auto-fixes
fixed_file, fixes_applied = validator.apply_auto_fixes(lars_file)

# Export fixed file
validator.export_file(fixed_file, "fixed.lrs")
```

### **Option 3: Quick Validation Function**

```python
from validator_custom import validate_lrs_file

# Quick validation
summary = validate_lrs_file("yourfile.lrs")
print(summary)
```

## 🔧 **Customizing the Configuration**

If you need to modify the field definitions:

1. **Edit `lars_config.py`**
2. **Update the `CUSTOM_FIELD_DEFINITIONS`** dictionary
3. **Adjust field positions, lengths, and types** as needed

### **Example: Adding a New Record Type**

```python
# In lars_config.py
CUSTOM_FIELD_DEFINITIONS = {
    LARSVersion.SN00: {
        # ... existing record types ...
        '01': {  # Header record
            'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True},
            'COMPANY_CODE': {'start': 3, 'length': 10, 'type': 'string', 'required': True},
            'CREATION_DATE': {'start': 13, 'length': 8, 'type': 'date', 'format': '%Y%m%d', 'required': True},
            # ... more header fields ...
        },
        '99': {  # Footer record
            'RECORD_TYPE': {'start': 0, 'length': 3, 'type': 'string', 'required': True},
            'TOTAL_RECORDS': {'start': 3, 'length': 6, 'type': 'integer', 'required': True},
            'TOTAL_AMOUNT': {'start': 9, 'length': 15, 'type': 'decimal', 'required': True, 'precision': 2},
            # ... more footer fields ...
        }
    }
}
```

## 📊 **Field Types and Validation**

| Type | Description | Validation | Example |
|------|-------------|------------|---------|
| `string` | Text field | Always valid | "ABC123" |
| `date` | Date field | Must match format | "20231201" |
| `decimal` | Decimal number | Must be valid number | "1250.50" |
| `integer` | Whole number | Must be valid integer | "1250" |

### **Special Field Validations**

The custom validator includes **additional validation rules** for your specific fields:

- **LARS-SATZ-ART**: Must be "300"
- **LARS-POS-SN**: Should be "00" (auto-fixable)
- **LARS-S-H-POS**: Must be "D", "C", or "H" (debit/credit)
- **LARS-POS-ART**: Must be "1", "2", "3", or "4" (billing item)
- **LARS-VERK-WAEHR**: Must be 3-character alphanumeric currency code

## 🎯 **Common Tasks**

### **1. Validate a File**
```bash
python cli_custom.py validate yourfile.lrs
```

### **2. Repair and Save a File**
```bash
python cli_custom.py repair yourfile.lrs --output fixed.lrs
```

### **3. Check File Information**
```bash
python cli_custom.py info yourfile.lrs
```

### **4. Export Validated File**
```bash
python cli_custom.py export yourfile.lrs --output validated.lrs
```

## 🐛 **Troubleshooting**

### **"Record type not found"**
If you get errors about unknown record types:
1. Check the first 3 characters of each line in your file
2. Add the missing record type to `CUSTOM_FIELD_DEFINITIONS` in `lars_config.py`

### **"Field truncated"**
If fields are being truncated:
1. Check the `length` parameter for the field in `lars_config.py`
2. Increase the length if needed
3. Make sure the `start` position is correct

### **"Invalid date format"**
If dates aren't parsing correctly:
1. Check the `format` parameter for date fields
2. Your format uses `'%Y%m%d'` for YYYYMMDD
3. If your dates use a different format, update the `format` parameter

## 📝 **File Format Notes**

- **Record Type 300** is your main transaction record
- **Positions are 0-based** in the code (1-based in your documentation)
- **All fields are fixed-width** - each field occupies a specific number of characters
- **Dates are in YYYYMMDD format** (8 digits)
- **Decimal fields** can have implied decimal places (e.g., 1250 with 2 decimal places = 12.50)
- **Filler fields** are typically spaces and can be ignored

## 🔗 **Integration with Existing Code**

If you want to use the custom configuration with the existing GUI:

1. **Modify `gui_fixed.py`** to use the custom validator:
```python
# In gui_fixed.py, change:
from main import LARSValidator

# To:
from validator_custom import CustomLARSValidator as LARSValidator
```

2. **Or create a new GUI** that uses the custom validator

## 📚 **Additional Resources**

- **Main Documentation**: See `README.md` for general usage
- **Field Definitions**: See `lars_config.py` for your specific format
- **Validation Logic**: See `validator_custom.py` for custom validation rules

---

**Custom LARS Validator** - Tailored for your Record Type 300 (SN00) format
