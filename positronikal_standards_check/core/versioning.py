"""
Version management validation for Positronikal standards.

Git tags are the authoritative version source for all Positronikal projects.
This module checks that each repo's versioning setup reflects that policy.
"""

import subprocess
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class VersioningValidator:
    """Validates version management practices."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def validate(self) -> List[Dict]:
        results = []
        results.extend(self._check_git_version_tags())
        results.extend(self._check_language_versioning())
        return results

    def _check_git_version_tags(self) -> List[Dict]:
        """Check that the repo has at least one semantic version tag."""
        try:
            # noqa justification: "git" is a fixed hardcoded executable
            # resolved via PATH, not derived from user input.
            result = subprocess.run(
                ["git", "tag", "--list", "v*.*.*"],  # noqa: S607
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=10,
            )
            if result.returncode != 0:
                return [
                    {
                        "check": "version_tags",
                        "status": "warning",
                        "message": (
                            "Not a git repository or git unavailable; "
                            "cannot check version tags"
                        ),
                    }
                ]
            tags = [t.strip() for t in result.stdout.splitlines() if t.strip()]
            if tags:
                recent = ", ".join(sorted(tags)[-3:])
                return [
                    {
                        "check": "version_tags",
                        "status": "pass",
                        "message": f"Git version tags found (most recent: {recent})",
                    }
                ]
            return [
                {
                    "check": "version_tags",
                    "status": "fail",
                    "message": (
                        "No semantic version tags (v*.*.*) found. "
                        "Git tags are the authoritative version source "
                        "per PCS versioning standards."
                    ),
                }
            ]
        except Exception as e:
            return [
                {
                    "check": "version_tags",
                    "status": "warning",
                    "message": f"Could not check git tags: {e}",
                }
            ]

    def _check_language_versioning(self) -> List[Dict]:
        """Check language-specific versioning tool setup."""
        results = []
        results.extend(self._check_python_versioning())
        results.extend(self._check_go_versioning())
        return results

    def _check_python_versioning(self) -> List[Dict]:
        """Check Python projects for git-tag-based dynamic versioning."""
        pyproject = self.repo_path / "pyproject.toml"
        if not pyproject.exists():
            return []
        try:
            content = pyproject.read_text(encoding="utf-8")
        except OSError:
            return []

        git_tools = (
            "hatch-vcs",
            "setuptools-scm",
            "setuptools_scm",
            "versioneer",
        )
        if any(tool in content for tool in git_tools):
            return [
                {
                    "check": "python_version_source",
                    "status": "pass",
                    "message": ("Python project uses git-tag-based dynamic versioning"),
                }
            ]
        has_dynamic = (
            'dynamic = ["version"]' in content or "dynamic=['version']" in content
        )
        if has_dynamic:
            return [
                {
                    "check": "python_version_source",
                    "status": "warning",
                    "message": (
                        "pyproject.toml declares dynamic versioning but no "
                        "recognized tool (hatch-vcs, setuptools-scm) detected "
                        "in build-system requires"
                    ),
                }
            ]
        return [
            {
                "check": "python_version_source",
                "status": "warning",
                "message": (
                    "Python project has pyproject.toml but no git-tag-based "
                    "versioning detected. Add hatch-vcs to [build-system] "
                    'requires and set dynamic = ["version"] in [project].'
                ),
            }
        ]

    def _check_go_versioning(self) -> List[Dict]:
        """Check Go projects for version injection via ldflags."""
        if not (self.repo_path / "go.mod").exists():
            return []
        makefile = self.repo_path / "Makefile"
        if makefile.exists():
            try:
                content = makefile.read_text(encoding="utf-8", errors="ignore")
                if "ldflags" in content and "version" in content.lower():
                    return [
                        {
                            "check": "go_version_source",
                            "status": "pass",
                            "message": (
                                "Go project has version injection via "
                                "ldflags in Makefile"
                            ),
                        }
                    ]
            except OSError:
                pass
        ldflags_example = '-ldflags "-X main.version=$(git describe --tags --abbrev=0)"'
        return [
            {
                "check": "go_version_source",
                "status": "warning",
                "message": (
                    "Go project detected but no ldflags version injection "
                    f"found in Makefile. Add: {ldflags_example}"
                ),
            }
        ]
