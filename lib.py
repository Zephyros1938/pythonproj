from ctypes import CDLL, POINTER
from ctypes import c_char_p, c_ubyte, c_int
import os
from typing import Any
LIBRARY_DIR = "./libraries"
COMPILED_DIR = os.path.join(LIBRARY_DIR, "compiled")

__initialized = False

_loaded_libraries: dict[str, CDLL] = {}

def get(libname: str) -> CDLL:
    return _loaded_libraries[libname]

class __cdll_function_def:
    def __init__(self, fname: str, argtypes: list = [], restype: Any = None):
        self.fname = fname
        self.argtypes = argtypes
        self.restype = restype

libraries: dict[str, list[__cdll_function_def]] = {
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
    "logger": []
}

def __set_lib_funcs(lib: CDLL, funcs: list[__cdll_function_def]):
    for f in funcs:
        print(f"[LIB]   Setting function {f.fname}")
        func = getattr(lib, f.fname)
        func.argtypes = f.argtypes
        func.restype = f.restype


def init():
    global __initialized
    if __initialized:
        raise Exception("[ERROR] Libraries already initialized, cannot initialize again.")
    print("[LIB] Initializing libraries")
    for lib, funcs in libraries.items():
        print(f"[LIB]  Loading library {lib}")
        l = __load_library(lib)
        __set_lib_funcs(l, funcs)
        _loaded_libraries[lib] = l
    __initialized = True


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
