#!/usr/bin/env bash

set -e

# change to parent dir
unset CDPATH
cd "$( dirname "${BASH_SOURCE[0]}" )/.."

# Copy source rst files
mkdir -p build/gen/sphinx/source
cp -R sphinx/src/* build/gen/sphinx/source/

# Transform those rst files into html docs
sphinx-build -a -b statichtml -c sphinx build/gen/sphinx/source build/gen/sphinx/build
