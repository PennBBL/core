%% Test methods in Flywheel.m
% Setup
% Before running this script, ensure the toolbox is installed
%   make sure you set SdkTestKey environment variable as user API key
%       for example: setenv('SdkTestKey', APIKEY)

% Create string to be used in testdrive
testString = '123235jakhf7sadf7v';

% Test Files
filename = 'test.txt';
fid = fopen(filename, 'w');
fprintf(fid, 'This is a test file');
fclose(fid);

filename2 = 'test2.txt';
fid = fopen(filename2, 'w');
fprintf(fid, 'This is a second test file');
fclose(fid);

% Define error message
errMsg = 'Strings not equal';

% Create client
apiKey = getenv('SdkTestKey');
assert(~isempty(apiKey));
fw = flywheel.Client(apiKey);

%% Users
disp('Testing Users')
user = fw.getCurrentUser();
assert(~isempty(user.id))

users = fw.getAllUsers();
assert(length(users) >= 1, 'No users returned')

% add a new user
email = strcat(testString, '@', testString, '.com');
userId = fw.addUser('id',email,'email',email,'firstname',testString,'lastname',testString);

% modify the new user
fw.modifyUser(userId, struct('firstname', 'John'));
user2 = fw.getUser(userId);
assert(strcmp(user2.email, email), errMsg)
assert(strcmp(user2.firstname,'John'), errMsg)

fw.deleteUser(userId);

%% Groups
disp('Testing Groups')

groupId = fw.addGroup('id',testString);
assert(strcmp(groupId, testString), errMsg);

fw.addGroupTag(groupId, 'blue');
fw.modifyGroup(groupId, struct('label','testdrive'));

groups = fw.getAllGroups();
assert(~isempty(groups))

group = fw.getGroup(groupId);
assert(strcmp(group.tags{1},'blue'), errMsg)
assert(strcmp(group.label,'testdrive'), errMsg)

%% Projects
disp('Testing Projects')

project = group.addProject('label', testString);
assert(strcmp(project.label, testString), errMsg)
projectId = project.id;

project.addTag('blue');
project.update('label', 'testdrive');
project.addNote('This is a note');

projects = fw.getAllProjects();
assert(~isempty(projects), errMsg)

project.uploadFile(filename);
projectDownloadFile = fullfile(tempdir, 'download.txt');
project.downloadFile(filename, projectDownloadFile);

project = project.reload();
assert(strcmp(project.tags{1},'blue'), errMsg)
assert(strcmp(project.label,'testdrive'), errMsg)
assert(strcmp(project.notes{1}.text, 'This is a note'), errMsg)
assert(strcmp(project.files{1}.name, filename), errMsg)
s = dir(projectDownloadFile);
assert(project.files{1}.size == s.bytes, errMsg)

projectDownloadUrl = project.files{1}.url;
assert(~strcmp(projectDownloadUrl, ''), errMsg)

%% Subjects
disp('Testing Subjects')

subject = project.addSubject('code', testString);
subjectId = subject.id;

fw.addSubjectTag(subjectId, 'blue');
fw.modifySubject(subjectId, struct('code', 'testdrive'));
fw.addSubjectNote(subjectId, 'This is a note');

subjects = fw.getProjectSubjects(projectId);
assert(~isempty(subjects), errMsg)

subjects = fw.getAllSubjects();
assert(~isempty(subjects), errMsg)

fw.uploadFileToSubject(subjectId, filename);
subjectDownloadFile = fullfile(tempdir, 'download2.txt');
fw.downloadFileFromSubject(subjectId, filename, subjectDownloadFile);

subject = fw.get(subjectId);
assert(strcmp(subject.tags{1}, 'blue'), errMsg)
assert(strcmp(subject.label, 'testdrive'), errMsg)
assert(strcmp(subject.notes{1}.text, 'This is a note'), errMsg)

subjectFile = subject.getFile(filename);
s = dir(subjectDownloadFile);
assert(subjectFile.size == s.bytes, errMsg)

subjectDownloadUrl = fw.getSubjectDownloadUrl(subjectId, filename);
assert(~strcmp(subjectDownloadUrl, ''), errMsg)

