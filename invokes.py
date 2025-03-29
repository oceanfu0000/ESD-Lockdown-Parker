import requests

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, **kwargs):
    """A simple wrapper for requests methods.
       url: the url of the http service;
       method: the http method;
       data: the JSON input when needed by the http method;
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
        return {"code": 500, "message": f"Invocation of service fails: {url}. {str(e)}"}

    # Handle non-2xx responses
    if r.status_code not in range(200, 300):
        try:
            return r.json()
        except Exception:
            return {"code": r.status_code, "message": f"HTTP error {r.status_code} from {url}"}

    # Handle normal response
    try:
        result = r.json() if len(r.content) > 0 else ""
    except Exception as e:
        return {"code": 500, "message": f"Invalid JSON output from service: {url}. {str(e)}"}

    return result

