#import faiss
import numpy as np
import pickle
from typing import List, Dict
from ..chat.session import Backend

class DB:
    def __init__(self,path:str,backend:Backend):
        self.path = path
        self.db = {}
        self.indices = []
        self.keywords = {}
        self.index = None
        self.chunkSize = 1000
        self.chunkOverlap = 100
        self.backend = backend

    @staticmethod
    def cosine_similarity(a, b):
        """
        Compute the cosine similarity between two vectors.
        
        Parameters:
            a (list or np.ndarray): First vector.
            b (list or np.ndarray): Second vector.
        
        Returns:
            float: Cosine similarity between the vectors.
        """
        # Convert inputs to NumPy arrays if they are not already
        a = np.array(a)
        b = np.array(b)
        
        # Compute dot product
        dot_product = np.dot(a, b)
        
        # Compute L2 norms
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        # Handle edge case: zero vectors
        if norm_a == 0 or norm_b == 0:
            return 1.0  # Return 1.0 as a safe default
        
        # Compute cosine similarity
        return dot_product / (norm_a * norm_b)


    def createChunks(self, text:str):
        assert self.chunkSize > self.chunkOverlap

        length = len(text)
        start = 0
        stop = self.chunkSize
        seek = []
        chunks = []
        while stop < length:
            # searching for a gap...
            while stop > start and text[stop].isalnum():
                stop -= 1
            
            chunks.append(text[start:stop].strip())
            seek.append((start, stop - start))
            stop -= self.chunkOverlap
            while stop > start and text[stop].isalnum():
                stop -= 1

            start = max(start + self.chunkOverlap, stop)
            stop = min(start + self.chunkSize, length)
        
        chunks.append(text[start:-1].strip())
        seek.append((start, stop - start))
        return seek, chunks

    @staticmethod
    def createIndex(embeddings:List):
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings,dtype=np.float32))
        return index

    def checkInFile(self, path:str):
        with open(path, "r") as f:
            self.checkIn(path, f.read())

    def checkIn(self, document:str, text:str, keywords:List=[]):
        seek, chunks = self.createChunks(text)
        embeddings = self.backend.createEmbeddings(chunks)
        index = DB.createIndex(embeddings)
        pickled = pickle.dumps(index)
        if self.index:
            self.index.merge_from(index)
        else:
            self.index = index
        for s in seek:
            self.indices.append((document, s[0], s[1]))
        self.db[document] = (seek, pickled, text)
        for k in keywords:
            self.keywords.setdefault(k,[])
            self.keywords[k].append(document)
    
    def search(self, query:str, num:int=3, padding:int=500, keywords:List=[]):
        query = self.backend.createEmbeddings([query])
        distances, indices = self.index.search(np.array(query,dtype=np.float32), num)
        result = []
        for i in indices[0]:
            doc, seek, length = self.indices[i]
            text = self.db[doc][2]
            start = max(0, seek - padding)
            stop = min(start + length + 2*padding, len(text))

            result.append((doc, text[start:stop]))
        return result

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump((self.db, self.keywords), f)

    def load(self):
        with open(self.path, "rb") as f:
            loaded = pickle.load(f)
            self.db, self.keywords = loaded

        for k in self.db:
            seek, pickled, text = self.db[k]
            index = pickle.loads(pickled)
            if self.index:
                self.index.merge_from(index)
            else:
                self.index = index
            for s in seek:
                self.indices.append((k, s[0], s[1]))
        print(self.db.keys())

def createDB(dbName:str, paths:List):
    db = DB(dbName)
    for p in paths:
        db.checkInFile(p)
    db.save()
    return db

def loadDB(dbName:str):
    db = DB(dbName)
    db.load()
    return db

db = createDB("../tmp/database.db",["../tmp/arrah.md","../tmp/balloon.md"])
print(db.search("cannons shoot balls",1))

### reference
#   @staticmethod
#   def tokenize(text:str):
#       """Convert text to lowercase and split into words"""
#       text = text.lower()
#       text = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation),))
#       return text.split()

#   @staticmethod
#   def preprocess(text:str):
#       """Remove stop words and non-alphabetic tokens"""
#       stop_words = {
#           'a', 'an', 'the', 'and', 'or', 'is', 'are', 'of', 'in', 'on', 'to',
#           'for', 'with', 'as', 'by', 'at', 'be', 'that', 'this', 'it', 'has',
#           'have', 'but', 'not'
#       }
#       tokens = DB.tokenize(text)
#       return [word for word in tokens if word not in stop_words and word.isalnum()]