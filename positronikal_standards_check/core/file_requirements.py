"""
File requirements validation for Positronikal standards.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FileRequirementsValidator:
    """Validates required files and directory structure."""
    
    # Core required files
    REQUIRED_FILES = {
        "README.md": "Project documentation",
        "CONTRIBUTING.md": "Contribution guidelines",
        ".gitignore": "Git ignore patterns"
    }
    
    # License files (at least one required)
    LICENSE_FILES = [
        "COPYING.md",
        "COPYING.LESSER.md", 
        "LICENSE.md",
        "LICENSE.CC.md"
    ]
    
    # Optional but recommended files
    RECOMMENDED_FILES = {
        "AUTHORS.md": "List of contributors",
        "BUGS.md": "Bug reporting guidelines",
        "SECURITY.md": "Security policy",
        "USING.md": "Usage instructions",
        ".editorconfig": "Editor configuration"
    }
    
    # GitHub-specific files
    GITHUB_FILES = {
        ".github/SECURITY.md": "GitHub security policy",
        ".github/CODEOWNERS": "Code ownership",
        ".github/dependabot.yml": "Dependabot configuration",
        ".github/workflows/ci.yml": "CI workflow",
        ".github/workflows/codeql.yml": "CodeQL security scanning"
    }
    
    # GitHub templates
    GITHUB_TEMPLATES = {
        ".github/ISSUE_TEMPLATE/bug_report.md": "Bug report template",
        ".github/ISSUE_TEMPLATE/feature_request.md": "Feature request template",
        ".github/pull_request_template.md": "Pull request template"
    }
    
    # Standard directories
    STANDARD_DIRECTORIES = {
        "src": "Source code",
        "test": "Test files",
        "docs": "Documentation"
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize file requirements validator.
        
        Args:
            repo_path: Path to repository to validate
        """
        self.repo_path = repo_path
        
    def validate(self) -> List[Dict]:
        """
        Validate all file requirements.
        
        Returns:
            List of validation results
        """
        results = []
        
        # Check required files
        results.extend(self._check_required_files())
        
        # Check license files
        results.extend(self._check_license_files())
        
        # Check recommended files
        results.extend(self._check_recommended_files())
        
        # Check GitHub files if .github exists
        if (self.repo_path / ".github").exists():
            results.extend(self._check_github_files())
            results.extend(self._check_github_templates())
            
        # Check standard directories
        results.extend(self._check_standard_directories())
        
        return results
        
    def _check_required_files(self) -> List[Dict]:
        """Check for required files."""
        results = []
        
        for filename, description in self.REQUIRED_FILES.items():
            file_path = self.repo_path / filename
            
            if file_path.exists():
                # Check if file is not empty
                if file_path.stat().st_size > 0:
                    results.append({
                        "check": f"required_file_{filename}",
                        "status": "pass",
                        "message": f"Required file exists: {filename}"
                    })
                else:
                    results.append({
                        "check": f"required_file_{filename}",
                        "status": "warning",
                        "message": f"Required file exists but is empty: {filename}"
                    })
            else:
                results.append({
                    "check": f"required_file_{filename}",
                    "status": "fail",
                    "message": f"Missing required file: {filename} ({description})"
                })
                
        return results
        
    def _check_license_files(self) -> List[Dict]:
        """Check for at least one license file."""
        results = []
        
        found_licenses = []
        for license_file in self.LICENSE_FILES:
            if (self.repo_path / license_file).exists():
                found_licenses.append(license_file)
                
        if found_licenses:
            results.append({
                "check": "license_file",
                "status": "pass",
                "message": f"License file(s) found: {', '.join(found_licenses)}"
            })
        else:
            results.append({
                "check": "license_file",
                "status": "fail",
                "message": f"No license file found. Need one of: {', '.join(self.LICENSE_FILES)}"
            })
            
        return results
        
    def _check_recommended_files(self) -> List[Dict]:
        """Check for recommended files."""
        results = []
        
        for filename, description in self.RECOMMENDED_FILES.items():
            file_path = self.repo_path / filename
            
            if file_path.exists():
                results.append({
                    "check": f"recommended_file_{filename}",
                    "status": "pass",
                    "message": f"Recommended file exists: {filename}"
                })
            else:
                results.append({
                    "check": f"recommended_file_{filename}",
                    "status": "warning",
                    "message": f"Missing recommended file: {filename} ({description})"
                })
                
        return results
        
    def _check_github_files(self) -> List[Dict]:
        """Check for GitHub-specific files."""
        results = []
        
        for filepath, description in self.GITHUB_FILES.items():
            file_path = self.repo_path / filepath
            
            if file_path.exists():
                results.append({
                    "check": f"github_file_{filepath.replace('/', '_')}",
                    "status": "pass",
                    "message": f"GitHub file exists: {filepath}"
                })
            else:
                results.append({
                    "check": f"github_file_{filepath.replace('/', '_')}",
                    "status": "fail",
                    "message": f"Missing GitHub file: {filepath} ({description})"
                })
                
        return results
        
    def _check_github_templates(self) -> List[Dict]:
        """Check for GitHub template files."""
        results = []
        
        for filepath, description in self.GITHUB_TEMPLATES.items():
            file_path = self.repo_path / filepath
            
            if file_path.exists():
                results.append({
                    "check": f"github_template_{filepath.replace('/', '_')}",
                    "status": "pass",
                    "message": f"GitHub template exists: {filepath}"
                })
            else:
                results.append({
                    "check": f"github_template_{filepath.replace('/', '_')}",
                    "status": "warning",
                    "message": f"Missing GitHub template: {filepath} ({description})"
                })
                
        return results
        
    def _check_standard_directories(self) -> List[Dict]:
        """Check for standard directory structure."""
        results = []
        
        for dirname, description in self.STANDARD_DIRECTORIES.items():
            dir_path = self.repo_path / dirname
            
            if dir_path.exists() and dir_path.is_dir():
                # Check if directory is not empty
                if any(dir_path.iterdir()):
                    results.append({
                        "check": f"standard_dir_{dirname}",
                        "status": "pass",
                        "message": f"Standard directory exists: {dirname}"
                    })
                else:
                    results.append({
                        "check": f"standard_dir_{dirname}",
                        "status": "warning",
                        "message": f"Standard directory exists but is empty: {dirname}"
                    })
            else:
                results.append({
                    "check": f"standard_dir_{dirname}",
                    "status": "warning",
                    "message": f"Missing standard directory: {dirname} ({description})"
                })
                
        return results
        
    def check_file_size_limits(self) -> List[Dict]:
        """Check that no files exceed 10MB limit."""
        results = []
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        
        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file():
                # Skip .git directory
                if ".git" in file_path.parts:
                    continue
                    
                file_size = file_path.stat().st_size
                if file_size > max_size:
                    results.append({
                        "check": f"file_size_{file_path.name}",
                        "status": "fail",
                        "message": f"File exceeds 10MB limit: {file_path.relative_to(self.repo_path)} ({file_size / 1024 / 1024:.2f}MB)"
                    })
                    
        if not results:
            results.append({
                "check": "file_size_limits",
                "status": "pass",
                "message": "All files within 10MB size limit"
            })
            
        return results
        
    def check_binary_files(self) -> List[Dict]:
        """Check for prohibited binary files."""
        results = []
        
        # Prohibited extensions
        prohibited_extensions = {
            ".exe", ".dll", ".so", ".dylib", ".bin",
            ".com", ".app", ".deb", ".rpm", ".dmg"
        }
        
        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file():
                # Skip .git directory
                if ".git" in file_path.parts:
                    continue
                    
                if file_path.suffix.lower() in prohibited_extensions:
                    results.append({
                        "check": f"binary_file_{file_path.name}",
                        "status": "fail",
                        "message": f"Prohibited binary file found: {file_path.relative_to(self.repo_path)}"
                    })
                    
        if not results:
            results.append({
                "check": "binary_files",
                "status": "pass",
                "message": "No prohibited binary files found"
            })
            
        return results