downloadNodes = { struct('level', 'subject', 'id', subjectId) };
summary = fw.createDownloadTicket(struct('optional', false, 'nodes', downloadNodes));
assert(~isempty(summary.ticket), errMsg)
subjectDownloadTar = fullfile(tempdir, 'subject-download.tar');
fw.downloadTicket(summary.ticket, subjectDownloadTar);
s = dir(subjectDownloadTar);
assert(s.bytes >= summary.size, errMsg)

%% Sessions
disp('Testing Sessions')

subjectAge = flywheel.Util.yearsToSeconds(35);
session = subject.addSession('label', testString, 'age', subjectAge);
sessionId = session.id;

fw.addSessionTag(sessionId, 'blue');
fw.modifySession(sessionId, struct('label', 'testdrive'));
fw.addSessionNote(sessionId, 'This is a note');

sessions = project.sessions();
assert(~isempty(sessions), errMsg)

sessions = fw.sessions();
assert(~isempty(sessions), errMsg)

fw.uploadFileToSession(sessionId, filename);
sessionDownloadFile = fullfile(tempdir, 'download2.txt');
fw.downloadFileFromSession(sessionId, filename, sessionDownloadFile);

session = fw.getSession(sessionId);
assert(strcmp(session.tags{1}, 'blue'), errMsg)
assert(strcmp(session.label, 'testdrive'), errMsg)
assert(strcmp(session.notes{1}.text, 'This is a note'), errMsg)
assert(strcmp(session.files{1}.name, filename), errMsg)
s = dir(sessionDownloadFile);
assert(session.files{1}.size == s.bytes, errMsg)
assert(session.ageYears == 35, errMsg)

sessionDownloadUrl = fw.getSessionDownloadUrl(sessionId, filename);
assert(~strcmp(sessionDownloadUrl, ''), errMsg)

sessionDownloadTar = fullfile(tempdir, 'session-download.tar');
summary = session.downloadTar(sessionDownloadTar);
s = dir(sessionDownloadTar);
assert(s.bytes >= summary.size, errMsg)

% Session Analysis
analysis = session.addAnalysis('label', 'testdrive', ...
    'inputs', { session.files{1}.ref() });
analysisId = analysis.id;

analysis.uploadOutput(filename2);

analysis = analysis.reload();
assert(strcmp(analysis.label, 'testdrive'), errMsg);

assert(strcmp(analysis.inputs{1}.name, filename), errMsg);
assert(strcmp(analysis.files{1}.name, filename2), errMsg);

%% Acquisitions
disp('Testing Acquisitions')

acq = session.addAcquisition(struct('label', testString));
acqId = acq.id;

fw.addAcquisitionTag(acqId, 'blue');
fw.modifyAcquisition(acqId, struct('label', 'testdrive'));
fw.addAcquisitionNote(acqId, 'This is a note');

acqs = session.acquisitions();
assert(~isempty(acqs), errMsg)

acqs = fw.acquisitions();
assert(~isempty(acqs), errMsg)

fw.uploadFileToAcquisition(acqId, filename);
acquisitionDownloadFile = fullfile(tempdir, 'download3.txt');
fw.downloadFileFromAcquisition(acqId, filename, acquisitionDownloadFile);

acq = fw.getAcquisition(acqId);
assert(strcmp(acq.tags{1},'blue'), errMsg)
assert(strcmp(acq.label,'testdrive'), errMsg)
assert(strcmp(acq.notes{1}.text, 'This is a note'), errMsg)
assert(strcmp(acq.files{1}.name, filename), errMsg)
s = dir(acquisitionDownloadFile);
assert(acq.files{1}.size == s.bytes, errMsg)

acqDownloadUrl = fw.getAcquisitionDownloadUrl(acqId, filename);
assert(~strcmp(acqDownloadUrl, ''), errMsg)

acqFile = acq.files{1};

% Update file modality and type
acqFile.update('modality', 'modality', 'type', 'type');

