from chat.backendOllama import BackendOllama
from db.db import DB, createDB

db = createDB("tmp/database.db",["tmp/arrah.md","tmp/balloon.md"],backend=BackendOllama())
#print(db.search("cannons shoot balls",1))
db.save()

db.db = {}
db.load()
print(db.search("cannons shoot balls",1))