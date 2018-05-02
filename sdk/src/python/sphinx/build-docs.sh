#!/usr/bin/env bash

set -e

# change to parent dir
unset CDPATH
cd "$( dirname "${BASH_SOURCE[0]}" )/.."

# Generate the rst files from the api package
sphinx-apidoc -o sphinx/source -f -d 3 gen/flywheel 

# Transform those rst files into html docs
sphinx-build -a -b statichtml sphinx/source sphinx/build
