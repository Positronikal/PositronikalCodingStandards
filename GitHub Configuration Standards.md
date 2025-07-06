# GitHub Configuration Standards

## Objective
To establish standard configuration requirements for GitHub user accounts, organizations, and repositories that support the security, compliance, and governance objectives outlined in the [Repository Security Rules](./Repository%20Security%20Rules.md). These settings provide the foundation for secure collaborative development and are essential for projects requiring audit trails and evidence integrity.

### Scope
These standards apply to:
- Individual developer accounts contributing to Positronikal projects
- Organizations managing multiple repositories
- All repositories implementing Positronikal Coding Standards
- Projects requiring forensic evidence compliance

## User Account Configuration

### Security Settings (Mandatory)

#### Two-Factor Authentication
- **Requirement**: TOTP-based 2FA must be enabled
- **Recommended**: Hardware security keys (FIDO2/WebAuthn) as primary method
- **Backup**: Recovery codes stored securely offline
- **SMS**: Avoid SMS-based 2FA due to SIM swapping vulnerabilities

```
Settings > Password and authentication > Two-factor authentication
✅ Authenticator app or security key required
✅ Recovery codes downloaded and stored securely
❌ SMS as primary method
```

#### SSH Key Management
- **Key Type**: Ed25519 preferred, RSA 4096-bit minimum
- **Passphrase**: Required for all private keys
- **Rotation**: Annual key rotation recommended
- **Storage**: Hardware security modules when available

```bash
# Generate secure SSH key
ssh-keygen -t ed25519 -C "your.email@example.com" -f ~/.ssh/github_ed25519

# Add to ssh-agent with passphrase
ssh-add ~/.ssh/github_ed25519
```

#### GPG Commit Signing
- **Requirement**: All commits to security-sensitive repositories must be signed
- **Key Type**: RSA 4096-bit or Ed25519
- **Expiration**: 2-year maximum, annual renewal recommended
- **Verification**: GitHub must show "Verified" badge on commits

```bash
# Generate GPG key
gpg --full-generate-key

# Add to GitHub
gpg --armor --export [KEY_ID]

# Configure Git signing
git config --global user.signingkey [KEY_ID]
git config --global commit.gpgsign true
```

### Profile Configuration

#### Public Profile
- **Real Name**: Use professional name for credibility
- **Email**: Professional email address preferred
- **Biography**: Include relevant certifications and expertise
- **Location**: General location acceptable, specific addresses not recommended
- **Company**: Organization affiliation where appropriate

#### Privacy Settings
- **Email Privacy**: Enable "Keep my email addresses private"
- **Web Commit Signoff**: Enable for audit trail purposes
- **Profile Visibility**: Public for open source contributors, private for sensitive projects

### Security and Analysis

#### Personal Security Settings
```
Settings > Code security and analysis
✅ Dependency graph (for public repos)
✅ Dependabot alerts
✅ Dependabot security updates
✅ Dependabot version updates
✅ Private vulnerability reporting
```

## Organization Configuration

### Access Control and Permissions

#### Member Privileges
- **Base Permissions**: Read access only by default
- **Repository Creation**: Restricted to owners and designated maintainers
- **Outside Collaborators**: Explicit approval required
- **Team Sync**: Configure with enterprise identity providers when available

#### Two-Factor Authentication
- **Requirement**: Mandatory for all organization members
- **Enforcement**: Automatic removal of non-compliant members after grace period
- **Exceptions**: None permitted for security-sensitive organizations

```
Organization Settings > Authentication security
✅ Require two-factor authentication for everyone
✅ Remove non-compliant members after 7 days
✅ Require SSO for SAML-enabled organizations
```

#### Application Access Policy
- **Third-Party Access**: Restricted by default
- **OAuth Apps**: Approval required for all applications
- **GitHub Apps**: Whitelist approach for approved applications only
- **Personal Access Tokens**: Organization visibility required

### Security Policies

#### Advanced Security Features
```
Organization Settings > Code security and analysis
✅ Dependency graph
✅ Dependabot alerts
✅ Dependabot security updates
✅ Code scanning (GitHub CodeQL)
✅ Secret scanning
✅ Private vulnerability reporting
✅ Security advisories
```

