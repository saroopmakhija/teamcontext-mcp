from fastmcp.server import FastMCP
from fastmcp.server.dependencies import get_http_headers
from api import make_api_call
mcp = FastMCP(name = "Client Context Manager")

@mcp.tool(name="get_my_info", description="Get user information by API KEY")
def get_my_info() -> dict:
    info = make_api_call()
    return {"name": "John Doe", "api_key": api_key}

@mcp.tool(name="get_my_projects", description="Get user projects")
def get_my_projects() -> list:
    headers = get_http_headers()
    api_key = headers.get("API-KEY")
    #make request to api/v1/projects
    #get user projects from db
    return [{"project_id": 1, "name": "Project 1"}, {"project_id": 2, "name": "Project 2"}]

@mcp.tool()


