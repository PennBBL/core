#!/bin/bash
set -exo pipefail

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

GRADLE_CONTAINER="gradle:4.5-jdk8-alpine"
PYTHON_CONTAINER="python:2.7-alpine"

if [ "$#" -ge 1 ]; then
	SDK_VERSION="-PsdkVersion=$1"
fi

# Containerized swagger code-gen
PERSISTENT_DIR="${PROJECT_DIR}/persistent"
if [ "$GRADLE_CACHE" = "" ]; then
	gradle_user_home="${PERSISTENT_DIR}/gradle"
	mkdir -p "${PERSISTENT_DIR}/gradle"
else
	gradle_user_home="${GRADLE_CACHE}"
fi

# This will produce the matlab toolbox
docker run --rm -it \
	-w /local \
	-u "$(id -u):$(id -g)" \
	-e GRADLE_USER_HOME=/gradle \
	-v "${PROJECT_DIR}:/local" \
	-v "${gradle_user_home}:/gradle" \
	${GRADLE_CONTAINER} gradle --no-daemon $SDK_VERSION clean build 

# Containerized python package gen
docker run --rm -it \
	-w /local/src/python/gen \
	-u "$(id -u):$(id -g)" \
	-v "${PROJECT_DIR}:/local" \
	${PYTHON_CONTAINER} python setup.py bdist_wheel