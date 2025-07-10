# Git Hooks Standards

## Objective
Establish standardized Git hooks using Husky to automatically enforce coding standards, security requirements, and quality gates at the developer level. This provides immediate feedback and prevents non-compliant code from entering repositories.

## Required Implementation

### Core Dependencies
All repositories must include:
```json
{
  "devDependencies": {
    "husky": "^9.1.7",
    "lint-staged": "^15.5.0",
    "prettier": "^3.5.3"
  },
  "scripts": {
    "prepare": "husky",
    "pre-commit": "lint-staged"
  },
  "lint-staged": {
    "*.{js,ts,astro,css,html,md}": [
      "prettier --write"
    ]
  }
}
```

### Required Git Hooks

#### Pre-commit Hook (`.husky/pre-commit`)
Must implement:
- **Code Formatting**: Automatic prettier formatting via lint-staged
- **Secret Detection**: Scan for potential secrets/sensitive data
- **GPG Configuration Check**: Verify GPG signing setup
- **Security Pattern Detection**: Check for TODO/FIXME items
- **File Size Validation**: Prevent large binary commits

```bash
#!/usr/bin/env sh
# Husky pre-commit hook for Positronikal repositories
# Enforces coding standards and security requirements

echo "🔍 Positronikal pre-commit checks..."

# Run lint-staged (prettier formatting)
echo "📝 Formatting code with Prettier..."
pnpm run pre-commit

# Security checks
echo "🔒 Running security checks..."

# Check for potential secrets
echo "   Checking for potential secrets..."
if git diff --cached --name-only | xargs grep -l -E "(password|secret|key|token|api_key)" 2>/dev/null; then
    echo "❌ Potential secrets detected in staged files!"
    echo "   Please review and remove any sensitive information before committing."
    exit 1
fi

# Verify GPG signing configuration
echo "   Verifying GPG configuration..."
if ! git config user.signingkey > /dev/null; then
    echo "⚠️  GPG signing key not configured!"
    echo "   Please configure your GPG key: git config user.signingkey YOUR_KEY_ID"
    echo "   Then enable signing: git config commit.gpgsign true"
    echo "   Continuing anyway, but remember to sign your commits!"
fi

echo "✅ Pre-commit checks completed!"
```

#### Commit Message Hook (`.husky/commit-msg`)
Must enforce:
- **Conventional Commit Format**: type(scope): description
- **Security Classification**: Special handling for security commits
- **Message Length Limits**: Reasonable subject line length
- **Required Information**: Proper commit categorization

```bash
#!/usr/bin/env sh
# Husky commit-msg hook for Positronikal repositories
# Enforces conventional commit format and security requirements

commit_regex='^(feat|fix|docs|style|refactor|test|chore|security|perf)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "📝 Commit messages must follow conventional commit format:"
    echo "   type(scope): description"
    echo ""
    echo "📋 Valid types: feat, fix, docs, style, refactor, test, chore, security, perf"
    echo ""
    echo "✅ Examples:"
    echo "   feat: add new terminal command for coding standards"
    echo "   fix(security): patch XSS vulnerability in user input"
    echo "   docs: update contributing guidelines"
    echo "   security: implement additional CSP headers"
    echo ""
    exit 1
fi

# Check for security keywords
if grep -qE "(security|vulnerability|cve|exploit|attack|breach)" "$1"; then
    echo "🔒 Security-related commit detected."
    echo "   Ensure proper security review has been completed."
fi

echo "✅ Commit message format validated!"
```

## Language-Specific Extensions

### JavaScript/TypeScript Projects
Add to lint-staged configuration:
```json
{
  "lint-staged": {
    "*.{js,ts,jsx,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{css,scss,sass}": [
      "prettier --write"
    ]
  }
}
```

### Python Projects
```json
{
  "lint-staged": {
    "*.py": [
      "black --check",
      "isort --check-only",
      "flake8"
    ]
  }
}
```

### Go Projects
```json
{
  "lint-staged": {
    "*.go": [
      "gofmt -w",
      "go vet",
      "golint"
    ]
  }
}
```

## Security Enhancements

