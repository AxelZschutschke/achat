import os
import inspect
from typing import List
from __future__ import annotations ## reflective typehints


class Message:
    class Serializer:
        @staticmethod
        def __call__(message:Message):
            return {"content":message.content, "role":message.role} | message.kwargs

    def __init__(self, content, role="user", **kwargs):
        self.content = content
        self.role = role
        self.kwargs = kwargs

    def serialize(self, serializer:Serializer=Serializer()):
        return serializer(self)
    
    def __repr__(self):
        return f"({self.role}) {self.content}"
    
class Tool:
    class Serializer:
        @staticmethod
        def __call__(tool:Tool):
            return [{
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        k: {"type":v} for k,v in tool.parameters.values()
                    },
                    "required": tool.required,
                    "additionalProperties": False
                },
                "strict": True
            }]

    def __init__(self, tool:callable):
        lut = {
            "int": "integer",
            "float": "number",
            "str": "string",
            "bool": "bool",
        }
        translate = lambda x: lut[x] if x in lut else x

        self.name = tool.__name__
        self.description = tool.__doc__
        spec = inspect.signature(tool).parameters.values()
        self.parameters = {
            param.name: translate(param.annotation.__class__) for param in spec
        }
        self.required = [
            param.name for param in spec if isinstance(param.default, inspect._empty)
        ]

    def serialize(self, serializer:Serializer=Serializer()):
        return serializer(self)

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
        tools = [t.serialize() for t in tools] if tools else None
        result:ChatResponse = chat(
            model=self.model,
            tools=tools,
            think=self.think,
            messages=[
                m.serializeOllama() for m in context
            ]
            )
        lastHash = None
        while result.message.tool_calls:
            results = []
            for tool in result.message.tool_calls:
                newHash = hash(tool.function.name + str(tool.function.arguments))
                if newHash == lastHash:
                    content = "error: multiple sequential identical calls detected!"
                else:
                    content = 
                results.append({"role":"tool", "content":content, "tool_name":tool.function.name})


        return Message(result.message.content, result.message.role)
    
class Session:
    def __init__(self, backend):
        self.backend:Backend = backend
        self.system = None
        self.history = []
        self.tools = {}

    def setSystem(self, prompt:str):
        self.system = Message(prompt, "system")
        self.history.append(self.system)

    def clear(self):
        self.history.clear()

    def query(self, prompt:str) -> str:
        self.history.append(Message(prompt, "user"))
        result = self.backend.create(self.history, self.tools)
        self.history.append(result)
        return result.content


if __name__ == "__main__":
    backend = BackendOllama("qwen3:8b", think=False)
    session = Session(backend)
    session.setSystem("you are a helpful assistant and add a hashtag to the start of each line of your answer.")
    print(session.query("hello"))
    print(session.history)
    print(session.query("what is the current time?"))
    print(session.history)