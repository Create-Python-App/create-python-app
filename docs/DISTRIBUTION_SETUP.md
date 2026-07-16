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

Configure **two** pending Trusted Publishers on PyPI (same workflow publishes both packages):

### `create-python-app-core`

1. Owner: `Create-Python-App`
2. Repository: `create-python-app`
3. Workflow: `publish.yml`
4. Environment: (leave empty unless you use one)

### `create-awesome-python-app`

Same owner/repo/workflow as above.

On the first tag `create-awesome-python-app@0.1.0`, OIDC creates the projects and uploads sdists/wheels for both packages.

## Cutting a release

1. Bump versions in both package `pyproject.toml` files and `__version__` / `_version.py`
2. Update `CHANGELOG.md`
3. Merge to `main`
4. Tag and push:

```bash
git tag create-awesome-python-app@0.1.0
git push origin create-awesome-python-app@0.1.0
```

5. Confirm the Release workflow published both packages
6. Smoke: `uvx create-awesome-python-app@0.1.0 --help`

## Docker Hub

Create a write token and set `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`.

## AUR

Bootstrap PKGBUILD in a future `Create-Python-App/aur-package` mirror; set SSH key secret.

## Homebrew

Create `Create-Python-App/homebrew-tap` and allow `repository_dispatch` with `HOMEBREW_TAP_TOKEN`.
