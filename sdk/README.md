# Flywheel SDK
An SDK for interaction with a remote Flywheel instance, in Golang, Python, and Matlab!




# Development
Gradle is used to build the various components of the SDK. Docker shortcuts are provided in the `docker/` folder to generate code, or run in the docker container.
(e.g `docker/run-in-docker.sh /bin/bash` to then run `gradle build` and keep the gradle daemon alive)

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
* **x-sdk-download-url** - Will be set to the operationId for retrieving a download url via ticket.
* **x-sdk-download-file-param** - Parameter name for destination file parameter for download operations.
