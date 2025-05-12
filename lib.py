from ctypes import CDLL, POINTER, c_char_p, c_ubyte, c_int
from dataclasses import dataclass
from enum import Enum, EnumMeta
from typing import Any, Union
import os

cstr = lambda s: s.encode('utf-8')

#
# Try not to use globals(), but rather LibraryStorage. If you are-
# unable to use LibraryStorage, use __local_storage, but only in-
# the last-case scenario.
#
# This is because definitions to globals() may cause issues if-
# they have the same name as anything defined inside of this-
# file.
#
# If you edit this file, you MUST put your username, what changes you-
# put, and the date. This file is essential to this project and must-
# function correctly.
#
# - Zephyros1938
#

__LIBRARY_DIR = "./libraries"
__COMPILED_DIR = os.path.join(__LIBRARY_DIR, "compiled")

__local_storage: dict[str, Any] = {};
__initialized = False

# Metaclass fro C-Style enums
@dataclass(init=False)
class CEnumMeta(type):
    _enumtype_: Union[EnumMeta, None]
    _values_ : dict[Any, Any]
    _name_: str
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # auto extracts metadata if enum base is present
        enum_base = next((b for b in bases if isinstance(b, EnumMeta)), None)
        if enum_base:
            cls._enumtype_ = enum_base
            cls._values_ = {getattr(e, "_name_"): getattr(e, "_value_") for e in enum_base}
            cls._name_ = name
        else:
            cls._enumtype_ = None
            cls._values_ = {}
            cls._name_ = name
        return cls

class __LibraryStorage(dict):
    """Used to store libraries"""
    __libraries: dict[str, tuple[CDLL, dict[str, type]]] = {}

    @classmethod
    def _addLibrary(cls, libName: str, library: CDLL):
        """Adds a library to the librarystorage"""
        cls.__libraries[libName] = (library, {})

    @classmethod
    def _getLibrary(cls, libName) -> CDLL:
        """Gets a library from the librarystorage"""
        return cls.__libraries[libName][0]

    @classmethod
    def _addEnum(cls, libName: str, enumName: str, enum: type):
        """Adds an enum to the specified library"""
        cls.__libraries[libName][1][enumName] = enum

    @classmethod
    def _getEnum(cls, libName: str, enumName: str) -> type :
        """Gets a enum from the specified library"""
        return cls.__libraries[libName][1][enumName]

def getlib(libName: str) -> CDLL:
    """Returns the specified library"""
    return __LibraryStorage._getLibrary(libName)
def getEnum(libName: str, enumName: str):
    """Returns the specified library's enum"""
    return __LibraryStorage._getEnum(libName, enumName)
def getEnumV(libName: str, enumName: str, valueName: str):
    """Returns the specified library's enum value"""
    return getattr(getEnum(libName, enumName), valueName).value

class _cdll_enum_arg:
    """Used when using an enum in a __cdll_function_def"""
    def __init__ (self, enumName: str):
        self.enumName = enumName

class _cdll_enum:
    """A container for C-Style Enums"""
    def __init__(self, enumName: str, enumValues: Union[dict[str, Any], list[str]] = {}):
        self.enumName = enumName
        self.enumValues = enumValues

class __cdll_function_def:
    """Used to define functions for CDLL\nThis should be placed after any _cdll_enum definitions if they are used in argtypes"""
    def __init__(self, fname: str, argtypes: list[Union[Any, _cdll_enum_arg]], restype: Any = None):
        self.fname = fname
        _argtypes = []
        for a in argtypes:
            if isinstance(a, _cdll_enum):
                _argtypes.append(__local_storage[a.enumName])
            else:
                _argtypes.append(a)
        self.argtypes = _argtypes
        self.restype = restype

