from ctypes import CDLL, POINTER
from ctypes import c_char_p, c_ubyte, c_int
from enum import Enum
import os
from typing import Any, Type, Union
LIBRARY_DIR = "./libraries"
COMPILED_DIR = os.path.join(LIBRARY_DIR, "compiled")

__initialized = False

_loaded_libraries: dict[str, CDLL] = {}
_loaded_enums: dict[str, type[Enum]] = {}

class LibraryStorage(dict):
    __libraries: dict[str, tuple[CDLL, dict[str, Enum]]] = {}

    @classmethod
    def _addLibrary(cls, libName: str, library: CDLL):
        cls.__libraries[libName] = (library, {})

    @classmethod
    def _getLibrary(cls, libName) -> CDLL:
        return cls.__libraries[libName][0]

    @classmethod
    def _addEnum(cls, libName: str, enumName: str, enum: Enum):
        cls.__libraries[libName][1][enumName] = enum

    @classmethod
    def _getEnum(cls, libName: str, enumName: str) -> Enum:
        return cls.__libraries[libName][1][enumName]



def getlib(libName: str) -> CDLL:
    return LibraryStorage._getLibrary(libName)
def getEnum(libName: str, enumName: str) -> Enum:
    return LibraryStorage._getEnum(libName, enumName)


class _cdll_enum_arg:
    def __init__ (self, enumName: str):
        self.enumName = enumName

class __cdll_function_def:
    def __init__(self, fname: str, argtypes: list = [], restype: Any = None):
        self.fname = fname
        self.argtypes = argtypes
        self.restype = restype

class _cdll_enum:
    def __init__(self, enumName: str, enumValues: Union[dict[str, int], list[str]] = {}):
        self.enumName = enumName
        self.enumValues = enumValues

class __cdll_enum_def:
    """Should be placed after the __cdll_enum definition in libraries"""
    def __init__(self, fname: str, argtypes: list[Union[Any, _cdll_enum_arg]], restype: Any = None):
        self.fname = fname
        _argtypes = []
        for a in argtypes:
            if isinstance(a, _cdll_enum):
                _argtypes.append(type(globals()[a.enumName]))
            else:
                _argtypes.append(a)
        self.argtypes = _argtypes
        self.restype = restype

libraries: dict[str, list[Union[__cdll_function_def, _cdll_enum, __cdll_enum_def]]] = {
    "stb_image":
        [
            __cdll_function_def
            (
                "stbi_set_flip_vertically_on_load",
                [c_int],
                None
            ),
            __cdll_function_def
            (
                "stbi_load",
                [c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int), c_int],
                POINTER(c_ubyte)
            ),
            __cdll_function_def(
                "stbi_image_free",
                [POINTER(c_ubyte)],
                None
            )
        ],
    "logger": [
        _cdll_enum
        (
            "LEVELS",
            ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
        ),
        __cdll_enum_def
        (
            "init",
            [_cdll_enum_arg("LEVELS")],
            None
        ),
        __cdll_enum_def
        (
            "log",
            [_cdll_enum_arg("LEVELS"), c_int, c_char_p],
            None
        )
    ]
}

def __cdll_enum_to_class(enum_name: str, enum_values):
    enum_type = Enum(enum_name, enum_values)

    class CTypesEnum(c_int):
        _values_ = enum_values
        _enumtype_ = enum_type
        _name_ = enum_name

        @classmethod
        def from_param(cls, obj):
            if obj in cls._values_:
                return cls(cls._values_[obj])


    for name, value in enum_values.items():
        setattr(CTypesEnum, name , CTypesEnum(value))
    return CTypesEnum

def __set_lib_funcs(lib: CDLL, libName: str, funcs: list[Union[__cdll_function_def, _cdll_enum, __cdll_enum_def]]):
    for f in funcs:
        if type(f) == __cdll_function_def:
            print(f"[LIB]   Setting function {libName}::{f.fname}")
            func = getattr(lib, f.fname)
            func.argtypes = f.argtypes
            func.restype = f.restype
        elif type(f) == _cdll_enum:
            print(f"[LIB]   Setting enum {libName}::{f.enumName}")
            if isinstance(f.enumValues, list):
                enumValues = {f.enumValues[i]: i for i in range(len(f.enumValues))}
            elif isinstance(f.enumValues, dict):
                enumValues = f.enumValues
            else:
                raise ValueError(f"f.enumValues was {f.enumValues}, expected list/dict.")
            enumClass = __cdll_enum_to_class(f.enumName, enumValues)
            globals()[f.enumName] = enumClass
            LibraryStorage._addEnum(libName, f.enumName, enumClass._enumtype_)
        elif type(f) == __cdll_enum_def:
            print(f"[LIB]   Setting enum function {libName}::{f.fname}")
            func = getattr(lib, f.fname)
            _argtypes = []
            for f_ in f.argtypes:
                if type(f_) == _cdll_enum_arg:
                    _argtypes.append(globals()[f_.enumName])
                else:
                    _argtypes.append(f_)
            func.argtypes = _argtypes
            func.restype = f.restype

def __load_library(libname: str) -> CDLL:
    if os.name == "posix":
        lib_path = os.path.abspath(os.path.join(COMPILED_DIR, libname, f"{libname}.so"))
    elif os.name == "nt":
        lib_path = os.path.abspath(os.path.join(COMPILED_DIR, libname, f"{libname}.dll"))
    else:
        raise OSError("Unsupported operating system: " + os.name)

    try:
        lib = CDLL(lib_path)
        globals()[libname] = lib
        return lib
    except Exception as e:
        raise Exception(f"[ERROR] Failed to load library {libname}: {e}")

def init():
    global __initialized
    if __initialized:
        raise Exception("[ERROR] Libraries already initialized, cannot initialize again.")
    print("[LIB] Initializing libraries")
    for lib, items in libraries.items():
        print(f"[LIB]  Loading library {lib}")
        l = __load_library(lib)
        LibraryStorage._addLibrary(lib, l)
        __set_lib_funcs(l, lib, items)
    __initialized = True
