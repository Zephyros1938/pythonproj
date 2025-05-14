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
        plist = parse_mangled_name(symbol)
        justlen = 150
        print(f"[{start: 8}]: {" ".join([x for x in plist])} ({symbol})")

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

def parse_mangled_name(s: str):
    parts = []
    print("s:", s)

    # extract the leading mangling prefix, like _ZN
    prefix_match = regex.match(PREFIX_MATCH, s)
    if prefix_match:
        prefix = prefix_match.group(1)
        # print("pre", prefix)
        parts.append(prefix)
        s = s[len(prefix):]
    operator_match = regex.match(OPERATOR_MATCH, s)
    if operator_match:
        op = operator_match.group(1)
        if op:
            parts.append(op)
            s = s[len(op):]


    # parse length-prefixed names

    i = 0
    length = 0
    while i < len(s):
        # Match a number indicating the length
        length_match = regex.match(r'(\d+)', s[i:])
        if not length_match:
            break

        length_str = length_match.group(1)
        length = int(length_str)
        i += len(length_str)
        # m = regex.match(r'ls*', s[i:i+length])
        # print(i, i+length, s[i:i+length])

        name = s[i:i+length]
        if not name:
            break
        # print(name)

        # parts.append(length_str)
        parts.append(name)
        i += length

    if(i < len(s)):
        remaining = s[i:]
        # print("R:", remaining)
        return_match = regex.match(RETURN_MATCH, remaining)
        # print("rm", return_match)
        if return_match:
            print("p:", return_match.group(1))
            parts.append(return_match.group(1))
        elif remaining.startswith("I"):
            remaining_processed = parse_mangled_name(remaining)
            print("I:", remaining_processed)
            # if len(remaining_processed) > 0:
            #     if remaining_processed[0].startswith("I"):
            #         remaining_temp = remaining_processed[1:]
            #         remaining_processed = ["I", remaining_processed[0].replace("I","")]
            #         [remaining_processed.append(x) for x in remaining_temp]
            [parts.append(n) for n in remaining_processed]
        elif remaining.startswith("E"):
            remaining_processed = parse_mangled_name(remaining)
            print("E:", remaining_processed)
            [parts.append(p) for p in remaining_processed]

    # parts[0] = parts[0].replace("_Z", "")
    parts = [p for p in parts if p != '']
    return parts

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
    NESTED = "N"

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

class CppOperators(Enum):
    OPERATOR            = "ls"

# Helper function for known substitutions or standard types
class CppStandardSubstitutions(Enum):
    STD_ALLOCATOR       = "Sa"
    STD_BASIC_STRING    = "Sb"
    STD_STRING          = "Ss"
    STD_ISTREAM         = "Si"
    STD_OSTREAM         = "So"
    STD_IOSTREAM        = "Sd"
    STD_NAMESPACE       = "St" # Represents 'std::'

PREFIX_MATCH = fr'^(E?(_Z)?I?[\
    ({CppSymbolLinkage.NESTED.value})\
    ({CppQualifiers.CONST.value})\
    ({CppQualifiers.VOLATILE.value})\
    ({CppSpecialForms.TEMPLATE_PARAM.value})\
    ({CppCompoundTypes.LVALUE_REFERENCE.value})\
    ({CppStandardSubstitutions.STD_NAMESPACE.value})\
    ({CppStandardSubstitutions.STD_ALLOCATOR.value})\
    ({CppStandardSubstitutions.STD_BASIC_STRING.value})\
    ({CppStandardSubstitutions.STD_STRING.value})\
    ({CppStandardSubstitutions.STD_ISTREAM.value})\
    ({CppStandardSubstitutions.STD_OSTREAM.value})\
    ({CppStandardSubstitutions.STD_IOSTREAM.value})\
    ]*)'

OPERATOR_MATCH = fr'^([\
({CppOperators.OPERATOR.value})\
]*)'

RETURN_MATCH = fr'(E?[\
({CppTypes.VOID.value})\
({CppTypes.WCHAR_T.value})\
({CppTypes.BOOL.value})\
({CppTypes.CHAR.value})\
({CppTypes.SIGNED_CHAR.value})\
({CppTypes.UNSIGNED_CHAR.value})\
({CppTypes.SHORT.value})\
({CppTypes.UNSIGNED_SHORT.value})\
({CppTypes.INT.value})\
({CppTypes.UNSIGNED_INT.value})\
({CppTypes.LONG.value})\
({CppTypes.UNSIGNED_LONG.value})\
({CppTypes.LONG_LONG.value})\
({CppTypes.UNSIGNED_LONG_LONG.value})\
({CppTypes.INT128.value})\
({CppTypes.UNSIGNED_INT128.value})\
({CppTypes.FLOAT.value})\
({CppTypes.DOUBLE.value})\
({CppTypes.LONG_DOUBLE.value})\
({CppTypes.FLOAT128.value})\
({CppTypes.ELLIPSIS.value})\
]+)$'
