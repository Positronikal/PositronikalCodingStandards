# GitHub Actions Permissions Architecture

## Objective
Document the proper configuration hierarchy and troubleshooting methodology for GitHub Actions permissions, based on systematic testing and real-world implementation experience. This guidance addresses common pitfalls and provides a reliable framework for configuring Actions across different organizational structures.

## Permission Hierarchy and Precedence

GitHub Actions permissions follow a strict hierarchy that determines which settings take precedence:

### 1. Enterprise-Level Settings (Highest Precedence)
- **Scope**: Applies to all organizations within the enterprise
- **Override Capability**: Cannot be overridden by lower levels
- **Use Case**: Enterprise-wide security policies and compliance requirements
- **Not applicable to most individual/organization setups**

### 2. Organization-Level Settings
- **Scope**: Applies to all repositories within the organization
- **Override Capability**: Can disable repository-level customization
- **Critical Discovery**: **Restrictive allowlists at this level prevent repository-level customization**
- **Recommended Approach**: Use for broad policies, avoid restrictive action allowlists

### 3. Repository-Level Settings
- **Scope**: Applies only to the specific repository
- **Override Capability**: Only works when organization allows repository control
- **Best Practice**: Primary location for action-specific allowlists
- **Granular Control**: Enables per-project security requirements

### 4. Workflow Files (Lowest Precedence)
- **Scope**: Individual workflow specifications
- **Override Capability**: Cannot override permission restrictions from higher levels
- **Function**: Specifies which actions to use, subject to allowlist approval

## Critical Discovery: Exact Version Matching Required

### The Problem
During systematic testing, we discovered that **wildcard patterns in Actions allowlists do not work as expected**.

### Evidence
**❌ Failed Configuration:**
```
Allowlist: withastro/action@*
Workflow: uses: withastro/action@v3
Result: Permission denied
```

**✅ Working Configuration:**
```
Allowlist: withastro/action@v3
Workflow: uses: withastro/action@v3
Result: Success
```

### Implications
- **Version Wildcards**: `@*` patterns are unreliable in allowlists
- **Exact Matching**: Specify exact versions in allowlists for guaranteed functionality
- **Maintenance Overhead**: Allowlists must be updated when action versions change
- **Security Benefit**: Forces explicit approval of specific action versions

## Recommended Architecture

### Organization-Level Configuration
**Purpose**: Broad governance and security policies

```yaml
Organization Settings > Actions > General:
  Actions permissions: "Allow all actions and reusable workflows"
  # This enables repository-level control while maintaining audit oversight
  
  Artifact and log retention: 90 days minimum
  Fork pull request workflows: "Require approval for first-time contributors"
  
Advanced Security:
  ✅ Dependency graph
  ✅ Dependabot alerts  
  ✅ Dependabot security updates
  ✅ Code scanning
  ✅ Secret scanning
```

**Rationale**: Enables repository flexibility while maintaining security oversight.

### Repository-Level Configuration  
**Purpose**: Project-specific action allowlists and security requirements

```yaml
Repository Settings > Actions > General:
  Actions permissions: "Allow select actions and reusable workflows"
  
Allowlist (Example - Web Project):
  actions/cache@*                    # Caching - wildcards work for GitHub actions
  actions/checkout@*                 # Source checkout - wildcards work
  actions/deploy-pages@v4            # Deployment - exact version required
  actions/download-artifact@*        # Artifact handling - wildcards work
  actions/setup-node@*               # Environment setup - wildcards work  
  actions/setup-python@*             # Environment setup - wildcards work
  actions/upload-artifact@*          # Artifact handling - wildcards work
  actions/upload-pages-artifact@*    # Pages deployment - wildcards work
  github/codeql-action@*             # Security scanning - wildcards work
  oven-sh/setup-bun@*                # Package manager - wildcards work
  pnpm/action-setup@*                # Package manager - wildcards work
  withastro/action@v3                # Build tool - exact version required
```

### Key Patterns Discovered

#### ✅ Wildcards Work For:
- **GitHub Official Actions**: `actions/*@*`, `github/*@*`
- **Stable Third-Party Actions**: `oven-sh/setup-bun@*`, `pnpm/action-setup@*`

