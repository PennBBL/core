# flywheel.DevicesApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_all_devices**](DevicesApi.md#get_all_devices) | **GET** /devices | List all devices.
[**get_all_devices_status**](DevicesApi.md#get_all_devices_status) | **GET** /devices/status | Get status for all known devices.
[**get_current_device**](DevicesApi.md#get_current_device) | **GET** /devices/self | Get device document for device making the request.
[**get_device**](DevicesApi.md#get_device) | **GET** /devices/{DeviceId} | Get device details
[**update_device**](DevicesApi.md#update_device) | **POST** /devices | Modify a device&#39;s interval, info or set errors.


# **get_all_devices**
> list[Device] get_all_devices()

List all devices.

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
api_instance = flywheel.DevicesApi(flywheel.ApiClient(configuration))

try:
    # List all devices.
    api_response = api_instance.get_all_devices()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->get_all_devices: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Device]**](Device.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_devices_status**
> DeviceStatus get_all_devices_status()

Get status for all known devices.

ok - missing - error - unknown

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
api_instance = flywheel.DevicesApi(flywheel.ApiClient(configuration))

try:
    # Get status for all known devices.
    api_response = api_instance.get_all_devices_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->get_all_devices_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**DeviceStatus**](DeviceStatus.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_device**
> Device get_current_device()

Get device document for device making the request.

Request must be a drone request.

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
api_instance = flywheel.DevicesApi(flywheel.ApiClient(configuration))

try:
    # Get device document for device making the request.
    api_response = api_instance.get_current_device()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->get_current_device: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Device**](Device.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device**
> Device get_device(device_id)

Get device details

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
api_instance = flywheel.DevicesApi(flywheel.ApiClient(configuration))
device_id = 'device_id_example' # str | 

try:
    # Get device details
    api_response = api_instance.get_device(device_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->get_device: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

[**Device**](Device.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_device**
> object update_device(body=body)

Modify a device's interval, info or set errors.

Will modify the device record of device making the request. Request must be drone request. 

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
api_instance = flywheel.DevicesApi(flywheel.ApiClient(configuration))
body = flywheel.Device() # Device |  (optional)

try:
    # Modify a device's interval, info or set errors.
    api_response = api_instance.update_device(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->update_device: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Device**](Device.md)|  | [optional] 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

