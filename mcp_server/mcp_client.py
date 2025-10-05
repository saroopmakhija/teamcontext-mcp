import asyncio
import json
import os
import sys
from typing import List, Dict, Any, Optional, Literal, Union, cast

# OpenAI imports
from openai import OpenAI, AsyncOpenAI

# FastMCP imports
from fastmcp import Client
from fastmcp.utilities.logging import configure_logging
from fastmcp.client.transports import StdioTransport 
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext

from dotenv import load_dotenv

# Configure logging
configure_logging(level="INFO")
load_dotenv()
# Define provider type
provider = "openai"
PORT = os.getenv("PORT", "8001")

class OPENAIClient:
    """A client that integrates Claude/GPT with FastMCP tools."""
    
    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 api_key: Optional[str] = None,
                 model: Optional[str] = None):
        """Initialize the client.
        """
        self.transport = StreamableHttpTransport(
            url="http://localhost:8001/mcp",
            headers={"Authorization": f"Bearer {api_key}"}
        )

        self.openai_client = OpenAI(api_key=openai_api_key)
        self.async_openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini" if model is None else model
            
        # Create the client using the transport WITH sampling handler
        self.mcp_client = Client(
            self.transport
        )

        self.messages: List[Dict[str, Any]] = []
            
        self.available_tools = []
        self.formatted_tools = []
    
    
    async def initialize(self):
        """Initialize the client by fetching available tools."""
        tools = await self.mcp_client.list_tools()
        self.available_tools = tools
        
        # Format tools based on the provider
        self.formatted_tools = []
        for tool in tools:

                # Format for OpenAI API
            self.formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool with the provided arguments and return the result as a string."""
        try:
            # Use the already established connection
            result = await self.mcp_client.call_tool(tool_name, arguments)
            if isinstance(result, dict) and "error" in result:
                if result.get("status_code") == 403:
                    return f"Authorization Error, User does not have access to this tool: {result['error']}"
                else:
                    return f"Error: {result['error']}"
            # Convert result to string based on type
            elif isinstance(result, list):
                if hasattr(result[0], 'text'):
                    return result[0].text
                else:
                    return json.dumps(result, default=str)
            else:
                return str(result)
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"
    
    async def _process_openai_query(self, query: str) -> str:
        """Process a user query using OpenAI's API with improved tool chaining."""
        if not self.openai_client or not self.async_openai_client:
            raise ValueError("OpenAI client not initialized")
            
        # Add the user's query to the conversation
        self.messages.append({
            "role": "user", 
            "content": query
        })
        
        final_output = []
        tool_usage_complete = False
        
        # Start a loop to handle multiple rounds of tool calling
        while not tool_usage_complete:
            # Get GPT's response
            response = await self.async_openai_client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.formatted_tools,
                tool_choice="auto"  # Let the model decide when to use tools
            )
            
            message = response.choices[0].message
            
            # Add the message content to the output if it exists
            if message.content:
                final_output.append(message.content)
            
            # Add the assistant's message to the conversation history
            assistant_message = {
                "role": "assistant",
                "content": message.content
            }
            if message.tool_calls:
                assistant_message["tool_calls"] = message.tool_calls
            self.messages.append(assistant_message)
            
            # Handle tool calls if they exist
            if message.tool_calls and len(message.tool_calls) > 0:
                # Process all tool calls and collect the results
                for idx, tool_call in enumerate(message.tool_calls):
                    if tool_call.type == "function":
                        tool_name = tool_call.function.name
                        
                        try:
                            # Parse arguments from JSON string
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                            
                        final_output.append(f"\n[Using tool {idx+1}/{len(message.tool_calls)}: {tool_name}]")
                        
                        # Call the tool
                        tool_result = await self._call_tool(tool_name, arguments)
                        final_output.append(f"[Tool result: {tool_result}]")
                        
                        # Add tool result to the conversation history
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": tool_result
                        })
                
                # Continue the loop to allow GPT to make more tool calls
                # We don't want to prematurely ask for a final response
                continue
            else:
                # No more tool calls - the process is complete
                tool_usage_complete = True
        
        return "\n".join(final_output)
    
    async def process_query(self, query: str) -> str:
        return await self._process_openai_query(query)
    
    async def chat(self):
        """Run an interactive chat loop with the selected model."""
        # Use the correct async with pattern for the client
        async with self.mcp_client:
            # Initialize and fetch tools
            await self.initialize()
            
            print(f"Connected to FastMCP. Found {len(self.available_tools)} tools.")
            if self.available_tools:
                print("Available tools:")
                for tool in self.available_tools:
                    print(f"  - {tool.name}: {tool.description}")
            
            model_name = "GPT"
            print(f"\nChat with {model_name} ({self.model}) - type 'exit' to quit:")

            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                try:
                    # Process the query
                    response = await self.process_query(user_input)
                    print(f"\n{model_name}: {response}")
                    
                except Exception as e:
                    print(f"\nError: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        print("MCP connection closed")

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    import os
    # Get provider from command line or environment
    provider = "openai"

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    

    if provider == "openai" and not openai_api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        return
    # Set user PAT when initialising client 
    api = os.getenv("AUTH_TOKEN")
    print(f"API Key: {api}")
    if not api:
        print("Please set the AUTH_TOKEN environment variable")
        return
    # Get model from environment if specified
    model = os.getenv("MODEL","gpt-4o-mini")
    print(f"model: {model}")
    # Create the client
    client = OPENAIClient(
        openai_api_key=openai_api_key,
        api_key=api,
        model=model
    )
    
    try:
        await client.chat()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    asyncio.run(main())