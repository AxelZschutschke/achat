from mcp.server.fastmcp import FastMCP

import datetime

server = FastMCP("TimeServer")

@server.tool()
def getTime() -> str:
    """returns the current system date and time in YYYY/MM/DD HH:MM:SS
    
    Args:
        None
    Returns:
        String representation of current date and time
    """
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

if __name__ == "__main__":
    server.run(transport="stdio")
