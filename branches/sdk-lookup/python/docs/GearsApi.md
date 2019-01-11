# flywheel.GearsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_gear**](GearsApi.md#add_gear) | **POST** /gears/{GearIdOrName} | Create or update a gear.
[**delete_gear**](GearsApi.md#delete_gear) | **DELETE** /gears/{GearIdOrName} | Delete a gear (not recommended)
[**get_all_gears**](GearsApi.md#get_all_gears) | **GET** /gears | List all gears
[**get_gear**](GearsApi.md#get_gear) | **GET** /gears/{GearIdOrName} | Retrieve details about a specific gear
[**get_gear_invocation**](GearsApi.md#get_gear_invocation) | **GET** /gears/{GearId}/invocation | Get a schema for invoking a gear.


# **add_gear**
> CollectionNewOutput add_gear(gear_id_or_name, body)

Create or update a gear.

If no existing gear is found, one will be created Otherwise, the specified gear will be updated 

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
api_instance = flywheel.GearsApi(flywheel.ApiClient(configuration))
gear_id_or_name = 'gear_id_or_name_example' # str | Name of the gear to interact with
body = flywheel.GearDoc() # GearDoc | 

try:
    # Create or update a gear.
    api_response = api_instance.add_gear(gear_id_or_name, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GearsApi->add_gear: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **gear_id_or_name** | **str**| Name of the gear to interact with | 
 **body** | [**GearDoc**](GearDoc.md)|  | 

### Return type

[**CollectionNewOutput**](CollectionNewOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_gear**
> delete_gear(gear_id_or_name)

Delete a gear (not recommended)

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
api_instance = flywheel.GearsApi(flywheel.ApiClient(configuration))
gear_id_or_name = 'gear_id_or_name_example' # str | Id of the gear to interact with

try:
    # Delete a gear (not recommended)
    api_instance.delete_gear(gear_id_or_name)
except ApiException as e:
    print("Exception when calling GearsApi->delete_gear: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **gear_id_or_name** | **str**| Id of the gear to interact with | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_gears**
> list[GearDoc] get_all_gears()

List all gears

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
api_instance = flywheel.GearsApi(flywheel.ApiClient(configuration))

try:
    # List all gears
    api_response = api_instance.get_all_gears()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GearsApi->get_all_gears: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[GearDoc]**](GearDoc.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_gear**
> GearDoc get_gear(gear_id_or_name)

Retrieve details about a specific gear

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
api_instance = flywheel.GearsApi(flywheel.ApiClient(configuration))
gear_id_or_name = 'gear_id_or_name_example' # str | Id of the gear to interact with

try:
    # Retrieve details about a specific gear
    api_response = api_instance.get_gear(gear_id_or_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GearsApi->get_gear: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **gear_id_or_name** | **str**| Id of the gear to interact with | 

### Return type

[**GearDoc**](GearDoc.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_gear_invocation**
> object get_gear_invocation(gear_id)

Get a schema for invoking a gear.

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
api_instance = flywheel.GearsApi(flywheel.ApiClient(configuration))
gear_id = 'gear_id_example' # str | Id of the gear to interact with

try:
    # Get a schema for invoking a gear.
    api_response = api_instance.get_gear_invocation(gear_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GearsApi->get_gear_invocation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **gear_id** | **str**| Id of the gear to interact with | 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