def __dict_enum_to_c_enum(enum_name: str, enum_values: dict[str, int]):
    """Converts a dictionary to a C-style enum."""
    enum_type = Enum(enum_name + "Enum", enum_values)

    class CEnumWrapper(metaclass=CEnumMeta):
        """A C-Style enum wrapper

        This is used because C-Style enums when used with CDLL must be formatted as classes
        """
        def __init__(self, value: int | str):
            if isinstance(value, str):
                self.value = type(enum_type)[value].value
            elif isinstance(value, int):
                self.value = value
            else:
                raise TypeError(f"Invalid value type: {type(value)}")

        @classmethod
        def from_param(cls, obj):
            return c_int(cls(obj).value)

        def __int__(self):
            return self.value

        def __hash__(self):
            return hash(self.value)

        def __repr__(self):
            for k, v in self._values_.items():
                if v == self.value:
                    return f"<{self._name_}.{k}: {v}>"
            return f"<{self._name_}.UNKNOWN: {self.value}>"

    # attach enum contents
    for name, val in enum_values.items():
        setattr(CEnumWrapper, name, CEnumWrapper(val))

    return CEnumWrapper


def __set_lib_contents(lib: CDLL, libName: str, funcs: list[Union[__cdll_function_def, _cdll_enum]]):
    """Sets all of the library's contents"""
    for f in funcs:
        if isinstance(f, __cdll_function_def):
            print(f"[LIB INFO]   Setting function {libName}::{f.fname}")
            func = getattr(lib, f.fname)
            _argtypes = []
            for f_ in f.argtypes:
                if type(f_) == _cdll_enum_arg:
                    _argtypes.append(__LibraryStorage._getEnum(libName, f_.enumName))
                else:
                    _argtypes.append(f_)
            func.argtypes = _argtypes
            func.restype = f.restype
        elif isinstance(f, _cdll_enum):
            print(f"[LIB INFO]   Setting enum {libName}::{f.enumName}")
            if isinstance(f.enumValues, list):
                enumValues = {f.enumValues[i]: i for i in range(len(f.enumValues))}
            elif isinstance(f.enumValues, dict):
                enumValues = f.enumValues
            else:
                raise ValueError(f"f.enumValues was {f.enumValues}, expected list/dict.")
            enumClass = __dict_enum_to_c_enum(f.enumName, enumValues)
            __LibraryStorage._addEnum(libName, f.enumName, enumClass)

def __load_library(libname: str) -> CDLL:
    """Loads the specified library"""
    if os.name == "posix": # Linux/Mac
        lib_path = os.path.abspath(os.path.join(__COMPILED_DIR, libname, f"{libname}.so"))
    elif os.name == "nt": # Windows
        lib_path = os.path.abspath(os.path.join(__COMPILED_DIR, libname, f"{libname}.dll"))
    else:
        raise OSError("[LIB ERROR] Unsupported operating system: " + os.name)

    try:
        lib = CDLL(lib_path)
        __local_storage[libname] = lib
        return lib
    except Exception as e:
        raise Exception(f"[LIB ERROR] Failed to load library {libname}: {e}")

