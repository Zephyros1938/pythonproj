import re
from typing import Union, Dict, TypeAlias
from . import ItaniumABITypes

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

def demangleABI(path: str): # main
    print("path", path)
    mangledNames = getMangledABI(path)
    symbols: TreeDict = {}
    for start, symbol in mangledNames.items():
        plist = []
        chunkedSymbols = chunkMangledName(symbol)
        for i in range(len(chunkedSymbols)):
            sym = chunkedSymbols[i]
            if i in range(1, len(chunkedSymbols)-1):
                if chunkedSymbols[i-1] in ["S", "T"] and chunkedSymbols[i+1] == "_":
                    plist.append(chunkedSymbols[i])
            if not sym.isnumeric():
                plist.append(sym)
        # [plist.append(sym) for sym in chunkMangledName(symbol) if not sym.isnumeric()]
        print(f"[{hex(start):<8}]: {" ".join([x for x in plist])} ({symbol})")
        print("\tParsed: "+parseMangledString(symbol))

def parseMangledString(s: str) -> str:
    sym=s[2:]
    out=""

    # print(sym)

    def processFunctionSpecifier():
        nonlocal sym, out
        print(sym, out)
        if "I" == sym[:1]:
            sym = sym[1:]
            out += "<"
            while "E" != sym[:1]:
                process()
                out += ","
            sym = sym[1:]
            out = out[:-1]
            out += ">"

    def process():
        nonlocal sym, out
        if sym[:2] in ItaniumABITypes.itanium_st:
            out += ItaniumABITypes.itanium_st[sym[:2]] + "::"
            sym = sym[2:]
        if sym[:2] in ItaniumABITypes.itanium_op:
            out += ItaniumABITypes.itanium_op[sym[:2]]
            sym = sym[2:]
        if "N" == sym[:1]:
            sym = sym[1:]
            while "E" != sym[:1]:
                process()
                out += "::"
            sym = sym[1:]
        processFunctionSpecifier()
        lengthMatch = re.match(r'\d+', sym)
        if lengthMatch:
            length = int(lengthMatch[0])
            lengthStr = len(str(length))
            out += sym[lengthStr:length+lengthStr]
            sym = sym[lengthStr+length:]
        processFunctionSpecifier()

    process()

    if sym:
        out += "("
        while sym:
            process()
            out += "," if sym else ")"

    return out


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
                if "@" in symbol:
                    i+=1
                    continue
                symbol = symbol.split('@')[0]  # strip GLIBCXX version info
                if isMangledABISymbol(symbol):
                    mangledNames[start] = symbol
            except UnicodeDecodeError:
                pass
            i = end
        else:
            i += 1
    return mangledNames
