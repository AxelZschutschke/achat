from mcp.server.fastmcp import FastMCP

server = FastMCP("sample mcp server")

@server.tool()
def helloWorld() -> str:
    return "hello world"

if __name__ == "__main__":
    server.run(transport="stdio")
