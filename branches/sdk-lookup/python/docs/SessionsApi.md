# flywheel.SessionsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_session**](SessionsApi.md#add_session) | **POST** /sessions | Create a new session
[**add_session_analysis**](SessionsApi.md#add_session_analysis) | **POST** /sessions/{SessionId}/analyses | Create an analysis and upload files.
[**add_session_analysis_note**](SessionsApi.md#add_session_analysis_note) | **POST** /sessions/{SessionId}/analyses/{AnalysisId}/notes | Add a note to session analysis.
[**add_session_note**](SessionsApi.md#add_session_note) | **POST** /sessions/{SessionId}/notes | Add a note to session.
[**add_session_tag**](SessionsApi.md#add_session_tag) | **POST** /sessions/{SessionId}/tags | Add a tag to session.
[**delete_session**](SessionsApi.md#delete_session) | **DELETE** /sessions/{SessionId} | Delete a session
[**delete_session_analysis**](SessionsApi.md#delete_session_analysis) | **DELETE** /sessions/{SessionId}/analyses/{AnalysisId} | Delete an anaylsis
[**delete_session_analysis_note**](SessionsApi.md#delete_session_analysis_note) | **DELETE** /sessions/{SessionId}/analyses/{AnalysisId}/notes/{NoteId} | Remove a note from session analysis.
[**delete_session_file**](SessionsApi.md#delete_session_file) | **DELETE** /sessions/{SessionId}/files/{FileName} | Delete a file
[**delete_session_note**](SessionsApi.md#delete_session_note) | **DELETE** /sessions/{SessionId}/notes/{NoteId} | Remove a note from session
[**delete_session_tag**](SessionsApi.md#delete_session_tag) | **DELETE** /sessions/{SessionId}/tags/{TagValue} | Delete a tag
[**download_file_from_session**](SessionsApi.md#download_file_from_session) | **GET** /sessions/{SessionId}/files/{FileName} | Download a file.
[**get_session_download_ticket**](SessionsApi.md#get_session_download_ticket) | **GET** /sessions/{SessionId}/files/{FileName} | Download a file.
[**download_session_analysis_inputs**](SessionsApi.md#download_session_analysis_inputs) | **GET** /sessions/{SessionId}/analyses/{AnalysisId}/inputs | Download analysis inputs.
[**download_session_analysis_inputs_by_filename**](SessionsApi.md#download_session_analysis_inputs_by_filename) | **GET** /sessions/{SessionId}/analyses/{AnalysisId}/inputs/{Filename} | Download anaylsis inputs with filter.
[**download_session_analysis_outputs**](SessionsApi.md#download_session_analysis_outputs) | **GET** /sessions/{SessionId}/analyses/{AnalysisId}/files | Download analysis outputs.
[**download_session_analysis_outputs_by_filename**](SessionsApi.md#download_session_analysis_outputs_by_filename) | **GET** /sessions/{SessionId}/analyses/{AnalysisId}/files/{Filename} | Download anaylsis outputs with filter.
[**get_all_sessions**](SessionsApi.md#get_all_sessions) | **GET** /sessions | Get a list of sessions
[**get_session**](SessionsApi.md#get_session) | **GET** /sessions/{SessionId} | Get a single session
[**get_session_acquisitions**](SessionsApi.md#get_session_acquisitions) | **GET** /sessions/{SessionId}/acquisitions | List acquisitions in a session
[**get_session_analyses**](SessionsApi.md#get_session_analyses) | **GET** /sessions/{SessionId}/analyses | Get analyses for session.
[**get_session_analysis**](SessionsApi.md#get_session_analysis) | **GET** /sessions/{SessionId}/analyses/{AnalysisId} | Get an analysis.
[**get_session_file_info**](SessionsApi.md#get_session_file_info) | **GET** /sessions/{SessionId}/files/{FileName}/info | Get info for a particular file.
[**get_session_jobs**](SessionsApi.md#get_session_jobs) | **GET** /sessions/{SessionId}/jobs | Return any jobs that use inputs from this session
[**get_session_note**](SessionsApi.md#get_session_note) | **GET** /sessions/{SessionId}/notes/{NoteId} | Get a note on session.
[**get_session_tag**](SessionsApi.md#get_session_tag) | **GET** /sessions/{SessionId}/tags/{TagValue} | Get the value of a tag, by name.
[**modify_session**](SessionsApi.md#modify_session) | **PUT** /sessions/{SessionId} | Update a session
[**modify_session_file**](SessionsApi.md#modify_session_file) | **PUT** /sessions/{SessionId}/files/{FileName} | Modify a file&#39;s attributes
[**modify_session_file_info**](SessionsApi.md#modify_session_file_info) | **POST** /sessions/{SessionId}/files/{FileName}/info | Update info for a particular file.
[**modify_session_info**](SessionsApi.md#modify_session_info) | **POST** /sessions/{SessionId}/info | Update or replace info for a session.
[**modify_session_note**](SessionsApi.md#modify_session_note) | **PUT** /sessions/{SessionId}/notes/{NoteId} | Update a note on session.
[**rename_session_tag**](SessionsApi.md#rename_session_tag) | **PUT** /sessions/{SessionId}/tags/{TagValue} | Rename a tag.
[**replace_session_file**](SessionsApi.md#replace_session_file) | **POST** /sessions/{SessionId}/files/{FileName} | Replace a file
[**upload_file_to_session**](SessionsApi.md#upload_file_to_session) | **POST** /sessions/{SessionId}/files | Upload a file to session.


# **add_session**
> ContainerNewOutput add_session(body)

Create a new session

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
body = flywheel.Session() # Session | 

try:
    # Create a new session
    api_response = api_instance.add_session(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->add_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Session**](Session.md)|  | 

### Return type

[**ContainerNewOutput**](ContainerNewOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_session_analysis**
> ContainerNewOutput add_session_analysis(session_id, body, job=job)

Create an analysis and upload files.

When query param \"job\" is \"true\", send JSON to create an analysis and job.  Otherwise, multipart/form-data to upload files and create an analysis. 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
body = flywheel.AnalysisInputAny() # AnalysisInputAny | 
job = true # bool | Return job as an object instead of an id (optional)

try:
    # Create an analysis and upload files.
    api_response = api_instance.add_session_analysis(session_id, body, job=job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->add_session_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **body** | [**AnalysisInputAny**](AnalysisInputAny.md)|  | 
 **job** | **bool**| Return job as an object instead of an id | [optional] 

### Return type

[**ContainerNewOutput**](ContainerNewOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json, multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_session_analysis_note**
> InlineResponse2001 add_session_analysis_note(session_id, analysis_id, body)

Add a note to session analysis.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Add a note to session analysis.
    api_response = api_instance.add_session_analysis_note(session_id, analysis_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->add_session_analysis_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **body** | [**Note**](Note.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_session_note**
> InlineResponse2001 add_session_note(session_id, body)

Add a note to session.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Add a note to session.
    api_response = api_instance.add_session_note(session_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->add_session_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **body** | [**Note**](Note.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_session_tag**
> InlineResponse2001 add_session_tag(session_id, body)

Add a tag to session.

Progates changes to projects, sessions and acquisitions

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
body = flywheel.Tag() # Tag | 

try:
    # Add a tag to session.
    api_response = api_instance.add_session_tag(session_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->add_session_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **body** | [**Tag**](Tag.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session**
> InlineResponse200 delete_session(session_id)

Delete a session

Read-write project permissions are required to delete a session. </br>Admin project permissions are required if the session or it's acquisitions contain data uploaded by sources other than users and jobs.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 

try:
    # Delete a session
    api_response = api_instance.delete_session(session_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->delete_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session_analysis**
> InlineResponse200 delete_session_analysis(session_id, analysis_id)

Delete an anaylsis

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 

try:
    # Delete an anaylsis
    api_response = api_instance.delete_session_analysis(session_id, analysis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->delete_session_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session_analysis_note**
> InlineResponse2001 delete_session_analysis_note(session_id, analysis_id, note_id)

Remove a note from session analysis.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Remove a note from session analysis.
    api_response = api_instance.delete_session_analysis_note(session_id, analysis_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->delete_session_analysis_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session_file**
> InlineResponse2001 delete_session_file(session_id, file_name)

Delete a file

A user with read-write or higher permissions on the container may delete files that were uploaded by users or were the output of jobs. (Specifically, files whose `origin.type` is either `job` or `user`.) <br/> A user with admin permissions on the container may delete any file. 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Delete a file
    api_response = api_instance.delete_session_file(session_id, file_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->delete_session_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session_note**
> InlineResponse2001 delete_session_note(session_id, note_id)

Remove a note from session

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Remove a note from session
    api_response = api_instance.delete_session_note(session_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->delete_session_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_session_tag**
> InlineResponse2001 delete_session_tag(session_id, tag_value)

Delete a tag

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Delete a tag
    api_response = api_instance.delete_session_tag(session_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->delete_session_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_file_from_session**
> DownloadTicket download_file_from_session(session_id, file_name, view=view, info=info, member=member)

Download a file.

Files can be downloaded directly from this endpoint with a valid \"Authorization\" header or via a ticket id.  To generate a ticket:   - Make a request with an empty \"ticket\" parameter and a valid \"Authorization\" header. The server will respond with a generated ticket id.   - Make another request with the received ticket id in the \"ticket\" parameter. A valid \"Authorization\" header is no longer required.  When \"view\" is true, [RFC7233](https://tools.ietf.org/html/rfc7233) range request headers are supported. 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 
view = false # bool | If true, the proper \"Content-Type\" header based on the file's mimetype is set on response If false, the \"Content-Type\" header is set to \"application/octet-stream\"  (optional) (default to false)
info = false # bool | If the file is a zipfile, return a json response of zipfile member information (optional) (default to false)
member = 'member_example' # str | The filename of a zipfile member to download rather than the entire file (optional)

try:
    # Download a file.
    api_response = api_instance.download_file_from_session(session_id, file_name, view=view, info=info, member=member)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->download_file_from_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 
 **view** | **bool**| If true, the proper \&quot;Content-Type\&quot; header based on the file&#39;s mimetype is set on response If false, the \&quot;Content-Type\&quot; header is set to \&quot;application/octet-stream\&quot;  | [optional] [default to false]
 **info** | **bool**| If the file is a zipfile, return a json response of zipfile member information | [optional] [default to false]
 **member** | **str**| The filename of a zipfile member to download rather than the entire file | [optional] 

### Return type

[**DownloadTicket**](DownloadTicket.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_download_ticket**
> DownloadTicket get_session_download_ticket(session_id, file_name, ticket=ticket, view=view, info=info, member=member)

Download a file.

Files can be downloaded directly from this endpoint with a valid \"Authorization\" header or via a ticket id.  To generate a ticket:   - Make a request with an empty \"ticket\" parameter and a valid \"Authorization\" header. The server will respond with a generated ticket id.   - Make another request with the received ticket id in the \"ticket\" parameter. A valid \"Authorization\" header is no longer required.  When \"view\" is true, [RFC7233](https://tools.ietf.org/html/rfc7233) range request headers are supported. 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 
ticket = 'ticket_example' # str | The generated ticket id for the download, or present but empty to generate a ticket id (optional)
view = false # bool | If true, the proper \"Content-Type\" header based on the file's mimetype is set on response If false, the \"Content-Type\" header is set to \"application/octet-stream\"  (optional) (default to false)
info = false # bool | If the file is a zipfile, return a json response of zipfile member information (optional) (default to false)
member = 'member_example' # str | The filename of a zipfile member to download rather than the entire file (optional)

try:
    # Download a file.
    api_response = api_instance.get_session_download_ticket(session_id, file_name, ticket=ticket, view=view, info=info, member=member)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_download_ticket: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 
 **ticket** | **str**| The generated ticket id for the download, or present but empty to generate a ticket id | [optional] 
 **view** | **bool**| If true, the proper \&quot;Content-Type\&quot; header based on the file&#39;s mimetype is set on response If false, the \&quot;Content-Type\&quot; header is set to \&quot;application/octet-stream\&quot;  | [optional] [default to false]
 **info** | **bool**| If the file is a zipfile, return a json response of zipfile member information | [optional] [default to false]
 **member** | **str**| The filename of a zipfile member to download rather than the entire file | [optional] 

### Return type

[**DownloadTicket**](DownloadTicket.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_session_analysis_inputs**
> AnalysisFilesCreateTicketOutput download_session_analysis_inputs(session_id, analysis_id, ticket=ticket)

Download analysis inputs.

If \"ticket\" query param is included and not empty, download inputs. If \"ticket\" query param is included and empty, create a ticket for all inputs in the anlaysis If no \"ticket\" query param is included, server error 500 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download analysis inputs.
    api_response = api_instance.download_session_analysis_inputs(session_id, analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->download_session_analysis_inputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **ticket** | **str**| ticket id of the inputs to download | [optional] 

### Return type

[**AnalysisFilesCreateTicketOutput**](AnalysisFilesCreateTicketOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_session_analysis_inputs_by_filename**
> AnalysisFilesCreateTicketOutput download_session_analysis_inputs_by_filename(session_id, analysis_id, filename, ticket=ticket)

Download anaylsis inputs with filter.

If \"ticket\" query param is included and not empty, download inputs. If \"ticket\" query param is included and empty, create a ticket for matching inputs in the anlaysis. If no \"ticket\" query param is included, inputs will be downloaded directly. 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select inputs for download
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download anaylsis inputs with filter.
    api_response = api_instance.download_session_analysis_inputs_by_filename(session_id, analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->download_session_analysis_inputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **filename** | **str**| regex to select inputs for download | 
 **ticket** | **str**| ticket id of the inputs to download | [optional] 

### Return type

[**AnalysisFilesCreateTicketOutput**](AnalysisFilesCreateTicketOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_session_analysis_outputs**
> AnalysisFilesCreateTicketOutput download_session_analysis_outputs(session_id, analysis_id, ticket=ticket)

Download analysis outputs.

If \"ticket\" query param is included and not empty, download outputs. If \"ticket\" query param is included and empty, create a ticket for all outputs in the anlaysis If no \"ticket\" query param is included, server error 500 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download analysis outputs.
    api_response = api_instance.download_session_analysis_outputs(session_id, analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->download_session_analysis_outputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **ticket** | **str**| ticket id of the outputs to download | [optional] 

### Return type

[**AnalysisFilesCreateTicketOutput**](AnalysisFilesCreateTicketOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_session_analysis_outputs_by_filename**
> AnalysisFilesCreateTicketOutput download_session_analysis_outputs_by_filename(session_id, analysis_id, filename, ticket=ticket)

Download anaylsis outputs with filter.

If \"ticket\" query param is included and not empty, download outputs. If \"ticket\" query param is included and empty, create a ticket for matching outputs in the anlaysis. If no \"ticket\" query param is included, outputs will be downloaded directly. 

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select outputs for download
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download anaylsis outputs with filter.
    api_response = api_instance.download_session_analysis_outputs_by_filename(session_id, analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->download_session_analysis_outputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **filename** | **str**| regex to select outputs for download | 
 **ticket** | **str**| ticket id of the outputs to download | [optional] 

### Return type

[**AnalysisFilesCreateTicketOutput**](AnalysisFilesCreateTicketOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_sessions**
> list[Session] get_all_sessions()

Get a list of sessions

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))

try:
    # Get a list of sessions
    api_response = api_instance.get_all_sessions()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_all_sessions: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Session]**](Session.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session**
> Session get_session(session_id)

Get a single session

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 

try:
    # Get a single session
    api_response = api_instance.get_session(session_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

[**Session**](Session.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_acquisitions**
> list[Acquisition] get_session_acquisitions(session_id)

List acquisitions in a session

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 

try:
    # List acquisitions in a session
    api_response = api_instance.get_session_acquisitions(session_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_acquisitions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

[**list[Acquisition]**](Acquisition.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_analyses**
> list[AnalysisListEntry] get_session_analyses(session_id)

Get analyses for session.

Returns analyses that directly belong to this resource.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 

try:
    # Get analyses for session.
    api_response = api_instance.get_session_analyses(session_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_analyses: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 

### Return type

[**list[AnalysisListEntry]**](AnalysisListEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_analysis**
> AnalysisOutput get_session_analysis(session_id, analysis_id, inflate_job=inflate_job)

Get an analysis.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
inflate_job = true # bool | Return job as an object instead of an id (optional)

try:
    # Get an analysis.
    api_response = api_instance.get_session_analysis(session_id, analysis_id, inflate_job=inflate_job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **analysis_id** | **str**|  | 
 **inflate_job** | **bool**| Return job as an object instead of an id | [optional] 

### Return type

[**AnalysisOutput**](AnalysisOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_file_info**
> FileEntry get_session_file_info(session_id, file_name)

Get info for a particular file.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Get info for a particular file.
    api_response = api_instance.get_session_file_info(session_id, file_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_file_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

[**FileEntry**](FileEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_jobs**
> SessionJobsOutput get_session_jobs(session_id, states=states, tags=tags)

Return any jobs that use inputs from this session

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
states = 'states_example' # str | filter results by job state (optional)
tags = 'tags_example' # str | filter results by job tags (optional)

try:
    # Return any jobs that use inputs from this session
    api_response = api_instance.get_session_jobs(session_id, states=states, tags=tags)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_jobs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **states** | **str**| filter results by job state | [optional] 
 **tags** | **str**| filter results by job tags | [optional] 

### Return type

[**SessionJobsOutput**](SessionJobsOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_note**
> Note get_session_note(session_id, note_id)

Get a note on session.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Get a note on session.
    api_response = api_instance.get_session_note(session_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**Note**](Note.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_tag**
> Tag get_session_tag(session_id, tag_value)

Get the value of a tag, by name.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Get the value of a tag, by name.
    api_response = api_instance.get_session_tag(session_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->get_session_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**Tag**](Tag.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_session**
> InlineResponse2001 modify_session(session_id, body)

Update a session

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
body = flywheel.Session() # Session | 

try:
    # Update a session
    api_response = api_instance.modify_session(session_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->modify_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **body** | [**Session**](Session.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_session_file**
> InlineResponse2003 modify_session_file(session_id, file_name, body)

Modify a file's attributes

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 
body = flywheel.FileEntry() # FileEntry | 

try:
    # Modify a file's attributes
    api_response = api_instance.modify_session_file(session_id, file_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->modify_session_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 
 **body** | [**FileEntry**](FileEntry.md)|  | 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_session_file_info**
> InlineResponse2001 modify_session_file_info(session_id, file_name, body)

Update info for a particular file.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 
body = flywheel.InfoUpdateInput() # InfoUpdateInput | 

try:
    # Update info for a particular file.
    api_response = api_instance.modify_session_file_info(session_id, file_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->modify_session_file_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 
 **body** | [**InfoUpdateInput**](InfoUpdateInput.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_session_info**
> modify_session_info(session_id, body)

Update or replace info for a session.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
body = flywheel.InfoUpdateInput() # InfoUpdateInput | 

try:
    # Update or replace info for a session.
    api_instance.modify_session_info(session_id, body)
except ApiException as e:
    print("Exception when calling SessionsApi->modify_session_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **body** | [**InfoUpdateInput**](InfoUpdateInput.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_session_note**
> InlineResponse2001 modify_session_note(session_id, note_id, body)

Update a note on session.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
note_id = 'note_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Update a note on session.
    api_response = api_instance.modify_session_note(session_id, note_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->modify_session_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **note_id** | **str**|  | 
 **body** | [**Note**](Note.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rename_session_tag**
> InlineResponse2001 rename_session_tag(session_id, tag_value, body=body)

Rename a tag.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with
body = flywheel.Tag() # Tag |  (optional)

try:
    # Rename a tag.
    api_response = api_instance.rename_session_tag(session_id, tag_value, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SessionsApi->rename_session_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 
 **body** | [**Tag**](Tag.md)|  | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_session_file**
> replace_session_file(session_id, file_name)

Replace a file

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Replace a file
    api_instance.replace_session_file(session_id, file_name)
except ApiException as e:
    print("Exception when calling SessionsApi->replace_session_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file_to_session**
> upload_file_to_session(session_id, file)

Upload a file to session.

### Example
```python
from __future__ import print_function
import time
import flywheel
from flywheel.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = flywheel.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = flywheel.SessionsApi(flywheel.ApiClient(configuration))
session_id = 'session_id_example' # str | 
file = '/path/to/file.txt' # file | The file to upload

try:
    # Upload a file to session.
    api_instance.upload_file_to_session(session_id, file)
except ApiException as e:
    print("Exception when calling SessionsApi->upload_file_to_session: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **str**|  | 
 **file** | **file**| The file to upload | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

