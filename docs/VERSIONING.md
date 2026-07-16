# Versioning

CPA uses **GitHub Releases + tags** with hatchling package versions.

Recommended flow (release-please or manual tags):

1. Bump `version` in package pyproject.toml files
2. Tag `create-awesome-python-app@X.Y.Z`
3. `publish.yml` builds and publishes to PyPI via OIDC (see #58)
