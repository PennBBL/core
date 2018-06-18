#!/bin/bash
set -exo pipefail

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JSONIO_DIR="${PROJECT_DIR}/src/matlab/JSONio"

GRADLE_CONTAINER="gradle:4.5-jdk8-alpine"
PYTHON_CONTAINER="python:3.4"

if [ "$#" -ge 1 ]; then
    SDK_VERSION="-PsdkVersion=$1"
fi

# Clone JSONio
if [ ! -d "${JSONIO_DIR}" ]; then
    git clone https://github.com/flywheel-io/JSONio "${JSONIO_DIR}"
fi

# Checkout latest JSONio commit
(
    cd "${JSONIO_DIR}"
    git pull
)

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

# Containerized python package and documentation gen
docker run --rm -it \
    -w /local/src \
    -v "${PROJECT_DIR}:/local" \
    ${PYTHON_CONTAINER} ./build-wheel-and-docs.sh

# Copy distribution artifacts to ./dist/
DIST_DIR=$PROJECT_DIR/dist
rm -rf $DIST_DIR
mkdir -p $DIST_DIR

cp $PROJECT_DIR/src/python/gen/dist/*.whl $DIST_DIR
cp $PROJECT_DIR/src/matlab/build/distributions/*.mltbx $DIST_DIR
