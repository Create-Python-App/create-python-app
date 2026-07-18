# syntax=docker/dockerfile:1.9
FROM python:3.12-slim-bookworm

# VERSION is passed at build time by the publish workflow so the image
# is pinned to a specific PyPI package version (makes each image
# reproducible for its tag).
ARG VERSION=latest

# git is required to clone cpa-templates (see #219).
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Retry pip install: PyPI simple-index / CDN edges can lag the JSON API
# that CI already observed as ready (see #217).
# hadolint ignore=DL3013
RUN useradd --create-home --uid 1000 --shell /bin/bash app \
    && if [ "$VERSION" = "latest" ]; then \
        pkg="create-awesome-python-app"; \
    else \
        pkg="create-awesome-python-app==${VERSION}"; \
    fi \
    && attempt=1 \
    && until pip install --no-cache-dir "$pkg"; do \
        if [ "$attempt" -ge 12 ]; then exit 1; fi; \
        echo "pip install failed (attempt ${attempt}/12); retrying in 15s"; \
        attempt=$((attempt + 1)); \
        sleep 15; \
    done

USER app
WORKDIR /home/app

ENTRYPOINT ["create-awesome-python-app"]
CMD ["--help"]
