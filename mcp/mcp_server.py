from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token
from api import *


mcp = FastMCP()

@mcp.tool(name="get_all_projects_for_user")
def get_all_projects_for_user(user_id: str) -> list[str]:
    return get_all_projects_for_user(user_id)

@mcp.tool(name="save_context_to_project")
def save_context_to_project(user_id: str, project_id: str, context: str) -> None:
    '''
    Save context to a project
    If the user isn't clear about what project they want to save to, you should take your best guess on which project they are talking about.
    If you are still unclear, you should ask the user to clarify.
    '''
    return save_context_to_project(user_id, project_id, context)

@mcp.tool(name="add_project")
def add_project(user_id: str, project_name: str, project_description: str) -> None:
    '''
    Add a project to the user's list of projects

    '''

    return add_project(user_id, project_name, project_description)

@mcp.tool(name="delete_project")
def delete_project(user_id: str, project_id: str) -> None:
    '''
    Delete a project from the user's list of projects
    '''
    return delete_project(user_id, project_id)


@mcp.tool(name="get_relevant_context")
def get_relevant_context(user_id: str, project_id: str, prompt: str) -> list[str]:
    return get_relevant_context(user_id, project_id, prompt)


if __name__ == "__main__":
    main()