libs: dict[str, list[Union[__cdll_function_def, _cdll_enum]]] = {}
with open("./libs.pylib") as file:
    def getCType(s:str) -> Union[type, None]:
        match s:
            case "i32":
                return c_int
            case "POINTER_i32":
                return POINTER(c_int)
            case "POINTER_u8":
                return POINTER(c_ubyte)
            case "char*":
                return c_char_p
            case "Null":
                return None
        raise Exception(f"Could not find type of value [{s}]!")

    class fun:
        def __init__(self):
            self.name = '\0'
            self.values = []
            self.res = c_int
            self.finish = False
        name: str = "\0"
        values: list[Any] = []
        res: Any
        finish: bool = False

    class en:
        def __init__(self):
            self.values = {}
            self.finish = False
        name: str
        values: dict[str, tuple[type, Any]] = {}
        finish: bool = False

    class libr:
        def __init__(self):
            self.data = []
        name: str
        data: list[Union[fun, en]] = []

    currentLibrary = libr()
    currentDef = fun()
    currentEnum = en()
    line = file.readline()
    lineindex = 0
    librs: list[libr] = []
    while line:
        line = line.strip()
        if lineindex >= 5:
            if line.startswith("//"):
                print(f"Skipping Line {lineindex}")
            if line.startswith("LIBRARY"):
                currentLibrary.name = line[8:]
                # print("LIB")
            if line.startswith("ENDLIBRARY"):
                if currentLibrary.name.startswith('\0'):
                    # print("Skipping Library")
                    pass
                else:
                    librs.append(currentLibrary)
                    currentLibrary = libr()
                # print("ENDLIBRARY")
            if line.startswith("F."):
                call = line[2:].strip()
                if call.startswith("DEF"):
                    currentDef = fun()
                    # print("DEF", line[6:])
                    currentDef.name = call[4:]
                    currentDef.finish = False
                elif call.startswith("ARG"):
                    if currentDef.finish:
                        raise Exception(f"Def [{call}] Already Finished!")
                    # print("ARG", line[6:])
                    if line[6:10] == "ENUM":
                        for t in [v for v in currentLibrary.data if type(v) == en]:
                            if t.name == line[11:]:
                                currentDef.values.append(t)
                                break
                        else:
                            raise Exception(f"Could not get enum '{line[11:]}'")
                    else:
                        currentDef.values.append(getCType(line[6:]))
                elif call.startswith("RET"):
                    if currentDef.finish:
                        raise Exception(f"Def [{call}] Already Finished!")
                    # print("RET")
                    currentDef.res = getCType(line[6:])
                    currentDef.finish = True
                    currentLibrary.data.append(currentDef)
            if line.startswith("E."):
                call = line[2:].strip()
                if call.startswith("DEF"):
                    currentEnum = en()
                    # print("DEF", line[6:])
                    currentEnum.name = call[4:]
                    currentEnum.finish = False
                elif call.startswith("VAL"):
                    if currentEnum.finish:
                        raise Exception(f"Enum [{call}] Already Finished!")
                    if len(line[6:].split(' ')) != 3:
                        raise Exception(f"Enum [{call}] Has Invalid Length! (got {len(line[6:].split(' '))})")
                    (valname, valtype, val) = line[6:].split(' ')
                    valtype = getCType(valtype)
                    if valtype == None:
                        raise Exception(f"Value of enum enum '{currentEnum.name}' was None!")
                    currentEnum.values[valname] = (valtype, val)
                    # print("VAL", line[6:].split(' '))
                elif call.startswith("END"):
                    if currentEnum.finish:
                        raise Exception(f"Enum [{call}] Already Finished!")
                    currentEnum.finish = True
                    currentLibrary.data.append(currentEnum)
        else:
            if lineindex == 0:
                if line[7:] != "1":
                    raise Exception(f"Invalid pylib format! (got {line[7:]})")

        line = file.readline()
        lineindex += 1
    # print("FIN")

    for l in librs:
        libs[l.name] = []
        for arg in l.data:
            if isinstance(arg, fun):
                libs[l.name].append(__cdll_function_def(arg.name, arg.values, arg.res))
            elif isinstance(arg, en):
                libs[l.name].append(_cdll_enum(arg.name, arg.values))

# Put libraries here
libraries: dict[str, list[Union[__cdll_function_def, _cdll_enum]]] = {
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
            {"ERROR": 0, "WARN": 1, "INFO": 2, "DEBUG": 3, "TRACE": 4}
        ),
        __cdll_function_def
        (
            "init",
            [_cdll_enum_arg("LEVELS")],
            None
        ),
        __cdll_function_def
        (
            "error",
            [c_int, c_char_p],
            None
        ),
        __cdll_function_def
        (
            "warn",
            [c_int, c_char_p],
            None
        ),
        __cdll_function_def
        (
            "info",
            [c_int, c_char_p],
            None
        ),
        __cdll_function_def
        (
            "debug",
            [c_int, c_char_p],
            None
        ),
        __cdll_function_def
        (
            "trace",
            [c_int, c_char_p],
            None
        )
    ]
}

def init():
    """Initializes the library loader; call this before any other imports."""
    global __initialized
    if __initialized:
        raise Exception("[LIB ERROR] Libraries already initialized, cannot initialize again.")
    print("[LIB INFO] Initializing libraries")
    for lib, items in libs.items():
        print(f"[LIB INFO]  Loading library {lib}")
        l = __load_library(lib)
        __LibraryStorage._addLibrary(lib, l)
        __set_lib_contents(l, lib, items)
    __initialized = True
