# Positronikal Coding Standards

A comprehensive framework for establishing consistent, secure, and maintainable development standards across software repositories. This framework provides both general-purpose coding standards suitable for any project, plus specialized addenda for specific use cases.

## Core Standards

### [Code Formatting Rules](./standards/Code%20Formatting%20Rules.md 'Code Formatting Rules')
Establishes standard code formatting and engineering philosophy based on Unix principles and GNU Coding Standards. Includes language-specific guidelines and best practices for maintainable, readable code.

### [Repository Security Rules](./standards/Repository%20Security%20Rules.md 'Repository Security Rules')
Comprehensive security framework covering CI/CD pipelines, dependency management, vulnerability scanning, and security automation. Scales from basic security practices to enterprise-grade protections.

### [GitHub Configuration Standards](./standards/GitHub%20Configuration%20Standards.md 'GitHub Configuration Standards')
Platform-specific configuration requirements for GitHub user accounts, organizations, and repositories. Covers security settings, access controls, audit requirements, and compliance features essential for professional development workflows.

## Specialized Standards

### [Forensic Evidence Tool Standards](./standards/Forensic%20Evidence%20Tool%20Standards.md 'Forensic Evidence Tool Standards')
Additional requirements for tools that may be used to generate or process digital evidence in legal proceedings. Addresses Daubert Standard compliance, legal discovery preparedness, and enhanced documentation requirements.

## Repository Templates
A pre-configured repository template that implements these standards:

- **[repo-template](./repo-template/ 'repo-template')** - Template for application, tool, or website repositories.

The template includes:
- Standard documentation files (`README`, `CONTRIBUTING`, `COPYING`, etc.)
- Git configuration files (`.gitignore`, `.gitattributes`, `.editorconfig`)
- Placeholder documentation structure
- Basic reference materials

## Reference Materials
The **[ref/](./ref/ 'ref/')** directory contains:
- Language-specific style guides and best practices
- GNU Coding Standards and other foundational documents
- Industry standard references for various programming languages
- Linting and code quality tool configurations

## Automated Standards Validation

### Positronikal Standards Checker
This repository includes an automated validation tool to help ensure your projects comply with these standards. The `positronikal_standards_check` module provides comprehensive pytest-compatible testing for repository structure, code formatting, security requirements, and forensic tool standards.

**Integration Instructions**
1. Copy the checker module to your project:
```bash
cp -r positronikal_standards_check/ /path/to/your/project/
```

2. Install **pytest** if not already available:
```bash
pip install pytest
```

3. Run standards validation:
```bash
# Run all standards checks
pytest positronikal_standards_check/

# Run specific validation categories
pytest positronikal_standards_check/tests/test_file_requirements.py
pytest positronikal_standards_check/tests/test_security_compliance.py
```

**CI/CD Integration**
Add to your GitHub Actions workflow (`.github/workflows/standards.yml`):
```yaml
name: Standards Compliance
on: [push, pull_request]
jobs:
  standards-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: pip install pytest
      - name: Run standards validation
        run: pytest positronikal_standards_check/ -v
```

**Pre-commit Integration**
Add to your `.pre-commit-hooks.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: positronikal-standards
        name: Positronikal Standards Check
        entry: pytest positronikal_standards_check/
        language: system
        pass_filenames: false
```

The checker validates:
- Required documentation files and structure
- Code formatting compliance (.editorconfig, line endings, encoding)
- Security framework implementation
- Build system requirements (GNU Make, configure scripts)
- Forensic tool standards (when applicable)

## Using These Standards

### For General Projects
1. Choose the appropriate repository template
2. Follow the [Code Formatting Rules](./standards/Code%20Formatting%20Rules.md 'Code Formatting Rules')
3. Implement the [Repository Security Rules](./standards/Repository%20Security%20Rules.md 'Repository Security Rules') appropriate to your project's security requirements

### For Forensic/Investigative Tools
1. Follow all general project requirements above
2. Additionally implement [Forensic Evidence Tool Standards](./standards/Forensic%20Evidence%20Tool%20Standards.md 'Forensic Evidence Tool Standards')
3. Consider legal compliance requirements from project inception

