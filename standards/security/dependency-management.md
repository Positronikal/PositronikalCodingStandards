# Dependency Management Policy

## Objective

Define how dependencies are selected, pinned, updated, and audited across
Positronikal projects. Every third-party dependency is permanent attack surface —
it must earn its place and remain under control.

See [COMMON.md](../COMMON.md) for common exceptions. These standards do not apply
to contributing forks.

---

## The Two-Policy Model

Supply chain attacks and zero-day vulnerabilities pull in opposite directions:
patching fast reduces zero-day exposure; patching slowly gives the community time
to find poisoned releases. The resolution is not a compromise — it is two policies
running simultaneously, each applied to a different severity tier.

The more important lever is blast radius. Egress filtering so a backdoored
dependency cannot phone home, scoped identity so lateral movement dies on contact,
and build provenance so you know exactly what shipped — these controls pay off
regardless of where you set the patch timer.

---

## Patching Policy

### Tier 1 — Patch Immediately

Apply immediately, accepting the supply chain risk. A live zero-day on an exposed
surface damages you faster than a poisoned package will.

All three criteria must be true:

1. The vulnerability exists in functionality your code actually uses (directly or
   transitively)
2. The vulnerability is remotely exploitable
3. A fix is available AND (CVSS ≥ 9.0 OR actively exploited in the wild)

### Tier 2 — Soak Window (Default)

Wait the soak window before upgrading. This gives the community time to discover
malicious releases, backdoored updates, and accidental regressions.

Default soak window: **7 days** from the package upload date.

Everything not meeting Tier 1 criteria belongs here, including:

- Vulnerabilities in code paths your project does not use
- Physical-access-only vulnerabilities
- Low/medium severity findings without active exploitation
- Feature releases and non-security upgrades

---

## Lock Files and Integrity

A lock file is the primary integrity mechanism. It pins the exact resolved version
and (where supported) cryptographic hash of every dependency, making builds
reproducible and auditable.

- The lock file is **committed to version control** — it is not a build artifact.
- CI installs from the lock file exclusively, without re-resolving.
- The soak window governs the *update step* (when you run `uv lock`, `go get`,
  etc.), not normal installs. With a committed lock file, routine installs are
  unaffected by `exclude-newer`.

**Lock file = reproducibility. Soak window = governs what gets resolved when you
update. They are complementary, not redundant.**

---

## By Ecosystem

### Python (uv)

**Lock file:**

```bash
uv lock           # generate or update uv.lock
uv sync           # install from uv.lock (development)
uv sync --frozen  # install from uv.lock without re-resolving (CI)
```

Commit `uv.lock` to version control. Do not commit `.venv/`.

**Soak window — user-level** (`~/.config/uv/uv.toml`):

```toml
exclude-newer = "7 days"
```

**Soak window — project-level** (`uv.toml` at repo root):

```toml
exclude-newer = "7 days"
```

Set both levels. User-level protects all interactive installs on the machine;
project-level travels with the code. The `repo-template/uv.toml` provides the
project-level starting point.

**Tier 1 override** (bypass the soak window for a critical security patch):

```bash
uv add package==version --exclude-newer "1 hour"
```

`"1 hour"` allows packages uploaded more than one hour ago, effectively removing
the 7-day gate while maintaining a minimal sanity delay.

**Audit:** See [automation-and-tooling.md §4.3](./automation-and-tooling.md) for
`pip-audit` integration.

### Go

Go's module system provides cryptographic integrity by default. The `go.sum` file
records the expected hash of every module version, validated against the Go
checksum database (`sum.golang.org`) — a global transparency log.

**Lock equivalent:**
`go.sum` is your lock file. Commit it. Never edit it manually.

```bash
go mod tidy    # prune unused dependencies and update go.mod/go.sum
go mod verify  # verify on-disk module cache matches go.sum
```

Run `go mod tidy` in CI to catch unexpected drift.

Go has no native equivalent to `exclude-newer`. Apply the two-policy model
manually: Tier 1 updates via `go get package@version` immediately; Tier 2 updates
batched, reviewed, and applied after the soak period.

**Audit:** See [automation-and-tooling.md §4.3](./automation-and-tooling.md) for
`govulncheck` integration.

### C

C projects typically depend on system libraries (via the host package manager) or
vendored source. Neither has a built-in lock mechanism.

**System dependencies:** Document all required libraries with minimum version
constraints in `docs/INSTALL.md`. Apply the two-policy model manually — treat
security-flagged library CVEs under Tier 1 criteria; all other updates soak for
7 days.

**Vendored source:** Third-party source copied into the repository must include a
companion `VENDOR.md` documenting the upstream URL, version or tag, commit hash,
and license. Vendored source is pinned by definition — update it deliberately,
following the two-policy model.

**Audit:** No automated equivalent to `govulncheck` or `pip-audit` for arbitrary
C system dependencies. Monitor upstream security advisories (e.g., OpenSSL,
libcurl CVE feeds) for libraries in use.

### bash/shell and PowerShell

Scripts that depend on external commands should document those dependencies in a
header comment:

```bash
# Dependencies: curl >= 7.76, jq >= 1.6, git >= 2.30
```

No lock file mechanism applies. Minimize external command dependencies; prefer the
language's own builtins over shelling out to additional tools.

---

## Dependency Minimization

Before adding any dependency:

1. **Check stdlib first.** Does the standard library cover the need?
2. **Evaluate scope.** Is the dependency actively maintained, narrowly scoped, and
   widely used? Popular dependencies have more eyes on them and faster CVE response.
3. **Audit before adding.** Run the relevant audit tool against the candidate
   package before committing it to the project.
4. **Remove unused dependencies.** Run `go mod tidy`, `uv lock`, or equivalent
   periodically to prune drift.

---

## CI Integration

- Install from the lock file, never re-resolve: `uv sync --frozen` (Python),
  `go mod verify` (Go).
- Run audit tools in CI per [automation-and-tooling.md §4.3](./automation-and-tooling.md).
- A Tier 1 finding from an audit tool in CI should fail the build.
