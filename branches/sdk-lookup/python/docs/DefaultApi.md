# flywheel.DefaultApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**clean_packfiles**](DefaultApi.md#clean_packfiles) | **POST** /clean-packfiles | Clean up expired upload tokens and invalid token directories.
[**engine_upload**](DefaultApi.md#engine_upload) | **POST** /engine | Upload a list of file fields.
[**get_config**](DefaultApi.md#get_config) | **GET** /config | Return public Scitran configuration information
[**get_config_js**](DefaultApi.md#get_config_js) | **GET** /config.js | Return public Scitran configuration information in javascript format.
[**get_version**](DefaultApi.md#get_version) | **GET** /version | Get server and database schema version info
[**login**](DefaultApi.md#login) | **POST** /login | Login
[**logout**](DefaultApi.md#logout) | **POST** /logout | Log Out
[**lookup_path**](DefaultApi.md#lookup_path) | **POST** /lookup | Perform path based lookup of a single node in the Flywheel hierarchy
[**resolve_path**](DefaultApi.md#resolve_path) | **POST** /resolve | Perform path based lookup of nodes in the Flywheel hierarchy
[**search**](DefaultApi.md#search) | **POST** /dataexplorer/search | Perform a search query


# **clean_packfiles**
> object clean_packfiles()

Clean up expired upload tokens and invalid token directories.

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))

try:
    # Clean up expired upload tokens and invalid token directories.
    api_response = api_instance.clean_packfiles()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->clean_packfiles: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **engine_upload**
> object engine_upload(level, id, job, body=body)

Upload a list of file fields.

### Default behavior:  >Uploads a list of file fields sent as file1, file2, etc to an existing   container and updates fields of the files, the container and it's   parents as specified in the metadata fileformfield using the   engine placer class  ### When ``level`` is ``analysis``: > Uploads a list of files to an existing analysis object, marking   all files as ``output=true`` using the job-based analyses placer   class.  See schemas/input/analysis.json 

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))
level = 'level_example' # str | Which level to store files in
id = 'id_example' # str | The ID of the container to place files in
job = 'job_example' # str | Required if ``level`` is ``analysis``
body = flywheel.EnginemetadataEngineUploadInput() # EnginemetadataEngineUploadInput | Object encoded as a JSON string. By default JSON must match the specified enginemetadata.json schema If ``level`` is ``analysis``, JSON must match AnalysisUploadMetadata schema  (optional)

try:
    # Upload a list of file fields.
    api_response = api_instance.engine_upload(level, id, job, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->engine_upload: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **level** | **str**| Which level to store files in | 
 **id** | **str**| The ID of the container to place files in | 
 **job** | **str**| Required if &#x60;&#x60;level&#x60;&#x60; is &#x60;&#x60;analysis&#x60;&#x60; | 
 **body** | [**EnginemetadataEngineUploadInput**](EnginemetadataEngineUploadInput.md)| Object encoded as a JSON string. By default JSON must match the specified enginemetadata.json schema If &#x60;&#x60;level&#x60;&#x60; is &#x60;&#x60;analysis&#x60;&#x60;, JSON must match AnalysisUploadMetadata schema  | [optional] 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_config**
> ConfigOutput get_config()

Return public Scitran configuration information

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))

try:
    # Return public Scitran configuration information
    api_response = api_instance.get_config()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_config: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ConfigOutput**](ConfigOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_config_js**
> get_config_js()

Return public Scitran configuration information in javascript format.

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))

try:
    # Return public Scitran configuration information in javascript format.
    api_instance.get_config_js()
except ApiException as e:
    print("Exception when calling DefaultApi->get_config_js: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/html

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_version**
> VersionOutput get_version()

Get server and database schema version info

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))

try:
    # Get server and database schema version info
    api_response = api_instance.get_version()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_version: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**VersionOutput**](VersionOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login**
> AuthLoginOutput login()

Login

Scitran Authentication

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))

try:
    # Login
    api_response = api_instance.login()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->login: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**AuthLoginOutput**](AuthLoginOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logout**
> AuthLogoutOutput logout()

Log Out

Remove authtokens for user

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))

try:
    # Log Out
    api_response = api_instance.logout()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->logout: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**AuthLogoutOutput**](AuthLogoutOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **lookup_path**
> ResolverNode lookup_path(body)

Perform path based lookup of a single node in the Flywheel hierarchy

This will perform a deep lookup of a node. See /resolve for more details. 

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))
body = flywheel.ResolverInput() # ResolverInput | 

try:
    # Perform path based lookup of a single node in the Flywheel hierarchy
    api_response = api_instance.lookup_path(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->lookup_path: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ResolverInput**](ResolverInput.md)|  | 

### Return type

[**ResolverNode**](ResolverNode.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resolve_path**
> ResolverOutput resolve_path(body)

Perform path based lookup of nodes in the Flywheel hierarchy

This will perform a deep lookup of a node (i.e. group/project/session/acquisition) and its children, including any files. The query path is an array of strings in the following order (by default):    * group id   * project label   * session label   * acquisition label  Additionally, analyses for project/session/acquisition nodes can be resolved by inserting the literal  string `\"analyses\"`. e.g. `['scitran', 'MyProject', 'analyses']`.  Files for projects, sessions, acquisitions and analyses can be resolved by inserting the literal string  `\"files\"`. e.g. `['scitran', 'MyProject', 'files']`.  An ID can be used instead of a label by formatting the string as `<id:project_id>`. The full path to the node, and the node's children will be included in the response. 

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))
body = flywheel.ResolverInput() # ResolverInput | 

try:
    # Perform path based lookup of nodes in the Flywheel hierarchy
    api_response = api_instance.resolve_path(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->resolve_path: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ResolverInput**](ResolverInput.md)|  | 

### Return type

[**ResolverOutput**](ResolverOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search**
> list[SearchResponse] search(body, simple=simple, limit=limit)

Perform a search query

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
api_instance = flywheel.DefaultApi(flywheel.ApiClient(configuration))
body = flywheel.SearchQuery() # SearchQuery | 
simple = true # bool |  (optional)
limit = 56 # int |  (optional)

try:
    # Perform a search query
    api_response = api_instance.search(body, simple=simple, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->search: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SearchQuery**](SearchQuery.md)|  | 
 **simple** | **bool**|  | [optional] 
 **limit** | **int**|  | [optional] 

### Return type

[**list[SearchResponse]**](SearchResponse.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

