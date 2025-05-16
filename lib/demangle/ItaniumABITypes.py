from enum import Enum
from typing import Union, Any
#
# Taken from https://www.swag.uwaterloo.ca/acd/docs/ItaniumC++ABI.htm
#




class CppTypes(Enum):
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

# Type qualifiers
class CppQualifiers(Enum):
    CONST      = "K"
    VOLATILE   = "V"
    RESTRICT   = "r"

# Name prefixes / scopes used in mangled names
class CppNamePrefixes(Enum):
    LOCAL      = "L"  # Local or static function scope
    LAMBDA     = "Z"  # Lambdas or local classes/functions
    NESTED     = "N"  # Nested names (e.g., namespaces, classes)

# Type constructors and compound types
class CppCompoundTypes(Enum):
    POINTER             = "P"
    LVALUE_REFERENCE    = "R"
    RVALUE_REFERENCE    = "O"
    COMPLEX             = "C"
    IMAGINARY           = "G"
    POINTER_TO_MEMBER   = "M"  # Followed by class type

# Special type forms (Itanium ABI §5.1.8)
class CppSpecialForms(Enum):
    FUNCTION_TYPE       = "F"  # Begins a function type; ends with 'E'
    ARRAY_TYPE          = "A"  # Array type, followed by dimension
    TEMPLATE_PARAM      = "T"  # Template parameter, e.g., T_ or T1_
    SUBSTITUTION        = "S"  # Type or name substitution (S_, S1_, etc.)

# Operator encodings for overloaded operators (Itanium ABI §5.1.7)
class CppOperators(Enum):
    NEW                     = "nw"
    DELETE                  = "dl"
    NEW_ARRAY               = "na"
    DELETE_ARRAY            = "da"
    UNARY_PLUS              = "ps"
    UNARY_MINUS             = "ng"
    DEREFERENCE             = "de"
    ADDRESS_OF              = "ad"
    COMPLEMENT              = "co"
    INCREMENT               = "pp"
    DECREMENT               = "mm"
    ADD                     = "pl"
    SUBTRACT                = "mi"
    MULTIPLY                = "ml"
    DIVIDE                  = "dv"
    MODULO                  = "rm"
    BITWISE_AND             = "an"
    BITWISE_OR              = "or"
    BITWISE_XOR             = "eo"
    LOGICAL_AND             = "aa"
    LOGICAL_OR              = "oo"
    ASSIGN                  = "aS"
    PLUS_ASSIGN             = "pL"
    MINUS_ASSIGN            = "mI"
    MULTIPLY_ASSIGN         = "mL"
    DIVIDE_ASSIGN           = "dV"
    MODULO_ASSIGN           = "rM"
    BITWISE_AND_ASSIGN      = "aN"
    BITWISE_OR_ASSIGN       = "oR"
    BITWISE_XOR_ASSIGN      = "eO"
    SHIFT_LEFT              = "ls"
    SHIFT_RIGHT             = "rs"
    SHIFT_LEFT_ASSIGN       = "lS"
    SHIFT_RIGHT_ASSIGN      = "rS"
    EQUAL                   = "eq"
    NOT_EQUAL               = "ne"
    LESS_THAN               = "lt"
    GREATER_THAN            = "gt"
    LESS_EQUAL              = "le"
    GREATER_EQUAL           = "ge"
    CALL                    = "cl"
    INDEX                   = "ix"
    ARROW                   = "pt"
    ARROW_STAR              = "pm"
    CONVERSION              = "cv"
    FUNCTION_POINTER        = "fp"  # Not standard—it may be internal
CppOperatorsList = ['new', 'delete', 'new[]', 'delete[]', '+', '-', '*', '&', '~', '++', '--', '/', '%', '|', '^', '&&', '||', '=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<', '>>', '<<=', '>>=', '==', '!=', '<', '>', '<=', '>=', '()', '[]', '->', '->*']
# Substitutions for common standard library names (Itanium ABI §5.1.9)
class CppStandardNamespaces(Enum):
    STD_NAMESPACE       = "St"  # Represents 'std::'
    STD_ALLOCATOR       = "Sa"
    STD_BASIC_STRING    = "Sb"
    STD_STRING          = "Ss"
    STD_ISTREAM         = "Si"
    STD_OSTREAM         = "So"
    STD_IOSTREAM        = "Sd"

