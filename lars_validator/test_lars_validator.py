#!/usr/bin/env python3
"""
Tests for LARS File Validator and Repair Tool
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    LARSValidator, LARSFile, LARSVersion, LARSRecord, 
    ValidationError, ErrorSeverity
)


def test_version_detection():
    """Test LARS version detection"""
    validator = LARSValidator()
    
    # Create a temporary file with version 3.0
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("013.0   COMPANY1  20231215FILE001          EUR\n")
        f.write("99000000000000000EUR\n")
        temp_file = f.name
    
    try:
        version = validator.detect_version(temp_file)
        assert version == LARSVersion.V3_0, f"Expected V3_0, got {version}"
        print("✓ Version 3.0 detection works")
    finally:
        os.unlink(temp_file)
    
    # Create a temporary file with version 2.0
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("012.0   COMPANY1  20231215FILE001EUR\n")
        f.write("990000000000000EUR\n")
        temp_file = f.name
    
    try:
        version = validator.detect_version(temp_file)
        assert version == LARSVersion.V2_0, f"Expected V2_0, got {version}"
        print("✓ Version 2.0 detection works")
    finally:
        os.unlink(temp_file)


def test_file_parsing():
    """Test LARS file parsing"""
    validator = LARSValidator()
    
    # Create a sample LARS file
    sample_content = """013.0   COMPANY1  20231215FILE001          EUR
0201    1234567890123456202312012023120200012500EURMERCHANT1   INV001      CC001     Flight ticket to Paris
0201    1234567890123456202312022023120300008500EURMERCHANT2   INV002      CC002     Hotel accommodation
9900000200021000EUR
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        lars_file = validator.parse_file(temp_file)
        
        assert lars_file.version == LARSVersion.V3_0
        assert len(lars_file.records) == 4  # Header + 2 transactions + footer
        assert lars_file.header is not None
        assert lars_file.footer is not None
        
        print("✓ File parsing works")
        print(f"  - Version: {lars_file.version}")
        print(f"  - Records: {len(lars_file.records)}")
        print(f"  - Header: {lars_file.header is not None}")
        print(f"  - Footer: {lars_file.footer is not None}")
        
    finally:
        os.unlink(temp_file)


def test_validation():
    """Test LARS file validation"""
    validator = LARSValidator()
    
    # Create a sample file with some errors
    sample_content = """013.0   COMPANY1  20231215FILE001          EUR
0201    1234567890123456202312012023120200012500EURMERCHANT1   INV001      CC001     Flight ticket to Paris
0201    123456789012345601/12/20232023120300008500EURMERCHANT2   INV002      CC002     Invalid date format
0201    123456789012345620231204202312041,250.00EURMERCHANT4   INV004      CC004     Invalid amount format
0201              202312062023120600003500EURMERCHANT6   INV006      CC006     Missing card number
9900000400045500EUR
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        lars_file = validator.parse_file(temp_file)
        errors = validator.validate_file(lars_file)
        
        assert len(errors) > 0, "Expected validation errors"
        
        # Check for specific error types
        error_types = [e.error_type for e in errors]
        assert 'invalid_date_format' in error_types, "Expected date format error"
        assert 'invalid_decimal_format' in error_types, "Expected decimal format error"
        assert 'required_field_missing' in error_types, "Expected missing field error"
        
        print("✓ Validation works")
        print(f"  - Total errors: {len(errors)}")
        print(f"  - Error types: {set(error_types)}")
        
    finally:
        os.unlink(temp_file)


def test_auto_fixes():
    """Test automatic error fixing"""
    validator = LARSValidator()
    
    # Create a sample file with fixable errors
    sample_content = """013.0   COMPANY1  20231215FILE001          EUR
0201    123456789012345601/12/20232023120300008500EURMERCHANT2   INV002      CC002     Invalid date format
0201    123456789012345620231204202312041,250.00EURMERCHANT4   INV004      CC004     Invalid amount format
9900000200045500EUR
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        lars_file = validator.parse_file(temp_file)
        errors_before = validator.validate_file(lars_file)
        
        # Apply auto-fixes
        fixed_file, fixes_applied = validator.apply_auto_fixes(lars_file)
        
        assert len(fixes_applied) > 0, "Expected fixes to be applied"
        
        # Re-validate
        errors_after = validator.validate_file(fixed_file)
        
        assert len(errors_after) < len(errors_before), "Expected fewer errors after fixing"
        
        print("✓ Auto-fixes work")
        print(f"  - Fixes applied: {len(fixes_applied)}")
        print(f"  - Errors before: {len(errors_before)}")
        print(f"  - Errors after: {len(errors_after)}")
        
    finally:
        os.unlink(temp_file)


def test_export():
    """Test file export"""
    validator = LARSValidator()
    
    # Create a sample file
    sample_content = """013.0   COMPANY1  20231215FILE001          EUR
0201    1234567890123456202312012023120200012500EURMERCHANT1   INV001      CC001     Flight ticket to Paris
9900000100012500EUR
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        input_file = f.name
    
    output_file = tempfile.mktemp(suffix='.txt')
    
    try:
        lars_file = validator.parse_file(input_file)
        success = validator.export_file(lars_file, output_file)
        
        assert success, "Export failed"
        assert os.path.exists(output_file), "Output file not created"
        
        # Read and verify output
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert len(content) > 0, "Output file is empty"
        assert "013.0" in content, "Header record missing"
        assert "99000001" in content, "Footer record missing"
        
        print("✓ File export works")
        print(f"  - Input: {input_file}")
        print(f"  - Output: {output_file}")
        
    finally:
        os.unlink(input_file)
        if os.path.exists(output_file):
            os.unlink(output_file)


def test_summary():
    """Test summary generation"""
    validator = LARSValidator()
    
    # Create a sample file
    sample_content = """013.0   COMPANY1  20231215FILE001          EUR
0201    1234567890123456202312012023120200012500EURMERCHANT1   INV001      CC001     Flight ticket to Paris
0201    1234567890123456202312022023120300008500EURMERCHANT2   INV002      CC002     Hotel accommodation
9900000200021000EUR
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        lars_file = validator.parse_file(temp_file)
        validator.validate_file(lars_file)
        summary = validator.get_summary(lars_file)
        
        assert 'version' in summary
        assert 'total_records' in summary
        assert 'valid_records' in summary
        assert 'total_errors' in summary
        assert 'errors_by_severity' in summary
        
        print("✓ Summary generation works")
        print(f"  - Summary: {summary}")
        
    finally:
        os.unlink(temp_file)


def run_all_tests():
    """Run all tests"""
    print("Running LARS Validator Tests...")
    print("=" * 50)
    
    tests = [
        test_version_detection,
        test_file_parsing,
        test_validation,
        test_auto_fixes,
        test_export,
        test_summary,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {str(e)}")
            failed += 1
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
