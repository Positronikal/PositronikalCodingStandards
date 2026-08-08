"""
Pytest integration tests for Positronikal Standards Checker.
"""

import os
import sys
import json
import stat
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from positronikal_standards_check import PositronikalStandardsChecker
from positronikal_standards_check.core.code_standards import (
    CodeStandardsValidator,
)


# Pytest markers for selective testing
pytestmark = [pytest.mark.positronikal, pytest.mark.standards]


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
        (repo_path / "README.md").write_text(
            "# Test Repository\n\nTest repository for standards validation."
        )

        yield repo_path


@pytest.fixture
def compliant_repo(temp_repo):
    """Create a fully compliant repository."""
    repo_path = temp_repo

    # Add all required files
    (repo_path / "CONTRIBUTING.md").write_text(
        "# Contributing\n\nContribution guidelines."
    )
    (repo_path / "CODE_OF_CONDUCT.md").write_text(
        "# Code of Conduct\n\nContributor Covenant v2.1."
    )
    (repo_path / ".gitignore").write_text("*.pyc\n__pycache__/\nnode_modules/")
    (repo_path / "LICENSE.md").write_text("MIT License\n\nCopyright (c) 2024")
    (repo_path / "AUTHORS.md").write_text("# Authors\n\n- Test Author")
    (repo_path / "SECURITY.md").write_text(
        "# Security Policy\n\nReport vulnerabilities to security@example.com"
    )

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
    (github_dir / "CODEOWNERS").write_text("* @testowner")

    # Add GitHub templates
    templates_dir = github_dir / "ISSUE_TEMPLATE"
    templates_dir.mkdir()
    (templates_dir / "bug_report.md").write_text(
        "---\ntitle: Bug Report\n---\n\nBug template"
    )
    (templates_dir / "feature_request.md").write_text(
        "---\ntitle: Feature Request\n---\n\nFeature template"
    )
    (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(
        "## Description\n\nPR template"
    )

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

    codeql_workflow = """
name: CodeQL
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: github/codeql-action/init@v3
      - uses: github/codeql-action/analyze@v3
"""
    (workflows_dir / "codeql.yml").write_text(codeql_workflow)

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
        "scripts": {"prepare": "husky", "pre-commit": "lint-staged"},
        "devDependencies": {
            "husky": "^9.1.7",
            "lint-staged": "^15.5.0",
            "prettier": "^3.5.3",
        },
        "lint-staged": {"*.js": ["prettier --write", "git add"]},
    }
    (repo_path / "package.json").write_text(json.dumps(package_json, indent=2))
    (repo_path / "package-lock.json").write_text(
        json.dumps({"name": "test-repo", "lockfileVersion": 3}, indent=2)
    )

    # Add Husky hooks
    husky_dir = repo_path / ".husky"
    husky_dir.mkdir()
    (husky_dir / "pre-commit").write_text("#!/bin/sh\nnpx lint-staged")
    (husky_dir / "commit-msg").write_text("#!/bin/sh\necho 'Checking commit message'")
    (husky_dir / "pre-push").write_text("#!/bin/sh\nbash .git/hooks/pre-push")
    for name in ("pre-commit", "commit-msg", "pre-push"):
        path = husky_dir / name
        mode = path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(path, mode)  # noqa: S103 -- test fixture hook, not shipped output

    # Add SBOM (CycloneDX JSON — preferred format)
    (repo_path / "sbom.cdx.json").write_text(
        '{"bomFormat": "CycloneDX", "specVersion": "1.6"}\n'
    )

    # Add sample source file
    # newline="" disables write_text's default platform newline
    # translation (CRLF on Windows), so the file is LF on every OS.
    (repo_path / "src" / "main.py").write_text(
        "#!/usr/bin/env python3\n\n"
        "def main():\n"
        "    print('Hello, World!')\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        newline="",
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
            r["status"] == "fail" and "CODE_OF_CONDUCT.md" in r["message"]
            for r in results.failed
        )
        assert any(
            r["status"] == "fail" and ".gitignore" in r["message"]
            for r in results.failed
        )
        assert any(
            r["status"] == "fail" and "SECURITY.md" in r["message"]
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
        assert any(
            r["check"] == "required_file_SECURITY.md" and r["status"] == "pass"
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

    @pytest.mark.positronikal_files
    def test_pr_template_missing(self, temp_repo):
        """Test warning when PR template is absent from a repo with .github/."""
        (temp_repo / ".github").mkdir()
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        assert any(
            "PULL_REQUEST_TEMPLATE.md" in r["check"] and r["status"] == "warning"
            for r in results.warnings
        )

    @pytest.mark.positronikal_files
    def test_pr_template_present(self, compliant_repo):
        """Test pass when PR template is present."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "github_template_.github_PULL_REQUEST_TEMPLATE.md"
            and r["status"] == "pass"
            for r in results.passed
        )

    @pytest.mark.positronikal_files
    def test_code_of_conduct_missing(self, temp_repo):
        """Test fail when CODE_OF_CONDUCT.md is absent."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "required_file_CODE_OF_CONDUCT.md" and r["status"] == "fail"
            for r in results.failed
        )

    @pytest.mark.positronikal_files
    def test_code_of_conduct_present(self, compliant_repo):
        """Test pass when CODE_OF_CONDUCT.md is present."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "required_file_CODE_OF_CONDUCT.md" and r["status"] == "pass"
            for r in results.passed
        )

    @pytest.mark.positronikal_files
    def test_sbom_file_missing(self, temp_repo):
        """Test warning when no SBOM file is present."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "sbom_file" and r["status"] == "warning"
            for r in results.warnings
        )

    @pytest.mark.positronikal_files
    def test_sbom_file_present(self, temp_repo):
        """Test pass when sbom.cdx.json exists at repo root."""
        (temp_repo / "sbom.cdx.json").write_text(
            '{"bomFormat": "CycloneDX", "specVersion": "1.6"}\n'
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "sbom_file" and r["status"] == "pass" for r in results.passed
        )

    @pytest.mark.positronikal_files
    def test_codeql_file_present(self, compliant_repo):
        """Test pass when codeql.yml workflow file exists."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "github_file_.github_workflows_codeql.yml"
            and r["status"] == "pass"
            for r in results.passed
        )

    @pytest.mark.positronikal_files
    def test_codeql_default_setup_active(self, temp_repo):
        """Test pass when codeql.yml absent but GitHub Default Setup is configured."""
        (temp_repo / ".github" / "workflows").mkdir(parents=True)

        remote_mock = MagicMock()
        remote_mock.returncode = 0
        remote_mock.stdout = (
            "https://github.com/Positronikal/PositronikalCodingStandards.git"
        )

        api_mock = MagicMock()
        api_mock.returncode = 0
        api_mock.stdout = json.dumps({"state": "configured", "languages": ["python"]})

        with patch(
            "positronikal_standards_check.core.file_requirements.subprocess.run",
            side_effect=[remote_mock, api_mock],
        ):
            from positronikal_standards_check.core.file_requirements import (
                FileRequirementsValidator,
            )

            validator = FileRequirementsValidator(temp_repo)
            results = validator._check_codeql_coverage()

        assert len(results) == 1
        assert results[0]["status"] == "pass"
        assert "Default Setup" in results[0]["message"]

    @pytest.mark.positronikal_files
    def test_codeql_coverage_missing(self, temp_repo):
        """Test fail when neither codeql.yml nor Default Setup is present."""
        (temp_repo / ".github" / "workflows").mkdir(parents=True)

        remote_mock = MagicMock()
        remote_mock.returncode = 0
        remote_mock.stdout = (
            "https://github.com/Positronikal/PositronikalCodingStandards.git"
        )

        api_mock = MagicMock()
        api_mock.returncode = 0
        api_mock.stdout = json.dumps({"state": "not-configured"})

        with patch(
            "positronikal_standards_check.core.file_requirements.subprocess.run",
            side_effect=[remote_mock, api_mock],
        ):
            from positronikal_standards_check.core.file_requirements import (
                FileRequirementsValidator,
            )

            validator = FileRequirementsValidator(temp_repo)
            results = validator._check_codeql_coverage()

        assert len(results) == 1
        assert results[0]["status"] == "fail"


class TestCodeStandardsFixes:
    """Tests for checker false-positive fixes."""

    @pytest.mark.positronikal_code
    def test_python_line_length_uses_88(self, temp_repo):
        """Python files are checked at 88 chars (Ruff limit), not 79."""
        (temp_repo / "src" / "module.py").write_text("x = " + "a" * 80 + "\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_code()
        assert not any(
            r["check"] == "line_length" and r["status"] == "fail"
            for r in results.failed
        ), "84-char Python line should not fail the 88-char Python limit"

    @pytest.mark.positronikal_code
    def test_sensitive_data_skips_checker_source(self, temp_repo):
        """Checker's own package directory is excluded from sensitive_data scan."""
        pkg = temp_repo / "positronikal_standards_check"
        pkg.mkdir()
        (pkg / "security.py").write_text(
            'PATTERN = r"-----BEGIN PGP PRIVATE KEY BLOCK-----"\n'
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_security()
        assert not any(
            r["check"] == "sensitive_data" and r["status"] == "fail"
            for r in results.failed
        ), "Regex pattern in checker source should not flag sensitive_data"

    @pytest.mark.positronikal_code
    def test_sensitive_data_skips_test_dirs(self, temp_repo):
        """Test directories are excluded from sensitive_data scan."""
        tests_dir = temp_repo / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_security.py").write_text(
            'PATTERNS = ["password=", "api_key=", "secret="]\n'
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_security()
        assert not any(
            r["check"] == "sensitive_data" and r["status"] == "fail"
            for r in results.failed
        ), "Detection patterns in tests/ should not flag sensitive_data"

    @pytest.mark.positronikal_code
    def test_line_length_exempts_url_lines(self, temp_repo):
        """Lines containing URLs are exempt from the line-length check."""
        url = "https://example.com/" + "x" * 70  # 92 chars total, well over 79
        (temp_repo / "src" / "script.sh").write_text(
            f"#!/usr/bin/env bash\n# See {url}\necho hello\n",
            newline="",
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_code()
        assert not any(
            r["check"] == "line_length" and r["status"] == "fail"
            for r in results.failed
        ), "Long URL-containing comment line should not fail line_length"

    @pytest.mark.positronikal_files
    def test_tests_dir_accepted_as_test_directory(self, temp_repo):
        """tests/ (with s) is accepted as a valid test directory."""
        tests_dir = temp_repo / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_foo.py").write_text("def test_foo(): pass\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        assert any(
            r["check"] == "standard_dir_test" and r["status"] == "pass"
            for r in results.passed
        ), "tests/ directory should pass the standard_dir_test check"

    @pytest.mark.positronikal_security
    def test_python_deps_pyproject_plus_uvlock(self, temp_repo):
        """pyproject.toml + uv.lock is accepted as valid Python dep management."""
        (temp_repo / "src" / "main.py").write_text("x = 1\n")
        (temp_repo / "pyproject.toml").write_text(
            '[project]\nname = "pkg"\ndependencies = ["requests"]\n'
        )
        (temp_repo / "uv.lock").write_text("version = 1\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_security()
        assert any(
            r["check"] == "python_dependencies" and r["status"] == "pass"
            for r in results.passed
        ), "pyproject.toml + uv.lock should pass python_dependencies check"

    @pytest.mark.positronikal_security
    def test_python_deps_pyproject_alone(self, temp_repo):
        """pyproject.toml alone (no lockfile) passes python_dependencies."""
        (temp_repo / "src" / "main.py").write_text("x = 1\n")
        (temp_repo / "pyproject.toml").write_text(
            '[project]\nname = "pkg"\ndependencies = ["requests"]\n'
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_security()
        assert any(
            r["check"] == "python_dependencies" and r["status"] == "pass"
            for r in results.passed
        ), "pyproject.toml alone should pass python_dependencies check"

    @pytest.mark.positronikal_build
    def test_gnu_make_skipped_for_pure_python(self, temp_repo):
        """GNU Make checks are skipped when no C/C++ source files are present."""
        (temp_repo / "src" / "main.py").write_text("x = 1\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_build()
        assert not any(
            r["check"] in ("gnu_make_configure", "gnu_make_automake")
            for r in results.passed + results.warnings + results.failed
        ), "GNU Make checks should not appear for a Python-only repo"

    @pytest.mark.positronikal_files
    def test_codeql_check_skipped_for_shell_only_repo(self, temp_repo):
        """CodeQL check is skipped entirely when no CodeQL-supported language exists."""
        github_dir = temp_repo / ".github" / "workflows"
        github_dir.mkdir(parents=True)
        (temp_repo / "script.sh").write_text("#!/usr/bin/env bash\necho hi\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()
        check_id = "github_file_.github_workflows_codeql.yml"
        assert not any(
            r["check"] == check_id
            for r in results.passed + results.warnings + results.failed
        ), "CodeQL check should be absent for a shell-only repo"

    @pytest.mark.positronikal_standards
    def test_exclude_paths_skips_configured_dir(self, temp_repo):
        """Files under [tool.positronikal-check] exclude-paths are not scanned."""
        from positronikal_standards_check.core.code_standards import (
            CodeStandardsValidator,
        )

        # A very long Python line that would normally fail the line-length check
        api_dir = temp_repo / "api"
        api_dir.mkdir()
        long_line = "x = " + "a" * 200
        (api_dir / "generated.py").write_text(long_line + "\n", newline="")

        # Without exclude-paths: the violation is detected
        validator_no_exclude = CodeStandardsValidator(temp_repo)
        results_no_exclude = validator_no_exclude._check_line_length()
        assert any(r["status"] == "fail" for r in results_no_exclude), (
            "Long line in api/ should fail without exclude-paths"
        )

        # With exclude-paths = ["api"]: the violation is suppressed
        pyproject = temp_repo / "pyproject.toml"
        pyproject.write_text('[tool.positronikal-check]\nexclude-paths = ["api"]\n')
        validator_with_exclude = CodeStandardsValidator(temp_repo)
        results_with_exclude = validator_with_exclude._check_line_length()
        assert not any(r["status"] == "fail" for r in results_with_exclude), (
            'Long line in api/ should be ignored with exclude-paths = ["api"]'
        )

    @pytest.mark.positronikal_standards
    def test_exclude_paths_no_config_is_noop(self, temp_repo):
        """Absence of exclude-paths in pyproject.toml does not affect scanning."""
        from positronikal_standards_check.core.code_standards import (
            CodeStandardsValidator,
        )

        (temp_repo / "src" / "main.py").write_text("x = 1\n", newline="")
        validator = CodeStandardsValidator(temp_repo)
        # Should not raise; returns an empty set
        assert validator._read_exclude_paths() == set()


class TestBuildSystem:
    """Test build system validation."""

    @pytest.mark.positronikal_build
    def test_npm_requirements(self, compliant_repo):
        """Test npm package requirements."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_build()

        # Check npm packages are detected
        assert any(
            "husky" in r["check"] and r["status"] == "pass" for r in results.passed
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
            "pre-commit" in r["check"] and r["status"] == "pass" for r in results.passed
        )
        assert any(
            "commit-msg" in r["check"] and r["status"] == "pass" for r in results.passed
        )

    @pytest.mark.positronikal_build
    def test_non_js_hooks_missing(self, temp_repo):
        """Test detection of missing hooks/ on a non-JS repo (no package.json)."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_build()

        assert any(
            r["check"] == "git_hook_hooks_pre-push" and r["status"] == "fail"
            for r in results.failed
        )
        assert any(
            r["check"] == "git_hook_hooks_ci-check.sh" and r["status"] == "fail"
            for r in results.failed
        )
        assert any(
            r["check"] == "security_review_command" and r["status"] == "fail"
            for r in results.failed
        )

    @pytest.mark.positronikal_build
    def test_non_js_hooks_present(self, temp_repo):
        """Test passing validation when hooks/ and security-review.md exist."""
        hooks_dir = temp_repo / "hooks"
        hooks_dir.mkdir()
        for name in ("pre-commit", "commit-msg", "ci-check.sh", "pre-push"):
            path = hooks_dir / name
            path.write_text("#!/usr/bin/env bash\necho ok\n")
            mode = path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.chmod(path, mode)  # noqa: S103 -- test fixture hook, not shipped output

        commands_dir = temp_repo / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "security-review.md").write_text("# Security Review")

        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_build()

        assert any(
            r["check"] == "git_hook_hooks_pre-push" and r["status"] == "pass"
            for r in results.passed
        )
        assert any(
            r["check"] == "security_review_command" and r["status"] == "pass"
            for r in results.passed
        )

    @pytest.mark.positronikal_build
    def test_missing_npm_scripts(self, temp_repo):
        """Test detection of missing npm scripts."""
        # Create package.json without required scripts
        package_json = {
            "name": "test-repo",
            "version": "1.0.0",
            "devDependencies": {"husky": "^9.1.7"},
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
        (temp_repo / "METHODOLOGY.md").write_text(
            "# Methodology\n\nAlgorithm documentation."
        )
        (temp_repo / "VALIDATION.md").write_text("# Validation\n\nTest results.")
        (temp_repo / "LEGAL.md").write_text("# Legal\n\nExpert witness info.")

        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_forensic()

        assert all(
            r["status"] == "pass"
            for r in results.passed
            if "forensic_file" in r["check"]
        )


class TestVersioning:
    """Test version management validation."""

    @pytest.mark.positronikal_version
    def test_version_tags_missing(self, temp_repo):
        """Version tags check must not crash in a non-git tmpdir."""
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_version()

        # Non-git directory: warning or fail are both acceptable; must not error out
        version_results = results.failed + results.warnings
        assert any(r["check"] == "version_tags" for r in version_results), (
            "version_tags check must produce a result"
        )

    @pytest.mark.positronikal_version
    def test_python_versioning_with_hatch_vcs(self, temp_repo):
        """Test pass when pyproject.toml references hatch-vcs."""
        (temp_repo / "pyproject.toml").write_text(
            '[build-system]\nrequires = ["hatchling", "hatch-vcs"]\n'
            'build-backend = "hatchling.build"\n\n'
            '[project]\ndynamic = ["version"]\n'
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_version()

        assert any(
            r["check"] == "python_version_source" and r["status"] == "pass"
            for r in results.passed
        )

    @pytest.mark.positronikal_version
    def test_python_versioning_missing(self, temp_repo):
        """Test warning when pyproject.toml exists but no versioning tool present."""
        (temp_repo / "pyproject.toml").write_text(
            '[project]\nname = "mypackage"\nversion = "1.0.0"\n'
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_version()

        assert any(
            r["check"] == "python_version_source" and r["status"] == "warning"
            for r in results.warnings
        )

    @pytest.mark.positronikal_version
    def test_go_versioning_with_ldflags(self, temp_repo):
        """Test pass when Makefile has ldflags version injection."""
        (temp_repo / "go.mod").write_text("module example.com/test\n\ngo 1.21\n")
        ldflags = '-ldflags "-X main.version=$(git describe --tags --abbrev=0)"'
        (temp_repo / "Makefile").write_text(f"build:\n\tgo build {ldflags} ./...\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_version()

        assert any(
            r["check"] == "go_version_source" and r["status"] == "pass"
            for r in results.passed
        )

    @pytest.mark.positronikal_version
    def test_go_versioning_missing(self, temp_repo):
        """Test warning when go.mod exists but no ldflags injection in Makefile."""
        (temp_repo / "go.mod").write_text("module example.com/test\n\ngo 1.21\n")
        (temp_repo / "Makefile").write_text("build:\n\tgo build ./...\n")
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_version()

        assert any(
            r["check"] == "go_version_source" and r["status"] == "warning"
            for r in results.warnings
        )

    @pytest.mark.positronikal_version
    def test_pr_template_missing(self, temp_repo):
        """Test warning when .github/ exists but PULL_REQUEST_TEMPLATE.md is absent."""
        github_dir = temp_repo / ".github"
        github_dir.mkdir()
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()

        assert any(
            "PULL_REQUEST_TEMPLATE" in r["check"] and r["status"] == "warning"
            for r in results.warnings
        )

    @pytest.mark.positronikal_version
    def test_pr_template_present(self, temp_repo):
        """Test pass when .github/PULL_REQUEST_TEMPLATE.md exists."""
        github_dir = temp_repo / ".github"
        github_dir.mkdir()
        (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(
            "## Summary\n\n## Type of Change\n\n## Checklist\n"
        )
        checker = PositronikalStandardsChecker(str(temp_repo))
        results = checker.check_files()

        assert not any(
            "PULL_REQUEST_TEMPLATE" in r["check"] and r["status"] == "warning"
            for r in results.warnings
        )


class TestComprehensiveValidation:
    """Test comprehensive validation scenarios."""

    @pytest.mark.positronikal_all
    def test_full_compliance(self, compliant_repo):
        """Test fully compliant repository."""
        checker = PositronikalStandardsChecker(str(compliant_repo))
        results = checker.check_all()

        summary = results.get_summary()
        assert summary["is_passing"] or summary["failed"] == 0, (
            f"Unexpected failures: {results.failed}"
        )
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


class TestPowerShellLinter:
    """Test the PowerShell linter (_run_powershell_linter)."""

    @pytest.mark.positronikal_code
    def test_no_ps1_files_returns_none(self, temp_repo):
        """No PS1/PSM1 files → linter returns None (caller skips the check)."""

        validator = CodeStandardsValidator(temp_repo)
        assert validator._run_powershell_linter() is None

    @pytest.mark.positronikal_code
    def test_pwsh_not_found_returns_warning(self, temp_repo):
        """pwsh not on PATH → warning result."""

        (temp_repo / "script.ps1").write_text("Write-Host 'hello'\n")
        validator = CodeStandardsValidator(temp_repo)

        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = validator._run_powershell_linter()

        assert result is not None
        assert result["check"] == "linter_powershell"
        assert result["status"] == "warning"
        assert "pwsh not found" in result["message"]

    @pytest.mark.positronikal_code
    def test_module_not_installed_returns_warning(self, temp_repo):
        """pwsh available but PSScriptAnalyzer not installed → warning."""

        (temp_repo / "script.ps1").write_text("Write-Host 'hello'\n")
        validator = CodeStandardsValidator(temp_repo)

        mock_unavailable = MagicMock()
        mock_unavailable.returncode = 1
        with patch("subprocess.run", return_value=mock_unavailable):
            result = validator._run_powershell_linter()

        assert result is not None
        assert result["check"] == "linter_powershell"
        assert result["status"] == "warning"
        assert "PSScriptAnalyzer" in result["message"]

    @pytest.mark.positronikal_code
    def test_linter_passes_clean_file(self, temp_repo):
        """PSScriptAnalyzer reports no issues → pass result."""

        ps1_file = temp_repo / "script.ps1"
        ps1_file.write_text("Write-Host 'hello'\n")
        validator = CodeStandardsValidator(temp_repo)

        mock_ok = MagicMock()
        mock_ok.returncode = 0

        # Patch _get_source_files so the git-ls-files subprocess mock
        # doesn't filter out the file before we reach the linter calls.
        with patch.object(validator, "_get_source_files", return_value=[ps1_file]):
            with patch("subprocess.run", return_value=mock_ok):
                result = validator._run_powershell_linter()

        assert result is not None
        assert result["check"] == "linter_powershell"
        assert result["status"] == "pass"

    @pytest.mark.positronikal_code
    def test_linter_fails_on_issues(self, temp_repo):
        """PSScriptAnalyzer finds issues → fail result with output."""

        ps1_file = temp_repo / "script.ps1"
        ps1_file.write_text("$x=1\n")
        validator = CodeStandardsValidator(temp_repo)

        mock_check_ok = MagicMock()
        mock_check_ok.returncode = 0
        mock_fail = MagicMock()
        mock_fail.returncode = 1
        mock_fail.stdout = "PSAvoidUsingWriteHost: Use Write-Output instead.\n"
        mock_fail.stderr = ""

        with patch.object(validator, "_get_source_files", return_value=[ps1_file]):
            with patch("subprocess.run", side_effect=[mock_check_ok, mock_fail]):
                result = validator._run_powershell_linter()

        assert result is not None
        assert result["check"] == "linter_powershell"
        assert result["status"] == "fail"
        assert "PSAvoidUsingWriteHost" in result["message"]


# Pytest configuration for running specific test groups
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "positronikal: All Positronikal standards tests")
    config.addinivalue_line("markers", "positronikal_core: Core functionality tests")
    config.addinivalue_line("markers", "positronikal_files: File requirements tests")
    config.addinivalue_line("markers", "positronikal_build: Build system tests")
    config.addinivalue_line("markers", "positronikal_code: Code standards tests")
    config.addinivalue_line(
        "markers", "positronikal_security: Security requirements tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_forensic: Forensic standards tests"
    )
    config.addinivalue_line(
        "markers", "positronikal_all: Comprehensive validation tests"
    )
    config.addinivalue_line("markers", "positronikal_version: Version management tests")