def chunkMangledName(s: str) -> list[str]:
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
            if two_chars in ItaniumABITypes.fixed_tokens:
                tokens.append(two_chars)
                i += 2
                continue

        # Try substitutions S<number>_
        sub_match = substitution_pattern.match(s, i)
        if sub_match:
            full_sub = sub_match.group(0)
            # print("Substitution", full_sub)
            tokens.append(full_sub)
            i += len(full_sub)
            continue

        # Try template params T_, T0_, T1_ ...
        temp_match = template_param_pattern.match(s, i)
        if temp_match:
            full_temp = temp_match.group(0)
            # print("Temp ", full_temp)
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
def parseMangledChunks2(mangled: list[str]):
    parsed = []
    argTypes = []
    typeModifiers = []
    nested = False
    functionParameterDepth = 0
    skip = False

    i = 0
    def isArgsSection(args: list[str]):
        for arg in args:
            if arg in ItaniumABITypes.itanium_types or arg in ItaniumABITypes.itanium_type_modifiers:
                continue
            elif arg not in ItaniumABITypes.itanium_symbols:
                print("ARG:", arg)
            return False
        return True
    while i < len(mangled):
        token = mangled[i]
        if token == "":
            i+=1
            continue
        print(i, token)
        if token == "I":
            functionParameterDepth += 1
            parsed.append("<")
            i+=1
            continue
        if functionParameterDepth >= 1:
            if token == "E":
                functionParameterDepth -= 1
                parsed.append(">")
                i+=1
                continue


        if isArgsSection(mangled[i:]):
            if token in ItaniumABITypes.itanium_types:
                argTypes.append(ItaniumABITypes.itanium_types[token] + " ".join(typeModifiers))
                typeModifiers.clear()
                i+=1
                continue

        if token in ItaniumABITypes.itanium_symbols:
            if token in ItaniumABITypes.itanium_type_modifiers:
                typeModifiers.append(ItaniumABITypes.itanium_type_modifiers[token])
            else:
                parsed.append(ItaniumABITypes.itanium_symbols[token])
        else:
            print("NE:", token, argTypes)
            parsed.append(token)
        # if token in ItaniumABITypes.itanium_type_modifiers:
        #     print(argTypes)
        #     if argTypes != []:
        #         argTypes[-1]+=ItaniumABITypes.itanium_type_modifiers[token]

        i+=1
    if len(argTypes) > 0 and argTypes != ["void"]:
        parsed.append("(")
        parsed.append(", ".join(argTypes))
        parsed.append(")")
    elif argTypes == ["void"]:
        parsed.append("(")
        parsed.append(")")

    parsedFinal = parsed[:]
    i = 0
    while i < len(parsed):
        p = parsed[i]
        print(f"F: [{p.encode("utf-8")}]")
        if p in ItaniumABITypes.itanium_symbols_special:
            i+=1
            continue
        if p not in ["(",")","<",">"] and parsedFinal[i+1] not in ["(",")","<",">"] and parsedFinal[i] != "::":
            parsedFinal.insert(i+1, "::")
        i +=1

    return parsedFinal
def parseMangledChunks(tokens: list[str], tree: dict) -> str:
    templateSet: dict[int, list[str]] = {}
    substitutions: list[str] = []

    storedCompoundTypes = []
    storedQualifiers = []
    nested = False
    functionMakeDepth = 0
    returnSet = False

    nameParts = []
    argTypes = []
    returnType = ""

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == "N":
            nested = True
            i += 1
            continue
        elif token == "E":
            nested = False
            i += 1
            continue
        elif token == "I":
            functionMakeDepth += 1
            templateSet[functionMakeDepth] = []
            i += 1
            continue

        try:
            # Namespace or identifier
            namespaces = ItaniumABITypes.getNamespaceFromItaniumABI(token)
            nameParts.extend(namespaces)
            i += 1
            continue
        except KeyError:
            pass

        try:
            storedCompoundTypes.append(ItaniumABITypes.getCompoundTypeFromItaniumABI(token))
            i += 1
            continue
        except KeyError:
            pass

        try:
            ty = " ".join(storedQualifiers) + " " if storedQualifiers else ""
            ty += ItaniumABITypes.getTypeFromItaniumABI(token)
            ty += "".join(storedCompoundTypes)
            storedQualifiers.clear()
            storedCompoundTypes.clear()

            # if not returnSet:
            #     returnType = ty
            #     returnSet = True
            # else:
            argTypes.append(ty)
            i += 1
            continue
        except KeyError:
            pass

        try:
            op = ItaniumABITypes.getOperatorFromItaniumABI(token)
            nameParts.append(f"operator{op}")
            i += 1
            continue
        except KeyError:
            pass

        try:
            qu = ItaniumABITypes.getQualifierFromItaniumABI(token)
            storedQualifiers.append(qu)
            i += 1
            continue
        except KeyError:
            pass

        if token.startswith("T"):
            nameParts.append(token)
        elif token not in ["I", "E"]:
            nameParts.append(token)

        i += 1

    qualifiedName = "::".join(nameParts)
    argsFormatted = ", ".join(argTypes)
    returnTypePrefix = f"{returnType} " if returnType else ""
    finalSignature = f"{returnTypePrefix}{qualifiedName}({argsFormatted})"
    return finalSignature
