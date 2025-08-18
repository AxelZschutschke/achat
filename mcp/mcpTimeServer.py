from mcp.server.fastmcp import FastMCP

import datetime

server = FastMCP("TimeServer")

@server.tool()
def getDateTime() -> str:
    """returns the current system date and time in YYYY/MM/DD HH:MM:SS TZ
    
    Args:
        None
    Returns:
        String representation of current date and time
    """
    tz = datetime.datetime.now().astimezone().tzinfo
    return datetime.datetime.now().replace(tzinfo=tz).strftime("%Y/%m/%d %H:%M:%S %Z")

if __name__ == "__main__":
    server.run(transport="stdio")
