
import numpy as np
import io
from typing import List, Generator, NamedTuple

from .embedding import Embedding

def cosineSimilarity(q:Embedding, ref:Embedding):
    """
    Compute the cosine similarity between two vectors.
    
    Parameters:
        q (Embedding): First vector / query.
        ref (Embedding): Second vector / reference.
    
    Returns:
        float: Cosine similarity between the vectors.
    """
    # Convert inputs to NumPy arrays if they are not already
    if ref.norm == 0 or q.norm == 0:
        return 1.0
    
    # Compute dot product
    dot_product = np.dot(q.data, ref.data)
    
    # Compute cosine similarity
    return float(dot_product / (q.norm * ref.norm))

def calcSimilarities(q:Embedding, refs=List[Embedding]):
    return [cosineSimilarity(q, ref) for ref in refs]

def createChunks(text:io.BufferedIOBase, stride:int=500, length:int=1000) -> Generator[str]:
    """
    decompose the document into smaller chunks of text, each chunk is overlapping the next -- the overlap is controlled via step and length

    Parameters:
        text (io base): to be processed
        stride (int): the offset step of each chunk (position = idx * stride)
        length (int): length to be read beginning at offset (creating the overlap)

    Returns:
        generator for chunks
    """
    backstep = max(0, length - stride)
    text.seek(0, io.SEEK_SET)
    first = True
    last = False

    while True:
        chunk = text.read(length).decode("utf8")
        if not text.read(1):
            last = True
        # searching for a gap...
        start = 0
        end = len(chunk)-1
        if not first:
            while start <= end and not chunk[start].isspace():
                start += 1
        if not last:
            while end > start and not chunk[end].isspace():
                end -= 1

        yield chunk[start:end]

        if last:
            break
        first = False
        text.seek(-backstep-1, io.SEEK_CUR)

def getChunk(text:io.BufferedIOBase, idx:int, stride:int=500, length:int=1000) -> str:
    """
    decompose the document into smaller chunks of text, each chunk is overlapping the next -- the overlap is controlled via step and length

    Parameters:
        text (io base): to be processed
        idx (int): chunk number
        stride (int): the offset step of each chunk (position = idx * stride)
        length (int): length to be read beginning at offset (creating the overlap)

    Returns:
        chunk
    """
    text.seek(idx * stride, io.SEEK_SET)
    return text.read(length).decode("utf8")