[![Build Status](https://travis-ci.org/flywheel-io/core.svg?branch=master)](https://travis-ci.org/flywheel-io/core)
[![Coverage Status](https://codecov.io/gh/flywheel-io/core/branch/master/graph/badge.svg)](https://codecov.io/gh/flywheel-io/core/branch/master)

# SciTran – Scientific Transparency

### Overview

SciTran Core is a RESTful HTTP API, written in Python and backed by MongoDB. It is the central component of the [SciTran data management system](https://scitran.github.io). Its purpose is to enable scientific transparency through secure data management and reproducible processing.

##### Versioning

This project uses [Semantic Versioning 2.0.0](https://semver.org/#semantic-versioning-200).
Alpha, Beta and RC builds will use the pre-release tags `alpha`, `beta` and `rc`, respectively. (e.g. `2.1.0-alpha.1`)


### [Documentation](https://flywheel-io.github.io/core)

* [Branches](https://flywheel-io.github.io/core/branches)
* [Tags](https://flywheel-io.github.io/core/tags)

### [Contributing](https://github.com/flywheel-io/core/blob/master/CONTRIBUTING.md)

### [Testing](https://github.com/flywheel-io/core/blob/master/tests/README.md)

### [License](https://github.com/flywheel-io/core/blob/master/LICENSE)

### Usage

```
docker build -t flywheel/core .
docker run \
    -e PRE_RUNAS_CMD='mongod >/dev/null 2>&1 &' \
    -e SCITRAN_CORE_DRONE_SECRET=secret \
    -p 9000:9000 \
    flywheel/core
```

### Continuous Deployment

To enable continuous delivery for a branch, add it to the list in variable CD_BRANCH_NAMES (separated by '|', no spaces)
of the CI configuration (https://travis-ci.org/flywheel-io/core/settings).
Builds for those branches will be pushed to dockerhub at flywheel/core:{BRANCH_NAME}.latest
