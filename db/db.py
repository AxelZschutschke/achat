#import faiss
import numpy as np
import json
from typing import List, Dict
from chat.session import Backend

class DB:
    def __init__(self,path:str,backend:Backend):
        self.path = path
        self.db = {"documents":{},"embeddings":{},"keywords":{}}
        self.chunkSize = 1000
        self.chunkOverlap = 100
        self.backend = backend

    @staticmethod
    def cosineSimilarity(a, b):
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

    def findKNN(self, query, k=5):
        dist = [(v[1:],DB.cosineSimilarity(query, v[0])) for v in self.db["embeddings"].values()]
        dist.sort(key=lambda x: x[1],reverse=True)
        return dist[:k]

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

    def checkInFile(self, path:str):
        with open(path, "r") as f:
            self.checkIn(path, f.read())

    def checkIn(self, document:str, text:str, keywords:List=[]):
        seek, chunks = self.createChunks(text)
        embeddings = self.backend.createEmbeddings(chunks)
        for i,c,e in zip(seek, chunks, embeddings):
            id = hash(c)
            self.db["embeddings"][id] = (e, i[0], i[1], document)
        self.db["documents"][document] = text
        for k in keywords:
            self.db["keywords"].setdefault(k,[])
            self.db["keywords"][k].append(document)
    
    def search(self, query:str, num:int=3, padding:int=500, keywords:List=[]):
        qEmbedding = self.backend.createEmbeddings([query])[0]
        knn = self.findKNN(qEmbedding, num)
        print(knn)
        result = []
        for info, dist in knn:
            seek, length, doc = info
            text = self.db["documents"][doc]
            start = max(0, seek - padding)
            stop = min(start + length + 2*padding, len(text))

            result.append((doc, text[start:stop]))
        return result

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.db, f, indent=3)

    def load(self):
        with open(self.path, "rb") as f:
            self.db = json.load(f)

def createDB(dbName:str, paths:List, backend:Backend):
    db = DB(dbName,backend=backend)
    for p in paths:
        db.checkInFile(p)
    db.save()
    return db

def loadDB(dbName:str, backend:Backend):
    db = DB(dbName, backend=backend)
    db.load()
    return db


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