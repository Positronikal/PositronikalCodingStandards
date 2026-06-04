"""
Positronikal Standards Checker

A pytest-compatible tool for validating repository compliance with
Positronikal coding standards.
"""

try:
    from ._version import version as __version__
except ImportError:
    try:
        from importlib.metadata import version
        __version__ = version("positronikal-standards-check")
    except Exception:
        __version__ = "unknown"

__author__ = "Positronikal"

from .core.checker import PositronikalStandardsChecker

__all__ = ["PositronikalStandardsChecker"]