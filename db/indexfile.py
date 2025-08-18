import pathlib
import json
import io
from typing import List

from .embedding import Embedding
from .hash import md5file
from .utils import createChunks, getChunk, calcSimilarities

class IndexFileConf:
    def __init__(self, chunkstride:int = 512, chunklength:int = 1024, md5:str="", keywords:List[str]=[], backend:str="", model:str="", **kwargs):
        self.chunkstride = chunkstride
        self.chunklength = chunklength
        self.backend = backend
        self.model = model
        self.keywords = keywords
        self.md5 = md5

class IndexFile:
    def __init__(self, ref:pathlib.Path):
        if isinstance(ref, str):
            ref = pathlib.Path(ref)
        self.orig = ref
        self.path = ref.with_name(ref.name + ".idx")
        self.conf = IndexFileConf()
        self.embeddings = []

    def updateMD5(self):
        if not self.orig.is_file():
            return False
        self.conf.md5 = md5file(self.orig)

    def check(self):
        if not self.path.is_file():
            return False

        self.readConf()
        if not self.orig.is_file():
            return False

        selfMD5 = self.conf.md5
        if not selfMD5:
            return False

        origMD5 = md5file(self.orig)
        if origMD5 != selfMD5:
            return False
        return True
    
    def compatible(self, backend:str, model:str):
        return self.conf.backend == backend and self.conf.model == model

    def setCompatible(self, backend:str, model:str):
        self.conf.backend = backend
        self.conf.model = model
        
    def readConf(self):
        if not self.path.is_file():
            return False

        with self.path.open("r") as f:
            confraw = []
            while line := f.readline():
                line = line.strip()
                if Embedding.checkMagic(line):
                    break
                if not line or line[0] == "#":
                    continue
                confraw.append(line)
            confj = json.loads("\n".join(confraw))
            self.conf = IndexFileConf(**confj)

    def readEmbeddings(self) -> List[Embedding]:
        if self.embeddings:
            return self.embeddings

        with self.path.open("rb") as f:
            while line := f.readline():
                try:
                    self.embeddings.append(Embedding.deserialize(line))
                except:
                    pass
        return self.embeddings

    def save(self):
        confraw = json.dumps(self.conf.__dict__,indent=3)

        with self.path.open("w") as f:
            f.write(confraw)
            f.write("\n# DO NOT CHANGE BELOW THIS LINE\n")

        with self.path.open("ab") as f:
            for e in self.embeddings:
                f.write(e.serialize() + b"\n")
    
    def unloadEmbeddings(self):
        self.embeddings = []

    def addKeyword(self, keyword:str):
        if not keyword in self.conf.keywords:
            self.conf.keywords.append(keyword)

    def getKeywords(self):
        return self.conf.keywords
    
    def similarities(self, q:Embedding):
        return calcSimilarities(q, self.readEmbeddings())

    def size(self):
        return len(self.embeddings)

    def load(self):
        self.readConf()
        self.readEmbeddings()

    def createChunks(self):
        with open(self.orig, "rb") as f:
            for chunk in createChunks(f, self.conf.chunkstride, self.conf.chunklength):
                yield chunk

    def getChunk(self, idx, length=0):
        length = length if length > self.conf.chunklength else self.conf.chunklength
        padding = int((length - self.conf.chunkstride)/2)
        start = max((idx * self.conf.chunkstride) - padding, 0)
        length = length if length else self.conf.chunklength
        with open(self.orig, "rb") as f:
            f.seek(start, io.SEEK_SET)
            return f.read(length).decode("utf8")