import hashlib
import pathlib

def md5file(path:pathlib.Path, chunkSize:int=1024) -> str:
    md5 = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(chunkSize):
            md5.update(chunk)
    return md5.hexdigest()

def md5str(content:str) -> str:
    md5 = hashlib.md5()
    md5.update(content.encode("utf-8"))
    return md5.hexdigest()