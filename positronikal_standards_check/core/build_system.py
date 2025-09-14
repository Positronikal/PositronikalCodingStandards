"""
Build system validation for Positronikal standards.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BuildSystemValidator:
    """Validates build system requirements."""
    
    # Required Husky/lint-staged dependencies and versions
    REQUIRED_NPM_PACKAGES = {
        "husky": "^9.1.7",
        "lint-staged": "^15.5.0",
        "prettier": "^3.5.3"
    }
    
    # Required npm scripts
    REQUIRED_NPM_SCRIPTS = {
        "prepare": "husky",
        "pre-commit": "lint-staged"
    }
    
    # GNU Make files
    GNU_MAKE_FILES = ["configure", "Makefile.am", "Makefile.in", "Makefile"]
    
    # Git hook files
    GIT_HOOKS = {
        ".husky/pre-commit": "Pre-commit hook",
        ".husky/commit-msg": "Commit message validation hook"
    }
    
    def __init__(self, repo_path: Path):
        """
        Initialize build system validator.
        
        Args:
            repo_path: Path to repository to validate
        """
        self.repo_path = repo_path
        
    def validate(self) -> List[Dict]:
        """
        Validate all build system requirements.
        
        Returns:
            List of validation results
        """
        results = []
        
        # Check for package.json (Node.js projects)
        if (self.repo_path / "package.json").exists():
            results.extend(self._check_npm_requirements())
            results.extend(self._check_git_hooks())
            
        # Check for GNU Make files
        results.extend(self._check_gnu_make())
        
        # Check for other build systems
        results.extend(self._check_other_build_systems())
        
        return results
        
    def _check_npm_requirements(self) -> List[Dict]:
        """Check npm/Node.js build requirements."""
        results = []
        package_json_path = self.repo_path / "package.json"
        
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)
                
            # Check devDependencies
            dev_deps = package_data.get("devDependencies", {})
            
            for package, required_version in self.REQUIRED_NPM_PACKAGES.items():
                if package in dev_deps:
                    # Simple version check (could be enhanced)
                    results.append({
                        "check": f"npm_package_{package}",
                        "status": "pass",
                        "message": f"Required package {package} found in devDependencies"
                    })
                else:
                    results.append({
                        "check": f"npm_package_{package}",
                        "status": "fail",
                        "message": f"Missing required package: {package} {required_version}"
                    })
                    
            # Check scripts
            scripts = package_data.get("scripts", {})
            
            for script_name, expected_value in self.REQUIRED_NPM_SCRIPTS.items():
                if script_name in scripts:
                    if scripts[script_name] == expected_value:
                        results.append({
                            "check": f"npm_script_{script_name}",
                            "status": "pass",
                            "message": f"Required script '{script_name}' configured correctly"
                        })
                    else:
                        results.append({
                            "check": f"npm_script_{script_name}",
                            "status": "warning",
                            "message": f"Script '{script_name}' exists but value differs: expected '{expected_value}', got '{scripts[script_name]}'"
                        })
                else:
                    results.append({
                        "check": f"npm_script_{script_name}",
                        "status": "fail",
                        "message": f"Missing required script: {script_name}"
                    })
                    
            # Check for lint-staged configuration
            if "lint-staged" in package_data or (self.repo_path / ".lintstagedrc").exists():
                results.append({
                    "check": "lint_staged_config",
                    "status": "pass",
                    "message": "lint-staged configuration found"
                })
            else:
                results.append({
                    "check": "lint_staged_config",
                    "status": "warning",
                    "message": "No lint-staged configuration found"
                })
                
        except json.JSONDecodeError as e:
            results.append({
                "check": "package_json",
                "status": "fail",
                "message": f"Invalid package.json: {e}"
            })
        except Exception as e:
            results.append({
                "check": "package_json",
                "status": "fail",
                "message": f"Error reading package.json: {e}"
            })
            
        return results
        
    def _check_git_hooks(self) -> List[Dict]:
        """Check for required git hooks."""
        results = []
        
        for hook_path, description in self.GIT_HOOKS.items():
            full_path = self.repo_path / hook_path
            
            if full_path.exists():
                # Check if hook file is executable (on Unix-like systems)
                if os.name != "nt":  # Not Windows
                    if os.access(full_path, os.X_OK):
                        results.append({
                            "check": f"git_hook_{hook_path.replace('/', '_')}",
                            "status": "pass",
                            "message": f"Git hook exists and is executable: {hook_path}"
                        })
                    else:
                        results.append({
                            "check": f"git_hook_{hook_path.replace('/', '_')}",
                            "status": "warning",
                            "message": f"Git hook exists but is not executable: {hook_path}"
                        })
                else:
                    results.append({
                        "check": f"git_hook_{hook_path.replace('/', '_')}",
                        "status": "pass",
                        "message": f"Git hook exists: {hook_path}"
                    })
            else:
                results.append({
                    "check": f"git_hook_{hook_path.replace('/', '_')}",
                    "status": "fail",
                    "message": f"Missing git hook: {hook_path} ({description})"
                })
                
        return results
        
    def _check_gnu_make(self) -> List[Dict]:
        """Check for GNU Make build system."""
        results = []
        
        # Check if this is a compiled language project
        has_source_code = any(
            self.repo_path.rglob(f"*.{ext}")
            for ext in ["c", "cpp", "cc", "cxx", "h", "hpp"]
        )
        
        if not has_source_code:
            # Not a compiled project, GNU Make not required
            return results
            
        # Check for configure script
        configure_path = self.repo_path / "configure"
        if configure_path.exists():
            # Check if executable
            if os.name != "nt" and os.access(configure_path, os.X_OK):
                results.append({
                    "check": "gnu_make_configure",
                    "status": "pass",
                    "message": "GNU configure script exists and is executable"
                })
            elif os.name == "nt":
                results.append({
                    "check": "gnu_make_configure",
                    "status": "pass",
                    "message": "GNU configure script exists"
                })
            else:
                results.append({
                    "check": "gnu_make_configure",
                    "status": "warning",
                    "message": "GNU configure script exists but is not executable"
                })
        else:
            results.append({
                "check": "gnu_make_configure",
                "status": "warning",
                "message": "No GNU configure script found (required for C/C++ projects)"
            })
            
        # Check for Makefile.am
        if (self.repo_path / "Makefile.am").exists():
            results.append({
                "check": "gnu_make_automake",
                "status": "pass",
                "message": "Makefile.am (Automake) found"
            })
        else:
            results.append({
                "check": "gnu_make_automake",
                "status": "warning",
                "message": "No Makefile.am found (recommended for GNU Make projects)"
            })
            
        # Check for Makefile
        if (self.repo_path / "Makefile").exists():
            results.append({
                "check": "gnu_make_makefile",
                "status": "pass",
                "message": "Makefile found"
            })
            
        return results
        
    def _check_other_build_systems(self) -> List[Dict]:
        """Check for language-specific build systems."""
        results = []
        
        # Python projects
        if (self.repo_path / "setup.py").exists() or (self.repo_path / "pyproject.toml").exists():
            results.append({
                "check": "python_build",
                "status": "pass",
                "message": "Python build configuration found"
            })
            
        # Go projects
        if (self.repo_path / "go.mod").exists():
            results.append({
                "check": "go_build",
                "status": "pass",
                "message": "Go module configuration found"
            })
            
        # Rust projects
        if (self.repo_path / "Cargo.toml").exists():
            results.append({
                "check": "rust_build",
                "status": "pass",
                "message": "Rust Cargo configuration found"
            })
            
        # Java projects
        if (self.repo_path / "pom.xml").exists():
            results.append({
                "check": "java_maven",
                "status": "pass",
                "message": "Maven configuration found"
            })
        elif (self.repo_path / "build.gradle").exists():
            results.append({
                "check": "java_gradle",
                "status": "pass",
                "message": "Gradle configuration found"
            })
            
        return results
        
    def check_github_actions(self) -> List[Dict]:
        """Check GitHub Actions configuration."""
        results = []
        workflows_dir = self.repo_path / ".github" / "workflows"
        
        if not workflows_dir.exists():
            results.append({
                "check": "github_workflows",
                "status": "warning",
                "message": "No GitHub workflows directory found"
            })
            return results
            
        # Check for workflow files
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        if not workflow_files:
            results.append({
                "check": "github_workflows",
                "status": "warning",
                "message": "No workflow files found in .github/workflows"
            })
            return results
            
        # Check for version pinning in workflows
        import re
        action_pattern = re.compile(r'uses:\s*([^@\s]+)@(.+)')
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                matches = action_pattern.findall(content)
                for action, version in matches:
                    # Check if version is pinned (not a branch name)
                    if version in ["main", "master", "develop", "latest"]:
                        results.append({
                            "check": f"action_version_{action}",
                            "status": "warning",
                            "message": f"Action {action} uses unpinned version: {version}"
                        })
                    elif action.startswith("actions/") and version == "*":
                        # Wildcard allowed for GitHub official actions
                        results.append({
                            "check": f"action_version_{action}",
                            "status": "pass",
                            "message": f"GitHub official action {action} uses wildcard (allowed)"
                        })
                    else:
                        results.append({
                            "check": f"action_version_{action}",
                            "status": "pass",
                            "message": f"Action {action} uses pinned version: {version}"
                        })
                        
            except Exception as e:
                results.append({
                    "check": f"workflow_file_{workflow_file.name}",
                    "status": "fail",
                    "message": f"Error reading workflow file {workflow_file.name}: {e}"
                })
                
        return results