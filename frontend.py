from chat.bubble import Bubble
from chat.backend import BackendOllama
from chat.mcpClientStdio import MCPClient
from chat.session import Session

import asyncio

user = Bubble(color="#aaeeaa",position="left")
agent = Bubble(color="#bbbbbb",position="right")

backend = BackendOllama("qwen3:8b", think=False)

mcpClient1 = MCPClient()
asyncio.run(mcpClient1.connectToServer("./mcpTimeServer.sh"))

session = Session(backend)
session.setSystem("you are a helpful assistant.")
for t in mcpClient1.tools:
    session.addTool(t)

agent.output("Hello, I'm ready!")
while True:
    query = user.input()
    with agent.loading():
        result = session.query(query)
    agent.output(result)