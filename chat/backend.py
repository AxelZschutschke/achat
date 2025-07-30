from __future__ import annotations ## reflective typehints
import os
from typing import List

from .message import Message
from .tool import Tool

class Backend:
    def create(self, context:List[Message], tools:List[Tool]=[]) -> Message:
        del context
        del tools

class BackendOpenAI(Backend):
    def __init__(self, model):
        from openai import OpenAI
        token = os.getenv("OPENAI_TOKEN")
        baseurl = os.getenv("OPENAI_URL")
        self.session = OpenAI(api_key=token,base_url=baseurl)
        self.model = model

    def create(self, context:List[Message], tools:List[Tool]=[]) -> Message:
        # loop until end of tools
        tools = [t.serialize() for t in tools] if tools else None
        tool_choice = "auto" if tools else None
        result = self.session.responses.create(
            model=self.model,
            tools=tools,
            tool_choice=tool_choice,
            input=[
                m.serialize() for m in context
            ]
            )
        return Message(result.content, "assistant")

class BackendOllama(Backend):
    def __init__(self, model, think=None):
        self.model = model
        self.think = think

    def create(self, context:List[Message], tools:List[Tool]=[]) -> Message:
        from ollama import chat, ChatResponse
        toolsSerialized = [t.serialize() for t in tools] if tools else None
        toolLUT = {t.name: t.cb for t in tools} if tools else {}
        messages = [m.serialize() for m in context]
        result = None
        lastHash = None

        while not result or result.message.tool_calls:
            result:ChatResponse = chat(
                model=self.model,
                think=self.think,
                messages=messages,
                tools=toolsSerialized,
                )
            if not result.message.tool_calls:
                break
            for tool in result.message.tool_calls:
                newHash = hash(tool.function.name + str(tool.function.arguments))
                if newHash == lastHash:
                    content = "error: multiple sequential identical calls detected!"
                elif tool.function.name not in toolLUT:
                    content = "error: invalid tool name (UNKNOWN)"
                else:
                    content = toolLUT[tool.function.name](**tool.function.arguments)
                messages.append({"role":"tool", "content":content, "tool_name":tool.function.name})
        return Message(result.message.content, result.message.role)
    