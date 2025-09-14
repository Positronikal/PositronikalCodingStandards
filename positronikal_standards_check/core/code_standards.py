"""
Code formatting standards validation for Positronikal standards.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CodeStandardsValidator:
    """Validates code formatting standards."""
    
    # Maximum line length per standards
    MAX_LINE_LENGTH = 79
    
    # File extensions to check for different languages
    LANGUAGE_EXTENSIONS = {
        "python": [".py"],
        "c": [".c", ".h"],
        "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hh"],
        "javascript": [".js", ".jsx"],
        "typescript": [".ts", ".tsx"],
        "go": [".go"],
        "java": [".java"],
        "shell": [".sh", ".bash"],
        "perl": [".pl", ".pm"],
        "php": [".php"],
        "powershell": [".ps1", ".psm1", ".psd1"],
        "html": [".html", ".htm"],
        "css": [".css", ".scss", ".less"],
        "awk": [".awk"]
    }
    
    # Linter commands for each language
    LINTERS = {
        "python": ["ruff", "check"],
        "shell": ["shellcheck"],
        "go": ["golangci-lint", "run"],
        "javascript": ["eslint"],
        "css": ["stylelint"],
        "perl": ["perlcritic"],
        "powershell": ["PSScriptAnalyzer"]
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize code standards validator.
        
        Args:
            repo_path: Path to repository to validate
        """
        self.repo_path = repo_path
        
    def validate(self) -> List[Dict]:
        """
        Validate all code formatting standards.
        
        Returns:
            List of validation results
        """
        results = []
        
        # Check .editorconfig if it exists
        if (self.repo_path / ".editorconfig").exists():
            results.extend(self._check_editorconfig())
            
        # Check line endings
        results.extend(self._check_line_endings())
        
        # Check encoding
        results.extend(self._check_encoding())
        
        # Check line length
        results.extend(self._check_line_length())
        
        # Check indentation (tabs vs spaces)
        results.extend(self._check_indentation())
        
        # Check trailing whitespace
        results.extend(self._check_trailing_whitespace())
        
        # Run linters if available
        results.extend(self._run_linters())
        
        return results
        
    def _check_editorconfig(self) -> List[Dict]:
        """Check .editorconfig configuration."""
        results = []
        editorconfig_path = self.repo_path / ".editorconfig"
        
        try:
            with open(editorconfig_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check for important settings
            checks = {
                "end_of_line = lf": "Unix line endings (LF)",
                "charset = utf-8": "UTF-8 encoding",
                "indent_style = space": "Space indentation",
                "trim_trailing_whitespace = true": "Trim trailing whitespace",
                "insert_final_newline = true": "Final newline"
            }
            
            for setting, description in checks.items():
                if setting in content:
                    results.append({
                        "check": f"editorconfig_{setting.split()[0]}",
                        "status": "pass",
                        "message": f".editorconfig specifies: {description}"
                    })
                else:
                    results.append({
                        "check": f"editorconfig_{setting.split()[0]}",
                        "status": "warning",
                        "message": f".editorconfig missing: {description}"
                    })
                    
        except Exception as e:
            results.append({
                "check": "editorconfig",
                "status": "fail",
                "message": f"Error reading .editorconfig: {e}"
            })
            
        return results
        
    def _check_line_endings(self) -> List[Dict]:
        """Check for consistent line endings (LF)."""
        results = []
        files_checked = 0
        files_with_crlf = []
        
        for file_path in self._get_source_files():
            files_checked += 1
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    
                if b"\r\n" in content:
                    files_with_crlf.append(str(file_path.relative_to(self.repo_path)))
                    
            except Exception as e:
                logger.warning(f"Could not check line endings in {file_path}: {e}")
                
        if files_with_crlf:
            results.append({
                "check": "line_endings",
                "status": "fail",
                "message": f"Files with Windows line endings (CRLF): {', '.join(files_with_crlf[:5])}{'...' if len(files_with_crlf) > 5 else ''}"
            })
        elif files_checked > 0:
            results.append({
                "check": "line_endings",
                "status": "pass",
                "message": f"All {files_checked} source files use Unix line endings (LF)"
            })
            
        return results
        
    def _check_encoding(self) -> List[Dict]:
        """Check for UTF-8 encoding."""
        results = []
        files_checked = 0
        files_with_issues = []
        
        for file_path in self._get_source_files():
            files_checked += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError:
                files_with_issues.append(str(file_path.relative_to(self.repo_path)))
            except Exception as e:
                logger.warning(f"Could not check encoding in {file_path}: {e}")
                
        if files_with_issues:
            results.append({
                "check": "encoding",
                "status": "fail",
                "message": f"Files with non-UTF-8 encoding: {', '.join(files_with_issues[:5])}{'...' if len(files_with_issues) > 5 else ''}"
            })
        elif files_checked > 0:
            results.append({
                "check": "encoding",
                "status": "pass",
                "message": f"All {files_checked} source files use UTF-8 encoding"
            })
            
        return results
        
    def _check_line_length(self) -> List[Dict]:
        """Check for maximum line length compliance."""
        results = []
        files_checked = 0
        violations = []
        
        for file_path in self._get_source_files():
            files_checked += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        # Remove trailing newline for length check
                        line = line.rstrip("\n\r")
                        if len(line) > self.MAX_LINE_LENGTH:
                            violations.append({
                                "file": str(file_path.relative_to(self.repo_path)),
                                "line": line_num,
                                "length": len(line)
                            })
                            
            except Exception as e:
                logger.warning(f"Could not check line length in {file_path}: {e}")
                
        if violations:
            # Report first few violations
            violation_msgs = [
                f"{v['file']}:{v['line']} ({v['length']} chars)"
                for v in violations[:5]
            ]
            results.append({
                "check": "line_length",
                "status": "fail",
                "message": f"Lines exceeding {self.MAX_LINE_LENGTH} characters: {', '.join(violation_msgs)}{'...' if len(violations) > 5 else ''}"
            })
        elif files_checked > 0:
            results.append({
                "check": "line_length",
                "status": "pass",
                "message": f"All lines in {files_checked} source files within {self.MAX_LINE_LENGTH} character limit"
            })
            
        return results
        
    def _check_indentation(self) -> List[Dict]:
        """Check for space-based indentation (no tabs)."""
        results = []
        files_checked = 0
        files_with_tabs = []
        
        for file_path in self._get_source_files():
            # Skip Makefiles (they require tabs)
            if file_path.name in ["Makefile", "makefile"] or file_path.suffix == ".mk":
                continue
                
            files_checked += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                if "\t" in content:
                    files_with_tabs.append(str(file_path.relative_to(self.repo_path)))
                    
            except Exception as e:
                logger.warning(f"Could not check indentation in {file_path}: {e}")
                
        if files_with_tabs:
            results.append({
                "check": "indentation",
                "status": "fail",
                "message": f"Files with tab indentation: {', '.join(files_with_tabs[:5])}{'...' if len(files_with_tabs) > 5 else ''}"
            })
        elif files_checked > 0:
            results.append({
                "check": "indentation",
                "status": "pass",
                "message": f"All {files_checked} source files use space indentation"
            })
            
        return results
        
    def _check_trailing_whitespace(self) -> List[Dict]:
        """Check for trailing whitespace."""
        results = []
        files_checked = 0
        files_with_trailing = []
        
        for file_path in self._get_source_files():
            files_checked += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.rstrip() != line.rstrip("\n\r"):
                            files_with_trailing.append(str(file_path.relative_to(self.repo_path)))
                            break
                            
            except Exception as e:
                logger.warning(f"Could not check trailing whitespace in {file_path}: {e}")
                
        if files_with_trailing:
            results.append({
                "check": "trailing_whitespace",
                "status": "fail",
                "message": f"Files with trailing whitespace: {', '.join(files_with_trailing[:5])}{'...' if len(files_with_trailing) > 5 else ''}"
            })
        elif files_checked > 0:
            results.append({
                "check": "trailing_whitespace",
                "status": "pass",
                "message": f"No trailing whitespace found in {files_checked} source files"
            })
            
        return results
        
    def _run_linters(self) -> List[Dict]:
        """Run available linters for detected languages."""
        results = []
        
        # Detect languages in repository
        detected_languages = self._detect_languages()
        
        for language in detected_languages:
            if language in self.LINTERS:
                linter_cmd = self.LINTERS[language]
                
                # Check if linter is available
                try:
                    # Try to run linter --version or equivalent
                    subprocess.run(
                        [linter_cmd[0], "--version"],
                        capture_output=True,
                        check=False,
                        cwd=self.repo_path
                    )
                    
                    # Run the actual linter
                    result = subprocess.run(
                        linter_cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.repo_path
                    )
                    
                    if result.returncode == 0:
                        results.append({
                            "check": f"linter_{language}",
                            "status": "pass",
                            "message": f"{language.capitalize()} linter passed"
                        })
                    else:
                        # Parse linter output if possible
                        output = result.stdout or result.stderr
                        results.append({
                            "check": f"linter_{language}",
                            "status": "fail",
                            "message": f"{language.capitalize()} linter found issues: {output[:200]}..."
                        })
                        
                except FileNotFoundError:
                    results.append({
                        "check": f"linter_{language}",
                        "status": "warning",
                        "message": f"{language.capitalize()} linter not available: {linter_cmd[0]}"
                    })
                except Exception as e:
                    results.append({
                        "check": f"linter_{language}",
                        "status": "warning",
                        "message": f"Could not run {language} linter: {e}"
                    })
                    
        return results
        
    def _get_source_files(self) -> List[Path]:
        """Get all source code files in the repository."""
        source_files = []
        
        # Common source code extensions
        extensions = set()
        for lang_exts in self.LANGUAGE_EXTENSIONS.values():
            extensions.update(lang_exts)
            
        for ext in extensions:
            source_files.extend(self.repo_path.rglob(f"*{ext}"))
            
        # Filter out vendor, node_modules, .git, etc.
        excluded_dirs = {".git", "node_modules", "vendor", "venv", ".venv", "dist", "build"}
        
        filtered_files = []
        for file_path in source_files:
            if not any(excluded in file_path.parts for excluded in excluded_dirs):
                filtered_files.append(file_path)
                
        return filtered_files
        
    def _detect_languages(self) -> List[str]:
        """Detect programming languages used in the repository."""
        detected = []
        
        for language, extensions in self.LANGUAGE_EXTENSIONS.items():
            for ext in extensions:
                if list(self.repo_path.rglob(f"*{ext}")):
                    detected.append(language)
                    break
                    
        return detected