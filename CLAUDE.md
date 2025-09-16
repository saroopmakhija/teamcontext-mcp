Working on an mcp client to make it easier for teams to collaborate using coding tools like mcp by sharing context through a central team focused API KEY.
Goal: Help multiple MCP clients and users to communicate with shared context
-> Singular user can share context between claude, chatgpt, cursor
-> Multiple users can access eachother's context via API key
-> How should we handle API keys? Per user, per project? Permissions? Party b shouldnt be able to access all projects of party A, only what is shared
-> Every user can have own API key and in the backend server we handle the logic of adding people to projects


Project class:

Project_id
name
owner_id
people(?) [user_ids]
description (to semantic search against)
data [vector store] (to semantic search)

Flow to find useful context: 
1. User asks LLM to get information about the OS assignment that him and his friend are working on
2. MCP tool called -> get_relevant_context
    2a. Semantic search against project description and retrieve top k relevant projects
    2b. Semantic search within relevant projects to get top k most important contexts
3. context returned to LLM

Flow to add context:
1. User asks LLM to save this information (Optional: to a certain project)
2. MCP tool called -> save_to_context
    2a. LLM decides a valid project to save this to (or it's already given)
    2b. LLM retrieves project. db[project].context.append(context)

