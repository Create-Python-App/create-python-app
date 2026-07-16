# syntax=docker/dockerfile:1.9
FROM python:3.12-slim-bookworm

# VERSION is passed at build time by the publish workflow so the image
# is pinned to a specific PyPI package version (makes each image
# reproducible for its tag).
ARG VERSION=latest

# hadolint ignore=DL3013
RUN useradd --create-home --uid 1000 --shell /bin/bash app \
    && if [ "$VERSION" = "latest" ]; then \
        pip install --no-cache-dir create-awesome-python-app; \
    else \
        pip install --no-cache-dir "create-awesome-python-app==${VERSION}"; \
    fi

USER app
WORKDIR /home/app

ENTRYPOINT ["create-awesome-python-app"]
CMD ["--help"]
