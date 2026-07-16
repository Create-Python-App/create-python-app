# Distribution Setup

Secrets and publishers (see also #58–#63):

| Channel | Secret / config |
|---------|-----------------|
| PyPI | Trusted Publishing OIDC (no long-lived token) |
| Docker Hub | `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` |
| AUR | `AUR_SSH_PRIVATE_KEY`, `AUR_REPO_TOKEN` |
| Homebrew | `HOMEBREW_TAP_TOKEN` |

## PyPI Trusted Publishing

1. Create a Trusted Publisher on PyPI for `create-awesome-python-app`
2. Repository: `Create-Python-App/create-python-app`
3. Workflow: `publish.yml`
4. No `PYPI_TOKEN` secret required when using OIDC

## AUR

Track sibling repo `Create-Python-App/aur-package` when ready. Secrets: `AUR_SSH_PRIVATE_KEY`, `AUR_REPO_TOKEN`.
