from ctypes import c_byte , c_ubyte , c_short , c_ushort , c_int , c_uint , c_long , c_ulong , c_longlong , c_ulonglong , c_size_t , c_ssize_t , c_time_t, c_void_p
from ctypes import c_float, c_double, c_longdouble
from ctypes import c_char_p, c_char
from ctypes import POINTER
from ctypes import c_bool
from typing import Union
from .types import _cdll_enum_arg

C_INTEGER_TYPES = [c_byte , c_ubyte , c_short , c_ushort , c_int , c_uint , c_long , c_ulong , c_longlong , c_ulonglong , c_size_t , c_ssize_t , c_time_t]
C_FLOAT_TYPES = [c_float, c_double, c_longdouble]

def mapStrCType(s:str) -> Union[type, None]:
    match s:
        case "i32":
            return c_int
        case "u32":
            return c_uint
        case "i16":
            return c_short
        case "u16":
            return c_ushort
        case "i64":
            return c_longlong
        case "u64":
            return c_ulonglong
        case "f32":
            return c_float
        case "f64":
            return c_double
        case "u8":
            return c_ubyte
        case "i8":
            return c_char
        case "char*":
            return c_char_p
        case "POINTER_i32":
            return POINTER(c_int)
        case "POINTER_u32":
            return POINTER(c_uint)
        case "POINTER_i16":
            return POINTER(c_short)
        case "POINTER_u16":
            return POINTER(c_ushort)
        case "POINTER_i64":
            return POINTER(c_longlong)
        case "POINTER_u64":
            return POINTER(c_ulonglong)
        case "POINTER_f32":
            return POINTER(c_float)
        case "POINTER_f64":
            return POINTER(c_double)
        case "POINTER_u8":
            return POINTER(c_ubyte)
        case "POINTER_i8":
            return POINTER(c_char)
        case "POINTER_char*":
            return POINTER(c_char_p)
        case "POINTER_void":
            return c_void_p
        case "Null":
            return None
        case _:
            raise ValueError(f"Unknown C type mapping for '{s}'")

def mapCType(t:Union[type, None]) -> str:
    # print(t)
    match t:
        # ints
        case t if t in [c_char, c_byte]:
            return "char"
        case t if t == c_ubyte:
            return "unsigned char"
        case t if t == c_short:
            return "short"
        case t if t == c_ushort:
            return "unsigned short"
        case t if t == c_int:
            return "int"
        case t if t == c_uint:
            return "unsigned int"
        case t if t == c_long:
            return "long"
        case t if t == c_ulong:
            return "unsigned long"
        case t if t == c_longlong:
            return "long long"
        case t if t == c_ulonglong:
            return "unsigned long long"
        # booleans
        case t if t == c_bool:
            return "bool"
        # pointers (int)

        case t if t in [POINTER(c_char), POINTER(c_byte)]:
            return "char*"
        case t if t == POINTER(c_char_p):
            return "char**"
        case t if t == POINTER(c_ubyte):
            return "unsigned char*"
        case t if t == POINTER(c_short):
            return "short*"
        case t if t == POINTER(c_ushort):
            return "unsigned short*"
        case t if t == POINTER(c_int):
            return "int*"
        case t if t == POINTER(c_uint):
            return "unsigned int*"
        case t if t == POINTER(c_long):
            return "long*"
        case t if t == POINTER(c_ulong):
            return "unsigned long*"
        case t if t == POINTER(c_longlong):
            return "long long*"
        case t if t == POINTER(c_ulonglong):
            return "unsigned long long*"
        # pointers (other)
        case t if t == c_void_p:
            return "void*"
        case t if t == c_char_p:
            return "char*"

        # float
        case t if t == c_float:
            return "float"
        case t if t == POINTER(c_float):
            return "float*"

        # other
        case t if t == None:
            return "void"
        case t if isinstance(t, _cdll_enum_arg):
            # print("Cast", t)
            return t.enumName
        # no match
        case _:
            raise ValueError(f"Unkown C type mapping for '{t}'")

def castCType(s:str, t:type) -> Union[int, float, bool, str, None]:
    match t:
        case t if t in C_INTEGER_TYPES:
            if s.startswith("0x"):
                return int(s, 16)
            return int(s)
        case t if t in C_FLOAT_TYPES:
            return float(s)
        case t if t == c_bool:
            return bool(s)
    raise Exception(f"Could not convert '{s}' from '{type(s)}' to '{type(t)}!'")
