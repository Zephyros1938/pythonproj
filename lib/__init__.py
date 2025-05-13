from ctypes import CDLL
from ctypes import c_int
from cffi import FFI
ffi = FFI()
from enum import Enum
from typing import Union
import os
from .pyffi import loadPyFFI
from .types import CEnumMeta, __cdll_function_def, _cdll_enum, _cdll_enum_arg

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
# TODO: switch this to cffi


__LIBRARY_DIR = "./libraries"
__COMPILED_DIR = os.path.join(__LIBRARY_DIR, "compiled")

__initialized = False

# Metaclass fro C-Style enums


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



def __dict_enum_to_c_enum(enum_name: str, enum_values: dict[str, int]):
    # print(enum_values)
    """Converts a dictionary to a C-style enum."""
    enum_type = Enum(enum_name + "Enum", enum_values)

    class CEnumWrapper(metaclass=CEnumMeta):
        """A C-Style enum wrapper

        This is used because C-Style enums when used with CDLL must be formatted as classes
        """

        _values_ = {}

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
        enum_instance = CEnumWrapper(val)
        setattr(CEnumWrapper, name, enum_instance)
        CEnumWrapper._values_[name] = val  # Add the name-value pair to _values_, breaks if this does not happen
        # print(f"{name} = {getattr(CEnumWrapper, name)}")

    return CEnumWrapper


def __set_lib_contents(lib: CDLL, libName: str, funcs: list[Union[__cdll_function_def, _cdll_enum]]):
    """Sets all of the library's contents"""
    for f in funcs:
        if isinstance(f, __cdll_function_def):
            print(f"[LIB INFO]   Setting function {libName}::{f.name}")
            func = getattr(lib, f.name)
            _argtypes = []
            for f_ in f.argtypes:
                if type(f_) == _cdll_enum_arg:
                    _argtypes.append(__LibraryStorage._getEnum(libName, f_.enumName))
                else:
                    _argtypes.append(f_)
            # print(_argtypes)
            # print(f"[DEBUG] Setting argtypes for {f.fname}: {_argtypes}")
            # for i, at in enumerate(_argtypes):
            #     print(f"  Arg {i}: {at} (has from_param? {'from_param' in dir(at)})")
            if any(a is None for a in _argtypes):
                raise TypeError(f"[LIB ERROR] Function {f.name} has None in argtypes: {_argtypes}")

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
        __LibraryStorage._addLibrary(libname, lib)
        return lib
    except Exception as e:
        raise Exception(f"[LIB ERROR] Failed to load library {libname}: {e}")



libs: dict[str, list[Union[__cdll_function_def, _cdll_enum]]] = loadPyFFI("./libs.pyffi", True)

def init():
    """Initializes the library loader; call this before any other imports."""
    global __initialized
    if __initialized:
        raise Exception("[LIB ERROR] Libraries already initialized, cannot initialize again.")
    print("[LIB INFO] Initializing libraries")
    for lib, items in libs.items():
        print(f"[LIB INFO]  Loading library {lib}")
        library = __load_library(lib)
        __set_lib_contents(library, lib, items)
    __initialized = True
