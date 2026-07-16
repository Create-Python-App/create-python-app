# Security Policy

## Supported versions

Security fixes are applied to the latest release of `create-awesome-python-app`.

## Reporting a vulnerability

Please open a private security advisory on GitHub or email the maintainers.
Do not open a public issue for undisclosed vulnerabilities.

OSV scanning runs via `.github/workflows/osv-scanner.yml`.

## Network endpoints

The CLI may fetch remote resources when scaffolding or refreshing the template catalog:

| Host | Purpose | Timeout | User-Agent |
|------|---------|---------|------------|
| `raw.githubusercontent.com` | Template catalog `templates.json` from `cpa-templates` | 10 s | `create-awesome-python-app/<version>` |
| `github.com` | Template and extension repositories (git clone) | — | git |

Override the catalog URL with `CPA_CATALOG_URL`. Use `CPA_OFFLINE=1` / `--offline` and local `file://` URLs when working air-gapped.
