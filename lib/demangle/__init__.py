import re as regex
from enum import Enum
from ..types import TreeDict

NUMERICS = [1,2,3,4,5,6,7,8,9,0]
VALID_MANGLED_CHARS = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@$."



def demangleABI(path: str):
    print("path", path)
    mangledNames = getMangledABI(path)
    symbols: TreeDict = {}
    for start, symbol in mangledNames.items():
        print(f"[{start: 8}]: {symbol}")

def isValidMangledChar(c: bytes):
    return c in VALID_MANGLED_CHARS

def isMangledABISymbol(symbol: str) -> bool:
    return symbol.startswith("_Z") and regex.match(r"^_Z[\w\d@.]+$", symbol) is not None

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




class CppTypes(Enum):
    # Fundamental types
    VOID                = "v"
    WCHAR_T             = "w"
    BOOL                = "b"
    CHAR                = "c"
    SIGNED_CHAR         = "a"
    UNSIGNED_CHAR       = "h"
    SHORT               = "s"
    UNSIGNED_SHORT      = "t"
    INT                 = "i"
    UNSIGNED_INT        = "j"
    LONG                = "l"
    UNSIGNED_LONG       = "m"
    LONG_LONG           = "x"
    UNSIGNED_LONG_LONG  = "y"
    INT128              = "n"
    UNSIGNED_INT128     = "o"
    FLOAT               = "f"
    DOUBLE              = "d"
    LONG_DOUBLE         = "e"
    FLOAT128            = "g"
    ELLIPSIS            = "z"

class CppQualifiers(Enum):
    CONST      = "K"
    VOLATILE   = "V"
    RESTRICT   = "r"

class CppSymbolLinkage(Enum):
    LOCAL = "L"  # internal linkage
    LAMBDA = "Z" # lamba / local function object

class CppCompoundTypes(Enum):
    POINTER             = "P"
    LVALUE_REFERENCE    = "R"
    RVALUE_REFERENCE    = "O"
    COMPLEX             = "C"
    IMAGINARY           = "G"
    POINTER_TO_MEMBER   = "M"  # Used with class type following it

class CppSpecialForms(Enum):
    FUNCTION_TYPE       = "F"  # Must be followed by parameters and closed with 'E'
    ARRAY_TYPE          = "A"  # Followed by size and type, ends with '_'
    TEMPLATE_PARAM      = "T"  # Followed by a digit
    SUBSTITUTION        = "S"  # Followed by other markers (e.g., 'S_' or 'S1_')
    STD_NAMESPACE       = "St" # Represents 'std::'

# Helper function for known substitutions or standard types
class CppStandardSubstitutions(Enum):
    STD_ALLOCATOR       = "Sa"
    STD_BASIC_STRING    = "Sb"
    STD_STRING          = "Ss"
    STD_ISTREAM         = "Si"
    STD_OSTREAM         = "So"
    STD_IOSTREAM        = "Sd"