### Enhanced Secret Detection
For sensitive repositories, implement additional patterns:
```bash
# Enhanced secret patterns
SECRET_PATTERNS="(password|secret|key|token|api_key|private_key|access_key|auth_token|bearer|oauth|jwt|ssh_key|pgp|gpg)"
EMAIL_PATTERNS="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
URL_PATTERNS="https?://[^\s]+"

if git diff --cached --name-only | xargs grep -l -E "$SECRET_PATTERNS" 2>/dev/null; then
    echo "❌ Potential secrets detected!"
    exit 1
fi
```

### File Size and Type Restrictions
```bash
# Check for large files (>10MB)
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -gt 10485760 ]; then
            echo "❌ File $file is larger than 10MB ($size bytes)"
            exit 1
        fi
    fi
done

# Check for forbidden file types
if git diff --cached --name-only | grep -E "\.(exe|dll|so|dylib|bin)$"; then
    echo "❌ Binary executables detected in commit!"
    echo "   Consider using package managers or build artifacts instead."
    exit 1
fi
```

## Forensic Evidence Tool Enhancements

For repositories subject to Forensic Evidence Tool Standards, add:

### Chain of Custody Verification
```bash
# Verify chain of custody documentation
if git diff --cached --name-only | grep -E "(evidence|forensic|acquisition)" >/dev/null; then
    echo "🔍 Forensic-related changes detected."
    echo "   Ensure proper chain of custody documentation is included."
    
    # Check for required documentation
    if ! git diff --cached --name-only | grep -E "(CHAIN_OF_CUSTODY|EVIDENCE_LOG)" >/dev/null; then
        echo "⚠️  Consider adding chain of custody documentation."
    fi
fi
```

### Legal Compliance Reminders
```bash
# Daubert Standard compliance check
if git diff --cached --name-only | grep -E "(analysis|algorithm|calculation)" >/dev/null; then
    echo "⚖️  Code changes may affect Daubert Standard compliance."
    echo "   Ensure proper documentation and validation testing."
fi
```

## Installation and Setup

### Automatic Installation
Include in repository setup scripts:
```bash
#!/bin/bash
# setup-repository.sh

echo "Installing Git hooks..."
pnpm install
pnpm run prepare

echo "Configuring Git..."
git config commit.gpgsign true
git config user.signingkey [YOUR_GPG_KEY]

echo "Testing hooks..."
echo "test" > .test-file
git add .test-file
git commit -m "test: verify hooks installation" --no-verify
git reset HEAD~1
rm .test-file

echo "✅ Repository setup completed!"
```

### Hook Bypass (Emergency Use Only)
For emergency situations, hooks can be bypassed:
```bash
# Emergency bypass (use sparingly!)
git commit --no-verify -m "emergency: critical hotfix"

# Must be followed by:
git commit --amend -S -m "emergency: critical hotfix - retroactive compliance"
```

## Integration with CI/CD

### Validation in CI Pipeline
Ensure CI validates the same requirements:
```yaml
- name: Validate Git Hooks Compliance
  run: |
    # Verify all commits follow conventional format
    git log --oneline --pretty=format:"%s" origin/main..HEAD | while read msg; do
      if ! echo "$msg" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|security|perf)(\(.+\))?: .{1,50}'; then
        echo "❌ Invalid commit message: $msg"
        exit 1
      fi
    done
    
    # Verify all commits are GPG signed
    git log --show-signature origin/main..HEAD | grep -q "Good signature" || {
      echo "❌ Unsigned commits detected"
      exit 1
    }
```

## Maintenance and Updates

### Hook Updates
- Hooks must be updated when standards evolve
- Test hook changes in development repositories first
- Document breaking changes in hook behavior

### Developer Onboarding
- Include hook setup in contributor guidelines
- Provide troubleshooting guide for common hook failures
- Maintain examples of compliant commit messages

### Performance Monitoring
- Monitor hook execution time
- Optimize patterns and checks for speed
- Provide bypass mechanisms for legitimate edge cases

---

*This Git Hooks Standard integrates with Code Formatting Rules, Repository Security Rules, and GitHub Configuration Standards to provide comprehensive automated enforcement of Positronikal coding standards.*
