from chat.db import DB
from chat.backendOllama import BackendOllama
from db.embedding import *

vdb = DB(BackendOllama(), float16)
vdb.open("tmp/db",".md",640,512)
q = vdb.embed("brown leather")
print(vdb.search(q,1,length=2048, debug=True))