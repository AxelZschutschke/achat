from __future__ import annotations ## reflective typehints
import os
from typing import List, Tuple

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

    def create(self, context:List[Tuple[int,Message]], tools:List[Tool]=[]) -> Message:
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