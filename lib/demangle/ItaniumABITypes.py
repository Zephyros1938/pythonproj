from enum import Enum
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
    ASSIGN                  = "as"
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
    ARROW_STAR              = "pt"
    CONVERSION              = "cv"
    FUNCTION_POINTER        = "fp"  # Not standard—it may be internal

# Substitutions for common standard library names (Itanium ABI §5.1.9)
class CppStandardNamespaces(Enum):
    STD_ALLOCATOR       = "Sa"
    STD_BASIC_STRING    = "Sb"
    STD_STRING          = "Ss"
    STD_ISTREAM         = "Si"
    STD_OSTREAM         = "So"
    STD_IOSTREAM        = "Sd"
    STD_NAMESPACE       = "St"  # Represents 'std::'

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

def getFromItaniumABI(s: str):
    match s:
        VOID
    WCHAR_T
    BOOL
    CHAR
    SIGNED_CHAR
    UNSIGNED_CHAR
    SHORT
    UNSIGNED_SHORT
    INT
    UNSIGNED_INT
    LONG
    UNSIGNED_LONG
    LONG_LONG
    UNSIGNED_LONG_LONG
    INT128
    UNSIGNED_INT128
    FLOAT
    DOUBLE
    LONG_DOUBLE
    FLOAT128
    ELLIPSIS
