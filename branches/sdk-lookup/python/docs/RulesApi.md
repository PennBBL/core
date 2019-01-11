# flywheel.RulesApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_site_rule**](RulesApi.md#add_site_rule) | **POST** /site/rules | Create a new site rule.
[**get_site_rule**](RulesApi.md#get_site_rule) | **GET** /site/rules/{RuleId} | Get a site rule.
[**get_site_rules**](RulesApi.md#get_site_rules) | **GET** /site/rules | List all site rules.
[**modify_site_rule**](RulesApi.md#modify_site_rule) | **PUT** /site/rules/{RuleId} | Update a site rule.
[**remove_site_rule**](RulesApi.md#remove_site_rule) | **DELETE** /site/rules/{RuleId} | Remove a site rule.


# **add_site_rule**
> add_site_rule(body=body)

Create a new site rule.

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
api_instance = flywheel.RulesApi(flywheel.ApiClient(configuration))
body = flywheel.Rule() # Rule |  (optional)

try:
    # Create a new site rule.
    api_instance.add_site_rule(body=body)
except ApiException as e:
    print("Exception when calling RulesApi->add_site_rule: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Rule**](Rule.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_site_rule**
> Rule get_site_rule(rule_id)

Get a site rule.

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
api_instance = flywheel.RulesApi(flywheel.ApiClient(configuration))
rule_id = 'rule_id_example' # str | 

try:
    # Get a site rule.
    api_response = api_instance.get_site_rule(rule_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RulesApi->get_site_rule: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 

### Return type

[**Rule**](Rule.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_site_rules**
> list[Rule] get_site_rules()

List all site rules.

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
api_instance = flywheel.RulesApi(flywheel.ApiClient(configuration))

try:
    # List all site rules.
    api_response = api_instance.get_site_rules()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RulesApi->get_site_rules: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Rule]**](Rule.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_site_rule**
> modify_site_rule(rule_id, body=body)

Update a site rule.

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
api_instance = flywheel.RulesApi(flywheel.ApiClient(configuration))
rule_id = 'rule_id_example' # str | 
body = flywheel.Rule() # Rule |  (optional)

try:
    # Update a site rule.
    api_instance.modify_site_rule(rule_id, body=body)
except ApiException as e:
    print("Exception when calling RulesApi->modify_site_rule: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 
 **body** | [**Rule**](Rule.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_site_rule**
> InlineResponse200 remove_site_rule(rule_id)

Remove a site rule.

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
api_instance = flywheel.RulesApi(flywheel.ApiClient(configuration))
rule_id = 'rule_id_example' # str | 

try:
    # Remove a site rule.
    api_response = api_instance.remove_site_rule(rule_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RulesApi->remove_site_rule: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