### Implementation Approach
The standards are designed to be:
- **Scalable**: Start with core requirements, add complexity as needed
- **Modular**: Pick and choose components appropriate to your project
- **Practical**: Based on real-world development experience and industry best practices
- **Legally Aware**: Address compliance and legal discovery requirements where applicable

## Build Systems
The choice of build systems depends on the goals and objectives of each repository. As a default when more contextually appropriate choices are not available, use [GNU Make](https://www.gnu.org/software/make/ 'GNU Make').
- **configure Script**: This script, generated by Autoconf, handles configuration for different system environments during installation and allows users to customize installation paths and other settings. Every repository using GNU Make should have a `configure` script.
- **Makefile.am**: This file, used by Automake, contains rules for building the package. It specifies how to compile source files, link libraries, and create executables. There should generally be one `Makefile.am` per build directory.

## Best Practices
- **Installation Directories**: Installation directories should be named using variables to allow for easy relocation, according to the GNU Coding Standards.
- **Installation Files - Unix**: Files installed by the rendered software on all Unix, Unix-like, and derivative operating systems including Apple Macintosh should be appropriately located according to the Linux [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html 'Filesystem Hierarchy Standard') or by running this command in a shell:
```
$ man hier
```
- **Installation Files - Windows**: Files installed by the rendered software on Microsoft Windows and derivative operating systems should be appropriately located according to Microsoft's [Installation Context](https://learn.microsoft.com/en-us/windows/win32/msi/installation-context 'Installation Context') for Windows Installer.
- **Header Files**: Header files should be functionally organized with separate files for different subsystems or likely-to-change declarations.

## Language Support
Current framework includes specific guidance for:
- **Shell Scripting**: bash, awk
- **Systems Programming**: C, C++
- **Web Development**: HTML, CSS, JavaScript, TypeScript
- **Application Development**: Python, Java, Go, C#
- **Specialized**: PowerShell, Perl, PHP, R

## Code and Materials Licensing
- Positronikal repositories that are contributing forks of external upstream projects retain and adhere to the full licesning terms of the upstream project.
- Positronikal repositories that are project or "hard" forks of external upstream projects reserve the right to license the project fork appropriately and without violation of the license requirements of the upstream project that govern such actions.
- Derivatives and forks of Positronikal projects are free to license the derivative in any way those developers see fit, but without violating any terms of any license applicable to the Positronikal project or applicable upstream projects.

### Licenses and Associate Files Commonly Used by Positronikal Projects
A Positronikal repository uses one or more of these as applicable:
- **COPYING**: Contains easy-to-understand exlanations of the requirements of the GNU General Public License (GPL) if it's used.
- **COPYING.LESSER**: Contains the GNU Lesser General Public License (LGPL) if it's used.
- **LICENSE**: Contains any license other than GPL, LGPL, or CC if it's used.
- **LICENSE.CC**: Contains the Creative Commons license per the ["Share Your Work"](https://creativecommons.org/share-your-work/ 'Share Your Work') help page if it's used.

## Philosophy
Based on the Unix Philosophy emphasizing:
- Modularity and clean interfaces
- Clarity over cleverness
- Simplicity and transparency
- Robustness through design
- Extensibility for future needs

## Getting Started
1. **Review** the [Code Formatting Rules](./standards/Code%20Formatting%20Rules.md 'Code Formatting Rules') for the engineering philosophy and general requirements
2. **Assess** your project's security needs using the [Repository Security Rules](./standards/Repository%20Security%20Rules.md 'Repository Security Rules')
3. **Determine** if specialized requirements apply (e.g. forensic tools)
4. **Copy** the appropriate repository template as your starting point
5. **Customize** the templates to your specific project needs

## Contributing
These standards are themselves subject to continuous improvement. See [CONTRIBUTING](./CONTRIBUTING.md 'CONTRIBUTING') for guidance on proposing improvements or additions.

## License
This framework is licensed under GPL-3.0. See [COPYING](./COPYING.md 'COPYING') for details. The license applies to the framework documentation itself, not to tools developed using these guidelines.

---

*This framework reflects 20+ years of software development experience across government, enterprise, and open source environments, with particular emphasis on security, forensics, and digital investigation use cases.*