#### ❌ Exact Versions Required For:  
- **Framework-Specific Actions**: `withastro/action@v3`
- **Deployment Actions**: `actions/deploy-pages@v4`
- **Actions with Complex Dependencies**: Actions that internally call other actions

#### 🔍 Hidden Transitive Dependencies
**Critical Discovery**: Actions may internally call other actions not explicitly listed in workflows.

**Example - Astro Action Dependencies:**
```yaml
# Your workflow only shows:
uses: withastro/action@v3

# But withastro/action@v3 internally calls:
# - oven-sh/setup-bun@v2
# - pnpm/action-setup@v4
# - actions/upload-pages-artifact@v3
```

**Implication**: Even if your workflow doesn't explicitly use `oven-sh/setup-bun`, it must be in your allowlist because `withastro/action@v3` calls it internally.

**Detection Method**: 
1. Remove suspected unused actions from allowlist
2. Test with actual workflow run
3. Error messages will reveal hidden dependencies
4. Add back only the actions that cause failures

## Systematic Troubleshooting Methodology

### Phase 1: Establish Known Baseline
```bash
# 1. Create preservation branch
git checkout -b troubleshooting/permissions-backup
git push origin troubleshooting/permissions-backup

# 2. Reset to last known working state
git checkout main
git reset --hard [LAST_WORKING_COMMIT]

# 3. Create minimal test mechanism
echo "1" > TESTFILE
git add TESTFILE
git commit -m "test: baseline permissions test - 1"
git push
```

### Phase 2: Configure Permission Hierarchy

#### Step 1: Organization Settings
- Remove restrictive allowlists at organization level
- Enable repository-level control
- Maintain security features (Dependabot, CodeQL, etc.)
- Test push to verify basic functionality

#### Step 2: Repository Settings  
- Configure action allowlists with exact versions for problematic actions
- Start with minimal required actions
- Test each addition incrementally

#### Step 3: Workflow Optimization
- Verify workflow files match allowlist entries exactly
- Use exact versions where wildcards fail
- Minimize external dependencies

### Phase 3: Incremental Testing

```bash
# Test each change individually
echo "2" > TESTFILE
git add TESTFILE  
git commit -m "test: after organization settings - 2"
git push

# Check Actions tab for results before proceeding
# Repeat for each configuration change
```

### Phase 4: Security Hardening (Permission Minimization)

Once workflows are functioning, systematically reduce permissions to the minimum required set.

#### Hardening Methodology
```bash
# 1. Analyze all workflow files to identify explicitly used actions
# 2. Compare with current allowlist to find potentially unused actions
# 3. Test removal of suspected unused actions in batches
# 4. Use error messages to identify hidden transitive dependencies

# Example test cycle:
echo "4" > TESTFILE
git add TESTFILE
git commit -m "test: security hardening - remove unused actions

- Remove actions/download-artifact@* (unused)
- Remove actions/setup-python@* (unused)  
- Remove actions/upload-artifact@* (unused)
- Test oven-sh/setup-bun@* removal

TESTFILE Change: 4 - Testing optimized allowlist"
git push

# Monitor Actions tab for permission errors
# Add back only actions that cause workflow failures
```

#### Real-World Example: Astro Project Hardening
**Initial allowlist (12 actions):**
```
actions/cache@*, actions/checkout@*, actions/deploy-pages@v4,
actions/download-artifact@*, actions/setup-node@*, actions/setup-python@*,
actions/upload-artifact@*, actions/upload-pages-artifact@*,
github/codeql-action@*, oven-sh/setup-bun@*, pnpm/action-setup@*,
withastro/action@v3
```

**Optimized allowlist (9 actions):**
```
actions/cache@*, actions/checkout@*, actions/deploy-pages@v4,
actions/setup-node@*, actions/upload-pages-artifact@*,
github/codeql-action@*, oven-sh/setup-bun@*, pnpm/action-setup@*,
withastro/action@v3
```

**Results:**
- ✅ **Removed 3 genuinely unused actions** (25% reduction)
- ✅ **Discovered hidden dependency**: `withastro/action@v3` → `oven-sh/setup-bun@v2`
- ✅ **Maintained full functionality** while improving security posture
- ✅ **Documented real requirements** vs. assumptions

