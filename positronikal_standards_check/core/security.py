"""
Security requirements validation for Positronikal standards.
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validates security requirements."""
    
    # Security-related files
    SECURITY_FILES = {
        ".github/SECURITY.md": "Security policy",
        ".github/dependabot.yml": "Dependabot configuration",
        ".github/workflows/codeql.yml": "CodeQL workflow"
    }
    
    # Sensitive patterns to check for
    SENSITIVE_PATTERNS = [
        # API keys and tokens
        (r'api[_-]?key\s*=\s*["\'][\w\-]{20,}["\']', "API key"),
        (r'token\s*=\s*["\'][\w\-]{20,}["\']', "Token"),
        (r'secret\s*=\s*["\'][\w\-]{20,}["\']', "Secret"),
        
        # AWS
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
        (r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\'][\w\/\+=]{40}["\']', "AWS Secret Key"),
        
        # Private keys
        (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', "Private Key"),
        (r'-----BEGIN PGP PRIVATE KEY BLOCK-----', "PGP Private Key"),
        
        # Database URLs
        (r'(mysql|postgresql|mongodb):\/\/[^:]+:[^@]+@[^\/]+', "Database URL with credentials"),
        
        # Generic passwords
        (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password"),
        (r'passwd\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password")
    ]
    
    # SAST tools by language
    SAST_TOOLS = {
        "python": ["bandit", "-r"],
        "go": ["gosec", "./..."],
        "javascript": ["eslint", "--ext", ".js,.jsx", "."],
        "java": ["spotbugs", "-textui"],
        "ruby": ["brakeman"],
        "php": ["psalm", "--show-info=false"]
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize security validator.
        
        Args:
            repo_path: Path to repository to validate
        """
        self.repo_path = repo_path
        
    def validate(self) -> List[Dict]:
        """
        Validate all security requirements.
        
        Returns:
            List of validation results
        """
        results = []
        
        # Check security files
        results.extend(self._check_security_files())
        
        # Check for sensitive data
        results.extend(self._check_sensitive_data())
        
        # Check git history for signed commits
        results.extend(self._check_commit_signing())
        
        # Check dependency files
        results.extend(self._check_dependencies())
        
        # Check GitHub Actions security
        results.extend(self._check_github_actions_security())
        
        # Run SAST tools if available
        results.extend(self._run_sast_tools())
        
        return results
        
    def _check_security_files(self) -> List[Dict]:
        """Check for required security files."""
        results = []
        
        for filepath, description in self.SECURITY_FILES.items():
            file_path = self.repo_path / filepath
            
            if file_path.exists():
                # Check if file has content
                if file_path.stat().st_size > 50:  # More than minimal content
                    results.append({
                        "check": f"security_file_{filepath.replace('/', '_')}",
                        "status": "pass",
                        "message": f"Security file exists: {filepath}"
                    })
                else:
                    results.append({
                        "check": f"security_file_{filepath.replace('/', '_')}",
                        "status": "warning",
                        "message": f"Security file exists but appears minimal: {filepath}"
                    })
            else:
                results.append({
                    "check": f"security_file_{filepath.replace('/', '_')}",
                    "status": "fail",
                    "message": f"Missing security file: {filepath} ({description})"
                })
                
        return results
        
    def _check_sensitive_data(self) -> List[Dict]:
        """Check for hardcoded sensitive data."""
        results = []
        found_issues = []
        
        # Get source files to check
        source_files = []
        for ext in [".py", ".js", ".java", ".go", ".rb", ".php", ".sh", ".yml", ".yaml", ".json"]:
            source_files.extend(self.repo_path.rglob(f"*{ext}"))
            
        # Filter out common excluded directories
        excluded_dirs = {".git", "node_modules", "vendor", "venv", ".venv", "dist", "build"}
        
        for file_path in source_files:
            # Skip if in excluded directory
            if any(excluded in file_path.parts for excluded in excluded_dirs):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                for pattern, pattern_type in self.SENSITIVE_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_issues.append({
                            "file": str(file_path.relative_to(self.repo_path)),
                            "type": pattern_type
                        })
                        break  # One issue per file is enough
                        
            except Exception as e:
                logger.warning(f"Could not check {file_path} for sensitive data: {e}")
                
        if found_issues:
            # Report first few issues
            issue_msgs = [f"{issue['file']} ({issue['type']})" for issue in found_issues[:3]]
            results.append({
                "check": "sensitive_data",
                "status": "fail",
                "message": f"Potential sensitive data found in: {', '.join(issue_msgs)}{'...' if len(found_issues) > 3 else ''}"
            })
        else:
            results.append({
                "check": "sensitive_data",
                "status": "pass",
                "message": "No obvious sensitive data patterns found"
            })
            
        return results
        
    def _check_commit_signing(self) -> List[Dict]:
        """Check if commits are signed."""
        results = []
        
        try:
            # Get last 10 commits
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H %G?", "-10"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                signed_count = 0
                unsigned_count = 0
                
                for commit in commits:
                    if commit:
                        parts = commit.split()
                        if len(parts) >= 2:
                            signature_status = parts[1]
                            if signature_status in ["G", "U", "X", "Y", "R"]:
                                signed_count += 1
                            else:
                                unsigned_count += 1
                                
                if unsigned_count == 0 and signed_count > 0:
                    results.append({
                        "check": "commit_signing",
                        "status": "pass",
                        "message": f"All recent commits are signed ({signed_count}/{signed_count})"
                    })
                elif signed_count > 0:
                    results.append({
                        "check": "commit_signing",
                        "status": "warning",
                        "message": f"Some commits are unsigned ({unsigned_count}/{signed_count + unsigned_count})"
                    })
                else:
                    results.append({
                        "check": "commit_signing",
                        "status": "fail",
                        "message": "No signed commits found in recent history"
                    })
            else:
                results.append({
                    "check": "commit_signing",
                    "status": "warning",
                    "message": "Could not check commit signing (not a git repository?)"
                })
                
        except Exception as e:
            results.append({
                "check": "commit_signing",
                "status": "warning",
                "message": f"Could not check commit signing: {e}"
            })
            
        return results
        
    def _check_dependencies(self) -> List[Dict]:
        """Check dependency management and security."""
        results = []
        
        # Check for package-lock.json (Node.js)
        if (self.repo_path / "package.json").exists():
            if (self.repo_path / "package-lock.json").exists():
                results.append({
                    "check": "npm_lockfile",
                    "status": "pass",
                    "message": "package-lock.json exists for dependency pinning"
                })
            else:
                results.append({
                    "check": "npm_lockfile",
                    "status": "fail",
                    "message": "Missing package-lock.json for dependency pinning"
                })
                
        # Check for requirements.txt or Pipfile.lock (Python)
        if any(self.repo_path.glob("*.py")):
            if (self.repo_path / "requirements.txt").exists() or (self.repo_path / "Pipfile.lock").exists():
                results.append({
                    "check": "python_dependencies",
                    "status": "pass",
                    "message": "Python dependency file found"
                })
            else:
                results.append({
                    "check": "python_dependencies",
                    "status": "warning",
                    "message": "No requirements.txt or Pipfile.lock found for Python project"
                })
                
        # Check for go.sum (Go)
        if (self.repo_path / "go.mod").exists():
            if (self.repo_path / "go.sum").exists():
                results.append({
                    "check": "go_lockfile",
                    "status": "pass",
                    "message": "go.sum exists for dependency pinning"
                })
            else:
                results.append({
                    "check": "go_lockfile",
                    "status": "fail",
                    "message": "Missing go.sum for dependency pinning"
                })
                
        return results
        
    def _check_github_actions_security(self) -> List[Dict]:
        """Check GitHub Actions security configurations."""
        results = []
        workflows_dir = self.repo_path / ".github" / "workflows"
        
        if not workflows_dir.exists():
            return results
            
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Check for minimum permissions
                if "permissions:" in content:
                    if "contents: read" in content or "permissions: read-all" in content:
                        results.append({
                            "check": f"workflow_permissions_{workflow_file.name}",
                            "status": "pass",
                            "message": f"Workflow {workflow_file.name} has restricted permissions"
                        })
                    else:
                        results.append({
                            "check": f"workflow_permissions_{workflow_file.name}",
                            "status": "warning",
                            "message": f"Workflow {workflow_file.name} may have excessive permissions"
                        })
                else:
                    results.append({
                        "check": f"workflow_permissions_{workflow_file.name}",
                        "status": "warning",
                        "message": f"Workflow {workflow_file.name} does not explicitly set permissions"
                    })
                    
                # Check for secret usage
                if "${{ secrets." in content and "GITHUB_TOKEN" not in content:
                    results.append({
                        "check": f"workflow_secrets_{workflow_file.name}",
                        "status": "warning",
                        "message": f"Workflow {workflow_file.name} uses custom secrets - ensure they are properly secured"
                    })
                    
            except Exception as e:
                results.append({
                    "check": f"workflow_file_{workflow_file.name}",
                    "status": "fail",
                    "message": f"Error reading workflow {workflow_file.name}: {e}"
                })
                
        return results
        
    def _run_sast_tools(self) -> List[Dict]:
        """Run Static Application Security Testing tools."""
        results = []
        
        # Detect languages
        detected_languages = []
        for language, extensions in {
            "python": [".py"],
            "go": [".go"],
            "javascript": [".js", ".jsx"],
            "java": [".java"],
            "ruby": [".rb"],
            "php": [".php"]
        }.items():
            for ext in extensions:
                if list(self.repo_path.rglob(f"*{ext}")):
                    detected_languages.append(language)
                    break
                    
        # Run SAST tools for detected languages
        for language in detected_languages:
            if language in self.SAST_TOOLS:
                tool_cmd = self.SAST_TOOLS[language]
                
                try:
                    # Check if tool is available
                    subprocess.run(
                        [tool_cmd[0], "--version"],
                        capture_output=True,
                        check=False,
                        cwd=self.repo_path
                    )
                    
                    # Run the SAST tool
                    result = subprocess.run(
                        tool_cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.repo_path,
                        timeout=60  # 60 second timeout
                    )
                    
                    if result.returncode == 0:
                        results.append({
                            "check": f"sast_{language}",
                            "status": "pass",
                            "message": f"{language.capitalize()} SAST scan passed"
                        })
                    else:
                        # Parse output for issues
                        output = result.stdout or result.stderr
                        results.append({
                            "check": f"sast_{language}",
                            "status": "fail",
                            "message": f"{language.capitalize()} SAST found issues: {output[:200]}..."
                        })
                        
                except FileNotFoundError:
                    results.append({
                        "check": f"sast_{language}",
                        "status": "warning",
                        "message": f"{language.capitalize()} SAST tool not available: {tool_cmd[0]}"
                    })
                except subprocess.TimeoutExpired:
                    results.append({
                        "check": f"sast_{language}",
                        "status": "warning",
                        "message": f"{language.capitalize()} SAST scan timed out"
                    })
                except Exception as e:
                    results.append({
                        "check": f"sast_{language}",
                        "status": "warning",
                        "message": f"Could not run {language} SAST: {e}"
                    })
                    
        return results