from __future__ import annotations

from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

import os
import asyncio
import json

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
            #print(f"calling {self.name} with {kwargs}")
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.parent.callTool(self.name, kwargs))
    
    def __init__(self, config:Dict|str=None):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []
        if config and isinstance(config,str):
            with open(config, "r") as f:
                dictConfig = json.load(f)
        elif config and isinstance(config,dict):
            dictConfig = config
        
        if dictConfig:
            assert "command" in dictConfig
            assert "arguments" in dictConfig
            assert "env" in dictConfig
            assert "workdir" in dictConfig
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.connectToServer(dictConfig["command"],dictConfig["arguments"],dictConfig["env"],dictConfig["workdir"]))
            del loop
        
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
    
    async def callTool(self, toolName:str, toolArgs:Any):
        result = await self.session.call_tool(toolName, toolArgs)
        return result.content[0].text