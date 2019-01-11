# flywheel.FilesApi

All URIs are relative to *https://dev.flywheel.io/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_download_ticket**](FilesApi.md#create_download_ticket) | **POST** /download | Create a download ticket
[**download_ticket**](FilesApi.md#download_ticket) | **GET** /download | Download files listed in the given ticket.
[**upload_by_label**](FilesApi.md#upload_by_label) | **POST** /upload/label | Multipart form upload with N file fields, each with their desired filename.
[**upload_by_reaper**](FilesApi.md#upload_by_reaper) | **POST** /upload/reaper | Bottom-up UID matching of Multipart form upload with N file fields, each with their desired filename.
[**upload_by_uid**](FilesApi.md#upload_by_uid) | **POST** /upload/uid | Multipart form upload with N file fields, each with their desired filename.
[**upload_match_uid**](FilesApi.md#upload_match_uid) | **POST** /upload/uid-match | Multipart form upload with N file fields, each with their desired filename.


# **create_download_ticket**
> DownloadTicketWithSummary create_download_ticket(body, prefix=prefix)

Create a download ticket

Use filters in the payload to exclude/include files. To pass a single filter, each of its conditions should be satisfied. If a file pass at least one filter, it is included in the targets. 

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
api_instance = flywheel.FilesApi(flywheel.ApiClient(configuration))
body = flywheel.Download() # Download | Download files with tag 'incomplete' OR type 'dicom'
prefix = 'prefix_example' # str | A string to customize the name of the download in the format <prefix>_<timestamp>.tar. Defaults to \"scitran\".  (optional)

try:
    # Create a download ticket
    api_response = api_instance.create_download_ticket(body, prefix=prefix)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FilesApi->create_download_ticket: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Download**](Download.md)| Download files with tag &#39;incomplete&#39; OR type &#39;dicom&#39; | 
 **prefix** | **str**| A string to customize the name of the download in the format &lt;prefix&gt;_&lt;timestamp&gt;.tar. Defaults to \&quot;scitran\&quot;.  | [optional] 

### Return type

[**DownloadTicketWithSummary**](DownloadTicketWithSummary.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_ticket**
> download_ticket(ticket)

Download files listed in the given ticket.

You can use POST to create a download ticket The files listed in the ticket are put into a tar archive 

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
api_instance = flywheel.FilesApi(flywheel.ApiClient(configuration))
ticket = 'ticket_example' # str | ID of the download ticket

try:
    # Download files listed in the given ticket.
    api_instance.download_ticket(ticket)
except ApiException as e:
    print("Exception when calling FilesApi->download_ticket: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ticket** | **str**| ID of the download ticket | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_by_label**
> object upload_by_label(form_data=form_data)

Multipart form upload with N file fields, each with their desired filename.

For technical reasons, no form field names can be repeated. Instead, use (file1, file2) and so forth. A non-file form field called \"metadata\" is also required, which must be a string containing JSON. See api/schemas/input/labelupload.json for the format of this metadata. 

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
api_instance = flywheel.FilesApi(flywheel.ApiClient(configuration))
form_data = 'form_data_example' # str |  (optional)

try:
    # Multipart form upload with N file fields, each with their desired filename.
    api_response = api_instance.upload_by_label(form_data=form_data)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FilesApi->upload_by_label: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **form_data** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_by_reaper**
> list[FileEntry] upload_by_reaper(form_data=form_data)

Bottom-up UID matching of Multipart form upload with N file fields, each with their desired filename.

Upload data, allowing users to move sessions during scans without causing new data to be created in referenced project/group.   ### Evaluation Order:  * If a matching acquisition UID is found anywhere on the system, the related files will be placed under that acquisition. * **OR** If a matching session UID is found, a new acquistion is created with the specified UID under that Session UID. * **OR** If a matching group ID and project label are found, a new session and acquisition will be created within that project * **OR** If a matching group ID is found, a new project and session and acquisition will be created within that group. * **OR** A new session and acquisition will be created within a special \"Unknown\" group and project, which is only visible to system administrators. 

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
api_instance = flywheel.FilesApi(flywheel.ApiClient(configuration))
form_data = 'form_data_example' # str |  (optional)

try:
    # Bottom-up UID matching of Multipart form upload with N file fields, each with their desired filename.
    api_response = api_instance.upload_by_reaper(form_data=form_data)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FilesApi->upload_by_reaper: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **form_data** | **str**|  | [optional] 

### Return type

[**list[FileEntry]**](FileEntry.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_by_uid**
> object upload_by_uid(form_data=form_data)

Multipart form upload with N file fields, each with their desired filename.

Same behavior as /api/upload/label,  except the metadata field must be uid format  See api/schemas/input/uidupload.json for the format of this metadata. 

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
api_instance = flywheel.FilesApi(flywheel.ApiClient(configuration))
form_data = 'form_data_example' # str |  (optional)

try:
    # Multipart form upload with N file fields, each with their desired filename.
    api_response = api_instance.upload_by_uid(form_data=form_data)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FilesApi->upload_by_uid: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **form_data** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_match_uid**
> object upload_match_uid(form_data=form_data)

Multipart form upload with N file fields, each with their desired filename.

Accepts uploads to an existing data hierarchy, matched via Session and Acquisition UID See api/schemas/input/uidmatchupload.json for the format of this metadata. 

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
api_instance = flywheel.FilesApi(flywheel.ApiClient(configuration))
form_data = 'form_data_example' # str |  (optional)

try:
    # Multipart form upload with N file fields, each with their desired filename.
    api_response = api_instance.upload_match_uid(form_data=form_data)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FilesApi->upload_match_uid: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **form_data** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

