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
	fw = flywheel.Client('my-key')

Once you have a client instance, you can interact with the system. For instance, you could get information about yourself:

.. code-block:: matlab

	self = fw.getCurrentUser();
	fprintf('I am %s %s\n', self.firstname, self.lastname);

Using CLI Credentials
---------------------
If you've logged in using the `CLI <https://docs.flywheel.io/display/EM/CLI+-+Installation>`_, you can create a client
instance without using an API key. This is useful when sharing SDK scripts for others to use.

.. code-block:: matlab

	% Create client, using CLI credentials
	fw = flywheel.Client()

Getting Help
------------
You can query the client or objects returned by api calls for additional information:

.. code-block:: matlab

	help(fw); % Display available functions
	disp(self); % Print the properties in the 'self' object

Finding Objects
---------------
With the exception of Groups, all containers and objects within Flywheel are referenced using Unique IDs.
Groups are the only object that have a human-readable id (e.g. ``flywheel``).

Finding an Object when you are only familiar with the label can be difficult. One method that may
help is the :meth:`flywheel.Flywheel.resolve` method.

Resolve takes a path (by label) to an Object in the system, and if found, returns the full path to that Object,
along with children. For example, to find the project labeled ``Anxiety Study`` that belongs to the ``flywheel``
group, I would call resolve with: ``'flywheel/Anxiety Study'``:

.. code-block:: matlab

	% Resolve project by id
	result = fw.resolve('flywheel/Anxiety Study');

	% Extract the resolved project id
	project = result.path{2};

	% Print the ids and labels of the path elements
	for idx = 1:numel(result.path)
	  fprintf('%s: %s\n', result.path{idx}.label, result.path{idx}.id);
	end

	% Print the children of project:
	for idx = 1:numel(result.children)
	  fprintf('%s: %s\n', result.children{idx}.label, result.children{idx}.id);
	end

In a similar vein to resolve, :meth:`flywheel.Flywheel.lookup` will directly resolve a container by path. For example:

.. code-block:: matlab

	% Lookup project by id
	project = fw.lookup('flywheel/Anxiety Study');

Finally, if the ID of the Object is known, then it can be retrieved directly using the :meth:`flywheel.Flywheel.get` method.

.. code-block:: matlab

	% Get session by id
	session = fw.get('5bed87475b0ab53e50d03e0c');

Working with Objects [NEW]
--------------------------
Most Objects in the Flywheel SDK provide methods for common operations. For example, to update properties on an object,
you can simply call the ``update`` method, passing in a dictionary or key value pairs:

.. code-block:: matlab

	% Update a project's label
	project.update('label', 'New Project Label');

	% Update a subject's type and sex
	subject.update(struct('type', 'human', 'sex', 'female'));

It's important to note that calling ``update`` will not update your local copy of the object! However, you can
quickly refresh an object by calling reload:

.. code-block:: matlab

	% Reload a session
	session = session.reload();

Working with Finders [NEW]
--------------------------
Another way to find objects is via Finders provided at the top level, and on objects. Finders allow locating objects
via arbitrary filtering. Depending on which version of a finder method you call, you can retrieve all matching objects,
or the first matching object. Finally, if you want to walk over a large number of objects, finders support iteration.

Filter Syntax
+++++++++++++
Filter strings are specified as the first argument to a find function. Multiple filters can be separated by commas.
Filtering can generally be done on any property on an object, using dotted notation for sub-properties.
Type conversion happens automatically. To treat a value as a string, wrap it in quotes: e.g. ``label="My Project"``.

Types supported are:

* Dates in the format ``YYYY-MM-DD``
* Timestamps in the format ``YYYY-MM-DDTHH:mm:ss``
* Numeric values (e.g. ``42`` or ``15.7``)
* The literal value ``null``

Operations supported are:

* Comparison operators: ``<, <=, =, !=, >=, >``
* Regular expression match: ``=~``

Sorting
+++++++
In addition to filtering, sorting is supported in the sytax: ``<fieldname>:<ordering>``.
Where ``fieldname`` can be any property, and ``ordering`` is either ``asc`` or ``desc``
for ascending or descending order, respectively.

Examples
++++++++

.. code-block:: matlab

	% Retrieve all projects (with a default limit)
	allProjects = fw.projects();

	% Find the first project with a label of 'My Project'
	project = fw.projects.findFirst('label=My Project');

	% Find all sessions in project created after 2018-10-31
	sessions = project.sessions.find('created>2018-10-31');

	% Iterate over all failed jobs
	itr = fw.jobs.iterFind('state=failed');
	while itr.hasNext()
		job = itr.next();
		fprintf('Job: %s, Gear: %s\n', job.id, job.gearInfo.name);
	end

	% Iterate over all sessions belonging to project
	iter = project.sessions.iter();
	while iter.hasNext()
		session = iter.next();
		fprintf('%s\n', session.label);
	end


.. _dealing-with-files:

Dealing with Files
------------------
Often times you'll find yourself wanting to upload or download file data to one of Flywheel's containers. When uploading,
you can either specify the path to the input file, or you can specify some in-memory data to upload using the FileSpec object.

.. code-block:: matlab

	% Upload the file at /tmp/hello.txt
	project.uploadFile('/tmp/hello.txt');

	% Upload the data 'Hello World!'
	fileSpec = flywheel.FileSpec('hello.txt', 'Hello World!\n', 'text/plain');
	project.uploadFile(fileSpec);

	% Some endpoints allow multiple file uploads:
	analysis.uploadOutput({'/tmp/hello1.txt', '/tmp/hello2.txt'});

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
	project.downloadFile('hello.txt', '/tmp/hello.txt');

	% Download file directly to memory as an array of doubles
	data = project.readFile('hello.txt');

	% Download file directly to memory as a char cell array
	data = project.readFile('hello.txt', 'OutputType', 'char');

Working with Zip Members
++++++++++++++++++++++++
Occasionally you may want to see the contents of a zip file, and possibly download a single member without downloading
the entire zipfile. There are a few operations provided to enable this. For example:

.. code-block:: matlab

	% Get information about a zip file
	zipInfo = acquisition.getZipInfo('my-archive.zip');

	% Download the first zip entry to /tmp/{entry_name}
	entryName = zipInfo.members{1}.path;
	outPath = fullfile('/tmp', entryName);
	acquisition.downloadFileZipMember('my-archive.zip', entryName, outPath);

	% Read the "readme.txt" zip entry directly to memory
	zipData = acquisition.readFileZipMember('my-archive.zip', 'readme.txt', 'OutputType', 'char');

Handling Exceptions
-------------------
When an error is encountered while accessing an endpoint, an exception is thrown. The exception message 
will have more details.

For example:

.. code-block:: matlab

	try
	  project = fw.getProject('NON_EXISTENT_ID');
	catch ME
	  fprintf('API Error: %s\n', ME.message);
	end
