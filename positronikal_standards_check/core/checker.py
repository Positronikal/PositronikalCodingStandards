"""
Main PositronikalStandardsChecker class for orchestrating validation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from .file_requirements import FileRequirementsValidator
from .build_system import BuildSystemValidator
from .code_standards import CodeStandardsValidator
from .security import SecurityValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.errors = []
        
    def add_pass(self, check_name: str, message: str = ""):
        """Record a passing check."""
        self.passed.append({
            "check": check_name,
            "message": message or "Check passed"
        })
        
    def add_fail(self, check_name: str, message: str):
        """Record a failing check."""
        self.failed.append({
            "check": check_name, 
            "message": message
        })
        
    def add_warning(self, check_name: str, message: str):
        """Record a warning."""
        self.warnings.append({
            "check": check_name,
            "message": message
        })
        
    def add_error(self, check_name: str, message: str):
        """Record an error during checking."""
        self.errors.append({
            "check": check_name,
            "message": message
        })
        
    @property
    def is_passing(self) -> bool:
        """Check if all validations passed."""
        return len(self.failed) == 0 and len(self.errors) == 0
        
    def get_summary(self) -> Dict:
        """Get summary of validation results."""
        return {
            "total_checks": len(self.passed) + len(self.failed),
            "passed": len(self.passed),
            "failed": len(self.failed),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "is_passing": self.is_passing
        }
        
    def print_report(self):
        """Print formatted validation report."""
        print("\n" + "="*60)
        print("POSITRONIKAL STANDARDS VALIDATION REPORT")
        print("="*60)
        
        summary = self.get_summary()
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Total Checks: {summary['total_checks']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Errors: {summary['errors']}")
        
        # Print failures
        if self.failed:
            print(f"\n❌ FAILED CHECKS ({len(self.failed)}):")
            for fail in self.failed:
                print(f"  - {fail['check']}: {fail['message']}")
                
        # Print warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning['check']}: {warning['message']}")
                
        # Print errors
        if self.errors:
            print(f"\n🔥 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error['check']}: {error['message']}")
                
        # Print passes (optionally verbose)
        if self.passed and os.environ.get("VERBOSE", "").lower() == "true":
            print(f"\n✅ PASSED CHECKS ({len(self.passed)}):")
            for pass_item in self.passed:
                print(f"  - {pass_item['check']}: {pass_item['message']}")
                
        # Final status
        print("\n" + "="*60)
        if self.is_passing:
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        print("="*60 + "\n")


class PositronikalStandardsChecker:
    """
    Main checker class for validating repository compliance with
    Positronikal coding standards.
    """
    
    def __init__(self, repo_path: str, config_path: Optional[str] = None):
        """
        Initialize the standards checker.
        
        Args:
            repo_path: Path to repository to validate
            config_path: Optional path to configuration file
        """
        self.repo_path = Path(repo_path).resolve()
        
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path not found: {repo_path}")
        if not self.repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {repo_path}")
            
        self.config_path = config_path
        self.results = ValidationResult()
        
        # Initialize validators
        self.file_validator = FileRequirementsValidator(self.repo_path)
        self.build_validator = BuildSystemValidator(self.repo_path)
        self.code_validator = CodeStandardsValidator(self.repo_path)
        self.security_validator = SecurityValidator(self.repo_path)
        
        logger.info(f"Initialized checker for repository: {self.repo_path}")
        
    def check_all(self, include_forensic: bool = False) -> ValidationResult:
        """
        Run all validation checks.
        
        Args:
            include_forensic: Whether to include forensic tool standards
            
        Returns:
            ValidationResult object with all check results
        """
        logger.info("Starting comprehensive validation...")
        
        # Check file requirements
        self._run_file_checks()
        
        # Check build system
        self._run_build_checks()
        
        # Check code standards
        self._run_code_checks()
        
        # Check security requirements
        self._run_security_checks()
        
        # Check forensic requirements if requested
        if include_forensic:
            self._run_forensic_checks()
            
        return self.results
        
    def check_files(self) -> ValidationResult:
        """Run only file requirement checks."""
        self._run_file_checks()
        return self.results
        
    def check_build(self) -> ValidationResult:
        """Run only build system checks."""
        self._run_build_checks()
        return self.results
        
    def check_code(self) -> ValidationResult:
        """Run only code standard checks."""
        self._run_code_checks()
        return self.results
        
    def check_security(self) -> ValidationResult:
        """Run only security checks."""
        self._run_security_checks()
        return self.results
        
    def check_forensic(self) -> ValidationResult:
        """Run only forensic tool checks."""
        self._run_forensic_checks()
        return self.results
        
    def _run_file_checks(self):
        """Execute file requirement validations."""
        logger.info("Checking file requirements...")
        
        try:
            file_results = self.file_validator.validate()
            for result in file_results:
                if result["status"] == "pass":
                    self.results.add_pass(result["check"], result["message"])
                elif result["status"] == "fail":
                    self.results.add_fail(result["check"], result["message"])
                elif result["status"] == "warning":
                    self.results.add_warning(result["check"], result["message"])
        except Exception as e:
            self.results.add_error("file_requirements", str(e))
            logger.error(f"Error during file checks: {e}")
            
    def _run_build_checks(self):
        """Execute build system validations."""
        logger.info("Checking build system requirements...")
        
        try:
            build_results = self.build_validator.validate()
            for result in build_results:
                if result["status"] == "pass":
                    self.results.add_pass(result["check"], result["message"])
                elif result["status"] == "fail":
                    self.results.add_fail(result["check"], result["message"])
                elif result["status"] == "warning":
                    self.results.add_warning(result["check"], result["message"])
        except Exception as e:
            self.results.add_error("build_system", str(e))
            logger.error(f"Error during build checks: {e}")
            
    def _run_code_checks(self):
        """Execute code standard validations."""
        logger.info("Checking code standards...")
        
        try:
            code_results = self.code_validator.validate()
            for result in code_results:
                if result["status"] == "pass":
                    self.results.add_pass(result["check"], result["message"])
                elif result["status"] == "fail":
                    self.results.add_fail(result["check"], result["message"])
                elif result["status"] == "warning":
                    self.results.add_warning(result["check"], result["message"])
        except Exception as e:
            self.results.add_error("code_standards", str(e))
            logger.error(f"Error during code checks: {e}")
            
    def _run_security_checks(self):
        """Execute security requirement validations."""
        logger.info("Checking security requirements...")
        
        try:
            security_results = self.security_validator.validate()
            for result in security_results:
                if result["status"] == "pass":
                    self.results.add_pass(result["check"], result["message"])
                elif result["status"] == "fail":
                    self.results.add_fail(result["check"], result["message"])
                elif result["status"] == "warning":
                    self.results.add_warning(result["check"], result["message"])
        except Exception as e:
            self.results.add_error("security", str(e))
            logger.error(f"Error during security checks: {e}")
            
    def _run_forensic_checks(self):
        """Execute forensic tool standard validations."""
        logger.info("Checking forensic tool standards...")
        
        # Check for forensic-specific documentation
        forensic_files = ["METHODOLOGY.md", "VALIDATION.md", "LEGAL.md"]
        
        for filename in forensic_files:
            file_path = self.repo_path / filename
            if file_path.exists():
                self.results.add_pass(
                    f"forensic_file_{filename}",
                    f"Required forensic documentation file exists: {filename}"
                )
            else:
                self.results.add_fail(
                    f"forensic_file_{filename}",
                    f"Missing required forensic documentation: {filename}"
                )
                
    def get_pytest_markers(self) -> List[str]:
        """
        Get pytest markers for selective testing.
        
        Returns:
            List of pytest marker strings
        """
        return [
            "positronikal_files",
            "positronikal_build",
            "positronikal_code",
            "positronikal_security",
            "positronikal_forensic"
        ]