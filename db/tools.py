from .db import DB
from chat.session import Session, Backend
from typing import List


def createSummary(text:str, backend:Backend):
    session = Session(backend)

    session.setSystem("you are a library helper and will create conciece and easy to find summaries of the text presented.")
    return session.query(text)

def createDB(dbName:str, paths:List, backend:Backend) -> DB:
    db = DB(dbName, backend)
    for p in paths:
        db.checkInFile(p)
    return db

def loadDB(dbName:str, backend:Backend) -> DB:
    db = DB(dbName, backend)
    db.load()
    return db