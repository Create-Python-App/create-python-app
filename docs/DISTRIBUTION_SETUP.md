# Distribution Channels — One-Time Setup

`create-awesome-python-app` publishes on release tags (`create-awesome-python-app@X.Y.Z`):

| Channel | Workflow | Secret(s) |
|---------|----------|-----------|
| **PyPI** | `publish.yml` | OIDC Trusted Publishing (no token) |
| **Docker** | `publish-docker.yml` | `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` |
| **AUR** | `publish-aur.yml` | `AUR_SSH_PRIVATE_KEY`, `AUR_REPO_TOKEN` |
| **Homebrew** | `notify-homebrew.yml` | `HOMEBREW_TAP_TOKEN` |

Configure secrets under **Settings → Secrets and variables → Actions**.

## PyPI Trusted Publishing

1. On PyPI, add a Trusted Publisher for project `create-awesome-python-app`
2. Owner/repo: `Create-Python-App/create-python-app`
3. Workflow name: `publish.yml`
4. Environment: (optional)

## Docker Hub

Create a write token and set `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`.

## AUR

Bootstrap PKGBUILD in a future `Create-Python-App/aur-package` mirror; set SSH key secret.

## Homebrew

Create `Create-Python-App/homebrew-tap` and allow `repository_dispatch` with `HOMEBREW_TAP_TOKEN`.
