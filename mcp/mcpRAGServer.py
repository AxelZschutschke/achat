from mcp.server.fastmcp import FastMCP
from chat.db import DB
from db.embedding import float32
from chat.backendOllama import BackendOllama

server = FastMCP("RAGServer")
db = DB(BackendOllama(),float32)
db.open("tmp/db")

@server.tool()
def search(query:str) -> str:
    global db
    """returns the best matching entry from a vector db / rag database 
    
    Args:
        query - a string for querying the rag database
    Returns:
        the best-matching result given as [DOCUMENT : OFFSET] TEXT
    """

    result = db.search(query, num=1, length=2048)

    return result[0][0]

if __name__ == "__main__":
    server.run(transport="stdio")
