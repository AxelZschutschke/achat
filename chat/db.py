from .session import Backend
from db.indexfile import IndexFile
from db.embedding import Embedding, EmbeddingT, float64
from db.vectordb import VectorDB

import pathlib

#def createSummary(text:str, backend:Backend):
#    session = Session(backend)
#
#    session.setSystem("you are a library helper and will create conciece and easy to find summaries of the text presented.")
#    return session.query(text)

class DB(VectorDB):
    def __init__(self, backend:Backend, embeddingT:EmbeddingT = float64):
        super().__init__()
        self.backend = backend
        self.embeddingT = embeddingT

    def open(self, root:pathlib.Path, pattern:str=".md", chunkLength=None, chunkStride=None) -> None:
        if isinstance(root, str):
            root = pathlib.Path(root)

        self.index = []
        if root.is_dir():
            for dirpath, dirnames, filenames in root.walk():
                del dirnames
                print("entering", dirpath)
                for f in filenames:
                    path = dirpath / f
                    if path.is_file() and path.name.endswith(pattern):
                        idx = IndexFile(path)
                        self.addIndex(idx)
                        if idx.check() and idx.compatible(self.backend.backend, self.backend.embeddings):
                            print(f"  {path} up-to-date")
                            continue

                        idx.conf.chunkstride = chunkStride if chunkStride else idx.conf.chunkstride
                        idx.conf.chunklength = chunkLength if chunkLength else idx.conf.chunklength
                        chunks = [x for x in idx.createChunks()]
                        raw = self.backend.createEmbeddings(chunks)
                        idx.embeddings = [Embedding.create(x, self.embeddingT) for x in raw]
                        idx.updateMD5()
                        idx.updateEmbedding()
                        idx.setCompatible(self.backend.backend, self.backend.embeddings)
                        idx.save()
                        idx.unloadEmbeddings()
                        print(f"  {path} refreshed")

    def embed(self, text:str):
        raw = self.backend.createEmbeddings([text])[0]
        return Embedding.create(raw, self.embeddingT)