acq = acq.reload();
acqFile = acq.files{1};
assert(strcmp(acqFile.modality, 'modality'), errMsg);
assert(strcmp(acqFile.type, 'type'), errMsg);

% Test classification functions
acqFile.replaceClassification('classification', ...
    struct('Custom', {{'measurement1', 'measurement2'}}), ...
    'modality', 'modality2');

acq = acq.reload();
acqFile = acq.files{1};
assert(strcmp(acqFile.modality, 'modality2'));
assert(strcmp(acqFile.classification.Custom{1}, 'measurement1'), errMsg);
assert(strcmp(acqFile.classification.Custom{2}, 'measurement2'), errMsg);

acqFile.updateClassification(struct('Custom', {{'HelloWorld'}}));
acqFile.deleteClassification(struct('Custom', {{'measurement2'}}));

acq = acq.reload();
acqFile = acq.files{1};
assert(strcmp(acqFile.classification.Custom{1}, 'measurement1'), errMsg);
assert(strcmp(acqFile.classification.Custom{2}, 'HelloWorld'), errMsg);

% Test file info
acqFile.replaceInfo(struct('a', 1, 'b', 2, 'c', 3, 'd', 4));
acqFile.updateInfo('c', 5);

acq = acq.reload();
acqFile = acq.files{1};
assert(acqFile.info.a == 1, errMsg);
assert(acqFile.info.b == 2, errMsg);
assert(acqFile.info.c == 5, errMsg);
assert(acqFile.info.d == 4, errMsg);

acqFile.deleteInfo({{'c', 'd'}});
acq = acq.reload();
acqFile = acq.files{1};
assert(acqFile.info.a == 1, errMsg);
assert(acqFile.info.b == 2, errMsg);
assert(~isfield(acqFile.info, 'c'), errMsg);
assert(~isfield(acqFile.info, 'd'), errMsg);

%% Collections
disp('Testing Collections')

colId = fw.addCollection(struct('label', testString));
collection = fw.getCollection(colId);

collSessions = collection.sessions();
assert(isempty(collSessions), errMsg)

collAqs = collection.acquisitions();
assert(isempty(collAqs), errMsg)

collection.addSessions(sessionId);
collection.addAcquisitions(acqId);

collSessions = collection.sessions();
assert(~isempty(collSessions), errMsg)

collAqs = collection.acquisitions();
assert(~isempty(collAqs), errMsg)

collection.addNote('This is a note');

collection.uploadFile(filename);
collectionDownloadFile = fullfile(tempdir, 'download4.txt');
collection.downloadFile(filename, collectionDownloadFile);

collection = collection.reload();
assert(strcmp(collection.notes{1}.text, 'This is a note'), errMsg)
assert(strcmp(collection.files{1}.name, filename), errMsg)
s = dir(collectionDownloadFile);
collFile = collection.files{1};
assert(collFile.size == s.bytes, errMsg)

colDownloadUrl = collFile.url;
assert(~strcmp(colDownloadUrl, ''), errMsg)

collection.deleteFile(filename);

collection = collection.reload();
assert(isempty(collection.files), errMsg)

%% Gears
disp('Testing Gears')

gearId = fw.addGear('test-drive-gear', struct(...
        'category','converter',...
        'exchange', struct(...
            'gitCommit','example',...
            'rootfsHash','sha384:example',...
            'rootfsUrl','https://example.example'...
        ),...
        'gear', struct(...
            'name','test-drive-gear',...
            'label','Test Drive Gear',...
            'version','3',...
            'author','None',...
            'description','An empty example gear',...
            'license','Other',...
            'source','http://example.example',...
            'url','http://example.example',...
            'inputs', struct(...
                'x', struct('base','file')...
            )...
        )));

gear = fw.getGear(gearId);
assert(strcmp(gear.gear.name, 'test-drive-gear'), errMsg)

gears = fw.getAllGears();
assert(~isempty(gears), errMsg)

jobId = gear.run('x', acqFile);

job = fw.getJob(jobId);
assert(strcmp(job.gearId,gearId), errMsg)

logs = fw.getJobLogs(jobId);
% Likely will not have anything in them yet

