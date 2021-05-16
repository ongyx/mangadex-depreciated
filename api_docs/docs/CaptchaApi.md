# mangadex.CaptchaApi

All URIs are relative to *https://api.mangadex.org*

Method | HTTP request | Description
------------- | ------------- | -------------
[**post_captcha_solve**](CaptchaApi.md#post_captcha_solve) | **POST** /captcha/solve | Solve Captcha

# **post_captcha_solve**
> InlineResponse2001 post_captcha_solve(body=body)

Solve Captcha

Captchas can be solved explicitly through this endpoint, another way is to add a `X-Captcha-Result` header to any request. The same logic will verify the captcha and is probably more convenient because it takes one less request.  Authentication is optional. Captchas are tracked for both the client ip and for the user id, if you are logged in you want to send your session token but that is not required.

### Example
```python
from __future__ import print_function
import time
import mangadex
from mangadex.rest import ApiException
from pprint import pprint


# create an instance of the API class
api_instance = mangadex.CaptchaApi(mangadex.ApiClient(configuration))
body = mangadex.Body() # Body |  (optional)

try:
    # Solve Captcha
    api_response = api_instance.post_captcha_solve(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CaptchaApi->post_captcha_solve: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Body**](Body.md)|  | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[Bearer](../README.md#Bearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
