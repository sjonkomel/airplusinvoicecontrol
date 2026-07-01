#!/bin/bash
# LARS File Validator and Repair Tool - Unix Launcher
# ====================================================

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Run the application
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/run.py" "$@"