fixed_tokens = {
    # start
    "_Z",
    # namespaces
    CppStandardNamespaces.STD_ALLOCATOR.value,
    CppStandardNamespaces.STD_BASIC_STRING.value,
    CppStandardNamespaces.STD_STRING.value,
    CppStandardNamespaces.STD_ISTREAM.value,
    CppStandardNamespaces.STD_OSTREAM.value,
    CppStandardNamespaces.STD_IOSTREAM.value,
    CppStandardNamespaces.STD_NAMESPACE.value,
    # operators
    CppOperators.NEW.value,
    CppOperators.DELETE.value,
    CppOperators.NEW_ARRAY.value,
    CppOperators.DELETE_ARRAY.value,
    CppOperators.UNARY_PLUS.value,
    CppOperators.UNARY_MINUS.value,
    CppOperators.DEREFERENCE.value,
    CppOperators.ADDRESS_OF.value,
    CppOperators.COMPLEMENT.value,
    CppOperators.INCREMENT.value,
    CppOperators.DECREMENT.value,
    CppOperators.ADD.value,
    CppOperators.SUBTRACT.value,
    CppOperators.MULTIPLY.value,
    CppOperators.DIVIDE.value,
    CppOperators.MODULO.value,
    CppOperators.BITWISE_AND.value,
    CppOperators.BITWISE_OR.value,
    CppOperators.BITWISE_XOR.value,
    CppOperators.LOGICAL_AND.value,
    CppOperators.LOGICAL_OR.value,
    CppOperators.ASSIGN.value,
    CppOperators.PLUS_ASSIGN.value,
    CppOperators.MINUS_ASSIGN.value,
    CppOperators.MULTIPLY_ASSIGN.value,
    CppOperators.DIVIDE_ASSIGN.value,
    CppOperators.MODULO_ASSIGN.value,
    CppOperators.BITWISE_AND_ASSIGN.value,
    CppOperators.BITWISE_OR_ASSIGN.value,
    CppOperators.BITWISE_XOR_ASSIGN.value,
    CppOperators.SHIFT_LEFT.value,
    CppOperators.SHIFT_RIGHT.value,
    CppOperators.SHIFT_LEFT_ASSIGN.value,
    CppOperators.SHIFT_RIGHT_ASSIGN.value,
    CppOperators.EQUAL.value,
    CppOperators.NOT_EQUAL.value,
    CppOperators.LESS_THAN.value,
    CppOperators.GREATER_THAN.value,
    CppOperators.LESS_EQUAL.value,
    CppOperators.GREATER_EQUAL.value,
    CppOperators.CALL.value,
    CppOperators.INDEX.value,
    CppOperators.ARROW.value,
    CppOperators.ARROW_STAR.value,
    CppOperators.CONVERSION.value,
    CppOperators.FUNCTION_POINTER.value
}

def getTypeFromItaniumABI(s: Union[str, CppTypes]):
    if isinstance(s, str):
        s = getEnumKeyFromValue(CppTypes, s)
    match s:
        case CppTypes.VOID: return "void"
        case CppTypes.WCHAR_T: return "wchar_t"
        case CppTypes.BOOL: return "bool"
        case CppTypes.CHAR: return "char"
        case CppTypes.SIGNED_CHAR: return "signed char"
        case CppTypes.UNSIGNED_CHAR: return "unsigned char"
        case CppTypes.SHORT: return "short"
        case CppTypes.UNSIGNED_SHORT: return "unsigned short"
        case CppTypes.INT: return "int"
        case CppTypes.UNSIGNED_INT: return "unsigned int"
        case CppTypes.LONG: return "long"
        case CppTypes.UNSIGNED_LONG: return "unsigned long"
        case CppTypes.LONG_LONG: return "long long"
        case CppTypes.UNSIGNED_LONG_LONG: return "unsigned long long"
        case CppTypes.INT128: return "__int128"
        case CppTypes.UNSIGNED_INT128: return "unsigned __int128"
        case CppTypes.FLOAT: return "float"
        case CppTypes.DOUBLE: return "double"
        case CppTypes.LONG_DOUBLE: return "long double"
        case CppTypes.FLOAT128: return "__float128"
        case CppTypes.ELLIPSIS: return "..."
        case _: raise KeyError(f"Invalid Itanium ABI value: {s}")
