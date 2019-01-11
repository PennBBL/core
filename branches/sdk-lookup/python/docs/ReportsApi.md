# flywheel.ReportsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_project_report**](ReportsApi.md#get_project_report) | **GET** /report/project | 
[**get_site_report**](ReportsApi.md#get_site_report) | **GET** /report/site | 


# **get_project_report**
> ReportProject get_project_report(projects=projects, start_date=start_date, end_date=end_date)



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
api_instance = flywheel.ReportsApi(flywheel.ApiClient(configuration))
projects = 'projects_example' # str | Specify multiple times to include projects in the report (optional)
start_date = 'start_date_example' # str | Report start date (optional)
end_date = 'end_date_example' # str | Report end date (optional)

try:
    api_response = api_instance.get_project_report(projects=projects, start_date=start_date, end_date=end_date)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReportsApi->get_project_report: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **projects** | **str**| Specify multiple times to include projects in the report | [optional] 
 **start_date** | **str**| Report start date | [optional] 
 **end_date** | **str**| Report end date | [optional] 

### Return type

[**ReportProject**](ReportProject.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_site_report**
> ReportSite get_site_report()



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
api_instance = flywheel.ReportsApi(flywheel.ApiClient(configuration))

try:
    api_response = api_instance.get_site_report()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ReportsApi->get_site_report: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ReportSite**](ReportSite.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

