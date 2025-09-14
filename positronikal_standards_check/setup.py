#!/usr/bin/env python3
"""
Setup script for Positronikal Standards Checker.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "A pytest-compatible tool for validating repository compliance with Positronikal coding standards."

setup(
    name="positronikal-standards-check",
    version="1.0.0",
    author="Positronikal",
    author_email="hoyt.harness@gmail.com",
    description="Validate repository compliance with Positronikal coding standards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Positronikal/PositronikalCodingStandards",
    packages=find_packages(),
    package_data={
        "positronikal_standards_check": ["config/*.yaml"]
    },
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "positronikal-check=positronikal_standards_check.cli:main",
            "psc=positronikal_standards_check.cli:main",  # Short alias
        ],
        "pytest11": [
            "positronikal_standards = positronikal_standards_check.tests.test_standards",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="coding standards, validation, testing, compliance, positronikal",
)