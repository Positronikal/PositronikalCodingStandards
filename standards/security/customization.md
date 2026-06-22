# Customization Guidelines

### Repository Assessment
1. **Language/Framework**: Adapt tools to primary technology stack
2. **Sensitivity Level**: Adjust security controls based on data/system criticality
3. **Compliance Requirements**: Add industry-specific security measures
4. **Team Size**: Scale review processes and automation accordingly
5. **Deployment Environment**: Consider cloud, on-premise, or hybrid security needs

### Tool Selection Matrix
| Language | Type Checker | SAST Tool | Dependency Scanner | License Checker | Test Framework | Dynamic/Memory Analysis |
|----------|--------------|-----------|-------------------|-----------------|----------------|--------------------------|
| Python | pyright/mypy | Bandit | Safety | pip-licenses | pytest | — (not applicable; managed memory) |
| Node.js | TypeScript | ESLint Security | npm audit | license-checker | Jest | — (not applicable; managed memory) |
| Java | Java Compiler | SpotBugs | OWASP Dependency Check | License Maven Plugin | JUnit | — (not applicable; managed memory) |
| Go | go vet | gosec | govulncheck | go-licenses | testing | `go test -race` (race detector) |
| C# | Roslyn | Security Code Scan | OWASP Dependency Check | dotnet list package | xUnit | — (not applicable; managed memory) |
| C | Clang Static Analyzer / `clang-tidy`, or GCC `-fanalyzer` | Cppcheck (also Flawfinder for security-pattern scanning) | OSV-Scanner (covers vcpkg.json/conanfile.txt where a package manager is in use; C has no central package ecosystem, so coverage is inherently weaker than the managed-language rows) | ScanCode Toolkit (language-agnostic fallback; no C-specific tool exists) | Check | **Valgrind** (memcheck and friends) plus AddressSanitizer/UndefinedBehaviorSanitizer (compiler-built-in, faster — good CI companion to Valgrind's more thorough but slower local runs) |

**Why Dynamic/Memory Analysis gets its own column:** manual memory management makes use-after-free, buffer overflows, and undefined behavior a class of risk that static analysis alone cannot reliably catch in C — unlike the garbage-collected languages above, where this category doesn't apply. Run sanitizers in CI for fast feedback on every change; reserve Valgrind for deeper local runs (slower, but catches a broader range of memory errors including some sanitizers miss).
