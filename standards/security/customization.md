# Customization Guidelines

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
