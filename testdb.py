from chat.backendOllama import BackendOllama
from db.db import DB
from db.tools import createDB, loadDB
import glob

folders = [".", "chat", "db", "mcp"]
filter = "*.py"
files = []
for f in folders:
    files += [
        f"{f}/{x}" for x in glob.glob(pathname=filter, root_dir=f,recursive=True)
        ]
print(files)


db = createDB("tmp/rag.db", files, backend=BackendOllama())
print(db.search("removeMessageFromHistory",1))

#db2 = loadDB("tmp/database.db",backend=BackendOllama())
#print(db2.search("cannons shoot balls",1,0))