def getQualifierFromItaniumABI(s: Union[str, CppQualifiers]):
    if isinstance(s, str):
        s = getEnumKeyFromValue(CppQualifiers, s)
    match s:
        case CppQualifiers.CONST: return "const"
        case CppQualifiers.VOLATILE: return "volatile"
        case CppQualifiers.RESTRICT: return "__restrict"
        case _: raise KeyError(f"Invalid Itanium ABI value: {s}")
def getOperatorFromItaniumABI(s: Union[str, CppOperators]):
    if isinstance(s, str):
        s = getEnumKeyFromValue(CppOperators, s)
    match s:
        case CppOperators.NEW: return "new"
        case CppOperators.DELETE: return "delete"
        case CppOperators.NEW_ARRAY: return "new[]"
        case CppOperators.DELETE_ARRAY: return "delete[]"
        case CppOperators.UNARY_PLUS: return "+"
        case CppOperators.UNARY_MINUS: return "-"
        case CppOperators.DEREFERENCE: return "*"
        case CppOperators.ADDRESS_OF: return "&"
        case CppOperators.COMPLEMENT: return "~"
        case CppOperators.INCREMENT: return "++"
        case CppOperators.DECREMENT: return "--"
        case CppOperators.ADD: return "+"
        case CppOperators.SUBTRACT: return "-"
        case CppOperators.MULTIPLY: return "*"
        case CppOperators.DIVIDE: return "/"
        case CppOperators.MODULO: return "%"
        case CppOperators.BITWISE_AND: return "&"
        case CppOperators.BITWISE_OR: return "|"
        case CppOperators.BITWISE_XOR: return "^"
        case CppOperators.LOGICAL_AND: return "&&"
        case CppOperators.LOGICAL_OR: return "||"
        case CppOperators.ASSIGN: return "="
        case CppOperators.PLUS_ASSIGN: return "+="
        case CppOperators.MINUS_ASSIGN: return "-="
        case CppOperators.MULTIPLY_ASSIGN: return "*="
        case CppOperators.DIVIDE_ASSIGN: return "/="
        case CppOperators.MODULO_ASSIGN: return "%="
        case CppOperators.BITWISE_AND_ASSIGN: return "&="
        case CppOperators.BITWISE_OR_ASSIGN: return "|="
        case CppOperators.BITWISE_XOR_ASSIGN: return "^="
        case CppOperators.SHIFT_LEFT: return "<<"
        case CppOperators.SHIFT_RIGHT: return ">>"
        case CppOperators.SHIFT_LEFT_ASSIGN: return "<<="
        case CppOperators.SHIFT_RIGHT_ASSIGN: return ">>="
        case CppOperators.EQUAL: return "=="
        case CppOperators.NOT_EQUAL: return "!="
        case CppOperators.LESS_THAN: return "<"
        case CppOperators.GREATER_THAN: return ">"
        case CppOperators.LESS_EQUAL: return "<="
        case CppOperators.GREATER_EQUAL: return ">="
        case CppOperators.CALL: return "()"
        case CppOperators.INDEX: return "[]"
        case CppOperators.ARROW: return "->"
        case CppOperators.ARROW_STAR: return "->*"
        case CppOperators.CONVERSION: raise Exception("Conversion operator not yet supported")
        case CppOperators.FUNCTION_POINTER: raise Exception("Function Pointer operator not yet supported")
        case _: raise KeyError(f"Invalid Itanium ABI value: {s}")
