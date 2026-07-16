# ADR 0002: PR automation — CodeRabbit-only (no Danger.js)

## Decision

Do **not** port `tools/danger` from create-node-app for CPA v0.

Rely on GitHub Actions PR validation + CodeRabbit (when enabled) for review comments.

## Rationale

- Smaller Python monorepo; Actions already cover lint/test/typecheck
- Avoid maintaining a JS Danger toolchain in a Python repo
- Can revisit if review automation gaps appear
