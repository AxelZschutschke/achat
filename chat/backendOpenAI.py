from __future__ import annotations ## reflective typehints
import os
from typing import List, Tuple
import json

from .message import Message
from .tool import Tool
from .session import Backend

class BackendOpenAI(Backend):
    def __init__(self, model):
        from openai import OpenAI
        token = os.getenv("OPENAI_TOKEN")
        baseurl = os.getenv("OPENAI_URL")
        self.session = OpenAI(api_key=token,base_url=baseurl)
        self.model = model
        self.backend = "openai"

    def create(self, context:List[Tuple[int,Message]], tools:List[Tool]=[]) -> Message:
        toolsSerialized = [t.serialize() for t in tools] if tools else None
        toolLUT = {t.name: t.cb for t in tools} if tools else {}
        tool_choice = "auto" if tools else None
        messages = [m.serialize() for _,m in context]
        lastHash = None

        while True:
            result = self.session.chat.completions.create(
                model=self.model,
                tools=toolsSerialized,
                tool_choice=tool_choice,
                messages=messages
                )

            if not result.choices:
                return None

            for part in result.choices:
                if part.message.tool_calls:
                    for partt in part.message.tool_calls:
                        fname = partt.function.name
                        fargs = partt.function.arguments
                        newHash = hash(fname + fargs)
                        if newHash == lastHash:
                            content = "error: multiple sequential identical calls detected!"
                        elif fname not in toolLUT:
                            content = "error: invalid tool name (UNKNOWN)"
                        else:
                            args = json.loads(part.arguments)
                            content = toolLUT[fname](**args)
                        messages.append({"role":"function", "content":content, "name":fname})
                elif part.message.content:
                    return Message(part.message.content, "assistant")
    
    def createEmbeddings(self, chunks):
        return super().createEmbeddings(chunks)