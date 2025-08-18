from mcp.server.fastmcp import FastMCP
import os

server = FastMCP("FileServer")

@server.tool()
def read(path:str) -> str:
    """read contents of file
    
    Args:
        path - name of the file to be read
    Returns:
        the content of the file
    """
    relpath = os.path.join(".", path)
    if not os.path.isfile(relpath):
        return "Error: no such file"
    with open(relpath, "r") as f:
        return f.read()

@server.tool()
def write(path:str, content:str) -> str:
    """write contents to file, overwriting an existing file is not possible.
    
    Args:
        path - name of the file to be written
        content - the raw content of the new file
    Returns:
        "ok" or error message
    """
    relpath = os.path.join(".", path)
    if os.path.isfile(relpath):
        return "Error: file existing"
    with open(relpath, "w") as f:
        f.write(content)
    return "ok"

@server.tool()
def ls(path:str) -> str:
    """list the directory contents of path
    
    Args:
        path - name of the directory to list contents from
    Returns:
        a list of file and folder names representing the directory contents
    """
    files = os.listdir(path)
    result = ""
    for f in files:
        if os.path.isfile(f):
            result += f"F {path}/{f}"
        elif os.path.isdir(f):
            result += f"D {path}/{f}/"
    return result

if __name__ == "__main__":
    server.run(transport="stdio")
