Getting Started with Flywheel SDK
*********************************

Introduction
------------
The Flywheel SDK is a python toolbox that provides programmatic 
access to the Flywheel API endpoints.

License
-------
Flywheel SDK has an MIT-based `license <https://github.com/flywheel-io/core/blob/master/LICENSE>`_.

Installation
------------
The latest python package can be installed using pip:

.. code-block:: bash

	pip install flywheel-sdk

The python wheel can also be downloaded from the `Releases Page <https://github.com/flywheel-io/core/releases>`_.

API Key
-------
The SDK requires an API key. You can find and generate your key on the Flywheel profile page. It will look like this:

.. image:: /../../../static/images/api-key.png

Making API Calls
----------------
In order to make API calls, you will need to create an instance of the Flywheel client:

.. code-block:: python

	# import flywheel package
	import flywheel

	# Create client
	fw = flywheel.Client('my-key')

Once you have a client instance, you can interact with the system. For instance, you could get information about yourself:

.. code-block:: python

	self = fw.get_current_user()
	print('I am %s %s' % (self.firstname, self.lastname))

Using CLI Credentials
---------------------
If you've logged in using the `CLI <https://docs.flywheel.io/display/EM/CLI+-+Installation>`_, you can create a client
instance without using an API key. This is useful when sharing SDK scripts for others to use.

.. code-block:: python

	# Create client, using CLI credentials
	fw = flywheel.Client()

Finding Objects
---------------
With the exception of Groups, all containers and objects within Flywheel are referenced using Unique IDs.
Groups are the only object that have a human-readable id (e.g. ``flywheel``).

Finding an Object when you are only familiar with the label can be difficult. One method that may
help is the :meth:`~flywheel.flywheel.Flywheel.resolve` method.

Resolve takes a path (by label) to an Object in the system, and if found, returns the full path to that Object,
along with children. For example, to find the project labeled ``Anxiety Study`` that belongs to the ``flywheel``
group, I would call resolve with: ``'flywheel/Anxiety Study'``:

.. code-block:: python

	# Resolve project by id
	result = fw.resolve('flywheel/Anxiety Study')

	# Extract the resolved project id
	project = result.path[-1]

	# Print the ids and labels of the path elements
	for el in result.path:
		print('%s: %s' % (el.label, el.id))

	# Print the children of project:
	for el in result.children:
		print('%s: %s' % (el.label, el.id))

In a similar vein to resolve, :meth:`~flywheel.flywheel.Flywheel.lookup` will directly resolve a container by path. For example:

.. code-block:: python

	# Lookup project by id
	project = fw.lookup('flywheel/Anxiety Study')

Finally, if the ID of the Object is known, then it can be retrieved directly using the :meth:`flywheel.flywheel.Flywheel.get` method.

.. code-block:: python

	# Get session by id
	session = fw.get('5bed87475b0ab53e50d03e0c')

Working with Objects [NEW]
--------------------------
Most Objects in the Flywheel SDK provide methods for common operations. For example, to update properties on an object,
you can simply call the ``update`` method, passing in a dictionary or key value pairs:

.. code-block:: python

	# Update a project's label
	project.update(label='New Project Label')

	# Update a subject's type and sex
	subject.update({'type': 'human', 'sex': 'female'})

It's important to note that calling ``update`` will not update your local copy of the object! However, you can
quickly refresh an object by calling reload:

.. code-block:: python

	# Reload a session
	session = session.reload()

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

.. code-block:: python

	# Retrieve all projects (with a default limit)
	all_projects = fw.projects()

	# Find the first project with a label of 'My Project'
	project = fw.projects.find_first('label=My Project');

	# Find all sessions in project created after 2018-10-31
	sessions = project.sessions.find('created>2018-10-31');

	# Iterate over all failed jobs
	for job in fw.jobs.iter_find('state=failed'):
		print('Job: {}, Gear: {}'.format(job.id, job.gear_info.name))

	# Iterate over all sessions belonging to project
	for session in project.sessions.iter():
		print(session.label)

.. _dealing-with-files:

Dealing with Files
------------------
Often times you'll find yourself wanting to upload or download file data to one of Flywheel's containers. When uploading,
you can either specify the path to the input file, or you can specify some in-memory data to upload using the FileSpec object.

.. code-block:: python

	# Upload the file at /tmp/hello.txt
	project.upload_file('/tmp/hello.txt')

	# Upload the data 'Hello World!'
	file_spec = flywheel.FileSpec('hello.txt', 'Hello World!\n', 'text/plain')
	project.upload_file(file_spec)

	# Some endpoints allow multiple file uploads:
	analysis.upload_output(['/tmp/hello1.txt', '/tmp/hello2.txt'])

When downloading, you specify the destination file, or you can download directly to memory

.. code-block:: python

	# Download file to /tmp/hello.txt
	project.download_file('hello.txt', '/tmp/hello.txt')

	# Download file contents directly to memory
	data = project.read_file('hello.txt')

Working with Zip Members
++++++++++++++++++++++++
Occasionally you may want to see the contents of a zip file, and possibly download a single member without downloading
the entire zipfile. There are a few operations provided to enable this. For example:

.. code-block:: python

	# Get information about a zip file
	zip_info = acquisition.get_file_zip_info('my-archive.zip')

	# Download the first zip entry to /tmp/{entry_name}
	entry_name = zip_info.members[0].path
	out_path = os.path.join('/tmp', entry_name)
	acquisition.download_file_zip_member('my-archive.zip', entry_name, out_path)

	# Read the "readme.txt" zip entry directly to memory
	zip_data = acquisition.read_file_zip_member('my-archive.zip', 'readme.txt')


Handling Exceptions
-------------------
When an error is encountered while accessing an endpoint, an :class:`flywheel.rest.ApiException` is thrown. 
The ApiException will typically have a ``status`` which is the HTTP Status Code (e.g. 404) and a ``reason`` 
(e.g. Not Found).

For example:

.. code-block:: python

	try:
	  project = fw.get_project('NON_EXISTENT_ID')
	except flywheel.ApiException as e:
	  print('API Error: %d -- %s' % (e.status, e.reason))
