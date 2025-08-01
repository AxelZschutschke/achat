from __future__ import annotations ## reflective typehints

from .message import Message
from .tool import Tool
from .session import Backend

from ollama import chat, ChatResponse, embed
from typing import List, Tuple

class BackendOllama(Backend):
    def __init__(self, model, think=None):
        self.model = model
        self.think = think

    def create(self, context:List[Tuple[int,Message]], tools:List[Tool]=[]) -> Message:
        toolsSerialized = [t.serialize() for t in tools] if tools else None
        toolLUT = {t.name: t.cb for t in tools} if tools else {}
        messages = [m.serialize() for _,m in context]
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
    