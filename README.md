# Positronikal Coding Standards

A comprehensive framework for establishing consistent, secure, and maintainable development standards across software repositories. This framework provides both general-purpose coding standards suitable for any project, plus specialized addenda for specific use cases.

## Core Standards

### [Code Formatting Rules](./Code%20Formatting%20Rules.md)
Establishes standard code formatting and engineering philosophy based on Unix principles and GNU Coding Standards. Includes language-specific guidelines and best practices for maintainable, readable code.

### [Repository Security Rules](./Repository%20Security%20Rules.md)
Comprehensive security framework covering CI/CD pipelines, dependency management, vulnerability scanning, and security automation. Scales from basic security practices to enterprise-grade protections.

### [GitHub Configuration Standards](./GitHub%20Configuration%20Standards.md)
Platform-specific configuration requirements for GitHub user accounts, organizations, and repositories. Covers security settings, access controls, audit requirements, and compliance features essential for professional development workflows.

### [GitHub Actions Permissions Architecture](./GitHub%20Actions%20Permissions%20Architecture.md)
Comprehensive guide to GitHub Actions permissions hierarchy, troubleshooting methodology, and configuration best practices. Includes critical discoveries about exact version matching requirements and systematic approaches to resolving permissions issues.

### [Git Hooks Standards](./Git%20Hooks%20Standards.md)
Automated enforcement of coding standards and security requirements using Husky. Provides immediate feedback through pre-commit formatting, secret detection, GPG verification, and commit message validation.

## Specialized Standards

### [Forensic Evidence Tool Standards](./Forensic%20Evidence%20Tool%20Standards.md)
Additional requirements for tools that may be used to generate or process digital evidence in legal proceedings. Addresses Daubert Standard compliance, legal discovery preparedness, and enhanced documentation requirements.

## Repository Templates

Pre-configured repository templates that implement these standards:

- **[repo-template-apps](./repo-template-apps/)** - Template for application/tool repositories
- **[repo-template-web](./repo-template-web/)** - Template for web-based projects

Each template includes:
- Standard documentation files (README, CONTRIBUTING, COPYING, etc.)
- Git configuration files (.gitignore, .gitattributes, .editorconfig)
- Placeholder documentation structure
- Basic reference materials

## Reference Materials

The **[ref/](./ref/)** directory contains:
- Language-specific style guides and best practices
- GNU Coding Standards and other foundational documents
- Industry standard references for various programming languages
- Linting and code quality tool configurations

## Using These Standards

### For General Projects
1. Choose the appropriate repository template
2. Follow the [Code Formatting Rules](./Code%20Formatting%20Rules.md)
3. Implement the [Repository Security Rules](./Repository%20Security%20Rules.md) appropriate to your project's security requirements
4. Set up [Git Hooks Standards](./Git%20Hooks%20Standards.md) for automated enforcement
5. Configure [GitHub Configuration Standards](./GitHub%20Configuration%20Standards.md) for repository management

### For Forensic/Investigative Tools
1. Follow all general project requirements above
2. Additionally implement [Forensic Evidence Tool Standards](./Forensic%20Evidence%20Tool%20Standards.md)
3. Consider legal compliance requirements from project inception

### Implementation Approach
The standards are designed to be:
- **Scalable**: Start with core requirements, add complexity as needed
- **Modular**: Pick and choose components appropriate to your project
- **Practical**: Based on real-world development experience and systematic testing
- **Legally Aware**: Address compliance and legal discovery requirements where applicable
- **Battle-Tested**: Incorporate lessons learned from actual implementation and troubleshooting

## Language Support

Current framework includes specific guidance for:
- **Shell Scripting**: bash, awk
- **Systems Programming**: C, C++
- **Web Development**: HTML, CSS, JavaScript, TypeScript
- **Application Development**: Python, Java, Go, C#
- **Specialized**: PowerShell, Perl, PHP, R

## Philosophy

Based on the Unix Philosophy emphasizing:
- Modularity and clean interfaces
- Clarity over cleverness
- Simplicity and transparency
- Robustness through design
- Extensibility for future needs

## Getting Started

1. **Review** the [Code Formatting Rules](./Code%20Formatting%20Rules.md) for the engineering philosophy and general requirements
2. **Assess** your project's security needs using the [Repository Security Rules](./Repository%20Security%20Rules.md)
3. **Determine** if specialized requirements apply (e.g., forensic tools)
4. **Copy** the appropriate repository template as your starting point
5. **Customize** the templates to your specific project needs

## Contributing

These standards are themselves subject to continuous improvement. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidance on proposing improvements or additions.

## License

This framework is licensed under GPL-3.0. See [COPYING.md](./COPYING.md) for details. The license applies to the framework documentation itself, not to tools developed using these guidelines.

---

*This framework reflects 20+ years of software development experience across government, enterprise, and open source environments, with particular emphasis on security, forensics, and digital investigation use cases.*
