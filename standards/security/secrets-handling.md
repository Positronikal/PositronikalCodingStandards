# Secrets Handling Standards

## Objective

Define how secrets are classified, prevented from entering version control, stored
and accessed at runtime, and remediated when exposed. These standards apply to all
Positronikal original repositories and hard forks.

See [COMMON.md](../COMMON.md) for common exceptions. These standards do not apply
to contributing forks.

---

## What Counts as a Secret

A secret is any value that grants access to a system or resource, authenticates an
identity, or — if disclosed — enables unauthorized action.

| Category | Examples |
|---|---|
| API keys and tokens | Anthropic API keys, GitHub PATs, Google service account keys |
| Credentials | Passwords, passphrases, database connection strings |
| Private keys | TLS/SSH private keys, code signing keys, PGP private keys |
| OAuth tokens | Access tokens, refresh tokens, client secrets |
| Configuration values | Webhook secrets, HMAC signing keys, encryption keys |

Secrets are never static documentation values or example placeholders — those belong
in `.env.example` with dummy values.

---

## Prevention: Keeping Secrets Out of Version Control

### .gitignore Patterns

Every repository must include these patterns in `.gitignore`:

```
# Secrets and credentials
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
*_credentials.json
*_service_account.json
secrets.json
.secrets/
```

The `.env.example` file (committed) documents which environment variables are
required, with placeholder values only. No actual values appear in `.env.example`.

### Pre-Commit Secret Scanning

Secret scanning runs as part of the pre-commit hook using
[gitleaks](https://github.com/gitleaks/gitleaks) — a single static binary with no
runtime dependency, detecting 170+ secret types by default.

**Installation:**
```bash
# Go projects — same toolchain already in use
go install github.com/gitleaks/gitleaks/v8@latest

# All other projects — download binary from releases and place on PATH
# https://github.com/gitleaks/gitleaks/releases
```

**Append to any pre-commit hook** (after language checks, before file size check):
```bash
# Secret scanning
if command -v gitleaks >/dev/null 2>&1; then
    if ! gitleaks protect --staged --no-banner; then
        echo "Secret scanning failed. Remove secrets before committing."
        echo "  If this is a false positive, add an exclusion to .gitleaks.toml."
        exit 1
    fi
else
    echo "Warning: gitleaks not installed. Secret scanning skipped."
    echo "  Install: https://github.com/gitleaks/gitleaks/releases"
fi
```

`--staged` scans only files staged for the current commit — fast, and prevents
secrets from entering git history at all.

**False positive handling** — commit a `.gitleaks.toml` at the repository root:
```toml
[allowlist]
  description = "Repository-specific false positives"
  paths = [
    '''\.env\.example''',
  ]
  # Add regexes for confirmed test fixtures or known non-secret patterns
```

### Relationship to the Pre-Push Claude Review

The gitleaks pre-commit hook catches obvious hardcoded tokens and keys before they
enter git history — it is the deterministic gate. The Claude Code pre-push security
review ([Git Hooks Standards](../Git%20Hooks%20Standards.md)) handles semantic cases
gitleaks cannot: secrets derived at runtime, credentials embedded in logic flow, and
access control flaws that expose data. Both layers are required; neither replaces
the other.

---

## Runtime Storage and Access

Secrets live in environment variables, not in source code or committed configuration
files.

**Rules that apply to all languages:**
- Read secrets from the environment at startup; fail fast if a required secret is absent.
- Never pass secrets as command-line arguments — they appear in process listings.
- Never log secret values, even partially or in debug output.

### Go

```go
import "os"

apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    log.Fatal("API_KEY not set")
}
```

For local development, load a `.env` file with `godotenv` — the load is a no-op in
production where the file is absent:

```go
import "github.com/joho/godotenv"

func init() {
    _ = godotenv.Load()
}
```

### Python

```python
import os

api_key = os.environ["API_KEY"]  # KeyError on missing — fail fast
```

For local development, use `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()  # no-op if .env absent
```

### C

```c
#include <stdlib.h>
#include <stdio.h>

const char *api_key = getenv("API_KEY");
if (!api_key) {
    fprintf(stderr, "error: API_KEY not set\n");
    exit(EXIT_FAILURE);
}
```

### bash/shell

```bash
: "${API_KEY:?API_KEY is required}"
```

The `:?` expansion exits non-zero with a descriptive error if the variable is unset
or empty.

### PowerShell

```powershell
$apiKey = $env:API_KEY
if (-not $apiKey) {
    Write-Error "API_KEY is required"
    exit 1
}
```

---

## CI/CD: GitHub Secrets

For GitHub-hosted workflows, secrets are stored in GitHub Secrets (repository or
organization level) and injected as environment variables:

```yaml
jobs:
  build:
    steps:
      - name: Step requiring a secret
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: ./build.sh
```

Rules:
- Use `${{ secrets.NAME }}` exclusively — never hardcode values in workflow YAML.
- Never echo or print secret values in workflow steps.
- Scope secrets to the minimum required jobs.

For CI secret scanning in public repositories, add the gitleaks GitHub Action:

```yaml
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Secret Exposure Response

If a secret is committed to any repository — local or remote:

1. **Rotate immediately.** Revoke and regenerate the exposed credential at the
   issuing service. Do not wait for history remediation.
2. **Assess access logs.** Check the issuing service for unauthorized use since the
   commit timestamp.
3. **Remove from history.** Use `git-filter-repo`:
   ```bash
   # Remove a file that contained the secret
   git filter-repo --path path/to/secret-file --invert-paths

   # Redact an inline secret value
   git filter-repo --replace-text <(echo "EXPOSED_VALUE==>REDACTED")
   ```
4. **Force-push the rewritten history.** Coordinate with all contributors to re-clone
   or hard-reset their local copies.
5. **Audit `.gitignore`.** Determine why the secret was not excluded and add the
   missing pattern.
6. **Document the incident** in the project's `SECURITY.md` or internal incident log.

---

## Repo Template

The [repo-template](../../repo-template/) should include:

- `.env.example` — documents required variables with placeholder values
- `.gitignore` — includes the secret patterns from this document
- `.gitleaks.toml` — stub allowlist for repository-specific exclusions
- `hooks/pre-commit` — includes the gitleaks block above

Propagating these to the repo template and updating existing repositories is tracked
as a separate workstream item.
