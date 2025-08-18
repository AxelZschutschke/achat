import numpy as np
import json
from typing import List, Tuple, NamedTuple

from .embedding import Embedding
from .indexfile import IndexFile

Dist = NamedTuple("Distance", [("idx", int), ("chunk", int), ("dist",np.float64)])

class VectorDB:
    def __init__(self):
        self.index:List[IndexFile] = []

    def addIndex(self, index:IndexFile):
        self.index.append(index)

    def search(self, q:Embedding, knn:int, length:int = 0, debug:bool=False) -> List[Tuple[str,float]]:
        knnlist = [] 

        # process query per idx -> file, idx, dist
        full = {}
        for i, idx in enumerate(self.index):
            dists = idx.similarities(q)
            if debug:
                full[idx.orig.name] = dists
            for chunk, dist in enumerate(dists):
                if not knnlist:
                    knnlist.append(Dist(i,chunk,dist))
                    continue
                for j, k in enumerate(knnlist):
                    if dist > k.dist:
                        knnlist.insert(j, Dist(i,chunk,dist))
                        knnlist = knnlist[:knn]
                        break

        res = [
            (self.index[idx].getChunk(chunk, length),float(dist)) for idx,chunk,dist in knnlist
        ]

        if debug:
            with open("debug.json", "w") as f:
                f.write('{\n"full":')
                json.dump(full,f,indent=3)
                f.write('\n, "res":\n')
                json.dump(res,f,indent=3)
                f.write('\n}')

        return res


    def filter(self, include:List[str] = [], exclude:List[str] = []):
        """
        Filters a list of Document instances based on include and exclude keywords.
        
        Args:
            include (list): List of keywords to include.
            exclude (list): List of keywords to exclude.
            
        Returns:
            list: A list of filtered Document instances.
        """
        filtered = VectorDB()
        
        for idx in self.index:
            # Check if the document contains any include keywords and does not contain any exclude keywords
            if any(keyword in idx.conf.keywords for keyword in include) and not any(keyword in idx.conf.keywords for keyword in exclude):
                filtered.addIndex(idx)
        
        return filtered
