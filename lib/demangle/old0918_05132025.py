from . import *
def isStdSymbol(mangled: str) -> bool:
    if mangled.startswith("_ZSt") or mangled.startswith("_ZNSt"):
        return True
    if mangled.startswith("_ZNS") or mangled.startswith("_ZNKSt"):
        return True
    return False





def getStdNamespaceFromSymbol(symbol: str) -> str:
    s = symbol.replace("_Z", "")
    if s.startswith(CppSpecialForms.STD_NAMESPACE.value): return "std"
    elif s.startswith(CppStandardSubstitutions.STD_ALLOCATOR.value): return "std::allocator"
    elif s.startswith(CppStandardSubstitutions.STD_BASIC_STRING.value): return "std::basic_string"
    elif s.startswith(CppStandardSubstitutions.STD_STRING.value): return "std::string"
    elif s.startswith(CppStandardSubstitutions.STD_ISTREAM.value): return "std::istream"
    elif s.startswith(CppStandardSubstitutions.STD_OSTREAM.value): return "std::ostream"
    elif s.startswith(CppStandardSubstitutions.STD_IOSTREAM.value): return "std::iostream"
    raise Exception(f"Could not get std symbol {symbol}")

def getFuncFromSymbol(symbol: str) -> str:
    s = symbol.replace("_Z", "")

    # Handle standard library substitutions
    try:
        return getStdNamespaceFromSymbol(s)
    except:
        pass

    # nested name (N...E) structure
    if s.startswith("N"):
        # print("Entering nested", symbol)
        s = s[1:]  # Remove leading 'N'
        # print("Nested", s)

        try:
            return getStdNamespaceFromSymbol(s)
        except:
            pass

        if not s[0].isdigit():
            raise ValueError(f"Invalid nested name: {symbol}")

        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            if j == i:
                break  # no digits found
            length = int(s[i:j])
            i = j
            name = s[i:i+length]
            return name  # return first namespace component
        raise ValueError(f"Could not parse nested name: {symbol}")

    # non-nested names with numeric prefix (ex. 4test)
    elif s[0].isdigit():
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        length = int(s[:i])
        return "" # s[i:i+length]
    elif s.startswith(CppSymbolLinkage.LOCAL.value):
        return getFuncFromSymbol(symbol.replace("_ZL", "_Z"))
    elif s.startswith(CppSymbolLinkage.LAMBDA.value):
        return getFuncFromSymbol(symbol.replace("_ZZ", "_Z"))

    raise Exception(f"Could not get namespace of {symbol}")


class Symbol:
    full: str
    ns: str
    def __init__(self, fullSymbol: str):
        self.full = fullSymbol
        self.ns = getFuncFromSymbol(fullSymbol)
