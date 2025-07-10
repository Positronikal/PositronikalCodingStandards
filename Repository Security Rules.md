# Repository Security Rules

## Objective
To establish standard security requirements for all code repositories that are either original to or hard project forks by Hoyt Harness, including any development organizations he manages, e.g. Positronikal. These requirements apply to both local and online repositories, e.g. GitHub. The result should be that such repositories exist as secure development environments with comprehensive security automation, testing, and governance. This policy adapts security best practices for different project types while maintaining consistency across repositories.

### EXCEPTIONS:
These rules do not apply to contributing repositories that will instead adhere to the rules of their respective origins.

### ADDITIONAL REQUIREMENTS:
For tools that may be used to generate or process digital evidence in legal proceedings, see the supplementary [Forensic Evidence Tool Standards](./Forensic%20Evidence%20Tool%20Standards.md) document for enhanced security and documentation requirements.

## Security Implementation Framework

### Phase 1: Repository Security Foundation

#### 1.1 GitHub Governance Structure
Create `.github/` directory with:

**SECURITY.md Policy**
- Supported versions table
- Responsible vulnerability disclosure process
- Response timelines by severity (Critical: 24-48h, High: 3-5 days, etc.)
- Security best practices for users
- Contact information and PGP key if applicable
- Legal framework for security researchers

**CODEOWNERS File**
```
# Assign repository maintainers
* @[username]
[specific-path]/ @[domain-expert]
```

**Issue Templates**
- `ISSUE_TEMPLATE/bug_report.md` with security consideration fields
- `ISSUE_TEMPLATE/feature_request.md` with security impact assessment
- Include version, reproduction steps, and impact analysis

**Pull Request Template**
- Security checklist items
- Type of change classification
- Testing verification requirements
- Documentation update confirmation

#### 1.2 Dependency Security Management

**Dependabot Configuration** (`.github/dependabot.yml`)
```yaml
version: 2
updates:
  - package-ecosystem: "[pip|npm|gradle|etc]"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "08:00"
      timezone: "[your-timezone]"
    open-pull-requests-limit: 3
    allow:
      - dependency-type: "security"
    reviewers:
      - "[maintainer-username]"
```

#### 2.2 GitHub Actions Security and Testing

**Actions Allowlist Configuration**
- **Principle**: Use repository-level allowlists for granular control
- **Avoid**: Organization-level restrictive allowlists that prevent customization
- **For comprehensive GitHub Actions permissions guidance, see [GitHub Actions Permissions Architecture](./GitHub%20Actions%20Permissions%20Architecture.md).**

**Version Specification Requirements**
```yaml
# ✅ Recommended patterns:
actions/checkout@*           # GitHub official actions support wildcards
github/codeql-action@*       # GitHub official actions support wildcards
withastro/action@v3          # Third-party actions often require exact versions
actions/deploy-pages@v4      # Deployment actions often require exact versions

# ❌ Unreliable patterns:
third-party/action@*         # May not work - test with exact versions
```

**Transitive Dependency Discovery**
- **Hidden Dependencies**: Actions may internally call other actions not listed in workflows
- **Detection Method**: Remove suspected unused actions and test workflow execution
- **Documentation**: Error messages will reveal required transitive dependencies
- **Example**: `withastro/action@v3` internally requires `oven-sh/setup-bun@v2`

**Systematic Testing Methodology**
```bash
# Create tracking mechanism for permission changes
echo "1" > TESTFILE
git add TESTFILE
git commit -m "test: permissions configuration - 1"
git push

# Monitor GitHub Actions tab for results
# Iterate with incremental changes
# Document working configurations
```

**Allowlist Optimization Process**
1. **Baseline**: Start with working configuration
2. **Analysis**: Compare allowlist with actual workflow file requirements
3. **Testing**: Remove suspected unused actions in batches
4. **Validation**: Use workflow execution errors to identify true requirements
5. **Documentation**: Record final optimized configuration

#### 2.1 Enhanced GitHub Actions Workflows

**Primary CI Workflow** (`.github/workflows/ci.yml`)
Core pipeline with language-specific adaptations:

**Python Projects:**
```yaml
- name: Type checking with pyright
  run: |
    npm install -g pyright
    pyright

- name: Security vulnerability scan
  run: |
    pip install safety
    safety check --json || echo "Safety check completed"

- name: SAST with Bandit
  run: |
    pip install bandit
    bandit -r src/ -f json -o bandit-report.json
```

**Node.js Projects:**
```yaml
- name: Security audit
  run: npm audit --audit-level=high

- name: License compliance
  run: |
    npm install -g license-checker
    license-checker --json --out licenses.json
```

**Java Projects:**
```yaml
- name: OWASP Dependency Check
  run: |
    ./gradlew dependencyCheckAnalyze
    
- name: SpotBugs Security
  run: ./gradlew spotbugsMain
```

**Go Projects:**
```yaml
- name: Security scan with gosec
  run: |
    go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest
    gosec ./...
```

#### 2.2 CodeQL Security Analysis

**Universal CodeQL Workflow** (`.github/workflows/codeql.yml`)
```yaml
strategy:
  matrix:
    language: [ '[python|javascript|java|go|cpp|csharp]' ]
```
Automatically adapts to repository's primary language(s).

### Phase 3: Security Testing Framework

#### 3.1 Language-Specific Security Tests

