#import faiss
import numpy as np
import json
import base64
import hashlib
import re
from typing import List, Dict
from collections import namedtuple
from chat.session import Backend

Index = namedtuple("Index", "document start length")
Dist = namedtuple("Distance", "id dist")
Result = namedtuple("Result", "document text start length dist")

class Filter:
    def __init__(self, regex:str = None):
        self.regex = regex

    def __call__(self, keywords:List[str]):
        if not self.regex:
            return True
        return bool(re.search(self.regex," ".join(keywords)))

class Embedding:
    mapping = {
        "int8": (np.int8, 0x7F),
        "int16": (np.int16, 0x7FFF),
        "int32": (np.int32, 0x7FFFFFFF),
        "int64": (np.int64, 0x7FFFFFFFFFFFFFFF),
        "float16": (np.float16, 1.),
        "float32": (np.float32, 1.),
        "float64": (np.float64, 1.)
    }

    def __init__(self, type:str="float64", values:List|str=[], transform=True):
        self.type = type
        if isinstance(values, str):
            self.vector = self.deserialize(values)
        else:
            if transform:
                new = [l * Embedding.mapping[self.type][1] for l in values]
            else:
                new = values
            self.vector = np.array(new, dtype=Embedding.mapping[self.type][0])
        self.norm = np.linalg.norm(self.vector)

    def deserialize(self, raw:str):
        decoded = base64.b85decode(raw.encode("ascii"))
        return np.frombuffer(decoded, Embedding.mapping[self.type][0])
    
    def serialize(self):
        return base64.b85encode(self.vector.tobytes()).decode("ascii")

class DB:
    def __init__(self,path:str, backend:Backend):
        self.path = path
        self.embeddings = {}
        self.documents = {}
        self.keywords = {}
        self.indices = {}
        self.embeddingType = "float16"
        self.chunkSize = 1000
        self.chunkOverlap = 100
        self.backend = backend
        self.model = self.backend.embeddings

    def cosineSimilarity(self, q:Embedding, id:str):
        """
        Compute the cosine similarity between two vectors.
        
        Parameters:
            a (list or np.ndarray): First vector.
            b (list or np.ndarray): Second vector.
        
        Returns:
            float: Cosine similarity between the vectors.
        """
        # Convert inputs to NumPy arrays if they are not already
        e:Embedding = self.embeddings[id]

        if e.norm == 0 or q.norm == 0:
            return 1.0
        
        # Compute dot product
        dot_product = np.dot(q.vector, e.vector)
        
        # Compute cosine similarity
        return float(dot_product / (q.norm * e.norm))

    def findKNN(self, query:Embedding, k=5, filter:Filter=Filter()):
        dist = [Dist(id,self.cosineSimilarity(query, id)) for id in self.embeddings if filter(self.keywords[id])]
        dist.sort(key=lambda x: x.dist,reverse=True)
        return dist[:k]

    def createChunks(self, document:str, text:str):
        assert self.chunkSize > self.chunkOverlap

        length = len(text)
        start = 0
        stop = self.chunkSize
        seek = []
        chunks = []
        while stop < length:
            # searching for a gap...
            while stop > start and stop < length and text[stop].isalnum():
                stop -= 1
            
            chunks.append(text[start:stop].strip())
            seek.append(Index(document, start, stop - start))
            stop -= self.chunkOverlap
            while stop > start and text[stop].isalnum():
                stop -= 1

            start = max(start + self.chunkOverlap, stop)
            stop = min(start + self.chunkSize, length)
        
        chunks.append(text[start:-1].strip())
        seek.append(Index(document, start, stop - start))
        return seek, chunks

    def checkInFile(self, path:str):
        with open(path, "r") as f:
            self.checkIn(path, f.read())

    def checkIn(self, document:str, text:str, keywords:List=[]):
        seek, chunks = self.createChunks(document, text)
        rawEmbeddings = self.backend.createEmbeddings(chunks)
        for i,c,e in zip(seek, chunks, rawEmbeddings):
            id = hashlib.md5(c.encode("utf-8")).hexdigest()[:8]
            self.embeddings[id] = Embedding(self.embeddingType, e)
            self.keywords[id] = keywords
            self.indices[id] = i
        self.documents[document] = text

        self.save()
    
    def search(self, query:str, num:int=3, padding:int=500, filter:Filter=Filter()) -> List[Result]:
        qRawEmbedding = self.backend.createEmbeddings([query])[0]
        qEmbedding = Embedding(self.embeddingType, qRawEmbedding)

        knn = self.findKNN(qEmbedding, num, filter)
        result = []
        for k in knn:
            index:Index = self.indices[k.id]
            text = self.documents[index.document]
            start = max(0, index.start - padding)
            stop = min(index.start + index.length + 2 * padding, len(text))

            result.append(Result(index.document, text[start:stop], index.start, index.length, k.dist))
        return result

    def save(self):
        config = {"backend":self.backend.__class__.__name__, "model": self.model, "type":self.embeddingType, "chunkSize":self.chunkSize, "chunkOverlap":self.chunkOverlap}
        embeddings = {i:v.serialize() for i,v in self.embeddings.items()}
        documents = self.documents
        indices = self.indices
        keywords = self.keywords
        db = {
            "config": config,
            "embeddings": embeddings,
            "documents": documents,
            "indices": indices,
            "keywords": keywords
        }

        with open(self.path, "w") as f:
            json.dump(db, f, indent=3)

    def load(self):
        """
        replace current database state with one from disk
        """
        with open(self.path, "rb") as f:
            db:Dict = json.load(f)

        config:Dict = db.get("config",{})
        assert self.backend.__class__.__name__ == config.get("backend","")
        self.model = config.get("model", self.model)
        self.embeddingType = config.get("type", self.embeddingType)
        self.chunkSize = config.get("chunkSize", self.chunkSize)
        self.chunkOverlap = config.get("chunkOverlap", self.chunkOverlap)

        self.embeddings = {i: Embedding(values=e, type=self.embeddingType,transform=False) for i,e in db["embeddings"].items()}
        self.indices = {i: Index(*v) for i,v in db["indices"].items()}
        self.documents = db["documents"]
        self.keywords = db["keywords"]
