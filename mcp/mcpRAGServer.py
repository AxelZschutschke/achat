from mcp.server.fastmcp import FastMCP
from db.tools import loadDB
from chat.backendOllama import BackendOllama

server = FastMCP("RAGServer")
db = loadDB("tmp/rag.db", BackendOllama())

@server.tool()
def search(query:str) -> str:
    global db
    """returns the best matching entry from a vector db / rag database 
    
    Args:
        query - a string for querying the rag database
    Returns:
        the best-matching result given as [DOCUMENT : OFFSET] TEXT
    """
    result = db.search(query, num=1, padding=500)[0]

    return f"[{result.document}:{result.start}] {result.text}"

if __name__ == "__main__":
    server.run(transport="stdio")
