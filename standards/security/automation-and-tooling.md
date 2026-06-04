# Security Automation & Tooling

### Phase 4: Security Automation & Tooling

#### 4.1 Security Scanning Architecture

Security scanning operates in two layers, each with a distinct role:

**Layer 1 — Pre-commit (fast, local, language-native)**
Fast pattern-based checks integrated into the pre-commit hook. These catch obvious issues at commit time with no external dependencies. See [Git Hooks Standards](../Git%20Hooks%20Standards.md) for hook implementation.

**Layer 2 — Pre-push and CI (semantic, thorough)**
Semantic security review via Claude Code. This is the primary vulnerability detection mechanism — it understands code intent, not just patterns, and covers injection attacks, authentication flaws, hardcoded secrets, weak cryptography, deserialization vulnerabilities, and data exposure. It runs as an informational pre-push hook locally and as a GitHub Action in CI for GitHub-public repositories.

Language-native SAST tools (gosec, Ruff security rules, etc.) complement Layer 2 by catching language-specific issues quickly at commit time. They do not replace the Claude security review.

#### 4.2 Language-Native SAST Integration

Integrate security rules into the existing linter invocation rather than running separate tools:

**Go** — include `gosec` rules via `golangci-lint`:
```yaml
# .golangci.yml
linters:
  enable:
    - gosec
```

**Python** — Ruff includes security rules (flake8-bandit subset) enabled via config:
```toml
# pyproject.toml or ruff.toml
[tool.ruff.lint]
select = ["S"]  # flake8-bandit security rules
```

**Node.js** — ESLint security plugin:
```json
{
  "plugins": ["security"],
  "extends": ["plugin:security/recommended"]
}
```

#### 4.3 Dependency Vulnerability Scanning

Dependency vulnerability scanning is distinct from code security review. Claude security review explicitly excludes outdated third-party libraries — dependency scanning fills that gap.

**Python:** `pip-audit` or `safety`
**Node.js:** `npm audit`
**Go:** `govulncheck`
**Java:** OWASP Dependency Check

These run in CI via Dependabot (automatic) and can be added as optional pre-push checks for sensitive repositories.

#### 4.4 Security Configuration Files

Where applicable, include tool configuration files in the repository root:

**golangci-lint (Go)** — `.golangci.yml`
**Ruff (Python)** — `pyproject.toml` or `ruff.toml`
**ESLint Security (Node.js)** — `.eslintrc.js`
