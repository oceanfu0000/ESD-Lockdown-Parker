import requests

# Supported HTTP methods
SUPPORTED_HTTP_METHODS = {
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
}

def invoke_http(url, method='GET', json=None, **kwargs):
    """
    A simple wrapper for making HTTP requests using the requests library.

    Args:
        url (str): The target URL for the HTTP request.
        method (str): HTTP method (e.g., 'GET', 'POST').
        json (dict, optional): JSON payload to send with the request.
        **kwargs: Additional arguments to pass to requests.request().

    Returns:
        dict: JSON response if available, or error information with a "code" field.
    """
    method = method.upper()
    if method not in SUPPORTED_HTTP_METHODS:
        return {"code": 405, "message": f"HTTP method {method} is not supported."}

    try:
        response = requests.request(method, url, json=json, **kwargs)
    except requests.exceptions.RequestException as e:
        return {"code": 500, "message": f"Service invocation failed: {url}. {str(e)}"}

    # Handle non-2xx status codes
    if not (200 <= response.status_code < 300):
        try:
            error_json = response.json()
            error_json["code"] = response.status_code
            return error_json
        except ValueError:
            return {
                "code": response.status_code,
                "message": f"HTTP error {response.status_code} from {url} with no JSON body."
            }

    # Handle successful response
    try:
        return response.json() if response.content else {}
    except ValueError as e:
        return {
            "code": 500,
            "message": f"Invalid JSON output from service: {url}. {str(e)}"
        }
