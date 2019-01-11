# flywheel.BatchApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_batch**](BatchApi.md#cancel_batch) | **POST** /batch/{BatchId}/cancel | Cancel a Job
[**get_all_batches**](BatchApi.md#get_all_batches) | **GET** /batch | Get a list of batch jobs the user has created.
[**get_batch**](BatchApi.md#get_batch) | **GET** /batch/{BatchId} | Get batch job details.
[**propose_batch**](BatchApi.md#propose_batch) | **POST** /batch | Create a batch job proposal and insert it as &#39;pending&#39;.
[**start_batch**](BatchApi.md#start_batch) | **POST** /batch/{BatchId}/run | Launch a job.


# **cancel_batch**
> BatchCancelOutput cancel_batch(batch_id)

Cancel a Job

Cancels jobs that are still pending, returns number of jobs cancelled. Moves a 'running' batch job to 'cancelled'. 

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
api_instance = flywheel.BatchApi(flywheel.ApiClient(configuration))
batch_id = 'batch_id_example' # str | 

try:
    # Cancel a Job
    api_response = api_instance.cancel_batch(batch_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->cancel_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_id** | **str**|  | 

### Return type

[**BatchCancelOutput**](BatchCancelOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_batches**
> list[Batch] get_all_batches()

Get a list of batch jobs the user has created.

Requires login.

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
api_instance = flywheel.BatchApi(flywheel.ApiClient(configuration))

try:
    # Get a list of batch jobs the user has created.
    api_response = api_instance.get_all_batches()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->get_all_batches: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Batch]**](Batch.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_batch**
> Batch get_batch(batch_id, jobs=jobs)

Get batch job details.

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
api_instance = flywheel.BatchApi(flywheel.ApiClient(configuration))
batch_id = 'batch_id_example' # str | 
jobs = true # bool | If true, return job objects instead of job ids (optional)

try:
    # Get batch job details.
    api_response = api_instance.get_batch(batch_id, jobs=jobs)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->get_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_id** | **str**|  | 
 **jobs** | **bool**| If true, return job objects instead of job ids | [optional] 

### Return type

[**Batch**](Batch.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **propose_batch**
> BatchProposal propose_batch(body)

Create a batch job proposal and insert it as 'pending'.

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
api_instance = flywheel.BatchApi(flywheel.ApiClient(configuration))
body = flywheel.BatchProposalInput() # BatchProposalInput | The batch proposal

try:
    # Create a batch job proposal and insert it as 'pending'.
    api_response = api_instance.propose_batch(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->propose_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BatchProposalInput**](BatchProposalInput.md)| The batch proposal | 

### Return type

[**BatchProposal**](BatchProposal.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_batch**
> list[Job] start_batch(batch_id)

Launch a job.

Creates jobs from proposed inputs, returns jobs enqueued. Moves 'pending' batch job to 'running'. 

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
api_instance = flywheel.BatchApi(flywheel.ApiClient(configuration))
batch_id = 'batch_id_example' # str | 

try:
    # Launch a job.
    api_response = api_instance.start_batch(batch_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BatchApi->start_batch: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_id** | **str**|  | 

### Return type

[**list[Job]**](Job.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

