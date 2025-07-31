from chat.viewport import Viewport
from chat.backendOllama import BackendOllama
from chat.backendOpenAI import BackendOpenAI
from chat.mcpClientStdio import MCPClient
from chat.session import Session

import json

with open("frontend.json", "r") as f:
    config = json.load(f)


viewport = Viewport(config)

if not "backend" in config or config["backend"] == "ollama":
    backend = BackendOllama(config.get("model","quen3:8b"), think=config.get("thinking",False))
elif config["backend"] == "openai":
    backend = BackendOpenAI(config.get("model","quen3:8b"))

session = Session(backend)
if "system" in config:
    session.setSystem(config["system"])

mcps = {}
for mcp, mcpConfig in config.get("mcpServers",{}).items():
    mcps[mcp] = MCPClient(mcpConfig)
    for t in mcps[mcp].tools:
        session.addTool(t)


viewport.agent.output("Hello, I'm ready!")
while True:
    query = viewport.user.input()
    with viewport.agent.loading():
        result = session.query(query)
    viewport.agent.output(result)