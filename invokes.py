import requests

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, **kwargs):
    """A simple wrapper for requests methods.
       url: the url of the http service;
       method: the http method;
       json: the JSON input when needed by the http method;
       return: the JSON reply content from the http service if the call succeeds;
            otherwise, return a JSON object with a "code" name-value pair.
    """
    code = 200
    result = {}

    try:
        if method.upper() in SUPPORTED_HTTP_METHODS:
            r = requests.request(method, url, json=json, **kwargs)
        else:
            raise Exception(f"HTTP method {method} unsupported.")
    except Exception as e:
        code = 500
        result = {"code": code, "message": f"Invocation of service fails: {url}. {str(e)}"}

    if code not in range(200, 300):  # If not a success status code
        result['code'] = code
        return result

    # Check http call result
    if r.status_code != requests.codes.ok:
        code = r.status_code
        result['code'] = code

    # Try to parse JSON result
    try:
        result = r.json() if len(r.content) > 0 else {"code": code, "message": "Empty response body"}
    except Exception as e:
        code = 500
        result = {"code": code, "message": f"Invalid JSON output from service: {url}. {str(e)}"}

    result['code'] = code  # Ensure the status code is added to the result
    return result