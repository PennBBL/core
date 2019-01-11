# flywheel.AnalysesApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_analysis_inputs**](AnalysesApi.md#download_analysis_inputs) | **GET** /analyses/{AnalysisId}/inputs | Download analysis inputs.
[**download_analysis_inputs_by_filename**](AnalysesApi.md#download_analysis_inputs_by_filename) | **GET** /analyses/{AnalysisId}/inputs/{Filename} | Download anaylsis inputs with filter.
[**download_analysis_outputs**](AnalysesApi.md#download_analysis_outputs) | **GET** /analyses/{AnalysisId}/files | Download analysis outputs.
[**download_analysis_outputs_by_filename**](AnalysesApi.md#download_analysis_outputs_by_filename) | **GET** /analyses/{AnalysisId}/files/{Filename} | Download anaylsis outputs with filter.
[**get_analyses**](AnalysesApi.md#get_analyses) | **GET** /{ContainerName}/{ContainerId}/{SubcontainerName}/analyses | Get nested analyses for a container
[**get_analysis**](AnalysesApi.md#get_analysis) | **GET** /analyses/{AnalysisId} | Get an analysis.


# **download_analysis_inputs**
> AnalysisFilesCreateTicketOutput download_analysis_inputs(analysis_id, ticket=ticket)

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
api_instance = flywheel.AnalysesApi(flywheel.ApiClient(configuration))
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download analysis inputs.
    api_response = api_instance.download_analysis_inputs(analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AnalysesApi->download_analysis_inputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **download_analysis_inputs_by_filename**
> AnalysisFilesCreateTicketOutput download_analysis_inputs_by_filename(analysis_id, filename, ticket=ticket)

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
api_instance = flywheel.AnalysesApi(flywheel.ApiClient(configuration))
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select inputs for download
ticket = 'ticket_example' # str | ticket id of the inputs to download (optional)

try:
    # Download anaylsis inputs with filter.
    api_response = api_instance.download_analysis_inputs_by_filename(analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AnalysesApi->download_analysis_inputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **download_analysis_outputs**
> AnalysisFilesCreateTicketOutput download_analysis_outputs(analysis_id, ticket=ticket)

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
api_instance = flywheel.AnalysesApi(flywheel.ApiClient(configuration))
analysis_id = 'analysis_id_example' # str | 
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download analysis outputs.
    api_response = api_instance.download_analysis_outputs(analysis_id, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AnalysesApi->download_analysis_outputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **download_analysis_outputs_by_filename**
> AnalysisFilesCreateTicketOutput download_analysis_outputs_by_filename(analysis_id, filename, ticket=ticket)

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
api_instance = flywheel.AnalysesApi(flywheel.ApiClient(configuration))
analysis_id = 'analysis_id_example' # str | 
filename = 'filename_example' # str | regex to select outputs for download
ticket = 'ticket_example' # str | ticket id of the outputs to download (optional)

try:
    # Download anaylsis outputs with filter.
    api_response = api_instance.download_analysis_outputs_by_filename(analysis_id, filename, ticket=ticket)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AnalysesApi->download_analysis_outputs_by_filename: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **get_analyses**
> list[AnalysisListEntry] get_analyses(container_name, container_id, subcontainer_name)

Get nested analyses for a container

Returns analyses that belong to containers of the specified type that belong to ContainerId.  For example: `projects/{ProjectId}/acquisitions/analyses` will return any analyses  that have an acquisition that is under that project as a parent. The `all` keyword is also supported, for example: projects/{ProjectId}/all/analyses  will return any analyses that have any session or acquisition or the project itself as a parent. 

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
api_instance = flywheel.AnalysesApi(flywheel.ApiClient(configuration))
container_name = 'container_name_example' # str | The parent container type
container_id = 'container_id_example' # str | The parent container id
subcontainer_name = 'subcontainer_name_example' # str | The sub container type

try:
    # Get nested analyses for a container
    api_response = api_instance.get_analyses(container_name, container_id, subcontainer_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AnalysesApi->get_analyses: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **container_name** | **str**| The parent container type | 
 **container_id** | **str**| The parent container id | 
 **subcontainer_name** | **str**| The sub container type | 

### Return type

[**list[AnalysisListEntry]**](AnalysisListEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_analysis**
> AnalysisOutput get_analysis(analysis_id, inflate_job=inflate_job)

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
api_instance = flywheel.AnalysesApi(flywheel.ApiClient(configuration))
analysis_id = 'analysis_id_example' # str | 
inflate_job = true # bool | Return job as an object instead of an id (optional)

try:
    # Get an analysis.
    api_response = api_instance.get_analysis(analysis_id, inflate_job=inflate_job)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AnalysesApi->get_analysis: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

