#!/usr/bin/env python3
"""
LARS File Validator and Repair Tool - Main Launcher
====================================================

This script provides a simple way to launch the application.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point"""
    # Check if we have command line arguments
    if len(sys.argv) > 1:
        # Launch CLI
        from lars_validator.cli import main as cli_main
        sys.exit(cli_main())
    else:
        # Launch GUI
        from lars_validator.gui import main as gui_main
        gui_main()


if __name__ == "__main__":
    main()