def getNamespaceFromItaniumABI(s: Union[str, CppStandardNamespaces]) -> list[str]:
    if isinstance(s, str):
        senum = getEnumKeyFromValue(CppStandardNamespaces, s)
    else:
        senum = s
    match senum:
        case CppStandardNamespaces.STD_NAMESPACE: return ["std"]
        case CppStandardNamespaces.STD_ALLOCATOR: return ["std", "allocator"]
        case CppStandardNamespaces.STD_BASIC_STRING: return ["std", "basic_string"]
        case CppStandardNamespaces.STD_STRING: return ["std", "string"]
        case CppStandardNamespaces.STD_ISTREAM: return ["std", "istream"]
        case CppStandardNamespaces.STD_OSTREAM: return ["std", "ostream"]
        case CppStandardNamespaces.STD_IOSTREAM: return ["std", "iostream"]
        case _: return list(s)
def getCompoundTypeFromItaniumABI(s: Union[str, CppCompoundTypes]):
    if isinstance(s, str):
        se = getEnumKeyFromValue(CppCompoundTypes, s)
    else:
        se = s
    match se:
        case CppCompoundTypes.POINTER: return "*"
        case CppCompoundTypes.LVALUE_REFERENCE: return "&"
        case CppCompoundTypes.RVALUE_REFERENCE: return "&&"
        case CppCompoundTypes.COMPLEX: return "COMPLEX"
        case CppCompoundTypes.IMAGINARY: return "i"
        case CppCompoundTypes.POINTER_TO_MEMBER: return "->*"
        case _: raise KeyError(f"Invalid Itanium ABI value: {s}")
def getSpecialFormFromItaniumABI(s: Union[str, CppSpecialForms]):
    if isinstance(s, str):
        se = getEnumKeyFromValue(CppSpecialForms, s)
    else:
        se = s
    match se:
        case CppSpecialForms.FUNCTION_TYPE: return
        case CppSpecialForms.ARRAY_TYPE: return
        case CppSpecialForms.TEMPLATE_PARAM: return
        case CppSpecialForms.SUBSTITUTION: return
        case _: raise KeyError(f"Invalid Itanium ABI value: {s}")
def getEnumKeyFromValue(enum, value: Any):
    for k, v in enum.__members__.items():
        # print(k, v.value)
        if v.value == value:
            # print(v)
            return v
    raise KeyError(f"{value} not found in {enum}!")
