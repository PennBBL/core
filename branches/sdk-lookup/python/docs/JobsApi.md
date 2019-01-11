# flywheel.JobsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_failed_output**](JobsApi.md#accept_failed_output) | **POST** /jobs/{JobId}/accept-failed-output | Accept failed job output.
[**add_job**](JobsApi.md#add_job) | **POST** /jobs/add | Add a job
[**add_job_logs**](JobsApi.md#add_job_logs) | **POST** /jobs/{JobId}/logs | Add logs to a job.
[**get_job**](JobsApi.md#get_job) | **GET** /jobs/{JobId} | Get job details
[**get_job_config**](JobsApi.md#get_job_config) | **GET** /jobs/{JobId}/config.json | Get a job&#39;s config
[**get_job_logs**](JobsApi.md#get_job_logs) | **GET** /jobs/{JobId}/logs | Get job logs
[**get_jobs_stats**](JobsApi.md#get_jobs_stats) | **GET** /jobs/stats | Get stats about all current jobs
[**get_next_job**](JobsApi.md#get_next_job) | **GET** /jobs/next | Get the next job in the queue
[**modify_job**](JobsApi.md#modify_job) | **PUT** /jobs/{JobId} | Update a job.
[**prepare_compete**](JobsApi.md#prepare_compete) | **POST** /jobs/{JobId}/prepare-complete | Create a ticket with the job id and its status.
[**reap_jobs**](JobsApi.md#reap_jobs) | **POST** /jobs/reap | Reap stale jobs
[**retry_job**](JobsApi.md#retry_job) | **POST** /jobs/{JobId}/retry | Retry a job.


# **accept_failed_output**
> accept_failed_output(job_id)

Accept failed job output.

Remove the 'from_failed_job' flag from the files. Create any automatic jobs for the accepted files. 

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 

try:
    # Accept failed job output.
    api_instance.accept_failed_output(job_id)
except ApiException as e:
    print("Exception when calling JobsApi->accept_failed_output: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_job**
> CommonObjectCreated add_job(body)

Add a job

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
body = flywheel.Job() # Job | 

try:
    # Add a job
    api_response = api_instance.add_job(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->add_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Job**](Job.md)|  | 

### Return type

[**CommonObjectCreated**](CommonObjectCreated.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_job_logs**
> add_job_logs(job_id, body)

Add logs to a job.

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 
body = [flywheel.JobLogStatement()] # list[JobLogStatement] | 

try:
    # Add logs to a job.
    api_instance.add_job_logs(job_id, body)
except ApiException as e:
    print("Exception when calling JobsApi->add_job_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **body** | [**list[JobLogStatement]**](JobLogStatement.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job**
> Job get_job(job_id)

Get job details

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 

try:
    # Get job details
    api_response = api_instance.get_job(job_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**Job**](Job.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_config**
> object get_job_config(job_id)

Get a job's config

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 

try:
    # Get a job's config
    api_response = api_instance.get_job_config(job_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_config: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_logs**
> JobLog get_job_logs(job_id)

Get job logs

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 

try:
    # Get job logs
    api_response = api_instance.get_job_logs(job_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_job_logs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**JobLog**](JobLog.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_stats**
> object get_jobs_stats()

Get stats about all current jobs

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))

try:
    # Get stats about all current jobs
    api_response = api_instance.get_jobs_stats()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_jobs_stats: %s\n" % e)
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

# **get_next_job**
> Job get_next_job(tags=tags)

Get the next job in the queue

Used by the engine.

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
tags = ['tags_example'] # list[str] |  (optional)

try:
    # Get the next job in the queue
    api_response = api_instance.get_next_job(tags=tags)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->get_next_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tags** | [**list[str]**](str.md)|  | [optional] 

### Return type

[**Job**](Job.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_job**
> modify_job(job_id, body)

Update a job.

Updates timestamp. Enforces a valid state machine transition, if any. Rejects any change to a job that is not currently in 'pending' or 'running' state. Accepts the same body as /api/jobs/add , except all fields are optional. 

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 
body = NULL # object | 

try:
    # Update a job.
    api_instance.modify_job(job_id, body)
except ApiException as e:
    print("Exception when calling JobsApi->modify_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **body** | **object**|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **prepare_compete**
> object prepare_compete(job_id, body=body)

Create a ticket with the job id and its status.

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 
body = NULL # object |  (optional)

try:
    # Create a ticket with the job id and its status.
    api_response = api_instance.prepare_compete(job_id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->prepare_compete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **body** | **object**|  | [optional] 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reap_jobs**
> object reap_jobs()

Reap stale jobs

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))

try:
    # Reap stale jobs
    api_response = api_instance.reap_jobs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->reap_jobs: %s\n" % e)
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

# **retry_job**
> object retry_job(job_id)

Retry a job.

The job must have a state of 'failed', and must not have already been retried. The failed jobs config is copied to a new job. The ID of the new job is returned 

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
api_instance = flywheel.JobsApi(flywheel.ApiClient(configuration))
job_id = 'job_id_example' # str | 

try:
    # Retry a job.
    api_response = api_instance.retry_job(job_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling JobsApi->retry_job: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

