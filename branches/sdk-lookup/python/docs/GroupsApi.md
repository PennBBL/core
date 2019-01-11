# flywheel.GroupsApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_group**](GroupsApi.md#add_group) | **POST** /groups | Add a group
[**add_group_permission**](GroupsApi.md#add_group_permission) | **POST** /groups/{GroupId}/permissions | Add a permission
[**add_group_tag**](GroupsApi.md#add_group_tag) | **POST** /groups/{GroupId}/tags | Add a tag to group.
[**delete_group**](GroupsApi.md#delete_group) | **DELETE** /groups/{GroupId} | Delete a group
[**delete_group_tag**](GroupsApi.md#delete_group_tag) | **DELETE** /groups/{GroupId}/tags/{TagValue} | Delete a tag
[**delete_group_user_permission**](GroupsApi.md#delete_group_user_permission) | **DELETE** /groups/{GroupId}/permissions/{UserId} | Delete a permission
[**get_all_groups**](GroupsApi.md#get_all_groups) | **GET** /groups | List all groups
[**get_group**](GroupsApi.md#get_group) | **GET** /groups/{GroupId} | Get group info
[**get_group_projects**](GroupsApi.md#get_group_projects) | **GET** /groups/{GroupId}/projects | Get all projects in a group
[**get_group_tag**](GroupsApi.md#get_group_tag) | **GET** /groups/{GroupId}/tags/{TagValue} | Get the value of a tag, by name.
[**get_group_user_permission**](GroupsApi.md#get_group_user_permission) | **GET** /groups/{GroupId}/permissions/{UserId} | List a user&#39;s permissions for this group.
[**modify_group**](GroupsApi.md#modify_group) | **PUT** /groups/{GroupId} | Update group
[**modify_group_user_permission**](GroupsApi.md#modify_group_user_permission) | **PUT** /groups/{GroupId}/permissions/{UserId} | Update a user&#39;s permission for this group.
[**rename_group_tag**](GroupsApi.md#rename_group_tag) | **PUT** /groups/{GroupId}/tags/{TagValue} | Rename a tag.


# **add_group**
> GroupNewOutput add_group(body)

Add a group

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
body = flywheel.Group() # Group | 

try:
    # Add a group
    api_response = api_instance.add_group(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->add_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Group**](Group.md)|  | 

### Return type

[**GroupNewOutput**](GroupNewOutput.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_group_permission**
> InlineResponse2001 add_group_permission(group_id, body=body)

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
body = flywheel.Permission() # Permission |  (optional)

try:
    # Add a permission
    api_response = api_instance.add_group_permission(group_id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->add_group_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **body** | [**Permission**](Permission.md)|  | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_group_tag**
> InlineResponse2001 add_group_tag(group_id, body)

Add a tag to group.

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
body = flywheel.Tag() # Tag | 

try:
    # Add a tag to group.
    api_response = api_instance.add_group_tag(group_id, body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->add_group_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **body** | [**Tag**](Tag.md)|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_group**
> InlineResponse200 delete_group(group_id)

Delete a group

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 

try:
    # Delete a group
    api_response = api_instance.delete_group(group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->delete_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_group_tag**
> InlineResponse2001 delete_group_tag(group_id, tag_value)

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Delete a tag
    api_response = api_instance.delete_group_tag(group_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->delete_group_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_group_user_permission**
> InlineResponse2001 delete_group_user_permission(group_id, user_id)

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
user_id = 'user_id_example' # str | 

try:
    # Delete a permission
    api_response = api_instance.delete_group_user_permission(group_id, user_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->delete_group_user_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **user_id** | **str**|  | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_groups**
> list[Group] get_all_groups()

List all groups

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))

try:
    # List all groups
    api_response = api_instance.get_all_groups()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->get_all_groups: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Group]**](Group.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group**
> Group get_group(group_id)

Get group info

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 

try:
    # Get group info
    api_response = api_instance.get_group(group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->get_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 

### Return type

[**Group**](Group.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_projects**
> list[Project] get_group_projects(group_id)

Get all projects in a group

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 

try:
    # Get all projects in a group
    api_response = api_instance.get_group_projects(group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->get_group_projects: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 

### Return type

[**list[Project]**](Project.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_tag**
> Tag get_group_tag(group_id, tag_value)

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with

try:
    # Get the value of a tag, by name.
    api_response = api_instance.get_group_tag(group_id, tag_value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->get_group_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **tag_value** | **str**| The tag to interact with | 

### Return type

[**Tag**](Tag.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_user_permission**
> Permission get_group_user_permission(group_id, user_id)

List a user's permissions for this group.

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
user_id = 'user_id_example' # str | 

try:
    # List a user's permissions for this group.
    api_response = api_instance.get_group_user_permission(group_id, user_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->get_group_user_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **user_id** | **str**|  | 

### Return type

[**Permission**](Permission.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_group**
> modify_group(group_id, body)

Update group

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
body = flywheel.Group() # Group | 

try:
    # Update group
    api_instance.modify_group(group_id, body)
except ApiException as e:
    print("Exception when calling GroupsApi->modify_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
 **body** | [**Group**](Group.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_group_user_permission**
> InlineResponse2001 modify_group_user_permission(group_id, user_id, body=body)

Update a user's permission for this group.

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
user_id = 'user_id_example' # str | 
body = flywheel.Permission() # Permission |  (optional)

try:
    # Update a user's permission for this group.
    api_response = api_instance.modify_group_user_permission(group_id, user_id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->modify_group_user_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
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

# **rename_group_tag**
> InlineResponse2001 rename_group_tag(group_id, tag_value, body=body)

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
api_instance = flywheel.GroupsApi(flywheel.ApiClient(configuration))
group_id = 'group_id_example' # str | 
tag_value = 'tag_value_example' # str | The tag to interact with
body = flywheel.Tag() # Tag |  (optional)

try:
    # Rename a tag.
    api_response = api_instance.rename_group_tag(group_id, tag_value, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling GroupsApi->rename_group_tag: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**|  | 
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