#### IP Allow Lists
- **Corporate Networks**: Restrict access to approved IP ranges where required
- **VPN Requirements**: Mandate VPN access for remote contributors
- **Exceptions**: Document and regularly review IP exemptions

### Audit and Compliance

#### Audit Log Configuration
- **Retention**: Maximum available retention period
- **Export**: Regular export to external SIEM systems
- **Monitoring**: Automated alerts for suspicious activities
- **Review**: Monthly audit log review process

#### Member Activity Monitoring
- **Login Tracking**: Monitor unusual login patterns
- **Permission Changes**: Alert on privilege escalations
- **Repository Access**: Track access pattern changes
- **Device Registration**: Monitor new device registrations

## Repository Configuration

### Branch Protection Rules

#### Default Branch Protection
```yaml
Protection Rules for 'main' branch:
✅ Require pull request reviews before merging
  - Required approving reviews: 2 minimum
  - Dismiss stale reviews when new commits are pushed
  - Require review from code owners
  - Restrict push from admins

✅ Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Status checks: [CI, Security Scan, Code Quality]

✅ Require conversation resolution before merging
✅ Require signed commits
✅ Require linear history
✅ Include administrators in restrictions
```

#### Development Branch Strategy
- **Feature Branches**: Short-lived, descriptive names
- **Release Branches**: Protected with additional review requirements
- **Hotfix Branches**: Emergency procedures with accelerated review
- **Delete Merged Branches**: Automatic cleanup enabled

### Security and Analysis Features

#### Repository Security Settings
```
Repository Settings > Code security and analysis
✅ Private vulnerability reporting
✅ Dependency graph
✅ Dependabot alerts
✅ Dependabot security updates
✅ Dependabot version updates
✅ Code scanning (CodeQL)
✅ Secret scanning
✅ Secret scanning push protection
```

#### Code Scanning Configuration
- **CodeQL**: Enable for all supported languages
- **Third-Party Tools**: Integrate additional SAST tools as needed
- **Custom Queries**: Implement organization-specific security rules
- **Alert Management**: Assign security team for alert triage

### Access and Permissions

#### Collaborator Management
- **Principle of Least Privilege**: Minimum required access only
- **Role-Based Access**: Use teams for permission management
- **Regular Review**: Quarterly access review and cleanup
- **External Collaborators**: Limited access with expiration dates

#### Team Permissions
```
Repository access levels:
- Read: Public contributors, community members
- Triage: Community moderators, issue managers
- Write: Active contributors, trusted developers
- Maintain: Senior developers, package maintainers
- Admin: Repository owners, security team leads
```

### Issue and PR Management

#### Templates and Automation
- **Issue Templates**: Bug reports, feature requests, security issues
- **PR Templates**: Standardized review checklists
- **Labels**: Consistent labeling scheme across repositories
- **Automated Workflows**: Stale issue management, welcome messages

#### Security Issue Handling
- **Private Reporting**: Enable private vulnerability reporting
- **Security Advisory**: Use GitHub Security Advisories for CVE management
- **Coordinated Disclosure**: 90-day disclosure timeline
- **Response Times**: SLA for security issue acknowledgment and resolution

## Advanced Configuration for Forensic Evidence Compliance

### Enhanced Audit Requirements

#### Comprehensive Logging
- **Git History**: Preserve complete commit history, no force pushes
- **Access Logs**: Detailed logging of all repository access
- **Change Tracking**: Document all configuration changes with rationale
- **User Attribution**: Clear mapping between GitHub accounts and real identities

#### Evidence Integrity
- **Signed Commits**: Mandatory GPG signing for all commits
- **Branch Protection**: Prevent history modification on protected branches
- **Backup Strategy**: Regular backups to immutable storage
- **Hash Verification**: Periodic verification of repository integrity

### Legal Discovery Preparedness

#### Data Retention
- **Repository Archives**: Quarterly snapshots for historical reference
- **Issue History**: Complete preservation of discussions and decisions
- **Access Records**: Long-term retention of audit logs
- **Communication**: Integration with external communication systems

