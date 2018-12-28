# Flywheel SDK
An SDK for interaction with a remote Flywheel instance, in Python, and Matlab!

## [Python Getting Started](https://flywheel-io.github.io/core/branches/master/python/getting_started.html)
## [Matlab Getting Started](https://flywheel-io.github.io/core/branches/master/matlab/getting_started.html)

# Development
NOTE: Docker is required for most development processes.

Gradle is used to build the various components of the SDK. Docker shortcuts are provided in the `docker/` folder to generate code, or run in the docker container.
(e.g `docker/run-in-docker.sh /bin/bash` to then run `gradle build` and keep the gradle daemon alive)

# Building
Running `sdk/make.sh [version number]` will build the matlab toolbox and python wheel in the `sdk/dist` folder.

# Testing
After running make.sh (above), tests can be run by invoking `sdk/scripts/docker-tests.sh`

### docker-tests.sh usage
* To enter a test shell, use `--shell` (`-s`)
* To skip building the image, use `--no-build` (`-B`)
* To test with python2 (python3 is the default), use `--python2`
* Any additional arguments are passed to `py.test`:
    * To run only a subset of test, use the [keyword expression filter](https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests) `-k`
    * To see `print` output during tests, increase verbosity with `-vvv`
    * To get a debugger session on failures, use [`--pdb`](https://docs.pytest.org/en/latest/usage.html#dropping-to-pdb-python-debugger-on-failures)

# Components

* **codegen** - Implementation of swagger codegen for Matlab, and extension of swagger codegen for Python.
* **src/java/rest_client** - Java implementation of a Rest Client for Matlab calls. Uses HttpClient 3.1 (present in matlab)
* **src/python** - Python client
* **src/matlab** - Matlab client

# Swagger Vendor Extensions

* **x-sdk-return** - In JSON schemas, will extract the specified field out when returning from an api call.
* **x-sdk-positional** - Normally arguments to matlab models are named parameters - this will make the defined parameter positional instead.
* **x-sdk-download-ticket** - Special casing for downloads, will produce both a normal download operation, and a get download url operation. 
		The value of this field is the name of the get download url operation.
* **x-sdk-get-zip-info** - Special case for files, retrieves zip member information.
        The value of this field is the name of the get zip info operation.
* **x-sdk-download-url** - Will be set to the operationId for retrieving a download url via ticket.
* **x-sdk-download-file-param** - Parameter name for destination file parameter for download operations.
* **x-sdk-include-empty** - On a JSON definition - indicates that the following list of properties should be included on JSON even when empty.
* **x-sdk-ignore-properties** - On a JSON schema includes a list of properties to exclude in codegen
* **x-sdk-schema** - Overrides a schema with the definition provided
