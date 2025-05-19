from cffi import FFI, FFIError
import os
ffi = FFI()
from enum import Enum
from typing import Union, Any
from .pyffi import loadPyFFI
from .types import CEnumMeta, __cdll_function_def, _cdll_enum, _cdll_enum_arg
from .util import mapCType
from .__storage import enum_values_storage

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

__initialized = False

# Metaclass fro C-Style enums

class __LibraryStorage(dict):
    """Used to store libraries"""
    __libraries: dict[str, tuple[Any, dict[str, type]]] = {}

    @classmethod
    def _addLibrary(cls, libName: str, library: Any):
        """Adds a library to the librarystorage"""
        cls.__libraries[libName] = (library, {})

    @classmethod
    def _getLibrary(cls, libName) -> Any:
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

def getlib(libName: str) -> Any:
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
            return cls(obj).value

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


def __set_lib_contents(library: Any, libName: str, funcs: list[Union[__cdll_function_def, _cdll_enum]], debugInternals: bool = False, debug: bool = False):
    """Sets all of the library's contents"""
    for f in funcs:
        if isinstance(f, __cdll_function_def):
            if debug: print(f"[LIB INFO]   Setting function {libName}::{f.name}")
            _argtypes = []
            typedefs = ""
            definedEnums: list[str] = []
            for arg in f.argtypes:
                if type(arg) == _cdll_enum_arg:
                    if not arg.enumName in definedEnums:
                        typedefs += "typedef enum {"
                        en = enum_values_storage[arg.enumName]
                        for (k, v) in en.items():
                            typedefs += f"{k}={v}, "
                        typedefs = f"{typedefs[:-2]} }} {arg.enumName};\n"
                        definedEnums += arg.enumName

                _argtypes.append(arg)
            if any(a is None for a in _argtypes):
                raise TypeError(f"[LIB ERROR] Function {f.name} has None in argtypes: {_argtypes}")

            funcRet = mapCType(f.restype)
            funcArgs = ""
            argIndex = 0
            for arg in _argtypes:
                funcArgs += f"{mapCType(arg)} arg{argIndex}"
                funcArgs += ", "
                argIndex+=1
            funcArgs = funcArgs[:-2]

            func = f"{funcRet} {f.name}({funcArgs});"
            funcFull = f"{typedefs}{func}"
            if debugInternals: print(f"[LIB INFO]    Function: '{func}'")

            try:
                ffi.cdef(funcFull)
            except FFIError as e:
                if str(e).startswith("multiple declarations of function"):
                    raise Exception(f"Function {libName}::{f.name} was redefined!")
                else:
                    raise FFIError(str(e))
        elif isinstance(f, _cdll_enum):
            if debug: print(f"[LIB INFO]   Setting enum {libName}::{f.enumName}")
            en = f"enum {f.enumName} {{"
            if isinstance(f.enumValues, list):
                enumValues = {f.enumValues[i]: i for i in range(len(f.enumValues))}
            elif isinstance(f.enumValues, dict):
                enumValues = f.enumValues
            else:
                raise TypeError(f"f.enumValues was {f.enumValues}, expected list/dict.")
            for (k, v) in enumValues.items():
                en += f"{k}={v},"
            en = f"{en[:-1]}}};"

            ffi.cdef(en)
            enum_values_storage[f.enumName] = enumValues
            if debugInternals: print(f"[LIB INFO]    Enum: '{en}'")
            enumClass = __dict_enum_to_c_enum(f.enumName, enumValues)

            __LibraryStorage._addEnum(libName, f.enumName, enumClass)

def __load_library(libname: str) -> Any:
    """Loads the specified library"""
    if os.name == "posix": # Linux/Mac
        lib_path = os.path.abspath(os.path.join(__COMPILED_DIR, libname, f"{libname}.so"))
    elif os.name == "nt": # Windows
        lib_path = os.path.abspath(os.path.join(__COMPILED_DIR, libname, f"{libname}.dll"))
    else:
        raise OSError("[LIB ERROR] Unsupported operating system: " + os.name)

    try:
        lib = ffi.dlopen(lib_path)
        __LibraryStorage._addLibrary(libname, lib)
        # from .demangle import getMangledABI
        # from cxxfilt import demangle
        # f = {k: "int " + demangle(v) + ";" for k, v in getMangledABI(lib_path).items() if not demangle(v).startswith("std")}
        # for k, v in f.items():
        #     print(k, v)
        #     # ffi.cdef(v)
        return lib
    except Exception as e:
        raise Exception(f"[LIB ERROR] Failed to load library {libname}: {e}")



libs: dict[str, list[Union[__cdll_function_def, _cdll_enum]]] = loadPyFFI("./libs.pyffi", False)

def init(debugLibInternals: bool = False, debug: bool = False):
    """Initializes the library loader; call this before any other imports."""
    global __initialized
    if debugLibInternals and not debug:
        print(
            "[LIB WARN] Lib debugLibInternals was 1, but debug was 0.\n\
             \b\bDefaulting to all 0.")
        debugLibInternals = False
    if __initialized:
        raise Exception("[LIB ERROR] Libraries already initialized, cannot initialize again.")
    print("[LIB INFO] Initializing libraries")
    for lib, items in libs.items():
        print(f"[LIB INFO]  Loading library {lib}")
        library = __load_library(lib)
        __set_lib_contents(library, lib, items, debugInternals=debugLibInternals, debug=debug)
    print("[LIB INFO] Finished Initializing libraries")
    __initialized = True
