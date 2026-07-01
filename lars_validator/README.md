# LARS File Validator and Repair Tool

A comprehensive application for validating and repairing AIRPLUS LARS invoice files before uploading to ERP systems. This tool helps travel assistants ensure their LARS files are correctly formatted and free from errors.

## Features

- **File Parsing**: Automatically parse LARS files (versions 2.0 and 3.0)
- **Validation**: Comprehensive validation of file structure, fields, and data
- **Error Detection**: Automatic detection of common LARS file errors
- **Error Repair**: Automatic and manual repair options for detected errors
- **Export**: Export corrected files for use in ERP systems
- **Multiple Interfaces**: Both graphical (GUI) and command-line (CLI) interfaces
- **Local Execution**: Runs locally on Windows, macOS, and Linux

## Supported LARS Versions

- **LARS Version 2.0** - Legacy format
- **LARS Version 3.0** - Current format (recommended)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Quick Installation

```bash
# Clone or download the repository
cd lars-validator

# Install the package
pip install .

# Or install in development mode
pip install -e .
```

### Install Dependencies

```bash
# Install basic dependencies
pip install -r requirements.txt

# For development
pip install -r requirements.txt -e ".[dev]"
```

### Install Tkinter (for GUI)

Tkinter is usually included with Python, but you might need to install it separately:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Windows:**
Tkinter is typically included with Python installations on Windows.

## Usage

### Graphical User Interface (GUI)

Run the GUI application:

```bash
# Run directly
python -m lars_validator.gui

# Or use the installed command
lars-gui
```

**GUI Features:**
- Drag and drop file selection
- Visual error display with color coding
- Interactive error filtering
- One-click auto-fix application
- Export corrected files
- Detailed error information

### Command Line Interface (CLI)

The CLI provides several commands for different operations:

#### Validate a File

```bash
# Basic validation
lars-validator validate myfile.txt

# With verbose output
lars-validator validate myfile.txt --verbose
```

#### Repair a File

```bash
# Repair and show results
lars-validator repair myfile.txt

# Repair and save to new file
lars-validator repair myfile.txt --output fixed.txt

# With verbose output
lars-validator repair myfile.txt --output fixed.txt --verbose
```

#### Export a File

```bash
# Export validated file
lars-validator export myfile.txt --output validated.txt
```

#### Show File Information

```bash
# Show file info
lars-validator info myfile.txt

# With verbose output
lars-validator info myfile.txt --verbose
```

### Command Line Help

```bash
# Show all commands
lars-validator --help

# Show help for specific command
lars-validator validate --help
lars-validator repair --help
lars-validator export --help
lars-validator info --help
```

## Error Types Detected

The validator detects and can fix many common LARS file errors:

### Critical Errors
- Missing header record (type 01)
- Missing footer record (type 99)
- Unknown record types

### Validation Errors
- Missing required fields
- Invalid date formats
- Invalid decimal/amount formats
- Invalid integer formats
- Invalid currency codes
- Invalid card numbers
- Field truncation

### Warnings
- Multiple currencies in file
- Invalid card number formats
- Decimal precision issues

### Information
- General file structure issues
- Non-critical formatting problems

## Automatic Fixes

The tool can automatically fix many common issues:

- **Date Format**: Corrects various date formats to YYYYMMDD
- **Decimal Formatting**: Fixes decimal number formatting
- **Integer Formatting**: Fixes integer formatting
- **Record Count**: Updates footer record count to match actual records
- **Field Truncation**: Handles truncated fields where possible

## File Structure

LARS files have a fixed-width format with the following structure:

### Header Record (Type 01)
- Contains file metadata (version, company code, creation date, etc.)
- Required for all LARS files

### Transaction Records (Type 02, 03, etc.)
- Individual transaction data
- Contains card numbers, amounts, dates, merchant information
- Multiple transaction records per file

### Footer Record (Type 99)
- File summary information
- Contains total record count and amounts
- Required for all LARS files

## Example LARS File

```
013.0   COMPANY1  20231215FILE001          EUR
0201    1234567890123456202312012023120200012500EURMERCHANT1   INV001      CC001     Flight ticket to Paris
0201    1234567890123456202312022023120300008500EURMERCHANT2   INV002      CC002     Hotel accommodation
9900000200021000EUR
```

## Common Issues and Solutions

### Issue: Invalid Date Format
```
Error: Invalid date format for TRANSACTION_DATE. Expected %Y%m%d
Actual: 01/12/2023
Fix: 20231201
```

### Issue: Missing Required Field
```
Error: Required field CARD_NUMBER is missing or empty
Fix: Ensure card number is present in the record
```

### Issue: Invalid Amount Format
```
Error: Invalid decimal format for AMOUNT
Actual: 1,250.00
Fix: 1250.00
```

### Issue: Record Count Mismatch
```
Error: Record count mismatch: expected 10, found 8
Fix: 8 (automatically updated in footer)
```

## Configuration

The validator uses default field definitions for LARS versions 2.0 and 3.0. You can customize these by modifying the `FIELD_DEFINITIONS` dictionary in the `main.py` file.

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

### Code Formatting

```bash
# Install formatting tools
pip install black flake8 mypy

# Format code
black lars_validator/

# Check code quality
flake8 lars_validator/
mypy lars_validator/
```

### Creating a Package

```bash
# Create distribution packages
python setup.py sdist bdist_wheel

# Upload to PyPI (if you have permissions)
python -m twine upload dist/*
```

## Troubleshooting

### Tkinter Not Found

If you get an error about Tkinter not being found:

**Linux:**
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
```

**Windows:**
Reinstall Python and ensure "tcl/tk and IDLE" is selected during installation.

### File Encoding Issues

LARS files should be UTF-8 encoded. If you encounter encoding issues:

```bash
# Convert file to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.txt -o output.txt
```

### Large Files

For very large LARS files, the GUI might be slow. Use the CLI for better performance:

```bash
lars-validator validate large_file.txt
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Check the [documentation](#)
- Review the [examples](#)
- Create an issue in the repository

## References

- [AirPlus Website](https://www.airplus.com)
- [LARS Format Specification](https://www.airplus.com) (official documentation)
- [SAP LARS Processing](https://community.sap.com) (SAP integration information)

---

**LARS File Validator and Repair Tool**

*Helping travel assistants ensure accurate invoice data for ERP systems*