#### Documentation Requirements
- **Decision Records**: Architecture Decision Records (ADRs) for significant changes
- **Process Documentation**: Clear procedures for evidence handling
- **Chain of Custody**: Documented handoff procedures for code artifacts
- **Expert Witness Preparation**: Contact information and qualifications documentation

## Implementation Checklist

### User Account Setup
- [ ] Enable 2FA with authenticator app or hardware key
- [ ] Generate and configure SSH keys with passphrases
- [ ] Set up GPG key for commit signing
- [ ] Configure Git client for signed commits
- [ ] Review and configure privacy settings
- [ ] Complete professional profile information

### Organization Configuration
- [ ] Enforce 2FA for all members
- [ ] Configure member base permissions
- [ ] Set up third-party application restrictions
- [ ] Enable all available security features
- [ ] Configure IP allow lists if required
- [ ] Set up audit log monitoring and export

### Repository Setup
- [ ] Configure branch protection rules
- [ ] Enable all security and analysis features
- [ ] Set up automated dependency updates
- [ ] Configure code scanning with appropriate tools
- [ ] Create issue and PR templates
- [ ] Set up team-based access controls
- [ ] Enable private vulnerability reporting

### Forensic Compliance (if applicable)
- [ ] Implement enhanced audit logging
- [ ] Set up automated backup procedures
- [ ] Document evidence handling procedures
- [ ] Configure immutable history requirements
- [ ] Set up legal discovery response procedures

## Monitoring and Maintenance

### Regular Review Schedule
- **Weekly**: Security alert triage and resolution
- **Monthly**: Access permission review and cleanup
- **Quarterly**: Complete security configuration audit
- **Annually**: Comprehensive policy review and updates

### Key Metrics to Track
- **Security Alerts**: Open vulnerability count and resolution time
- **Access Patterns**: Unusual access or permission changes
- **Compliance Status**: Configuration drift from established standards
- **Audit Activity**: Regular review of audit logs for anomalies

### Automated Monitoring
- **Security Alerts**: Integration with incident response systems
- **Configuration Changes**: Notifications for critical setting modifications
- **Access Anomalies**: Alerts for unusual login or access patterns
- **Compliance Drift**: Automated detection of configuration violations

## Tools and Integrations

### Recommended Tools
- **Git Client**: Git with GPG signing configured
- **SSH Client**: OpenSSH with hardware key support
- **2FA Apps**: Authy, 1Password, or hardware tokens
- **GPG Tools**: GnuPG with smartcard support where available

### Enterprise Integrations
- **SAML/SSO**: Integration with enterprise identity providers
- **SIEM**: Audit log export to security information systems
- **Backup**: Integration with enterprise backup solutions
- **Monitoring**: Connection to security operations centers

### GitHub Apps and Actions
- **Security Scanning**: CodeQL, Snyk, or equivalent tools
- **Dependency Management**: Dependabot and license compliance tools
- **Code Quality**: SonarCloud, CodeClimate, or similar platforms
- **Documentation**: Automated documentation generation and updates

## Troubleshooting Common Issues

### 2FA Problems
- **Lost Device**: Use recovery codes, contact admin for reset
- **Locked Account**: Organization admin can temporarily disable 2FA requirement
- **Hardware Key Issues**: Ensure FIDO2/WebAuthn compatibility

### GPG Signing Issues
- **Key Expiration**: Renew keys before expiration, update GitHub settings
- **Verification Failures**: Check Git configuration and key association
- **Multiple Keys**: Ensure correct signing key is configured in Git

### Permission Problems
- **Access Denied**: Review team membership and repository permissions
- **Branch Protection**: Verify compliance with protection rules
- **Organization Policies**: Check organization-level restrictions

## Success Criteria

A properly configured GitHub environment will demonstrate:
- ✅ **Strong Authentication**: 2FA enabled across all accounts
- ✅ **Verified Commits**: GPG signing implemented and working
- ✅ **Automated Security**: All available security features enabled
- ✅ **Proper Access Control**: Least privilege principles enforced
- ✅ **Audit Readiness**: Comprehensive logging and monitoring in place
- ✅ **Compliance Documentation**: Clear procedures for evidence handling
- ✅ **Regular Maintenance**: Scheduled reviews and updates performed

This configuration provides a robust foundation for secure, compliant, and legally defensible software development workflows.
