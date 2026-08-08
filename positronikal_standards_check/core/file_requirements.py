# SPDX-License-Identifier: GPL-3.0-or-later
"""
File requirements validation for Positronikal standards.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FileRequirementsValidator:
    """Validates required files and directory structure."""

    # Core required files
    REQUIRED_FILES = {
        "README.md": "Project documentation",
        "CONTRIBUTING.md": "Contribution guidelines",
        "CODE_OF_CONDUCT.md": "Community code of conduct",
        ".gitignore": "Git ignore patterns",
        "SECURITY.md": "Security policy",
    }

    # License files (at least one required).
    # Preferred: bare names (no extension) — detected by GitHub licensee and SPDX tools.
    # The .md variants are accepted for backward compatibility but trigger a migration
    # warning. See GitHub Configuration Standards.md § Licensing (SPDX).
    LICENSE_FILES = [
        "COPYING",
        "COPYING.LESSER",
        "LICENSE",  # preferred
        "COPYING.md",
        "COPYING.LESSER.md",
        "LICENSE.md",
        "LICENSE.CC.md",  # legacy
    ]
    LICENSE_FILES_PREFERRED = frozenset({"COPYING", "COPYING.LESSER", "LICENSE"})

    # Source file extensions that require an SPDX-License-Identifier header.
    SPDX_EXTENSIONS = frozenset({".py", ".go", ".sh", ".c", ".cpp", ".h", ".hpp"})

    # Optional but recommended files
    RECOMMENDED_FILES = {
        "AUTHORS.md": "List of contributors",
        "BUGS.md": "Bug reporting guidelines",
        "USING.md": "Usage instructions",
        ".editorconfig": "Editor configuration",
    }

    # GitHub-specific files
    GITHUB_FILES = {
        ".github/CODEOWNERS": "Code ownership",
        ".github/dependabot.yml": "Dependabot configuration",
        ".github/workflows/ci.yml": "CI workflow",
    }

    # GitHub templates
    GITHUB_TEMPLATES = {
        ".github/ISSUE_TEMPLATE/bug_report.md": "Bug report template",
        ".github/ISSUE_TEMPLATE/feature_request.md": "Feature request template",
        ".github/PULL_REQUEST_TEMPLATE.md": "Pull request template",
    }

    # SBOM files — any one of these at repo root satisfies the check.
    # Preferred: sbom.cdx.json (CycloneDX JSON). See standards/security/sbom.md.
    SBOM_FILES = [
        "sbom.cdx.json",
        "bom.json",
        "sbom.cdx.xml",
        "sbom.spdx.json",
        "sbom.spdx",
    ]

    # Infrastructure directories excluded from Python package detection.
    _INFRA_DIRS = frozenset(
        {
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "build",
            "dist",
            ".github",
            ".husky",
            "__pycache__",
            "repo-template",
            "var",
            "ref",
            "api",
            "docs",
        }
    )

    # Standard directories. "test" accepts tests/ too — see _check_standard_directories.
    # "docs" is intentionally absent: docs/ is optional human-authored content.
    # Doxygen output goes to api/ (tracked in git, excluded from linting).
    STANDARD_DIRECTORIES = {
        "src": "Source code",
        "test": "Test files",
    }

    # File extensions supported by CodeQL — shell is NOT included
    CODEQL_EXTENSIONS = frozenset(
        [
            ".py",
            ".go",
            ".java",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".rb",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".swift",
        ]
    )

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
            if self._has_codeql_language():
                results.extend(self._check_codeql_coverage())

        # Check standard directories
        results.extend(self._check_standard_directories())

        # Check for machine-readable SBOM
        results.extend(self._check_sbom_file())

        # Check SPDX-License-Identifier headers in source files
        results.extend(self._check_spdx_headers())

        return results

    def _check_required_files(self) -> List[Dict]:
        """Check for required files."""
        results = []

        for filename, description in self.REQUIRED_FILES.items():
            file_path = self.repo_path / filename

            if file_path.exists():
                # Check if file is not empty
                if file_path.stat().st_size > 0:
                    results.append(
                        {
                            "check": f"required_file_{filename}",
                            "status": "pass",
                            "message": f"Required file exists: {filename}",
                        }
                    )
                else:
                    results.append(
                        {
                            "check": f"required_file_{filename}",
                            "status": "warning",
                            "message": f"Required file exists but is empty: {filename}",
                        }
                    )
            else:
                results.append(
                    {
                        "check": f"required_file_{filename}",
                        "status": "fail",
                        "message": f"Missing required file: {filename} ({description})",
                    }
                )

        return results

    def _check_license_files(self) -> List[Dict]:
        """Check for at least one license file."""
        results = []

        found_licenses = []
        for license_file in self.LICENSE_FILES:
            if (self.repo_path / license_file).exists():
                found_licenses.append(license_file)

        if not found_licenses:
            results.append(
                {
                    "check": "license_file",
                    "status": "fail",
                    "message": (
                        "No license file found. Preferred: COPYING or LICENSE "
                        "(no extension, SPDX-detectable). Also accepted: "
                        + ", ".join(
                            f
                            for f in self.LICENSE_FILES
                            if f not in self.LICENSE_FILES_PREFERRED
                        )
                    ),
                }
            )
            return results

        preferred = [f for f in found_licenses if f in self.LICENSE_FILES_PREFERRED]
        legacy = [f for f in found_licenses if f not in self.LICENSE_FILES_PREFERRED]

        if preferred:
            results.append(
                {
                    "check": "license_file",
                    "status": "pass",
                    "message": f"License file(s) found: {', '.join(found_licenses)}",
                }
            )
        else:
            results.append(
                {
                    "check": "license_file",
                    "status": "warning",
                    "message": (
                        f"License file uses .md extension ({', '.join(legacy)}). "
                        f"Rename to bare filename (COPYING or LICENSE) for SPDX "
                        f"machine-detection by GitHub licensee and registry tooling."
                    ),
                }
            )

        return results

    def _check_spdx_headers(self) -> List[Dict]:
        """Check source files for SPDX-License-Identifier headers (warning level)."""
        results = []
        missing = []

        for path in self.repo_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in self.SPDX_EXTENSIONS:
                continue
            parts = path.relative_to(self.repo_path).parts
            if any(p.startswith(".") or p in self._INFRA_DIRS for p in parts):
                continue
            try:
                with path.open(encoding="utf-8", errors="ignore") as f:
                    header = "".join(f.readline() for _ in range(5))
                if "SPDX-License-Identifier:" not in header:
                    missing.append(str(path.relative_to(self.repo_path)))
            except OSError:
                continue

        if not missing:
            results.append(
                {
                    "check": "spdx_headers",
                    "status": "pass",
                    "message": "All source files have SPDX-License-Identifier headers.",
                }
            )
        else:
            results.append(
                {
                    "check": "spdx_headers",
                    "status": "warning",
                    "message": (
                        f"{len(missing)} source file(s) missing "
                        f"SPDX-License-Identifier header: "
                        f"{', '.join(missing[:5])}"
                        + (" ..." if len(missing) > 5 else "")
                    ),
                }
            )

        return results

    def _check_recommended_files(self) -> List[Dict]:
        """Check for recommended files."""
        results = []

        for filename, description in self.RECOMMENDED_FILES.items():
            file_path = self.repo_path / filename

            if file_path.exists():
                results.append(
                    {
                        "check": f"recommended_file_{filename}",
                        "status": "pass",
                        "message": f"Recommended file exists: {filename}",
                    }
                )
            else:
                results.append(
                    {
                        "check": f"recommended_file_{filename}",
                        "status": "warning",
                        "message": (
                            f"Missing recommended file: {filename} ({description})"
                        ),
                    }
                )

        return results

    def _check_github_files(self) -> List[Dict]:
        """Check for GitHub-specific files."""
        results = []

        for filepath, description in self.GITHUB_FILES.items():
            file_path = self.repo_path / filepath

            if file_path.exists():
                results.append(
                    {
                        "check": f"github_file_{filepath.replace('/', '_')}",
                        "status": "pass",
                        "message": f"GitHub file exists: {filepath}",
                    }
                )
            else:
                results.append(
                    {
                        "check": f"github_file_{filepath.replace('/', '_')}",
                        "status": "fail",
                        "message": f"Missing GitHub file: {filepath} ({description})",
                    }
                )

        return results

    def _check_github_templates(self) -> List[Dict]:
        """Check for GitHub template files."""
        results = []

        for filepath, description in self.GITHUB_TEMPLATES.items():
            file_path = self.repo_path / filepath

            if file_path.exists():
                results.append(
                    {
                        "check": f"github_template_{filepath.replace('/', '_')}",
                        "status": "pass",
                        "message": f"GitHub template exists: {filepath}",
                    }
                )
            else:
                results.append(
                    {
                        "check": f"github_template_{filepath.replace('/', '_')}",
                        "status": "warning",
                        "message": (
                            f"Missing GitHub template: {filepath} ({description})"
                        ),
                    }
                )

        return results

    def _has_codeql_language(self) -> bool:
        """Return True if the repo contains any CodeQL-supported language files."""
        excluded = {".git", ".venv", "venv", "node_modules", "build", "dist"}
        for ext in self.CODEQL_EXTENSIONS:
            for f in self.repo_path.rglob(f"*{ext}"):
                if not any(part in excluded for part in f.parts):
                    return True
        return False

    def _check_codeql_coverage(self) -> List[Dict]:
        """Check for CodeQL scanning via workflow file or GitHub Default Setup."""
        codeql_file = self.repo_path / ".github" / "workflows" / "codeql.yml"
        check_id = "github_file_.github_workflows_codeql.yml"

        if codeql_file.exists():
            return [
                {
                    "check": check_id,
                    "status": "pass",
                    "message": "GitHub file exists: .github/workflows/codeql.yml",
                }
            ]

        # File absent — check whether GitHub Default Setup covers this repo.
        # Org-enforced Default Setup prevents repos from running a custom
        # codeql.yml alongside it, so the file may be intentionally absent.
        try:
            # "git" and "gh" are fixed executable names resolved via PATH,
            # not derived from user input.
            remote = subprocess.run(  # noqa: S603
                ["git", "remote", "get-url", "origin"],  # noqa: S607
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=10,
            )
            if remote.returncode != 0:
                raise RuntimeError("no git remote")

            match = re.search(
                r"github\.com[/:]([^/]+/[^/]+?)(?:\.git)?$",
                remote.stdout.strip(),
            )
            if not match:
                raise RuntimeError(f"unrecognized remote: {remote.stdout.strip()}")

            owner_repo = match.group(1)
            endpoint = f"repos/{owner_repo}/code-scanning/default-setup"
            api = subprocess.run(  # noqa: S603
                ["gh", "api", endpoint],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=15,
            )
            if api.returncode == 0:
                data = json.loads(api.stdout)
                if data.get("state") == "configured":
                    return [
                        {
                            "check": check_id,
                            "status": "pass",
                            "message": (
                                "CodeQL coverage provided by GitHub Default Setup "
                                f"({owner_repo}); no codeql.yml needed"
                            ),
                        }
                    ]
        except Exception as exc:
            logger.debug("CodeQL Default Setup check failed: %s", exc)

        return [
            {
                "check": check_id,
                "status": "fail",
                "message": (
                    "Missing CodeQL scanning: add .github/workflows/codeql.yml "
                    "or enable GitHub Default Setup for this repo"
                ),
            }
        ]

    def _find_python_package_dirs(self) -> List[Path]:
        """Return top-level Python package directories (contain __init__.py)."""
        return [
            d
            for d in self.repo_path.iterdir()
            if d.is_dir()
            and d.name not in self._INFRA_DIRS
            and not d.name.startswith(".")
            and (d / "__init__.py").exists()
        ]

    def _check_standard_directories(self) -> List[Dict]:
        """Check for standard directory structure."""
        results = []

        for dirname, description in self.STANDARD_DIRECTORIES.items():
            # The test directory accepts both test/ and tests/
            candidates = [self.repo_path / dirname]
            if dirname == "test":
                candidates.append(self.repo_path / "tests")

            # Also recognize Python flat-layout packages:
            # source root = any top-level dir with __init__.py;
            # test root = test/ or tests/ nested inside one.
            pkg_dirs = self._find_python_package_dirs()
            if dirname == "src":
                candidates.extend(pkg_dirs)
            if dirname == "test":
                for pkg in pkg_dirs:
                    candidates.append(pkg / "test")
                    candidates.append(pkg / "tests")

            existing = [p for p in candidates if p.exists() and p.is_dir()]
            # Prefer a non-empty candidate so tests/ wins over an empty test/
            found_path = next(
                (p for p in existing if any(p.iterdir())),
                existing[0] if existing else None,
            )

            if found_path is not None:
                if any(found_path.iterdir()):
                    results.append(
                        {
                            "check": f"standard_dir_{dirname}",
                            "status": "pass",
                            "message": (
                                f"Standard directory exists: {found_path.name}"
                            ),
                        }
                    )
                else:
                    results.append(
                        {
                            "check": f"standard_dir_{dirname}",
                            "status": "warning",
                            "message": (
                                f"Standard directory exists but is empty: "
                                f"{found_path.name}"
                            ),
                        }
                    )
            else:
                label = "test or tests" if dirname == "test" else dirname
                results.append(
                    {
                        "check": f"standard_dir_{dirname}",
                        "status": "warning",
                        "message": (
                            f"Missing standard directory: {label} ({description})"
                        ),
                    }
                )

        return results

    def _check_sbom_file(self) -> List[Dict]:
        """Check for a machine-readable SBOM at the repo root."""
        for filename in self.SBOM_FILES:
            if (self.repo_path / filename).exists():
                return [
                    {
                        "check": "sbom_file",
                        "status": "pass",
                        "message": f"SBOM file found: {filename}",
                    }
                ]
        return [
            {
                "check": "sbom_file",
                "status": "warning",
                "message": (
                    "No machine-readable SBOM found. Generate one with cyclonedx-py "
                    "and commit as sbom.cdx.json. See standards/security/sbom.md."
                ),
            }
        ]

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
                    results.append(
                        {
                            "check": f"file_size_{file_path.name}",
                            "status": "fail",
                            "message": (
                                f"File exceeds 10MB limit: "
                                f"{file_path.relative_to(self.repo_path)} "
                                f"({file_size / 1024 / 1024:.2f}MB)"
                            ),
                        }
                    )

        if not results:
            results.append(
                {
                    "check": "file_size_limits",
                    "status": "pass",
                    "message": "All files within 10MB size limit",
                }
            )

        return results

    def check_binary_files(self) -> List[Dict]:
        """Check for prohibited binary files."""
        results = []

        # Prohibited extensions
        prohibited_extensions = {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".bin",
            ".com",
            ".app",
            ".deb",
            ".rpm",
            ".dmg",
        }

        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file():
                # Skip .git directory
                if ".git" in file_path.parts:
                    continue

                if file_path.suffix.lower() in prohibited_extensions:
                    results.append(
                        {
                            "check": f"binary_file_{file_path.name}",
                            "status": "fail",
                            "message": (
                                f"Prohibited binary file found: "
                                f"{file_path.relative_to(self.repo_path)}"
                            ),
                        }
                    )

        if not results:
            results.append(
                {
                    "check": "binary_files",
                    "status": "pass",
                    "message": "No prohibited binary files found",
                }
            )

        return results
