# Versioning

CPA uses **release-prep PRs + GitHub Releases + tags** with hatchling package
versions.

## Prepare a release PR

Run the `Prepare release PR` workflow manually with:

- `version`: the next CLI/core version, for example `0.1.1`
- `notes`: markdown release notes to prepend to `CHANGELOG.md`

The workflow runs `scripts/prepare_release.py`, opens a PR, and updates:

- `packages/create-python-app-core/pyproject.toml`
- `packages/create-awesome-python-app/pyproject.toml`
- `create-python-app-core` dependency pin in the CLI package
- both runtime `__version__` files
- `CHANGELOG.md`

Local equivalent:

```bash
uv run python scripts/prepare_release.py 0.1.1 --notes "- Fix release automation."
```

## Publish after merge

After the release-prep PR is merged:

1. Tag `create-awesome-python-app@X.Y.Z`
2. Push the tag
3. `publish.yml` builds and publishes both packages to PyPI via OIDC (see #58)
4. GitHub Release notes are extracted from the matching `CHANGELOG.md` section
5. Distribution workflows update Docker, Homebrew, and AUR

```bash
git tag create-awesome-python-app@X.Y.Z
git push origin create-awesome-python-app@X.Y.Z
```

Before closing the release issue, confirm PyPI, GitHub Release, Docker,
Homebrew, AUR, and `smoke-distribution.yml`.
