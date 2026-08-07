# Software Bill of Materials (SBOM) Policy

## Objective

Require every Positronikal software release to include a machine-readable
Software Bill of Materials (SBOM) that captures the components, versions,
licenses, and dependency relationships that make up the software. An SBOM
enables downstream consumers and security tooling to reason about supply chain
risk without manual inspection.

See [COMMON.md](../COMMON.md) for common exceptions. These standards do not
apply to contributing forks.

---

## Standard

Positronikal SBOM practice follows the **CISA 2026 Minimum Elements for a
Software Bill of Materials** (v2.1, July 29, 2026), co-authored by CISA, NSA,
FBI, and 15 international cybersecurity agencies.

The minimum elements define two categories of requirements:

- **Data Fields** — component name, version, producer, identifiers, license,
  hash value and algorithm, dependency relationships; SBOM author, timestamp,
  tool, format, and version.
- **Practices and Processes** — machine-processable format, transitive coverage,
  per-release frequency, distribution alongside the release.

---

## Format

**Preferred: CycloneDX JSON** (ECMA-424, CycloneDX 1.6+).

CycloneDX JSON is machine-processable, widely supported by vulnerability and
compliance tooling, and produced by the standard Python toolchain (`cyclonedx-py`).
It satisfies the CISA requirement for a machine-processable data format.

**Also accepted:** SPDX JSON (`.spdx.json`) and CycloneDX XML (`.cdx.xml`).
SPDX tag-value (`.spdx`) is accepted but less tooling-friendly.

---

## File Name and Location

Place the SBOM at the **repository root**. The `positronikal-check` warning
check recognizes any of these names (in preference order):

1. `sbom.cdx.json` — CycloneDX JSON **(preferred)**
2. `bom.json` — CycloneDX default output name
3. `sbom.cdx.xml` — CycloneDX XML
4. `sbom.spdx.json` — SPDX JSON
5. `sbom.spdx` — SPDX tag-value

Use `sbom.cdx.json` for all new repos. Commit the file to version control; it
is not a build artifact to be gitignored.

---

## Generation

### Python (uv projects)

Add `cyclonedx-bom` to the repo's dev dependencies:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "cyclonedx-bom>=4.0.0",
    # ... other dev deps
]
```

Generate from the active virtual environment:

```bash
uv sync --extra dev
uv run cyclonedx-py environment \
    --output-format json \
    --outfile sbom.cdx.json
```

Regenerate and commit whenever dependencies change or a release is tagged.

### Go

Use `syft` (recommended) or `cyclonedx-gomod`:

```bash
syft . -o cyclonedx-json=sbom.cdx.json
```

### C

Use `syft` against the build output or source tree:

```bash
syft . -o cyclonedx-json=sbom.cdx.json
```

Document any system library dependencies without a lock mechanism in
`VENDOR.md` so they appear in the SBOM's manual inventory.

### Ruby

Use `cyclonedx-ruby` or `syft`:

```bash
syft . -o cyclonedx-json=sbom.cdx.json
```

---

## Lifecycle

| Trigger | Action |
|---|---|
| New release (version tag) | Regenerate SBOM; commit before tagging |
| Dependency added or updated | Regenerate and commit |
| Dependency removed | Regenerate and commit |

The SBOM version should match the software release version where possible.

---

## Distribution

Two delivery points are required:

1. **Repository root** — the committed `sbom.cdx.json` is always present for
   anyone who clones or downloads the source archive.
2. **GitHub Release asset** — attach `sbom.cdx.json` to the GitHub Release at
   publish time so downstream consumers who do not clone the repo can access it
   directly alongside the release notes and build artifacts.

See [GitHub Configuration Standards](../GitHub%20Configuration%20Standards.md)
for the release asset attachment procedure.

---

## Checker Integration

`positronikal-check` warns (does not hard-fail) when no recognized SBOM file is
found at the repo root. The warning surfaces in `repo-health-check` output and
disappears automatically once any of the accepted file names is present.

To silence the warning, generate an SBOM and commit it — do not add the file
to an exclusion list.

---

## Reference

CISA et al., "2026 Minimum Elements for a Software Bill of Materials (SBOM),"
July 29, 2026. TLP:CLEAR.
