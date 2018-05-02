#!/bin/bash
set -eo pipefail

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

PYTHON_CONTAINER="python:3.4"

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <pypi username> <pypi password>"
    exit 1
fi

# Containerized python package gen
docker run --rm -it \
    -w /local \
    -e "TWINE_USERNAME=$1" \
    -e "TWINE_PASSWORD=$2" \
    -v "${PROJECT_DIR}:/local" \
    ${PYTHON_CONTAINER} bash -c "pip -qq install --upgrade pip setuptools twine && twine upload src/python/gen/dist/*.whl"

