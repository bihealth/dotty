#!/bin/bash

# Utility script to start the Docker build process.

set -x
set -euo pipefail

GIT_DESCRIBE=$((git describe --tags || echo 0.0.0) | cut -d - -f 1)
GIT_TAG=${GIT_TAG-$GIT_DESCRIBE}
DOCKER_VERSION=$(echo $GIT_TAG | sed -e 's/^v//')

ORG=bihealth
REPO=dotty

(git describe --tags --dirty || echo 0.0.0) >VERSION

sudo docker build . \
    --build-arg version_file=VERSION \
    --file utils/docker/Dockerfile \
    --pull \
    -t ghcr.io/$ORG/$REPO:$DOCKER_VERSION \
    "$@"
