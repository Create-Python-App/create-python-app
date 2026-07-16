# Distribution Channels — One-Time Setup

`create-awesome-python-app` publishes on release tags (`create-awesome-python-app@X.Y.Z`):

| Channel | Workflow | Secret(s) |
|---------|----------|-----------|
| **PyPI** | `publish.yml` | OIDC Trusted Publishing (no token) |
| **Docker** | `publish-docker.yml` | `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` |
| **AUR** | `publish-aur.yml` | `AUR_SSH_PRIVATE_KEY`, `AUR_REPO_TOKEN` |
| **Homebrew** | `notify-homebrew.yml` → `homebrew-tap` | `HOMEBREW_TAP_TOKEN` |

Configure secrets under **Settings → Secrets and variables → Actions**.

## PyPI Trusted Publishing

The Release job uses the GitHub Actions environment **`pypi`**
(Settings → Environments). Configure Trusted Publishers on PyPI for:

| Project | Owner | Repository | Workflow | Environment |
|---------|-------|------------|----------|-------------|
| `create-python-app-core` | `Create-Python-App` | `create-python-app` | `publish.yml` | `pypi` |
| `create-awesome-python-app` | `Create-Python-App` | `create-python-app` | `publish.yml` | `pypi` |

## Cutting a release

1. Bump versions in both package `pyproject.toml` files and `__version__` / `_version.py`
2. Update `CHANGELOG.md`
3. Merge to `main`
4. Tag and push:

```bash
git tag create-awesome-python-app@X.Y.Z
git push origin create-awesome-python-app@X.Y.Z
```

Then:

1. Confirm Release (PyPI), Notify Homebrew, Publish to AUR, and Docker workflows
2. Smoke: `uvx create-awesome-python-app@X.Y.Z --help`

## Docker Hub

Image: [`ulisesjeremias/create-awesome-python-app`](https://hub.docker.com/r/ulisesjeremias/create-awesome-python-app)

Secrets (already used by CNA; reuse the same Hub account):

- `DOCKERHUB_USERNAME` — e.g. `ulisesjeremias`
- `DOCKERHUB_TOKEN` — Hub access token with write scope

Verify:

```bash
gh workflow run "Publish Docker image" --repo Create-Python-App/create-python-app -f version=0.1.0
docker run --rm ulisesjeremias/create-awesome-python-app:0.1.0 --version
```

## AUR (`AUR_SSH_PRIVATE_KEY`, `AUR_REPO_TOKEN`)

**Prereqs**: An AUR account that can own `create-awesome-python-app`, and the mirror
[`Create-Python-App/aur-package`](https://github.com/Create-Python-App/aur-package).

### Bootstrap the AUR package (first release only)

```bash
ssh-keyscan -H aur.archlinux.org >> ~/.ssh/known_hosts

cd /tmp
rm -rf aur-bootstrap
git clone git@github.com:Create-Python-App/aur-package.git aur-bootstrap
cd aur-bootstrap
git remote add aur ssh://aur@aur.archlinux.org/create-awesome-python-app.git
git push aur main:master
```

If AUR rejects the push because the package does not exist yet, create it via
[aur.archlinux.org/submit](https://aur.archlinux.org/submit) first, then retry.

### Generate / register the AUR SSH key

```bash
ssh-keygen -t ed25519 -C "aur-publish-cpa" -f ~/.ssh/aur_publish_cpa -N ""
cat ~/.ssh/aur_publish_cpa.pub
```

Paste the public key under [AUR → My Account → SSH Public Key](https://aur.archlinux.org/account).
Paste the **private** key as repo secret `AUR_SSH_PRIVATE_KEY`.

### Generate `AUR_REPO_TOKEN`

Fine-grained PAT with **Contents: Read and write** on `Create-Python-App/aur-package` only.
Store as `AUR_REPO_TOKEN`.

## Homebrew (`HOMEBREW_TAP_TOKEN`)

**Prereqs**: [`Create-Python-App/homebrew-tap`](https://github.com/Create-Python-App/homebrew-tap)
with `Formula/create-awesome-python-app.rb` and `update-formula.yml`.

Fine-grained PAT with:

- Repository: `Create-Python-App/homebrew-tap`
- **Contents**: Read and write
- **Actions**: Read and write (needed for `repository_dispatch`)

Store as `HOMEBREW_TAP_TOKEN`.

Install:

```bash
brew tap Create-Python-App/tap
brew install create-awesome-python-app
```

## Verification

```bash
# Homebrew notify
gh workflow run "Notify Homebrew tap" --repo Create-Python-App/create-python-app -f version=0.1.0

# AUR publish
gh workflow run "Publish to AUR" --repo Create-Python-App/create-python-app -f version=0.1.0

# End-user checks
uvx create-awesome-python-app@0.1.0 --version
brew install create-awesome-python-app && create-awesome-python-app --version
yay -S create-awesome-python-app && create-awesome-python-app --version
```

## After secrets are in place

Every subsequent release only requires tagging `create-awesome-python-app@X.Y.Z`.
PyPI, Homebrew notify, AUR, and Docker workflows fan out from that tag.
