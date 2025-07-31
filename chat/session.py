from .message import Message
from .tool import Tool

from typing import List

class Backend:
    def create(self, context:List[Message], tools:List[Tool]=[]) -> Message:
        del context
        del tools

class Session:
    def __init__(self, backend):
        self.backend:Backend = backend
        self.history = []
        self.tools = []
        self.id = 0

    def setSystem(self, prompt:str):
        self.history.append((self.id, Message(prompt, "system")))
        self.id += 1

    def clear(self):
        self.history.clear()
        self.id = 0

    def removeMessageFromHistory(self, id):
        self.history = [m for m in self.history if not m[0] == id]

    def addTool(self, tool:Tool):
        self.tools.append(tool)

    def query(self, prompt:str) -> str:
        self.history.append((self.id, Message(prompt, "user")))
        self.id += 1

        result = self.backend.create(self.history, [t for t in self.tools])

        self.history.append((self.id, result))
        self.id += 1

        return result.content