#!/bin/bash
set -eu

pip install -qq --upgrade pip setuptools
pip install -qq -r python/gen/requirements.txt
pip install -qq -r requirements-docs.txt

# Build python sphinx docs
(
	cd python/sphinx/
	./build-docs.sh
)

# Build matlab sphinx docs
(
	cd matlab/sphinx/
	./build-docs.sh
)


# Build python wheel
(
	cd python/gen/
	python setup.py -q bdist_wheel
)

