# flywheel.CollectionsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_collection**](CollectionsApi.md#add_collection) | **POST** /collections | Create a collection
[**add_collection_analysis**](CollectionsApi.md#add_collection_analysis) | **POST** /collections/{CollectionId}/analyses | Create an analysis and upload files.
[**add_collection_analysis_note**](CollectionsApi.md#add_collection_analysis_note) | **POST** /collections/{CollectionId}/analyses/{AnalysisId}/notes | Add a note to collection analysis.
[**add_collection_note**](CollectionsApi.md#add_collection_note) | **POST** /collections/{CollectionId}/notes | Add a note to collection.
[**add_collection_permission**](CollectionsApi.md#add_collection_permission) | **POST** /collections/{CollectionId}/permissions | Add a permission
[**add_collection_tag**](CollectionsApi.md#add_collection_tag) | **POST** /collections/{CollectionId}/tags | Add a tag to collection.
[**delete_collection**](CollectionsApi.md#delete_collection) | **DELETE** /collections/{CollectionId} | Delete a collection
[**delete_collection_analysis**](CollectionsApi.md#delete_collection_analysis) | **DELETE** /collections/{CollectionId}/analyses/{AnalysisId} | Delete an anaylsis
[**delete_collection_analysis_note**](CollectionsApi.md#delete_collection_analysis_note) | **DELETE** /collections/{CollectionId}/analyses/{AnalysisId}/notes/{NoteId} | Remove a note from collection analysis.
[**delete_collection_file**](CollectionsApi.md#delete_collection_file) | **DELETE** /collections/{CollectionId}/files/{FileName} | Delete a file
[**delete_collection_note**](CollectionsApi.md#delete_collection_note) | **DELETE** /collections/{CollectionId}/notes/{NoteId} | Remove a note from collection
[**delete_collection_tag**](CollectionsApi.md#delete_collection_tag) | **DELETE** /collections/{CollectionId}/tags/{TagValue} | Delete a tag
[**delete_collection_user_permission**](CollectionsApi.md#delete_collection_user_permission) | **DELETE** /collections/{CollectionId}/permissions/{UserId} | Delete a permission
[**download_collection_analysis_inputs**](CollectionsApi.md#download_collection_analysis_inputs) | **GET** /collections/{CollectionId}/analyses/{AnalysisId}/inputs | Download analysis inputs.
[**download_collection_analysis_inputs_by_filename**](CollectionsApi.md#download_collection_analysis_inputs_by_filename) | **GET** /collections/{CollectionId}/analyses/{AnalysisId}/inputs/{Filename} | Download anaylsis inputs with filter.
[**download_collection_analysis_outputs**](CollectionsApi.md#download_collection_analysis_outputs) | **GET** /collections/{CollectionId}/analyses/{AnalysisId}/files | Download analysis outputs.
[**download_collection_analysis_outputs_by_filename**](CollectionsApi.md#download_collection_analysis_outputs_by_filename) | **GET** /collections/{CollectionId}/analyses/{AnalysisId}/files/{Filename} | Download anaylsis outputs with filter.
[**download_file_from_collection**](CollectionsApi.md#download_file_from_collection) | **GET** /collections/{CollectionId}/files/{FileName} | Download a file.
[**get_collection_download_ticket**](CollectionsApi.md#get_collection_download_ticket) | **GET** /collections/{CollectionId}/files/{FileName} | Download a file.
[**get_all_collections**](CollectionsApi.md#get_all_collections) | **GET** /collections | List all collections.
[**get_all_collections_curators**](CollectionsApi.md#get_all_collections_curators) | **GET** /collections/curators | List all curators of collections
[**get_collection**](CollectionsApi.md#get_collection) | **GET** /collections/{CollectionId} | Retrieve a single collection
[**get_collection_acquisitions**](CollectionsApi.md#get_collection_acquisitions) | **GET** /collections/{CollectionId}/acquisitions | List acquisitions in a collection
[**get_collection_analyses**](CollectionsApi.md#get_collection_analyses) | **GET** /collections/{CollectionId}/analyses | Get analyses for collection.
[**get_collection_analysis**](CollectionsApi.md#get_collection_analysis) | **GET** /collections/{CollectionId}/analyses/{AnalysisId} | Get an analysis.
[**get_collection_file_info**](CollectionsApi.md#get_collection_file_info) | **GET** /collections/{CollectionId}/files/{FileName}/info | Get info for a particular file.
[**get_collection_note**](CollectionsApi.md#get_collection_note) | **GET** /collections/{CollectionId}/notes/{NoteId} | Get a note on collection.
[**get_collection_sessions**](CollectionsApi.md#get_collection_sessions) | **GET** /collections/{CollectionId}/sessions | List sessions in a collection
[**get_collection_tag**](CollectionsApi.md#get_collection_tag) | **GET** /collections/{CollectionId}/tags/{TagValue} | Get the value of a tag, by name.
[**get_collection_user_permission**](CollectionsApi.md#get_collection_user_permission) | **GET** /collections/{CollectionId}/permissions/{UserId} | List a user&#39;s permissions for this collection.
[**modify_collection**](CollectionsApi.md#modify_collection) | **PUT** /collections/{CollectionId} | Update a collection and its contents
[**modify_collection_file**](CollectionsApi.md#modify_collection_file) | **PUT** /collections/{CollectionId}/files/{FileName} | Modify a file&#39;s attributes
[**modify_collection_file_info**](CollectionsApi.md#modify_collection_file_info) | **POST** /collections/{CollectionId}/files/{FileName}/info | Update info for a particular file.
[**modify_collection_info**](CollectionsApi.md#modify_collection_info) | **POST** /collections/{CollectionId}/info | Update or replace info for a collection.
[**modify_collection_note**](CollectionsApi.md#modify_collection_note) | **PUT** /collections/{CollectionId}/notes/{NoteId} | Update a note on collection.
[**modify_collection_user_permission**](CollectionsApi.md#modify_collection_user_permission) | **PUT** /collections/{CollectionId}/permissions/{UserId} | Update a user&#39;s permission for this collection.
[**rename_collection_tag**](CollectionsApi.md#rename_collection_tag) | **PUT** /collections/{CollectionId}/tags/{TagValue} | Rename a tag.
[**replace_collection_file**](CollectionsApi.md#replace_collection_file) | **POST** /collections/{CollectionId}/files/{FileName} | Replace a file
[**upload_file_to_collection**](CollectionsApi.md#upload_file_to_collection) | **POST** /collections/{CollectionId}/files | Upload a file to collection.


# **add_collection**
> CollectionNewOutput add_collection(body)

Create a collection

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
body = flywheel.Collection() # Collection | 

try:
    # Create a collection
    api_response = api_instance.add_collection(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->add_collection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Collection**](Collection.md)|  | 

### Return type

[**CollectionNewOutput**](CollectionNewOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_collection_analysis**
> ContainerNewOutput add_collection_analysis(collection_id, body, job=job)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
body = flywheel.AnalysisInputAny() # AnalysisInputAny | 
job = true # bool | Return job as an object instead of an id (optional)

try:
    # Create an analysis and upload files.
    api_response = api_instance.add_collection_analysis(collection_id, body, job=job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->add_collection_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **add_collection_analysis_note**
> InlineResponse2001 add_collection_analysis_note(collection_id, analysis_id, body)

Add a note to collection analysis.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Add a note to collection analysis.
    api_response = api_instance.add_collection_analysis_note(collection_id, analysis_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->add_collection_analysis_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **add_collection_note**
> InlineResponse2001 add_collection_note(collection_id, body)

Add a note to collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Add a note to collection.
    api_response = api_instance.add_collection_note(collection_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->add_collection_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **body** | [**Note**](Note.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_collection_permission**
> InlineResponse2001 add_collection_permission(collection_id, body=body)

Add a permission

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
body = flywheel.Permission() # Permission |  (optional)

try:
    # Add a permission
    api_response = api_instance.add_collection_permission(collection_id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->add_collection_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **body** | [**Permission**](Permission.md)|  | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_collection_tag**
> InlineResponse2001 add_collection_tag(collection_id, body)

Add a tag to collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
body = flywheel.Tag() # Tag | 

try:
    # Add a tag to collection.
    api_response = api_instance.add_collection_tag(collection_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->add_collection_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **body** | [**Tag**](Tag.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_collection**
> delete_collection(collection_id)

Delete a collection

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 

try:
    # Delete a collection
    api_instance.delete_collection(collection_id)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_collection_analysis**
> InlineResponse200 delete_collection_analysis(collection_id, analysis_id)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 

try:
    # Delete an anaylsis
    api_response = api_instance.delete_collection_analysis(collection_id, analysis_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **analysis_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_collection_analysis_note**
> InlineResponse2001 delete_collection_analysis_note(collection_id, analysis_id, note_id)

Remove a note from collection analysis.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Remove a note from collection analysis.
    api_response = api_instance.delete_collection_analysis_note(collection_id, analysis_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection_analysis_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **delete_collection_file**
> InlineResponse2001 delete_collection_file(collection_id, file_name)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Delete a file
    api_response = api_instance.delete_collection_file(collection_id, file_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_collection_note**
> InlineResponse2001 delete_collection_note(collection_id, note_id)

Remove a note from collection

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Remove a note from collection
    api_response = api_instance.delete_collection_note(collection_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_collection_tag**
> InlineResponse2001 delete_collection_tag(collection_id, tag_value)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Delete a tag
    api_response = api_instance.delete_collection_tag(collection_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_collection_user_permission**
> InlineResponse2001 delete_collection_user_permission(collection_id, user_id)

Delete a permission

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
user_id = 'user_id_example' # str | 

try:
    # Delete a permission
    api_response = api_instance.delete_collection_user_permission(collection_id, user_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->delete_collection_user_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **user_id** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_collection_analysis_inputs**
> AnalysisFilesCreateTicketOutput download_collection_analysis_inputs(collection_id, analysis_id, ticket=ticket)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download analysis inputs.
    api_response = api_instance.download_collection_analysis_inputs(collection_id, analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->download_collection_analysis_inputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **download_collection_analysis_inputs_by_filename**
> AnalysisFilesCreateTicketOutput download_collection_analysis_inputs_by_filename(collection_id, analysis_id, filename, ticket=ticket)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select inputs for download
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download anaylsis inputs with filter.
    api_response = api_instance.download_collection_analysis_inputs_by_filename(collection_id, analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->download_collection_analysis_inputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **download_collection_analysis_outputs**
> AnalysisFilesCreateTicketOutput download_collection_analysis_outputs(collection_id, analysis_id, ticket=ticket)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download analysis outputs.
    api_response = api_instance.download_collection_analysis_outputs(collection_id, analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->download_collection_analysis_outputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **download_collection_analysis_outputs_by_filename**
> AnalysisFilesCreateTicketOutput download_collection_analysis_outputs_by_filename(collection_id, analysis_id, filename, ticket=ticket)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select outputs for download
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download anaylsis outputs with filter.
    api_response = api_instance.download_collection_analysis_outputs_by_filename(collection_id, analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->download_collection_analysis_outputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **download_file_from_collection**
> DownloadTicket download_file_from_collection(collection_id, file_name, view=view, info=info, member=member)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 
view = false # bool | If true, the proper \"Content-Type\" header based on the file's mimetype is set on response If false, the \"Content-Type\" header is set to \"application/octet-stream\"  (optional) (default to false)
info = false # bool | If the file is a zipfile, return a json response of zipfile member information (optional) (default to false)
member = 'member_example' # str | The filename of a zipfile member to download rather than the entire file (optional)

try:
    # Download a file.
    api_response = api_instance.download_file_from_collection(collection_id, file_name, view=view, info=info, member=member)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->download_file_from_collection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **get_collection_download_ticket**
> DownloadTicket get_collection_download_ticket(collection_id, file_name, ticket=ticket, view=view, info=info, member=member)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 
ticket = 'ticket_example' # str | The generated ticket id for the download, or present but empty to generate a ticket id (optional)
view = false # bool | If true, the proper \"Content-Type\" header based on the file's mimetype is set on response If false, the \"Content-Type\" header is set to \"application/octet-stream\"  (optional) (default to false)
info = false # bool | If the file is a zipfile, return a json response of zipfile member information (optional) (default to false)
member = 'member_example' # str | The filename of a zipfile member to download rather than the entire file (optional)

try:
    # Download a file.
    api_response = api_instance.get_collection_download_ticket(collection_id, file_name, ticket=ticket, view=view, info=info, member=member)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_download_ticket: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **get_all_collections**
> list[Collection] get_all_collections()

List all collections.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))

try:
    # List all collections.
    api_response = api_instance.get_all_collections()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_all_collections: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Collection]**](Collection.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_collections_curators**
> list[InlineResponse2002] get_all_collections_curators()

List all curators of collections

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))

try:
    # List all curators of collections
    api_response = api_instance.get_all_collections_curators()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_all_collections_curators: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[InlineResponse2002]**](InlineResponse2002.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection**
> Collection get_collection(collection_id)

Retrieve a single collection

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 

try:
    # Retrieve a single collection
    api_response = api_instance.get_collection(collection_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 

### Return type

[**Collection**](Collection.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_acquisitions**
> list[Acquisition] get_collection_acquisitions(collection_id, session=session)

List acquisitions in a collection

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
session = 'session_example' # str | The id of a session, to which the acquisitions returned will be restricted (optional)

try:
    # List acquisitions in a collection
    api_response = api_instance.get_collection_acquisitions(collection_id, session=session)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_acquisitions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **session** | **str**| The id of a session, to which the acquisitions returned will be restricted | [optional] 

### Return type

[**list[Acquisition]**](Acquisition.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_analyses**
> list[AnalysisListEntry] get_collection_analyses(collection_id)

Get analyses for collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 

try:
    # Get analyses for collection.
    api_response = api_instance.get_collection_analyses(collection_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_analyses: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 

### Return type

[**list[AnalysisListEntry]**](AnalysisListEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_analysis**
> AnalysisOutput get_collection_analysis(collection_id, analysis_id, inflate_job=inflate_job)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
analysis_id = 'analysis_id_example' # str | 
inflate_job = true # bool | Return job as an object instead of an id (optional)

try:
    # Get an analysis.
    api_response = api_instance.get_collection_analysis(collection_id, analysis_id, inflate_job=inflate_job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **get_collection_file_info**
> FileEntry get_collection_file_info(collection_id, file_name)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Get info for a particular file.
    api_response = api_instance.get_collection_file_info(collection_id, file_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_file_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

[**FileEntry**](FileEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_note**
> Note get_collection_note(collection_id, note_id)

Get a note on collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
note_id = 'note_id_example' # str | 

try:
    # Get a note on collection.
    api_response = api_instance.get_collection_note(collection_id, note_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **note_id** | **str**|  | 

### Return type

[**Note**](Note.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_sessions**
> list[Session] get_collection_sessions(collection_id)

List sessions in a collection

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 

try:
    # List sessions in a collection
    api_response = api_instance.get_collection_sessions(collection_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_sessions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 

### Return type

[**list[Session]**](Session.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_tag**
> Tag get_collection_tag(collection_id, tag_value)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Get the value of a tag, by name.
    api_response = api_instance.get_collection_tag(collection_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**Tag**](Tag.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection_user_permission**
> Permission get_collection_user_permission(collection_id, user_id)

List a user's permissions for this collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
user_id = 'user_id_example' # str | 

try:
    # List a user's permissions for this collection.
    api_response = api_instance.get_collection_user_permission(collection_id, user_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->get_collection_user_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **user_id** | **str**|  | 

### Return type

[**Permission**](Permission.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_collection**
> modify_collection(collection_id, body)

Update a collection and its contents

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
body = flywheel.Collection() # Collection | 

try:
    # Update a collection and its contents
    api_instance.modify_collection(collection_id, body)
except ApiException as e:
    print("Exception when calling CollectionsApi->modify_collection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **body** | [**Collection**](Collection.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_collection_file**
> InlineResponse2003 modify_collection_file(collection_id, file_name, body)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 
body = flywheel.FileEntry() # FileEntry | 

try:
    # Modify a file's attributes
    api_response = api_instance.modify_collection_file(collection_id, file_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->modify_collection_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **modify_collection_file_info**
> InlineResponse2001 modify_collection_file_info(collection_id, file_name, body)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 
body = flywheel.InfoUpdateInput() # InfoUpdateInput | 

try:
    # Update info for a particular file.
    api_response = api_instance.modify_collection_file_info(collection_id, file_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->modify_collection_file_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **modify_collection_info**
> modify_collection_info(collection_id, body)

Update or replace info for a collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
body = flywheel.InfoUpdateInput() # InfoUpdateInput | 

try:
    # Update or replace info for a collection.
    api_instance.modify_collection_info(collection_id, body)
except ApiException as e:
    print("Exception when calling CollectionsApi->modify_collection_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **body** | [**InfoUpdateInput**](InfoUpdateInput.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_collection_note**
> InlineResponse2001 modify_collection_note(collection_id, note_id, body)

Update a note on collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
note_id = 'note_id_example' # str | 
body = flywheel.Note() # Note | 

try:
    # Update a note on collection.
    api_response = api_instance.modify_collection_note(collection_id, note_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->modify_collection_note: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **modify_collection_user_permission**
> InlineResponse2001 modify_collection_user_permission(collection_id, user_id, body=body)

Update a user's permission for this collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
user_id = 'user_id_example' # str | 
body = flywheel.Permission() # Permission |  (optional)

try:
    # Update a user's permission for this collection.
    api_response = api_instance.modify_collection_user_permission(collection_id, user_id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->modify_collection_user_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **user_id** | **str**|  | 
 **body** | [**Permission**](Permission.md)|  | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rename_collection_tag**
> InlineResponse2001 rename_collection_tag(collection_id, tag_value, body=body)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with
body = flywheel.Tag() # Tag |  (optional)

try:
    # Rename a tag.
    api_response = api_instance.rename_collection_tag(collection_id, tag_value, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->rename_collection_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
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

# **replace_collection_file**
> replace_collection_file(collection_id, file_name)

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file_name = 'file_name_example' # str | 

try:
    # Replace a file
    api_instance.replace_collection_file(collection_id, file_name)
except ApiException as e:
    print("Exception when calling CollectionsApi->replace_collection_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **file_name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file_to_collection**
> upload_file_to_collection(collection_id, file)

Upload a file to collection.

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
api_instance = flywheel.CollectionsApi(flywheel.ApiClient(configuration))
collection_id = 'collection_id_example' # str | 
file = '/path/to/file.txt' # file | The file to upload

try:
    # Upload a file to collection.
    api_instance.upload_file_to_collection(collection_id, file)
except ApiException as e:
    print("Exception when calling CollectionsApi->upload_file_to_collection: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**|  | 
 **file** | **file**| The file to upload | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

