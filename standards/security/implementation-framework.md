# Security Implementation Framework

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
- **For comprehensive GitHub Actions permissions guidance, see [../GitHub%20Actions%20Permissions%20Architecture.md](../GitHub%20Actions%20Permissions%20Architecture.md).**

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
