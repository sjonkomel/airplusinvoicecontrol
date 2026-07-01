#!/usr/bin/env python3
"""
Setup script for LARS File Validator and Repair Tool
"""

import os
import sys
from setuptools import setup, find_packages
from pathlib import Path

# Read version from __init__.py or use default
version = "1.0.0"

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="lars-validator",
    version=version,
    description="LARS File Validator and Repair Tool for AIRPLUS invoice files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Travel Assistant Tools",
    author_email="",
    url="",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "lars-validator=lars_validator.cli:main",
            "lars-gui=lars_validator.gui:main",
        ],
    },
    install_requires=[
        # No external dependencies required for basic functionality
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    package_data={
        "lars_validator": [
            "*.txt",
            "*.md",
            "*.json",
        ],
    },
    include_package_data=True,
)
