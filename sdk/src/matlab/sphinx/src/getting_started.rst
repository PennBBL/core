Getting Started with Flywheel SDK
*********************************

Introduction
------------
The Flywheel SDK is a matlab toolbox that provides programmatic 
access to the Flywheel API endpoints.

License
-------
Flywheel SDK has an MIT-based `license <https://github.com/flywheel-io/core/blob/master/LICENSE>`_.

Installation
------------
The latest Matlab Toolbox can be downloaded from the `Releases Page <https://github.com/flywheel-io/core/releases>`_.
Installation can be done one of two ways, depending on your Operating System. For OSX and Windows you should be able 
to double-click the downloaded toolbox in order to perform the installation.

If your Operating System does not support double-click installation of toolboxes, you can install from within the matlab console.

.. code-block:: matlab

	toolboxFile = '/path/to/flywheel-sdk-version.mltbx';
	installedToolbox = matlab.addons.toolbox.installToolbox(toolboxFile)

API Key
-------
The SDK requires an API key. You can find and generate your key on the Flywheel profile page. It will look like this:

.. image:: /../../../static/images/api-key.png

Making API Calls
----------------
In order to make API calls, you will need to create an instance of the Flywheel client:

.. code-block:: matlab

	% Create client
	fw = flywheel.Flywheel('my-key')

Once you have a client instance, you can interact with the system. For instance, you could get information about yourself:

.. code-block:: matlab

	self = fw.getCurrentUser();
	fprintf('I am %s %s\n', self.firstname, self.lastname);

Getting Help
------------
You can query the client or objects returned by api calls for additional information:

.. code-block:: matlab

	help(fw); % Display available functions
	disp(self); % Print the properties in the 'self' object

.. _dealing-with-files:

Dealing with Files
------------------
Often times you'll find yourself wanting to upload or download file data to one of Flywheel's containers. When uploading,
you can either specify the path to the input file, or you can specify some in-memory data to upload using the FileSpec object.

.. code-block:: matlab

	% Upload the file at /tmp/hello.txt
	fw.uploadFileToProject(projectId, '/tmp/hello.txt');

	% Upload the data 'Hello World!'
	fileSpec = flywheel.FileSpec('hello.txt', 'Hello World!\n', 'text/plain');
	fw.uploadFileToProject(projectId, fileSpec);

	% Some endpoints allow multiple file uploads:
	fw.uploadOutputToAnalysis(analysisId, {'/tmp/hello1.txt', '/tmp/hello2.txt'});

When downloading, you specify the destination file, or you can download directly to memory.
Supported ``OutputType`` values are:

	- ``int8``
	- ``int16``
	- ``int32``
	- ``int64``
	- ``double`` (default)
	- ``char``

.. code-block:: matlab

	% Download file to /tmp/hello.txt
	fw.downloadFileFromProject(projectId, 'hello.txt', '/tmp/hello.txt');

	% Download file directly to memory as an array of doubles
	data = fw.downloadFileFromProjectAsData(projectId, 'hello.txt');

	% Download file directly to memory as a char cell array
	data = fw.downloadFileFromProjectAsData(projecgtId, 'hello.txt', 'OutputType', 'char');

Object IDs
----------
With the exception of Groups, all containers and objects within Flywheel are referenced using Unique IDs.
Groups are the only object that have a human-readable id (e.g. ``flywheel``).

Finding the ID of an object when you are only familiar with the label can be difficult. One method that may 
help is the :meth:`flywheel.Flywheel.resolve` method.

Resolve takes a path (by label) to an object in the system, and if found, returns the full path to that object,
along with children. For example, to find the ID of the project labeled ``Anxiety Study`` that belongs to the ``flywheel`` 
group, I would call resolve with: ``'flywheel/Anxiety Study'``:

.. code-block:: matlab

	# Resolve project by id
	result = fw.resolve('flywheel/Anxiety Study');

	# Extract the resolved project id
	projectId = result.path{2}.id

	# Print the ids and labels of the path elements
	for idx = 1:numel(result.path)
	  fprintf('%s: %s\n', result.path{idx}.label, result.path{idx}.id);
	end

	# Print the children of project:
	for idx = 1:numel(result.children)
	  fprintf('%s: %s\n', result.children{idx}.label, result.children{idx}.id);
	end

Handling Exceptions
-------------------
When an error is encountered while accessing an endpoint, an exception is thrown. The exception message 
will have more details.

For example:

.. code-block:: python

	try
	  project = fw.getProject('NON_EXISTENT_ID');
	catch ME
	  fprintf('API Error: %s\n', ME.message);
	end
