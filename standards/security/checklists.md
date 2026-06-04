# Implementation Checklist by Repository Type

All repository types should have the pre-push security review hook configured. See [Git Hooks Standards](../Git%20Hooks%20Standards.md) for the Claude Code pre-push hook that provides semantic vulnerability analysis before each push.

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
