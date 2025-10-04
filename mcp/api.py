import httpx

# Hackathon MVP: hardcoded API key
API_KEY = "hackathon-demo-key-2025"
TIMEOUT = 30

async def make_api_call(
    method: str,
    endpoint: str,
    params=None,
    data=None
):
    """Make an async API call to the TeamContext backend."""

    # Create headers with API key
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            if method.lower() == "get":
                response = await client.get(endpoint, headers=headers, params=params)
            elif method.lower() == "post":
                response = await client.post(endpoint, headers=headers, json=data)
            elif method.lower() == "put":
                response = await client.put(endpoint, headers=headers, json=data)
            elif method.lower() == "delete":
                response = await client.delete(endpoint, headers=headers, params=params)

            # Check for errors
            if response.status_code == 403:
                return {
                    "error": "Access forbidden",
                    "status_code": 403
                }
            elif response.status_code == 401:
                return {
                    "error": "Unauthorized - Invalid API key",
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
