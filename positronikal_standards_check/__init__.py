"""
Positronikal Standards Checker

A pytest-compatible tool for validating repository compliance with 
Positronikal coding standards.
"""

__version__ = "1.0.0"
__author__ = "Positronikal"

from .core.checker import PositronikalStandardsChecker

__all__ = ["PositronikalStandardsChecker"]