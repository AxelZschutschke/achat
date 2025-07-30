from .message import Message
from .tool import Tool
from .backend import Backend

class Session:
    def __init__(self, backend):
        self.backend:Backend = backend
        self.system = None
        self.history = []
        self.tools = []

    def setSystem(self, prompt:str):
        self.system = Message(prompt, "system")
        self.history.append(self.system)

    def addTool(self, tool:Tool):
        self.tools.append(tool)

    def clear(self):
        self.history.clear()

    def query(self, prompt:str) -> str:
        self.history.append(Message(prompt, "user"))
        result = self.backend.create(self.history, [t for t in self.tools])
        self.history.append(result)
        return result.content