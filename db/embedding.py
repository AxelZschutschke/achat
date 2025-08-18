from __future__ import annotations
import numpy as np
import base64

class EmbeddingT:
    def __init__(self, numpyT, factor):
        self.numpyT = numpyT
        self.factor = factor

int8 = EmbeddingT(np.int8, 0x7F) 
int16 = EmbeddingT(np.int16, 0x7FFF) 
int32 = EmbeddingT(np.int32, 0x7FFFFFFF) 
int64 = EmbeddingT(np.int64, 0x7FFFFFFFFFFFFFFF) 
float16 = EmbeddingT(np.float16, 1.) 
float32 = EmbeddingT(np.float32, 1.) 
float64 = EmbeddingT(np.float64, 1.) 

EmbeddingTypes = [
    int8,
    int16,
    int32,
    int64,
    float16,
    float32,
    float64
]

class Embedding:
    def __init__(self):
        self.type = None
        self.data = None
        self.norm = None

    @staticmethod
    def create(data:list, type:EmbeddingT) -> Embedding:
        res = Embedding()
        res.type = type
        res.data = np.array([x * type.factor for x in data], type.numpyT)
        res.norm = np.linalg.norm(res.data)
        return res

    @staticmethod
    def deserialize(data:bytes) -> Embedding:
        res = Embedding()
        flag = data[:2]
        if flag != b'#E':
            raise Exception("cannot parse: not an embedding")
        typeno = int(data[2:4])
        res.type = EmbeddingTypes[typeno]
        decoded = base64.b64decode(data[4:])
        res.data = np.frombuffer(decoded, res.type.numpyT)
        res.norm = np.linalg.norm(res.data)
        return res

    @staticmethod
    def checkMagic(line:str):
        return line[0:2] == "#E"

    def serialize(self) -> bytes:
        typeno = EmbeddingTypes.index(self.type)
        return f'#E{typeno:02}'.encode("ascii") + base64.b64encode(self.data.tobytes())
