#!/usr/bin/env bash

set -e

unset CDPATH
cd "$( dirname "${BASH_SOURCE[0]}" )/.."

SCITRAN_RUNTIME_PATH=${SCITRAN_RUNTIME_PATH:-"./runtime"}

echo() { builtin echo -e "\e[1;7mSCITRAN\e[0;7m $@\e[27m"; }

if hash brew 2>/dev/null; then
    echo "Homebrew is installed"
else
    echo "Installing Homebrew"
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    echo "Installed Homebrew"
fi

if brew list | grep -q openssl; then
    echo "OpenSSL is installed"
else
    echo "Installing OpenSSL"
    brew install openssl
    echo "Installed OpenSSL"
fi

if brew list | grep -q "^python$"; then
    echo "Python is installed"
else
    echo "Installing Python"
    brew install python
    echo "Installed Python"
fi

if hash virtualenv 2>/dev/null; then
    echo "Virtualenv is installed"
else
    echo "Installing Virtualenv"
    pip install virtualenv
    echo "Installed Virtualenv"
fi

if [ -d "$SCITRAN_RUNTIME_PATH" ]; then
    echo "Virtualenv exists at $SCITRAN_RUNTIME_PATH"
else
    echo "Creating 'scitran' Virtualenv at $SCITRAN_RUNTIME_PATH"
    virtualenv -p `brew --prefix`/bin/python --prompt="(scitran) " $SCITRAN_RUNTIME_PATH
    echo "Created 'scitran' Virtualenv at $SCITRAN_RUNTIME_PATH"
fi


echo "Activating Virtualenv"
. $SCITRAN_RUNTIME_PATH/bin/activate # will fail with `set -u`


echo "Installing Python requirements"
pip install "pip>=8"
# Compile uwsgi with https support
CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install  --no-cache-dir  uwsgi
pip install -r requirements.txt


# Install MongoDB
MONGODB_URL="http://downloads.mongodb.org/osx/mongodb-osx-x86_64-v3.2-latest.tgz"
if [ -x "$SCITRAN_RUNTIME_PATH/bin/mongod" ]; then
    MONGODB_VERSION=$($SCITRAN_RUNTIME_PATH/bin/mongod --version | grep "db version" | cut -d "v" -f 3)
    echo "MongoDB version $MONGODB_VERSION is installed"
    echo "Remove $SCITRAN_RUNTIME_PATH/bin/mongod to install latest version"
else
    echo "Installing MongoDB"
    curl $MONGODB_URL | tar xz -C $SCITRAN_RUNTIME_PATH/bin --strip-components 2
    MONGODB_VERSION=$($SCITRAN_RUNTIME_PATH/bin/mongod --version | grep "db version" | cut -d "v" -f 3)
    echo "MongoDB version $MONGODB_VERSION installed"
fi


# Install Node.js
if [ ! -f "$SCITRAN_RUNTIME_PATH/bin/node" ]; then
  echo "Installing nodejs"
  node_source_dir=`mktemp -d`
  curl https://nodejs.org/dist/v6.4.0/node-v6.4.0-darwin-x64.tar.gz | tar xz -C "$node_source_dir"
  mv $node_source_dir/node-v6.4.0-darwin-x64/bin/* "$SCITRAN_RUNTIME_PATH/bin"
  mv $node_source_dir/node-v6.4.0-darwin-x64/lib/* "$SCITRAN_RUNTIME_PATH/lib"
  rm -rf "$node_source_dir"
fi


# Install testing dependencies
pip install -r "test/integration_tests/requirements-integration-test.txt"
if [ ! -f "$SCITRAN_RUNTIME_PATH/bin/abao" ]; then
  npm install -g git+https://github.com/flywheel-io/abao.git#better-jsonschema-ref
fi
if [ ! -f "$SCITRAN_RUNTIME_PATH/bin/newman" ]; then
  npm install -g newman@3.1.0
fi