itanium_st = {
    'St': 'std',
    'Sa': 'std::allocator',
    'Sb': 'std::basic_string',
    'Ss': 'std::string',
    'Si': 'std::istream',
    'So': 'std::ostream',
    'Sd': 'std::iostream'
}
itanium_op = {
    'nw': 'operator new',
    'na': 'operator new[]',
    'dl': 'operator delete',
    'da': 'operator delete[]',
    'ps': 'operator+',
    'ng': 'operator-',
    'de': 'operator*',
    'ad': 'operator&',
    'co': 'operator~',
    'pp': 'operator++',
    'mm': 'operator--',
    'pl': 'operator+',
    'mi': 'operator-',
    'ml': 'operator*',
    'dv': 'operator/',
    'rm': 'operator%',
    'an': 'operator&',
    'or': 'operator|',
    'eo': 'operator^',
    'aS': 'operator=',
    'pL': 'operator+=',
    'mI': 'operator-=',
    'mL': 'operator*=',
    'dV': 'operator/=',
    'rM': 'operator%=',
    'aN': 'operator&=',
    'oR': 'operator|=',
    'eO': 'operator^=',
    'ls': 'operator<<',
    'rs': 'operator>>',
    'lS': 'operator<<=',
    'rS': 'operator>>=',
    'eq': 'operator==',
    'ne': 'operator!=',
    'lt': 'operator<',
    'gt': 'operator>',
    'le': 'operator<=',
    'ge': 'operator>=',
    'cl': 'operator()',
    'ix': 'operator[]',
    'pt': 'operator->',
    'pm': 'operator->*',
    'cv': 'operator '
}
itanium_symbols = {
    # Compound Types (CppCompoundTypes)
    'P': '*',                     # T* (pointer to T)
    'R': '&',           # T& (reference to T)
    'O': '&&',           # T&& (rvalue reference to T)
    'C': '_Complex',             # complex T (from C++)
    'G': '_Imaginary',           # imaginary T (from C++)
    'M': '::*',          # T X::* (pointer to member of class X)

    # Name Prefixes (CppNamePrefixes)
    'L': 'local name (block-scope)',   # e.g., lambda local variable
    'Z': '\00',
    'N': '\01',                # e.g., namespaces or nested classes

    # Operators (CppOperators)
    'nw': 'operator new',
    'na': 'operator new[]',
    'dl': 'operator delete',
    'da': 'operator delete[]',
    'ps': 'operator+',
    'ng': 'operator-',
    'de': 'operator*',
    'ad': 'operator&',
    'co': 'operator~',
    'pp': 'operator++',
    'mm': 'operator--',
    'pl': 'operator+',
    'mi': 'operator-',
    'ml': 'operator*',
    'dv': 'operator/',
    'rm': 'operator%',
    'an': 'operator&',
    'or': 'operator|',
    'eo': 'operator^',
    'aS': 'operator=',
    'pL': 'operator+=',
    'mI': 'operator-=',
    'mL': 'operator*=',
    'dV': 'operator/=',
    'rM': 'operator%=',
    'aN': 'operator&=',
    'oR': 'operator|=',
    'eO': 'operator^=',
    'ls': 'operator<<',
    'rs': 'operator>>',
    'lS': 'operator<<=',
    'rS': 'operator>>=',
    'eq': 'operator==',
    'ne': 'operator!=',
    'lt': 'operator<',
    'gt': 'operator>',
    'le': 'operator<=',
    'ge': 'operator>=',
    'cl': 'operator()',
    'ix': 'operator[]',
    'pt': 'operator->',
    'pm': 'operator->*',
    'cv': 'operator ',

    # Type Qualifiers (CppQualifiers)
    'K': 'const',
    'V': 'volatile',
    'r': '__restrict',

    # Special Forms (CppSpecialForms)
    'F': '\02',        # e.g., F_iE = function taking int
    'E': '\03',
    'A': 'array type',
    'T': '\04',
    'S': '\05',

    # Standard Namespaces (CppStandardNamespaces)
    'St': 'std',
    'Sa': 'std::allocator',
    'Sb': 'std::basic_string',
    'Ss': 'std::string',
    'Si': 'std::istream',
    'So': 'std::ostream',
    'Sd': 'std::iostream',

    # Built-in Types (CppTypes)
    'v': 'void',
    'w': 'wchar_t',
    'b': 'bool',
    'c': 'char',
    'a': 'signed char',
    'h': 'unsigned char',
    's': 'short',
    't': 'unsigned short',
    'i': 'int',
    'j': 'unsigned int',
    'l': 'long',
    'm': 'unsigned long',
    'x': 'long long',
    'y': 'unsigned long long',
    'n': '__int128',
    'o': 'unsigned __int128',
    'f': 'float',
    'd': 'double',
    'e': 'long double',
    'g': '__float128',
    'z': '...'
}
itanium_symbols_special = {
    '\00': '',
    '\01': '',
    '\02': '',
    '\03': '',
    '\04': '',
    '\05': ''
}
itanium_types = {
    'v': 'void',
    'w': 'wchar_t',
    'b': 'bool',
    'c': 'char',
    'a': 'signed char',
    'h': 'unsigned char',
    's': 'short',
    't': 'unsigned short',
    'i': 'int',
    'j': 'unsigned int',
    'l': 'long',
    'm': 'unsigned long',
    'x': 'long long',
    'y': 'unsigned long long',
    'n': '__int128',
    'o': 'unsigned __int128',
    'f': 'float',
    'd': 'double',
    'e': 'long double',
    'g': '__float128',
    'z': '...'
}
itanium_type_modifiers = {
    'K': 'const',
    'V': 'volatile',
    'r': 'restrict',
    'P': '*',                     # T* (pointer to T)
    'R': '&',           # T& (reference to T)
    'O': '&&',           # T&& (rvalue reference to T)
    'C': '_Complex',             # complex T (from C++)
    'G': '_Imaginary',           # imaginary T (from C++)
    'M': '::*',          # T X::* (pointer to member of class X)
}
