Examples
********
This page provides some brief, minimal examples for common tasks with the SDK.

Groups
======
For managing permissions, see :ref:`data-model-permissions`.

Add Group
---------
Create a new group, with an id of ``my_group`` and a label of ``My Test Group``:

.. code-block:: matlab

	groupId = fw.addGroup(struct('id', 'my_group', 'label', 'My Test Group'));


List Groups
-----------
List all groups that I have access to:

.. code-block:: matlab

	groups = fw.getAllGroups();

	for i = 1:numel(groups) 
	  fprintf('%s: %s\n', groups{i}.id, groups{i}.label);
	end

Modify Group Tags
-----------------
Add tags named ``Control`` and ``Study`` to a group identified by ``groupId``.

.. code-block:: matlab

	fw.addGroupTag(groupId, 'Control');
	fw.addGroupTag(groupId, 'Study');

	group = fw.getGroup(groupId);
	fprintf('%s\n', strjoin(group.tags, ', '));

List Projects in Group
----------------------
List all of the projects belonging to group identified by ``groupId``.

.. code-block:: matlab

	projects = fw.getGroupProjects(groupId);

	for i = 1:numel(projects) 
	  fprintf('%s: %s\n', projects{i}.id, projects{i}.label);
	end

Projects
========
For managing tags, files, notes or info, see :ref:`data-model-containers`.

For managing permissions, see :ref:`data-model-permissions`.

Add Project
-----------
Create a new project that belongs to ``groupId`` with a label of ``My Test Project``.

.. code-block:: matlab

	projectId = fw.addProject(struct('group', groupId, 'label', 'My Test Project'));

List Projects
-------------
List all of the projects that I have access to:

.. code-block:: matlab

	projects = fw.getAllProjects();

	for i = 1:numel(projects) 
	  fprintf('%s: %s\n', projects{i}.id, projects{i}.label);
	end

List Sessions in Project
------------------------
List all of the sessions belonging to project identified by ``projectId``.

.. code-block:: matlab

	sessions = fw.getProjectSessions(projectId);

	for i = 1:numel(sessions) 
	  fprintf('%s: %s\n', sessions{i}.id, sessions{i}.label);
	end


Sessions
========
For managing tags, files, notes or info, see :ref:`data-model-containers`.

Add Session
-----------
Create a new session that belongs to ``projectId`` with a label of ``Session 01``.

.. code-block:: matlab

	sessionId = fw.addSession(struct('project', projectId, 'label', 'Session 01'));

List Sessions
-------------
List all of the sessions that I have access to:

.. code-block:: matlab

	sessions = fw.getAllSessions();

	for i = 1:numel(sessions) 
	  fprintf('%s: %s\n', sessions{i}.id, sessions{i}.label);
	end

List Acquisitions in Session
----------------------------
List all of the acquisitions belonging to session identified by ``sessionId``.

.. code-block:: matlab

	acquisitions = fw.getSessionAcquisitions(sessionId);

	for i = 1:numel(acquisitions) 
	  fprintf('%s: %s\n', acquisitions{i}.id, acquisitions{i}.label);
	end

Acquisitions
============
For managing tags, files, notes or info, see :ref:`data-model-containers`.

For uploading and downloading files, see :ref:`dealing-with-files`.

Add Acquisition
---------------
Create a new acquisition that belongs to ``sessionId`` with a label of ``Localizer``,
and upload a file.

.. code-block:: matlab

	acquisitionId = fw.addAcquisition(struct('session', sessionId, 'label', 'Localizer'));

	fw.uploadFileToAcquisition(acquisitionId, 'localizer.nii.gz');

List Acquisitions
-----------------
List all of the acquisitions that I have access to:
(Not recommended)

.. code-block:: matlab

	acquisitions = fw.getAllAcquisitions();

	for i = 1:numel(acquisitions) 
	  fprintf('%s: %s\n', acquisitions{i}.id, acquisitions{i}.label);
	end

List Files in Acquisition
-------------------------
List all of the files on an acquisition identified by ``acquisitionId``.

.. code-block:: matlab

	acquisition = fw.getAcquisition(acquisitionId);

	for i = 1:numel(acquisition.files) 
	  fprintf('%s: %s\n', acquisition.files{i}.name);
	end


Analyses
========
NOTE: Analyses are available on Projects, Subjects, Sessions and Acquisitions.

For managing tags, files, notes or info, see :ref:`data-model-containers`.

For uploading and downloading files, see :ref:`dealing-with-files`.


Add Analysis
------------
Create a new analysis on session identified by ``sessionId`` referencing an input file from an 
acquisition, then upload a file.

.. code-block:: matlab

	file_ref = struct('id', acquisitionId, 'type', 'acquisition', 'name', 'localizer.nii.gz');
	analysis = struct('label', 'Localizer Analysis', 'inputs', {{file_ref}});

	analysisId = fw.addSessionAnalysis(sessionId, analysis);

	fw.uploadOutputToAnalysis(analysisId, 'my-analysis.csv');

List Session Analyses
---------------------
List all of the analyses belonging to session identified by ``sessionId``.

.. code-block:: matlab

	analyses = fw.getSessionAnalyses(sessionId);

	for i = 1:numel(analyses) 
	  fprintf('%s: %s\n', analyses{i}.id, analyses{i}.label);
	end