## Common Pitfalls and Solutions

### Pitfall 1: Organization-Level Restrictive Allowlists
**Problem**: Organization allowlist blocks repository customization
**Solution**: Use organization settings for policies, not restrictive action lists

### Pitfall 2: Wildcard Pattern Assumptions
**Problem**: Assuming `@*` works for all action allowlists
**Solution**: Test with exact versions for third-party actions

### Pitfall 3: Nested Action Dependencies  
**Problem**: Allowed action internally calls blocked action
**Solution**: Identify and allowlist all transitive dependencies

### Pitfall 4: Version Mismatch
**Problem**: Allowlist has `@v3`, workflow uses `@v4`
**Solution**: Maintain exact version matching between allowlist and workflows

## Security Considerations

### Principle of Least Privilege
- **Minimal Allowlists**: Only include actions actually required
- **Regular Audits**: Review and remove unused action permissions
- **Version Control**: Specific versions prevent supply chain attacks
- **Monitoring**: Alert on allowlist changes and new action usage

### Supply Chain Security
- **Action Verification**: Verify action publishers and reputation
- **Pin Versions**: Avoid `@main` or `@latest` in production workflows
- **Dependency Scanning**: Monitor actions for vulnerabilities
- **Backup Plans**: Have alternatives for critical external actions

### Audit and Compliance
- **Change Tracking**: Document all allowlist modifications
- **Access Control**: Limit who can modify action permissions
- **Approval Process**: Require review for new action additions
- **Evidence Trail**: Maintain records for compliance and forensic needs

## Template Configurations

### Web Development Project
```yaml
# Repository allowlist for Astro/React/Vue projects
# Based on real-world testing and hidden dependency discovery
actions/cache@*
actions/checkout@*
actions/deploy-pages@v4
actions/setup-node@*
actions/upload-pages-artifact@*
github/codeql-action@*
oven-sh/setup-bun@*                # Required by withastro/action@v3 internally
pnpm/action-setup@*
withastro/action@v3
```

**Note**: This configuration represents the **optimized minimum** after security hardening. The following actions were tested and confirmed unused:
- `actions/download-artifact@*` - Removed ✅
- `actions/setup-python@*` - Removed ✅  
- `actions/upload-artifact@*` - Removed ✅

### Python/Data Science Project  
```yaml
# Repository allowlist for Python projects
actions/cache@*
actions/checkout@*
actions/setup-python@*
actions/upload-artifact@*
github/codeql-action@*
codecov/codecov-action@v3
```

### Forensic Tools Project
```yaml  
# Repository allowlist for security-focused projects
actions/cache@*
actions/checkout@*
actions/setup-python@*
actions/upload-artifact@*
github/codeql-action@*
github/super-linter@v4
anchore/scan-action@v3
```

## Success Metrics

### Technical Indicators
- ✅ **All workflows run without permission errors**
- ✅ **Minimal allowlist with only required actions**  
- ✅ **Exact version matching where needed**
- ✅ **Organization settings enable repository flexibility**

### Process Indicators  
- ✅ **Systematic troubleshooting methodology documented**
- ✅ **Configuration changes tracked and reversible**
- ✅ **Security review completed after permissions work**
- ✅ **Template configurations created for reuse**

### Compliance Indicators
- ✅ **All permission changes have documented rationale**
- ✅ **Regular audit schedule established**
- ✅ **Principle of least privilege maintained**
- ✅ **Evidence trail preserved for forensic requirements**

## Maintenance Procedures

### Regular Reviews
- **Monthly**: Audit action allowlists for unused permissions
- **Quarterly**: Review organization vs repository permission distribution  
- **After Incidents**: Update procedures based on troubleshooting experiences
- **Version Updates**: Coordinate action version updates with security reviews

### Automation Opportunities
- **Allowlist Monitoring**: Alert on unauthorized action usage attempts
- **Version Tracking**: Monitor for new versions of allowed actions
- **Compliance Checking**: Automated verification of permission configurations
- **Documentation Updates**: Generate current configuration documentation

This architecture provides a robust, secure, and maintainable approach to GitHub Actions permissions while avoiding common configuration pitfalls.
