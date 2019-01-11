# flywheel.AcquisitionsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_acquisition**](AcquisitionsApi.md#add_acquisition) | **POST** /acquisitions | Create a new acquisition
[**add_acquisition_analysis**](AcquisitionsApi.md#add_acquisition_analysis) | **POST** /acquisitions/{AcquisitionId}/analyses | Create an analysis and upload files.
[**add_acquisition_analysis_note**](AcquisitionsApi.md#add_acquisition_analysis_note) | **POST** /acquisitions/{AcquisitionId}/analyses/{AnalysisId}/notes | Add a note to acquisition analysis.
[**add_acquisition_note**](AcquisitionsApi.md#add_acquisition_note) | **POST** /acquisitions/{AcquisitionId}/notes | Add a note to acquisition.
[**add_acquisition_tag**](AcquisitionsApi.md#add_acquisition_tag) | **POST** /acquisitions/{AcquisitionId}/tags | Add a tag to acquisition.
[**delete_acquisition**](AcquisitionsApi.md#delete_acquisition) | **DELETE** /acquisitions/{AcquisitionId} | Delete a acquisition
[**delete_acquisition_analysis**](AcquisitionsApi.md#delete_acquisition_analysis) | **DELETE** /acquisitions/{AcquisitionId}/analyses/{AnalysisId} | Delete an anaylsis
[**delete_acquisition_analysis_note**](AcquisitionsApi.md#delete_acquisition_analysis_note) | **DELETE** /acquisitions/{AcquisitionId}/analyses/{AnalysisId}/notes/{NoteId} | Remove a note from acquisition analysis.
[**delete_acquisition_file**](AcquisitionsApi.md#delete_acquisition_file) | **DELETE** /acquisitions/{AcquisitionId}/files/{FileName} | Delete a file
[**delete_acquisition_note**](AcquisitionsApi.md#delete_acquisition_note) | **DELETE** /acquisitions/{AcquisitionId}/notes/{NoteId} | Remove a note from acquisition
[**delete_acquisition_tag**](AcquisitionsApi.md#delete_acquisition_tag) | **DELETE** /acquisitions/{AcquisitionId}/tags/{TagValue} | Delete a tag
[**download_acquisition_analysis_inputs**](AcquisitionsApi.md#download_acquisition_analysis_inputs) | **GET** /acquisitions/{AcquisitionId}/analyses/{AnalysisId}/inputs | Download analysis inputs.
[**download_acquisition_analysis_inputs_by_filename**](AcquisitionsApi.md#download_acquisition_analysis_inputs_by_filename) | **GET** /acquisitions/{AcquisitionId}/analyses/{AnalysisId}/inputs/{Filename} | Download anaylsis inputs with filter.
[**download_acquisition_analysis_outputs**](AcquisitionsApi.md#download_acquisition_analysis_outputs) | **GET** /acquisitions/{AcquisitionId}/analyses/{AnalysisId}/files | Download analysis outputs.
[**download_acquisition_analysis_outputs_by_filename**](AcquisitionsApi.md#download_acquisition_analysis_outputs_by_filename) | **GET** /acquisitions/{AcquisitionId}/analyses/{AnalysisId}/files/{Filename} | Download anaylsis outputs with filter.
[**download_file_from_acquisition**](AcquisitionsApi.md#download_file_from_acquisition) | **GET** /acquisitions/{AcquisitionId}/files/{FileName} | Download a file.
[**get_acquisition_download_ticket**](AcquisitionsApi.md#get_acquisition_download_ticket) | **GET** /acquisitions/{AcquisitionId}/files/{FileName} | Download a file.
[**get_acquisition**](AcquisitionsApi.md#get_acquisition) | **GET** /acquisitions/{AcquisitionId} | Get a single acquisition
[**get_acquisition_analyses**](AcquisitionsApi.md#get_acquisition_analyses) | **GET** /acquisitions/{AcquisitionId}/analyses | Get analyses for acquisition.
[**get_acquisition_analysis**](AcquisitionsApi.md#get_acquisition_analysis) | **GET** /acquisitions/{AcquisitionId}/analyses/{AnalysisId} | Get an analysis.
[**get_acquisition_file_info**](AcquisitionsApi.md#get_acquisition_file_info) | **GET** /acquisitions/{AcquisitionId}/files/{FileName}/info | Get info for a particular file.
[**get_acquisition_note**](AcquisitionsApi.md#get_acquisition_note) | **GET** /acquisitions/{AcquisitionId}/notes/{NoteId} | Get a note on acquisition.
[**get_acquisition_tag**](AcquisitionsApi.md#get_acquisition_tag) | **GET** /acquisitions/{AcquisitionId}/tags/{TagValue} | Get the value of a tag, by name.
[**get_all_acquisitions**](AcquisitionsApi.md#get_all_acquisitions) | **GET** /acquisitions | Get a list of acquisitions
[**modify_acquisition**](AcquisitionsApi.md#modify_acquisition) | **PUT** /acquisitions/{AcquisitionId} | Update a acquisition
[**modify_acquisition_file**](AcquisitionsApi.md#modify_acquisition_file) | **PUT** /acquisitions/{AcquisitionId}/files/{FileName} | Modify a file&#39;s attributes
[**modify_acquisition_file_info**](AcquisitionsApi.md#modify_acquisition_file_info) | **POST** /acquisitions/{AcquisitionId}/files/{FileName}/info | Update info for a particular file.
[**modify_acquisition_info**](AcquisitionsApi.md#modify_acquisition_info) | **POST** /acquisitions/{AcquisitionId}/info | Update or replace info for a acquisition.
[**modify_acquisition_note**](AcquisitionsApi.md#modify_acquisition_note) | **PUT** /acquisitions/{AcquisitionId}/notes/{NoteId} | Update a note on acquisition.
[**rename_acquisition_tag**](AcquisitionsApi.md#rename_acquisition_tag) | **PUT** /acquisitions/{AcquisitionId}/tags/{TagValue} | Rename a tag.
[**replace_acquisition_file**](AcquisitionsApi.md#replace_acquisition_file) | **POST** /acquisitions/{AcquisitionId}/files/{FileName} | Replace a file
[**upload_file_to_acquisition**](AcquisitionsApi.md#upload_file_to_acquisition) | **POST** /acquisitions/{AcquisitionId}/files | Upload a file to acquisition.


# **add_acquisition**
> ContainerNewOutput add_acquisition(body)

Create a new acquisition

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
body = flywheel.Acquisition() # Acquisition | 

try:
    # Create a new acquisition
    api_response = api_instance.add_acquisition(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->add_acquisition: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Acquisition**](Acquisition.md)|  | 

### Return type

[**ContainerNewOutput**](ContainerNewOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_acquisition_analysis**
> ContainerNewOutput add_acquisition_analysis(acquisition_id, body, job=job)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
body = flywheel.AnalysisInputAny() # AnalysisInputAny | 
job = true # bool | Return job as an object instead of an id (optional)

try:
    # Create an analysis and upload files.
    api_response = api_instance.add_acquisition_analysis(acquisition_id, body, job=job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->add_acquisition_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **add_acquisition_analysis_note**
> InlineResponse2001 add_acquisition_analysis_note(acquisition_id, analysis_id, body)

Add a note to acquisition analysis.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Add a note to acquisition analysis.
    api_response = api_instance.add_acquisition_analysis_note(acquisition_id, analysis_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->add_acquisition_analysis_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **add_acquisition_note**
> InlineResponse2001 add_acquisition_note(acquisition_id, body)

Add a note to acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Add a note to acquisition.
    api_response = api_instance.add_acquisition_note(acquisition_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->add_acquisition_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **body** | [**Note**](Note.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_acquisition_tag**
> InlineResponse2001 add_acquisition_tag(acquisition_id, body)

Add a tag to acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
body = flywheel.Tag() # Tag | 

try:
    # Add a tag to acquisition.
    api_response = api_instance.add_acquisition_tag(acquisition_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->add_acquisition_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **body** | [**Tag**](Tag.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_acquisition**
> InlineResponse200 delete_acquisition(acquisition_id)

Delete a acquisition

Read-write project permissions are required to delete an acquisition. </br>Admin project permissions are required if the acquisition contains data uploaded by sources other than users and jobs.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 

try:
    # Delete a acquisition
    api_response = api_instance.delete_acquisition(acquisition_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->delete_acquisition: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_acquisition_analysis**
> InlineResponse200 delete_acquisition_analysis(acquisition_id, analysis_id)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 

try:
    # Delete an anaylsis
    api_response = api_instance.delete_acquisition_analysis(acquisition_id, analysis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->delete_acquisition_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **analysis_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_acquisition_analysis_note**
> InlineResponse2001 delete_acquisition_analysis_note(acquisition_id, analysis_id, note_id)

Remove a note from acquisition analysis.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Remove a note from acquisition analysis.
    api_response = api_instance.delete_acquisition_analysis_note(acquisition_id, analysis_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->delete_acquisition_analysis_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **delete_acquisition_file**
> InlineResponse2001 delete_acquisition_file(acquisition_id, file_name)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Delete a file
    api_response = api_instance.delete_acquisition_file(acquisition_id, file_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->delete_acquisition_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_acquisition_note**
> InlineResponse2001 delete_acquisition_note(acquisition_id, note_id)

Remove a note from acquisition

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Remove a note from acquisition
    api_response = api_instance.delete_acquisition_note(acquisition_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->delete_acquisition_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_acquisition_tag**
> InlineResponse2001 delete_acquisition_tag(acquisition_id, tag_value)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Delete a tag
    api_response = api_instance.delete_acquisition_tag(acquisition_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->delete_acquisition_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_acquisition_analysis_inputs**
> AnalysisFilesCreateTicketOutput download_acquisition_analysis_inputs(acquisition_id, analysis_id, ticket=ticket)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download analysis inputs.
    api_response = api_instance.download_acquisition_analysis_inputs(acquisition_id, analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->download_acquisition_analysis_inputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **download_acquisition_analysis_inputs_by_filename**
> AnalysisFilesCreateTicketOutput download_acquisition_analysis_inputs_by_filename(acquisition_id, analysis_id, filename, ticket=ticket)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select inputs for download
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download anaylsis inputs with filter.
    api_response = api_instance.download_acquisition_analysis_inputs_by_filename(acquisition_id, analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->download_acquisition_analysis_inputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **download_acquisition_analysis_outputs**
> AnalysisFilesCreateTicketOutput download_acquisition_analysis_outputs(acquisition_id, analysis_id, ticket=ticket)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download analysis outputs.
    api_response = api_instance.download_acquisition_analysis_outputs(acquisition_id, analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->download_acquisition_analysis_outputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **download_acquisition_analysis_outputs_by_filename**
> AnalysisFilesCreateTicketOutput download_acquisition_analysis_outputs_by_filename(acquisition_id, analysis_id, filename, ticket=ticket)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select outputs for download
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download anaylsis outputs with filter.
    api_response = api_instance.download_acquisition_analysis_outputs_by_filename(acquisition_id, analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->download_acquisition_analysis_outputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **download_file_from_acquisition**
> DownloadTicket download_file_from_acquisition(acquisition_id, file_name, view=view, info=info, member=member)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 
view = false # bool | If true, the proper \"Content-Type\" header based on the file's mimetype is set on response If false, the \"Content-Type\" header is set to \"application/octet-stream\"  (optional) (default to false)
info = false # bool | If the file is a zipfile, return a json response of zipfile member information (optional) (default to false)
member = 'member_example' # str | The filename of a zipfile member to download rather than the entire file (optional)

try:
    # Download a file.
    api_response = api_instance.download_file_from_acquisition(acquisition_id, file_name, view=view, info=info, member=member)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->download_file_from_acquisition: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **get_acquisition_download_ticket**
> DownloadTicket get_acquisition_download_ticket(acquisition_id, file_name, ticket=ticket, view=view, info=info, member=member)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 
ticket = 'ticket_example' # str | The generated ticket id for the download, or present but empty to generate a ticket id (optional)
view = false # bool | If true, the proper \"Content-Type\" header based on the file's mimetype is set on response If false, the \"Content-Type\" header is set to \"application/octet-stream\"  (optional) (default to false)
info = false # bool | If the file is a zipfile, return a json response of zipfile member information (optional) (default to false)
member = 'member_example' # str | The filename of a zipfile member to download rather than the entire file (optional)

try:
    # Download a file.
    api_response = api_instance.get_acquisition_download_ticket(acquisition_id, file_name, ticket=ticket, view=view, info=info, member=member)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition_download_ticket: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **get_acquisition**
> Acquisition get_acquisition(acquisition_id)

Get a single acquisition

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 

try:
    # Get a single acquisition
    api_response = api_instance.get_acquisition(acquisition_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 

### Return type

[**Acquisition**](Acquisition.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_acquisition_analyses**
> list[AnalysisListEntry] get_acquisition_analyses(acquisition_id)

Get analyses for acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 

try:
    # Get analyses for acquisition.
    api_response = api_instance.get_acquisition_analyses(acquisition_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition_analyses: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 

### Return type

[**list[AnalysisListEntry]**](AnalysisListEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_acquisition_analysis**
> AnalysisOutput get_acquisition_analysis(acquisition_id, analysis_id, inflate_job=inflate_job)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
inflate_job = true # bool | Return job as an object instead of an id (optional)

try:
    # Get an analysis.
    api_response = api_instance.get_acquisition_analysis(acquisition_id, analysis_id, inflate_job=inflate_job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **get_acquisition_file_info**
> FileEntry get_acquisition_file_info(acquisition_id, file_name)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Get info for a particular file.
    api_response = api_instance.get_acquisition_file_info(acquisition_id, file_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition_file_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

[**FileEntry**](FileEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_acquisition_note**
> Note get_acquisition_note(acquisition_id, note_id)

Get a note on acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Get a note on acquisition.
    api_response = api_instance.get_acquisition_note(acquisition_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**Note**](Note.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_acquisition_tag**
> Tag get_acquisition_tag(acquisition_id, tag_value)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Get the value of a tag, by name.
    api_response = api_instance.get_acquisition_tag(acquisition_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_acquisition_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**Tag**](Tag.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_acquisitions**
> list[Acquisition] get_all_acquisitions()

Get a list of acquisitions

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))

try:
    # Get a list of acquisitions
    api_response = api_instance.get_all_acquisitions()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->get_all_acquisitions: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Acquisition]**](Acquisition.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_acquisition**
> InlineResponse2001 modify_acquisition(acquisition_id, body)

Update a acquisition

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
body = flywheel.Acquisition() # Acquisition | 

try:
    # Update a acquisition
    api_response = api_instance.modify_acquisition(acquisition_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->modify_acquisition: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **body** | [**Acquisition**](Acquisition.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_acquisition_file**
> InlineResponse2003 modify_acquisition_file(acquisition_id, file_name, body)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 
body = flywheel.FileEntry() # FileEntry | 

try:
    # Modify a file's attributes
    api_response = api_instance.modify_acquisition_file(acquisition_id, file_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->modify_acquisition_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **modify_acquisition_file_info**
> InlineResponse2001 modify_acquisition_file_info(acquisition_id, file_name, body)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 
body = flywheel.InfoUpdateInput() # InfoUpdateInput | 

try:
    # Update info for a particular file.
    api_response = api_instance.modify_acquisition_file_info(acquisition_id, file_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->modify_acquisition_file_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **modify_acquisition_info**
> modify_acquisition_info(acquisition_id, body)

Update or replace info for a acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
body = flywheel.InfoUpdateInput() # InfoUpdateInput | 

try:
    # Update or replace info for a acquisition.
    api_instance.modify_acquisition_info(acquisition_id, body)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->modify_acquisition_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **body** | [**InfoUpdateInput**](InfoUpdateInput.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_acquisition_note**
> InlineResponse2001 modify_acquisition_note(acquisition_id, note_id, body)

Update a note on acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
note_id = 'note_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Update a note on acquisition.
    api_response = api_instance.modify_acquisition_note(acquisition_id, note_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->modify_acquisition_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **rename_acquisition_tag**
> InlineResponse2001 rename_acquisition_tag(acquisition_id, tag_value, body=body)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with
body = flywheel.Tag() # Tag |  (optional)

try:
    # Rename a tag.
    api_response = api_instance.rename_acquisition_tag(acquisition_id, tag_value, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->rename_acquisition_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
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

# **replace_acquisition_file**
> replace_acquisition_file(acquisition_id, file_name)

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Replace a file
    api_instance.replace_acquisition_file(acquisition_id, file_name)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->replace_acquisition_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file_to_acquisition**
> upload_file_to_acquisition(acquisition_id, file)

Upload a file to acquisition.

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
api_instance = flywheel.AcquisitionsApi(flywheel.ApiClient(configuration))
acquisition_id = 'acquisition_id_example' # str | 
file = '/path/to/file.txt' # file | The file to upload

try:
    # Upload a file to acquisition.
    api_instance.upload_file_to_acquisition(acquisition_id, file)
except ApiException as e:
    print("Exception when calling AcquisitionsApi->upload_file_to_acquisition: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **acquisition_id** | **str**|  | 
 **file** | **file**| The file to upload | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

