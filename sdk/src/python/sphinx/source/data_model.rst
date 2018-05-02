Data Model
**********

Hierarchy
---------
Data in a Flywheel system is organized in a tree-like hierarchy, as indicated in the following diagram.

.. image:: /../../../static/images/data-model.png

- :class:`flywheel.models.user.User` - An authorized entity, usually referenced by email address.
- :class:`flywheel.models.group.Group` - A grouping of users and projects.
- :class:`flywheel.models.project.Project` - A project represents a grouping of subjects and sessions, e.g. within a study.
- :class:`flywheel.models.subject.Subject` - An individual under study.
- :class:`flywheel.models.session.Session` - A grouping of acquired data, typically data acquired within a limited timeframe.
- :class:`flywheel.models.acquisition.Acquisition` - A set of one or more files, typically acquired as part of the same process, at the same time.
- :class:`flywheel.models.analysis_output.AnalysisOutput` - A set of one or more derivative files from analyzing files after they have been acquired.

.. _data-model-permissions:

Permissions
-----------
Permissions in Flywheel are managed at the Group and Project level. Users that belong to a Group or a Project have a 
Role, which is one of: 

- **Admin** (``admin``) - Administrators can perform administrative-level actions such as setting permissions or creating and deleting projects.
- **Read-Write** (``rw``) - Users can read, create and delete data, but cannot assign permissions or delete entire projects.
- **Read-Only** (``ro``) - Users can only read data

By default when a new Project is created belonging to a Group, permissions will be copied from the Group to the Project, keeping
user roles intact. From that point on, permissions for that Project must be managed at that project, changes made to the Group
will not propagate to the project.

.. code-block:: python

	from pprint import pprint

	# See project permissions
	project = fw.get_project(project_id)
	pprint(project.permissions)

	# Add permission to a project
	fw.add_project_permission(project_id, flywheel.Permission('justinehlert@flywheel.io', 'ro'))

	# Remove permission from a project
	fw.delete_project_user_permission(project_id, 'justinehlert@flywheel.io')

.. _data-model-containers:

Containers
----------
Projects, Subjects, Sessions, Acquisitions and Analyses are all different types of *Containers*. Containers in Flywheel all support 
the following features:

Tags
++++
Tags are concise labels that provide descriptive metadata that can be searched on. Available tags are managed on the Group.

.. code-block:: python

	# See tags on a session
	session = fw.get_session(session_id)
	print(', '.join(session.tags))

	# Add a tag to a session
	fw.add_session_tag(session_id, 'Control')

	# Remove a tag from a session
	fw.delete_session_tag(session_id, 'Analysis Required')

Notes
+++++
Notes are user-entered, human readable metadata attached to a container. They are timestamped and attributed to the user that entered them.

.. code-block:: python

	from pprint import pprint

	# See notes on a session
	session = fw.get_session(session_id)
	pprint(session.notes)

	# Add a note to a session
	fw.add_session_note(session_id, 'This is a note')

	# Delete a note from a session
	fw.delete_session_note(session_id, session.notes[0].id)

Info
++++

Info is free-form JSON metadata associated with a container or file.

.. code-block:: python

	from pprint import pprint

	# Print the info for an acquisition
	acquisition = fw.get_acquisition(acquisition_id)
	pprint(acquisition.info)

	# Replace the entire contents of acquisition info
	fw.replace_acquisition_info(acquisition_id, { 'splines': 34 })

	# Add additional fields to acquisition info
	fw.set_acquisition_info(acquisition_id, { 'curve': 'bezier' })

	# Delete fields from acquisition info
	fw.delete_acquisition_info_fields(acquisition_id, ['splines'])

Files
+++++
Files are a set of file attachments associated with a container. See also :ref:`dealing-with-files`.

.. code-block:: python

	from pprint import pprint

	# List files on an acquisition
	acquisition = fw.get_acquisition(acquisition_id)

	for f in acquisition.files:
	  print('Name: %s, type: %s' % (f.name, f.type))

	# Upload a file to an acquisition
	fw.upload_file_to_acquisition(acquisition_id, '/path/to/file.txt')

	# Download a file to disk
	fw.download_file_from_acquisition(acquisition_id, 'file.txt', '/path/to/file.txt')

	# Files can also have metadata
	pprint(acquisition.files[0].info)

	fw.replace_acquisition_file_info(acquisition_id, 'file.txt', {'wordCount': 327})
