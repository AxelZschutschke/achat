from __future__ import annotations ## reflective typehints

from .message import Message
from .tool import Tool
from .session import Backend

from ollama import chat, ChatResponse, embed
from typing import List, Tuple

class BackendOllama(Backend):
    def __init__(self, model:str = "qwen3:14b", think:bool=None, embeddings:str = "all-minilm"):
        self.model = model
        self.think = think
        self.embeddings = embeddings
        self.backend = "ollama"

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

                print()
                print(tool.function.name)
                print(tool.function.arguments)
                print(content)

                messages.append({"role":"tool", "content":content, "tool_name":tool.function.name})
        return Message(result.message.content, result.message.role)
    
    def createEmbeddings(self, chunks:List[str], model:str=None):
        model = model if model else self.embeddings
        return embed(model,chunks).embeddings