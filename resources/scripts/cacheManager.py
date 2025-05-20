import os
import hashlib
from typing import Any, Union

def getCachedItemBytes(path: str) -> bytes:
    hashedPath = hashlib.sha256(path.encode("utf-8"), usedforsecurity=False).hexdigest()
    totalHashedPath = os.path.join("cached", hashedPath)
    if not os.path.exists(totalHashedPath):
        raise FileNotFoundError(f"Cached file for {path} does not exist!")
    with open(totalHashedPath, "rb") as f:
        return f.read()

def cacheFileBytes(path: str, data: Union[bytes, str, list[Any]]) -> None:
    hashedPath = hashlib.sha256(path.encode("utf-8"), usedforsecurity=False).hexdigest()
    totalHashedPath = os.path.join("cached", hashedPath)

    if isinstance(data, str):
        dat = data.encode("utf-8")
    elif isinstance(data, list):
        dat = bytes(data)
    elif isinstance(data, bytes):
        dat = data
    else:
        raise TypeError(f"Data value was {type(data)}! expected bytes | str | list[Any]")

    os.makedirs("cached", exist_ok=True)

    with open(totalHashedPath, "wb") as f:
        f.write(dat)

def getOrCacheFileBytes(path: str, data: Union[bytes, str, list[Any]]) -> bytes:
    hashedPath = hashlib.sha256(path.encode("utf-8"), usedforsecurity=False).hexdigest()
    totalHashedPath = os.path.join("cached", hashedPath)

    if os.path.exists(totalHashedPath):
        with open(totalHashedPath, "rb") as f:
            return f.read()

    if isinstance(data, str):
        dat = data.encode("utf-8")
    elif isinstance(data, list):
        dat = bytes(data)
    elif isinstance(data, bytes):
        dat = data
    else:
        raise TypeError(f"Data value was {type(data)}! expected bytes | str | list[Any]")

    os.makedirs("cached", exist_ok=True)

    with open(totalHashedPath, "wb") as f:
        f.write(dat)

    return dat
