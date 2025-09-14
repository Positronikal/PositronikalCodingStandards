"""
Pytest integration tests for Positronikal Standards Checker.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
import pytest
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from positronikal_standards_check import PositronikalStandardsChecker


# Pytest markers for selective testing
pytestmark = [
    pytest.mark.positronikal,
    pytest.mark.standards
]


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Create basic structure
        (repo_path / "src").mkdir()
        (repo_path / "test").mkdir()
        (repo_path / "docs").mkdir()
        
        # Create README
        (repo_path / "README.md").write_text("# Test Repository\n\nTest repository for standards validation.")
        
        yield repo_path


@pytest.fixture
def compliant_repo(temp_repo):
    """Create a fully compliant repository."""
    repo_path = temp_repo
    
    # Add all required files
    (repo_path / "CONTRIBUTING.md").write_text("# Contributing\n\nContribution guidelines.")
    (repo_path / ".gitignore").write_text("*.pyc\n__pycache__/\nnode_modules/")
    (repo_path / "LICENSE.md").write_text("MIT License\n\nCopyright (c) 2024")
    (repo_path / "AUTHORS.md").write_text("# Authors\n\n- Test Author")
    (repo_path / "SECURITY.md").write_text("# Security Policy\n\nReport vulnerabilities to security@example.com")
    
    # Add .editorconfig
    editorconfig_content = """
root = true

[*]
end_of_line = lf
charset = utf-8
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true
"""
    (repo_path / ".editorconfig").write_text(editorconfig_content)
    
    # Add GitHub files
    github_dir = repo_path / ".github"
    github_dir.mkdir()
    (github_dir / "SECURITY.md").write_text("# Security Policy\n\nGitHub security policy.")
    (github_dir / "CODEOWNERS").write_text("* @testowner")
    
    # Add GitHub templates
    templates_dir = github_dir / "ISSUE_TEMPLATE"
    templates_dir.mkdir()
    (templates_dir / "bug_report.md").write_text("---\ntitle: Bug Report\n---\n\nBug template")
    (templates_dir / "feature_request.md").write_text("---\ntitle: Feature Request\n---\n\nFeature template")
    (github_dir / "pull_request_template.md").write_text("## Description\n\nPR template")
    
    # Add workflows
    workflows_dir = github_dir / "workflows"
    workflows_dir.mkdir()
    
    ci_workflow = """
name: CI
on: [push, pull_request]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: echo "Running tests"
"""
    (workflows_dir / "ci.yml").write_text(ci_workflow)
    
    # Add dependabot config
    dependabot_config = """
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
"""
    (github_dir / "dependabot.yml").write_text(dependabot_config)
    
    # Add package.json with required dependencies
    package_json = {
        "name": "test-repo",
        "version": "1.0.0",
        "scripts": {
            "prepare": "husky",
            "pre-commit": "lint-staged"
        },
        "devDependencies": {
            "husky": "^9.1.7",
            "lint-staged": "^15.5.0",
            "prettier": "^3.5.3"
        },
        "lint-staged": {
            "*.js": ["prettier --write", "git add"]
        }
    }
    (repo_path / "package.json").write_text(json.dumps(package_json, indent=2))
    
    # Add Husky hooks
    husky_dir = repo_path / ".husky"
    husky_dir.mkdir()
    (husky_dir / "pre-commit").write_text("#!/bin/sh\nnpx lint-staged")
    (husky_dir / "commit-msg").write_text("#!/bin/sh\necho 'Checking commit message'")
    
    # Add sample source file
    (repo_path / "src" / "main.py").write_text(
        "#!/usr/bin/env python3\n"
        "# -*- coding: utf-8 -*-\n\n"
        "def main():\n"
        "    print('Hello, World!')\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )
    
    return repo_path


class TestPositronikalStandardsChecker:
    """Test the main checker class."""
    
    @pytest.mark.positronikal_core
    def test_initialization(self, temp_repo):
        """Test checker initialization."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        assert checker.repo_path == temp_repo
        assert checker.results is not None
        
    @pytest.mark.positronikal_core
    def test_invalid_path(self):
        """Test initialization with invalid path."""
        with pytest.raises(FileNotFoundError):
            PositronikalStandardsChecker("/nonexistent/path")
            
    @pytest.mark.positronikal_core
    def test_not_directory(self, temp_repo):
        """Test initialization with file instead of directory."""
        file_path = temp_repo / "test.txt"
        file_path.write_text("test")
        
        with pytest.raises(ValueError):
            PositronikalStandardsChecker(str(file_path))


