from fastmcp.server.dependencies import get_http_request
import httpx
API_URL = "DUMMY"
TIMEOUT = 30
async def make_api_call(
    method: str, 
    endpoint: str,
    params=None, 
    data=None
):
    """Make an async API call using the client's PAT from context."""
    url = f"{API_URL}{endpoint}"
    print(f"Debug: making request to {url}")
    #Retrieve auth header from request
    headers = get_http_request().headers
    auth_header = headers.get("Authorization")
    # Extract the authorization header from the request headers

    if not auth_header:
        return {"error": "No authorization token provided"}
    
    # Create headers for the request
    headers = {
        "Authorization": auth_header,
        "Accept": "application/json"
    }

    print(f"Debug: {auth_header}")
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            if method.lower() == "get":
                response = await client.get(url, headers=headers, params=params)
            elif method.lower() == "post":
                response = await client.post(url, headers=headers, json=data)
            elif method.lower() == "put":
                response = await client.put(url, headers=headers, json=data)
            elif method.lower() == "delete":
                response = await client.delete(url, headers=headers, json=data if data else params)
                # Error in delete: "error": "Request failed: 
                # AsyncClient.delete() got an unexpected keyword argument 'json'"
            
            # Check for authorization errors. LLM Should handle this??
            if response.status_code == 403:
                return {
                    "error": "User doesn't have access to this tool",
                    "status_code": 403
                }
            elif response.status_code == 401:
                
                return {
                    "error": "Unauthorized access",
                    "status_code": 401
                }
            
            response.raise_for_status()
            return response.json()


    except httpx.HTTPStatusError as e:
        return {
            "error": f"API error: {e.response.status_code}",
            "message": str(e)
        }
    except Exception as e:
        return {
            "error": f"Request failed: {str(e)}"
        }
