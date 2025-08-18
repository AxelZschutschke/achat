from chat.viewport import Viewport
from chat.session import Session
from chat.mcpClientStdio import MCPClient
from chat.backendFactory import createBackend
import json

with open("frontend.json", "r") as f:
    config = json.load(f)

viewport = Viewport(config)
backend = createBackend(**config)
session = Session(backend)

if "system" in config:
    session.setSystem(config["system"])

mcps = {}
for mcp, mcpConfig in config.get("mcpServers",{}).items():
    mcps[mcp] = MCPClient(mcpConfig)
    for t in mcps[mcp].tools:
        session.addTool(t)


viewport.agent.output("Hello, I'm ready!")
try:
    while True:
        query = viewport.user.input()
        with viewport.agent.loading():
            result = session.query(query)
        viewport.agent.output(result)
except Exception as e:
    print(f"exception occoured: {e}")
finally:
    with open("tmp/last.json", "w") as f:
        json.dump(session.dumpj(), f, indent=3)