from __future__ import annotations

from typing import Optional, List, Dict
from contextlib import AsyncExitStack
from mcp import ClientSession
#from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters

import os
import asyncio

from .tool import Tool

class MCPClient:
    class MCPTool(Tool):
        def __init__(self, parent:MCPClient, name, description, schema):
            self.name = name
            self.cb = self
            self.parent = parent
            self.description = description
            self.parameters = schema
            self.required = [p for p in self.parameters]
        
        def __call__(self, **kwargs):
            print(f"calling {self.name} with {kwargs}")
            response = asyncio.run(
                self.parent.session.call_tool(self.name, **kwargs)
            )
            text = response.content[0].text
            print(text)
            return text
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []
        
    async def connectToServer(self, exec, args:List[str]=[], env:Dict[str,str]={}, cwd=os.curdir):
        cmd = StdioServerParameters(command=exec, args=args, env=env, cwd=cwd)
        transport = await self.exit_stack.enter_async_context(
            stdio_client(cmd)
        )
        read, write = transport
        
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        await self.session.initialize()       
                
    
        response = await self.session.list_tools()
        for tool in response.tools:
            self.tools.append(MCPClient.MCPTool(self, tool.name, tool.description, tool.inputSchema["properties"]))
        return self.session
    
    async def disconnect(self):
        """Cleanly disconnects from the MCP server.
        
        Closes the async exit stack and cleans up the client session.
        After disconnection, the client will need to reconnect before making
        further server requests.
        """
        await self.exit_stack.aclose()
        self.session = None