class TestFileRequirements:
    """Test file requirements validation."""
    
    @pytest.mark.positronikal_files
    def test_required_files_missing(self, temp_repo):
        """Test detection of missing required files."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        
        # Check that missing files are detected
        assert any(
            r["status"] == "fail" and "CONTRIBUTING.md" in r["message"]
            for r in results.failed
        )
        assert any(
            r["status"] == "fail" and ".gitignore" in r["message"]
            for r in results.failed
        )
        
    @pytest.mark.positronikal_files
    def test_required_files_present(self, compliant_repo):
        """Test passing validation with all required files."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_files()
        
        # Check that required files pass
        assert any(
            r["check"] == "required_file_README.md" and r["status"] == "pass"
            for r in results.passed
        )
        assert any(
            r["check"] == "required_file_CONTRIBUTING.md" and r["status"] == "pass"
            for r in results.passed
        )
        
    @pytest.mark.positronikal_files
    def test_license_file_check(self, temp_repo):
        """Test license file validation."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        
        # Should fail without license
        assert any(
            r["check"] == "license_file" and r["status"] == "fail"
            for r in results.failed
        )
        
        # Add license and recheck
        (temp_repo / "COPYING.md").write_text("GPL License")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        
        assert any(
            r["check"] == "license_file" and r["status"] == "pass"
            for r in results.passed
        )


class TestBuildSystem:
    """Test build system validation."""
    
    @pytest.mark.positronikal_build
    def test_npm_requirements(self, compliant_repo):
        """Test npm package requirements."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_build()
        
        # Check npm packages are detected
        assert any(
            "husky" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        assert any(
            "lint-staged" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        
    @pytest.mark.positronikal_build
    def test_git_hooks(self, compliant_repo):
        """Test git hook validation."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_build()
        
        # Check git hooks are detected
        assert any(
            "pre-commit" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        assert any(
            "commit-msg" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        
    @pytest.mark.positronikal_build
    def test_missing_npm_scripts(self, temp_repo):
        """Test detection of missing npm scripts."""
        # Create package.json without required scripts
        package_json = {
            "name": "test-repo",
            "version": "1.0.0",
            "devDependencies": {
                "husky": "^9.1.7"
            }
        }
        (temp_repo / "package.json").write_text(json.dumps(package_json))
        
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_build()
        
        assert any(
            r["check"] == "npm_script_prepare" and r["status"] == "fail"
            for r in results.failed
        )


class TestCodeStandards:
    """Test code formatting standards validation."""
    
    @pytest.mark.positronikal_code
    def test_line_length_check(self, temp_repo):
        """Test line length validation."""
        # Create file with long line
        long_line = "x" * 100  # Exceeds 79 character limit
        (temp_repo / "src" / "test.py").write_text(f"# {long_line}\n")
        
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_code()
        
        assert any(
            r["check"] == "line_length" and r["status"] == "fail"
            for r in results.failed
        )
        
    @pytest.mark.positronikal_code
    def test_trailing_whitespace(self, temp_repo):
        """Test trailing whitespace detection."""
        # Create file with trailing whitespace
        (temp_repo / "src" / "test.py").write_text("def test():  \n    pass\n")
        
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_code()
        
        assert any(
            r["check"] == "trailing_whitespace" and r["status"] == "fail"
            for r in results.failed
        )
        
    @pytest.mark.positronikal_code
    def test_tab_indentation(self, temp_repo):
        """Test tab indentation detection."""
        # Create file with tabs
        (temp_repo / "src" / "test.py").write_text("def test():\n\tpass\n")
        
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_code()
        
        assert any(
            r["check"] == "indentation" and r["status"] == "fail"
            for r in results.failed
        )
        
    @pytest.mark.positronikal_code
    def test_editorconfig_validation(self, compliant_repo):
        """Test .editorconfig validation."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_code()
        
        # Check editorconfig settings are validated
        assert any(
            "editorconfig_end_of_line" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        assert any(
            "editorconfig_charset" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )


class TestSecurity:
    """Test security requirements validation."""
    
    @pytest.mark.positronikal_security
    def test_security_files(self, compliant_repo):
        """Test security file validation."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_security()
        
        assert any(
            ".github_SECURITY.md" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        assert any(
            "dependabot.yml" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        
    @pytest.mark.positronikal_security
    def test_sensitive_data_detection(self, temp_repo):
        """Test detection of hardcoded sensitive data."""
        # Create file with API key
        (temp_repo / "config.py").write_text(
            'API_KEY = "sk-1234567890abcdef1234567890abcdef"\n'
        )
        
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_security()
        
        assert any(
            r["check"] == "sensitive_data" and r["status"] == "fail"
            for r in results.failed
        )
        
    @pytest.mark.positronikal_security
    def test_workflow_permissions(self, compliant_repo):
        """Test GitHub workflow permissions validation."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_security()
        
        assert any(
            "workflow_permissions_ci.yml" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )


class TestForensicStandards:
    """Test forensic tool standards validation."""
    
    @pytest.mark.positronikal_forensic
    def test_forensic_files_missing(self, temp_repo):
        """Test detection of missing forensic documentation."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_forensic()
        
        assert any(
            r["check"] == "forensic_file_METHODOLOGY.md" and r["status"] == "fail"
            for r in results.failed
        )
        assert any(
            r["check"] == "forensic_file_VALIDATION.md" and r["status"] == "fail"
            for r in results.failed
        )
        assert any(
            r["check"] == "forensic_file_LEGAL.md" and r["status"] == "fail"
            for r in results.failed
        )
        
    @pytest.mark.positronikal_forensic
    def test_forensic_files_present(self, temp_repo):
        """Test passing forensic validation."""
        # Add forensic documentation
        (temp_repo / "METHODOLOGY.md").write_text("# Methodology\n\nAlgorithm documentation.")
        (temp_repo / "VALIDATION.md").write_text("# Validation\n\nTest results.")
        (temp_repo / "LEGAL.md").write_text("# Legal\n\nExpert witness info.")
        
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_forensic()
        
        assert all(
            r["status"] == "pass"
            for r in results.passed
            if "forensic_file" in r["check"]
        )


class TestComprehensiveValidation:
    """Test comprehensive validation scenarios."""
    
    @pytest.mark.positronikal_all
    def test_full_compliance(self, compliant_repo):
        """Test fully compliant repository."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_all()
        
        summary = results.get_summary()
        assert summary["is_passing"] or summary["failed"] == 0
        assert summary["passed"] > 0
        
    @pytest.mark.positronikal_all
    def test_forensic_compliance(self, compliant_repo):
        """Test forensic tool compliance."""
        # Add forensic files
        (compliant_repo / "METHODOLOGY.md").write_text("# Methodology")
        (compliant_repo / "VALIDATION.md").write_text("# Validation")
        (compliant_repo / "LEGAL.md").write_text("# Legal")
        
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_all(include_forensic=True)
        
        # Check forensic files are validated
        assert any(
            "forensic_file" in r["check"] and r["status"] == "pass"
            for r in results.passed
        )
        
    @pytest.mark.positronikal_all
    def test_validation_report(self, temp_repo, capsys):
        """Test validation report output."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_all()
        
        # Print report
        results.print_report()
        
        # Check output
        captured = capsys.readouterr()
        assert "POSITRONIKAL STANDARDS VALIDATION REPORT" in captured.out
        assert "Summary:" in captured.out
        assert "VALIDATION" in captured.out


# Pytest configuration for running specific test groups
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "positronikal: All Positronikal standards tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_core: Core functionality tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_files: File requirements tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_build: Build system tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_code: Code standards tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_security: Security requirements tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_forensic: Forensic standards tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_all: Comprehensive validation tests"
    )