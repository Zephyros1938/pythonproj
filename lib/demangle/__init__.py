import re
from typing import Union, Dict, TypeAlias
from .ItaniumABITypes import fixed_tokens

NUMERICS = [1,2,3,4,5,6,7,8,9,0]
VALID_MANGLED_CHARS = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@$."

TreeDict: TypeAlias = Dict[
    str, # Namespace / Class
    Union
        [
        tuple # Method
            [
            str, # Method name
            list # Method args
                [
                Union
                    [
                    str, # One version of method
                        # ex: fun(int) -> _Z3funi
                    list # Method with overloads
                        # ex: fun(int) -> _Z3funi
                        # ex: fun(float) -> _Z3funf
                        [
                        str
                    ]
                ]
            ]
        ],
        'TreeDict' # Nested namespace/class
    ]
]

def demangleABI(path: str):
    print("path", path)
    mangledNames = getMangledABI(path)
    symbols: TreeDict = {}
    for start, symbol in mangledNames.items():
        plist = []
        [plist.append(sym) for sym in chunk_mangled_name(symbol) if not sym.isnumeric()]
        print(f"[{start: 8}]: {" ".join([x for x in plist])} ({symbol})")

def isValidMangledChar(c: bytes):
    assert len(c) == 1
    return c in VALID_MANGLED_CHARS

def isMangledABISymbol(symbol: str) -> bool:
    return symbol.startswith("_Z") and re.match(r"^_Z[\w\d@.]+$", symbol) is not None

def getMangledABI(path: str) -> dict[int, str]:
    mangledNames: dict[int, str] = {}
    with open(path, "rb") as file:
        data = file.read()
    i = 0
    while i < len(data) - 2:
        if(data[i:i+2]==b'_Z'):
            start = i
            end = i + 2
            while end < len(data) and isValidMangledChar(data[end:end+1]):
                end += 1
            try:
                symbol = data[start:end].decode('ascii')
                symbol = symbol.split('@')[0]  # strip GLIBCXX version info
                if isMangledABISymbol(symbol):
                    mangledNames[start] = symbol
            except UnicodeDecodeError:
                pass
            i = end
        else:
            i += 1
    return mangledNames

def chunk_mangled_name(s: str) -> list[str]:
    tokens = []
    i = 0



    # Pattern for substitutions like S<number>_
    substitution_pattern = re.compile(r'S(\d+)_')

    # Pattern for template parameter like T_, T0_, T1_ ...
    template_param_pattern = re.compile(r'T(\d*)_')

    if s.startswith("_Z"):
        # tokens.append("_Z")
        i = 2

    while i < len(s):
        # Try to match fixed tokens (two-char fixed tokens)
        if i + 1 < len(s):
            two_chars = s[i:i+2]
            if two_chars in fixed_tokens:
                tokens.append(two_chars)
                i += 2
                continue

        # Try substitutions S<number>_
        sub_match = substitution_pattern.match(s, i)
        if sub_match:
            full_sub = sub_match.group(0)
            tokens.append(full_sub)
            i += len(full_sub)
            continue

        # Try template params T_, T0_, T1_ ...
        temp_match = template_param_pattern.match(s, i)
        if temp_match:
            full_temp = temp_match.group(0)
            tokens.append(full_temp)
            i += len(full_temp)
            continue

        # Length-prefixed identifiers
        if s[i].isdigit():
            length_match = re.match(r'(\d+)', s[i:])
            if length_match:
                length_str = length_match.group(1)
                length = int(length_str)
                i += len(length_str)
                name = s[i:i + length]
                tokens.append(length_str)
                tokens.append(name)
                i += length
                continue
            else:
                raise ValueError(f"Malformed length prefix at position {i}")

        # Otherwise, single char token
        tokens.append(s[i])
        i += 1

    assert "".join(tokens) == s[2:], "Tokens do not reassemble original string"
    return tokens