%% Batch proposal

proposal = gear.proposeBatch(session.acquisitions());
assert(1 == numel(proposal.matched));

jobs = proposal.run();
assert(1 == numel(jobs));

assert(strcmp(jobs{1}.gearId, gearId), errMsg);


%% Analysis Job
disp('Testing Analysis Job')

analysisGearId = fw.addGear('test-drive-analysis-gear', struct(...
        'category','analysis',...
        'exchange', struct(...
            'gitCommit','example',...
            'rootfsHash','sha384:example',...
            'rootfsUrl','https://example.example'...
        ),...
        'gear', struct(...
            'name','test-drive-analysis-gear',...
            'label','Test Drive Analysis Gear',...
            'version','3',...
            'author','None',...
            'description','An empty example gear',...
            'license','Other',...
            'source','http://example.example',...
            'url','http://example.example',...
            'config', struct(...
              'y', struct('type', 'string', 'default', 'z')...  
            ),...
            'inputs', struct(...
                'x', struct('base','file')...
            )...
        )));

analysisGear = fw.getGear(analysisGearId);

jobAnalysisId = analysisGear.run('config', struct('y', 'a'), ...
    'destination', session, 'x', acq.files{1});

jobAnalysis = fw.getAnalysis(jobAnalysisId);
assert(startsWith(jobAnalysis.label, 'test-drive-analysis-gear'));

assert(strcmp(analysis.inputs{1}.name, acq.files{1}.name), errMsg);
assert(strcmp(analysis.parent.type, 'session'), errMsg);
assert(strcmp(analysis.parent.id, sessionId), errMsg);

%% Containers
disp('Testing Abstract Containers')
cgroup = fw.getContainer(groupId);
assert(strcmp(group.id, cgroup.id), errMsg)

cproject = fw.getContainer(projectId);
assert(strcmp(project.id, cproject.id), errMsg)
assert(strcmp(project.label, cproject.label), errMsg)

csession = fw.getContainer(sessionId);
assert(strcmp(session.id, csession.id), errMsg)
assert(strcmp(session.label, csession.label), errMsg)

cacq = fw.getContainer(acqId);
assert(strcmp(acq.id, cacq.id), errMsg)
assert(strcmp(acq.label, cacq.label), errMsg)

fw.modifyContainer(acqId, struct('label', 'testdrive'));
cacq = fw.getContainer(acqId);
acq = fw.getAcquisition(acqId);
assert(strcmp(cacq.label,'testdrive'), errMsg)
assert(strcmp(acq.label,'testdrive'), errMsg)

fw.uploadFileToContainer(acqId, filename);
acquisitionDownloadFile = fullfile(tempdir, 'download3.txt');
fw.downloadFileFromContainer(acqId, filename, acquisitionDownloadFile);

acq = fw.getContainer(acqId);
assert(strcmp(acq.tags{1},'blue'), errMsg)
assert(strcmp(acq.label,'testdrive'), errMsg)
assert(strcmp(acq.notes{1}.text, 'This is a note'), errMsg)

acqFiles = acq.getFiles();
assert(strcmp(acqFiles{1}.name, filename), errMsg)
s = dir(acquisitionDownloadFile);
assert(acqFiles{1}.size == s.bytes, errMsg)

acqDownloadUrl = fw.getContainerDownloadUrl(acqId, filename);
assert(~strcmp(acqDownloadUrl, ''), errMsg)

%% Misc
disp('Testing Misc')

config = fw.getConfig();
assert(~isempty(config), errMsg)

fwVersion = fw.getVersion();
assert(fwVersion.database >= 25, errMsg)

%% Cleanup
disp('Cleanup')

fw.deleteCollection(colId);
fw.deleteSessionAnalysis(sessionId, jobAnalysisId);
fw.deleteAcquisition(acqId);
fw.deleteSession(sessionId);
fw.deleteProject(projectId);
fw.deleteGroup(groupId);
fw.deleteGear(gearId);
fw.deleteGear(analysisGearId);

delete(filename, filename2);

disp('')
disp('Test drive complete.')