**Python Security Test Suite** (`tests/test_security.py`)
- Hardcoded secret detection in code and git history
- Dependency vulnerability scanning integration
- File permission validation
- Dangerous import detection (eval, exec, subprocess)
- Configuration security scanning

**Node.js Security Tests** (`tests/security.test.js`)
- NPM audit integration
- Prototype pollution detection
- XSS vulnerability patterns
- SQL injection pattern detection

**Java Security Tests** (`src/test/java/SecurityTest.java`)
- OWASP dependency check integration
- Deserialization vulnerability detection
- XXE (XML External Entity) prevention validation
- Path traversal protection testing

#### 3.2 Universal Security Test Categories
Adapt these concepts to any language:

1. **Secret Detection**: Scan for API keys, passwords, tokens
2. **Dependency Security**: Check for known vulnerabilities
3. **File Security**: Validate permissions and sensitive file handling
4. **Input Validation**: Test injection vulnerability protections
5. **Configuration Security**: Scan config files for exposed secrets
6. **Network Security**: Validate secure communication patterns

### Phase 4: Security Automation & Tooling

#### 4.1 Universal Security Audit Script

Create language-appropriate security audit automation:

**Core Audit Functions:**
- Dependency vulnerability scanning
- Static Application Security Testing (SAST)
- License compliance checking
- Security test execution
- Code quality analysis with security focus

**Reporting:**
- JSON results for CI/CD integration
- Human-readable security reports
- Trend tracking for security metrics

#### 4.2 Security Configuration Files

**Bandit (Python)** - `.bandit`
**ESLint Security (Node.js)** - `.eslintrc.security.js`
**SpotBugs (Java)** - `spotbugs-security.xml`
**gosec (Go)** - `.gosec.json`

### Phase 5: Documentation & Compliance

#### 5.1 Security Documentation
- README security section with setup instructions
- CONTRIBUTING.md with security guidelines
- Architecture documentation highlighting security design
- Incident response procedures

#### 5.2 Compliance Integration
- SOC 2 preparation documentation
- GDPR compliance notes (if applicable)
- Industry-specific compliance (HIPAA, PCI-DSS, etc.)
- Audit trail maintenance procedures

## Implementation Checklist by Repository Type

### Web Application Repositories
- [ ] OWASP Top 10 vulnerability testing
- [ ] Content Security Policy validation
- [ ] Authentication/authorization testing
- [ ] Session management security
- [ ] API endpoint security testing

### Library/SDK Repositories
- [ ] Supply chain security measures
- [ ] Code signing implementation
- [ ] Version integrity verification
- [ ] Backward compatibility security review
- [ ] Public API security validation

### Infrastructure/DevOps Repositories
- [ ] Secrets management integration
- [ ] Infrastructure as Code security scanning
- [ ] Container security scanning
- [ ] Network security validation
- [ ] Access control verification

### Data/ML Repositories
- [ ] Data privacy compliance checks
- [ ] Model security validation
- [ ] Data lineage security
- [ ] Sensitive data detection
- [ ] Bias and fairness testing

## Customization Guidelines

### Repository Assessment
1. **Language/Framework**: Adapt tools to primary technology stack
2. **Sensitivity Level**: Adjust security controls based on data/system criticality
3. **Compliance Requirements**: Add industry-specific security measures
4. **Team Size**: Scale review processes and automation accordingly
5. **Deployment Environment**: Consider cloud, on-premise, or hybrid security needs

### Tool Selection Matrix
| Language | Type Checker | SAST Tool | Dependency Scanner | License Checker | Test Framework |
|----------|--------------|-----------|-------------------|-----------------|----------------|
| Python | pyright/mypy | Bandit | Safety | pip-licenses | pytest |
| Node.js | TypeScript | ESLint Security | npm audit | license-checker | Jest |
| Java | Java Compiler | SpotBugs | OWASP Dependency Check | License Maven Plugin | JUnit |
| Go | go vet | gosec | govulncheck | go-licenses | testing |
| C# | Roslyn | Security Code Scan | OWASP Dependency Check | dotnet list package | xUnit |

## Metrics & KPIs

Track these security metrics across all repositories:
- **MTTR for Security Issues**: Target < 48 hours for critical, < 7 days for high
- **Dependency Update Frequency**: Weekly automated, monthly manual review
- **Security Test Coverage**: Maintain > 80% coverage including security tests
- **Vulnerability Backlog**: Zero tolerance for critical/high severity issues
- **Security Scan Frequency**: Every commit + weekly scheduled comprehensive scans

## Implementation Priority

### High Priority (Week 1)
1. SECURITY.md policy creation
2. Dependabot security scanning activation
3. Basic CI/CD security integration
4. Critical vulnerability assessment

### Medium Priority (Week 2-3)
1. CodeQL implementation
2. Comprehensive security test suite
3. Security automation scripts
4. Documentation updates

### Low Priority (Month 1)
1. Advanced threat modeling
2. Compliance documentation
3. Security metrics dashboard
4. Team training materials

## Success Criteria

A successfully hardened repository will have:
- ✅ Zero known critical/high severity vulnerabilities
- ✅ Automated security scanning in CI/CD
- ✅ Comprehensive security test coverage
- ✅ Clear security governance processes
- ✅ Regular security audit automation
- ✅ Incident response procedures
- ✅ Compliance documentation (where applicable)

This framework transforms any repository into a secure development environment suitable for professional and enterprise use cases while maintaining developer productivity and code quality.