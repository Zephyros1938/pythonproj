from .util import mapStrCType, castCType
from .types import _cdll_enum, _cdll_enum_arg, __cdll_function_def
from .__storage import enum_storage
from typing import Any, Union
from ctypes import c_int
import sys

def loadPyFFI(path: str, debug: bool = False) -> dict[str, list[Union[__cdll_function_def, _cdll_enum]]]:
    orig_stdout = sys.stdout
    if not debug:
        from os import devnull
        sys.stdout = open(devnull, "w")
    file = open(path)
    print(f"[ PYFFI INFO ] Opened PyFFI File {path}")
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
    currentDef.finish = True
    lineindex = 0
    librs: list[libr] = []
    print("[ PYFFI INFO ]  Begin Build")
    (libstarts, libends, funcstarts, funcends, enumstarts, enumends) = (0,0,0,0,0,0)

    line = file.readline()
    if line.strip()[7:] != "1":
        raise Exception(f"Invalid pyffi format! (got {line[7:]})")
    else:
        FORMAT = line.strip()[7:]
    print(f"[ PYFFI GEN  ]   Format: {FORMAT}")
    while line:
        line = line.strip()
        if line.startswith("//"):
            print(f"[ PYFFI GEN  ]   Comment at line.{lineindex}: {line[3:]}")
        elif line.startswith("LIBRARY"):
            currentLibrary.name = line[8:]
            print(f"[ PYFFI GEN  ]   Begin Library {currentLibrary.name}")
            libstarts+=1
        elif line.startswith("ENDLIBRARY"):
            if currentLibrary.name.startswith('\0'):
                pass
            else:
                librs.append(currentLibrary)
                name = currentLibrary.name
                currentLibrary = libr()
                print(f"[ PYFFI GEN  ]   End Library {name}")
                libends+=1
        elif line.startswith("F."):
            call = line[2:].strip()
            if call.startswith("DEF"):
                if not currentDef.finish:
                    raise Exception(f"Def {currentDef.name} was not closed!")
                currentDef = fun()
                currentDef.name = call[4:]
                currentDef.finish = False
                print(f"[ PYFFI GEN  ]    Begin Function {currentDef.name}")
                funcstarts+=1
            elif call.startswith("ARG"):
                if currentDef.finish:
                    raise Exception(f"Def [{call}] Already Finished!")
                if line[6:10] == "ENUM":
                    for t in [v for v in currentLibrary.data if type(v) == en]:
                        if t.name == line[11:]:
                            currentDef.values.append(t)
                            print(f"[ PYFFI GEN  ]     ENUM ARG: {t.name}")
                            break
                    else:
                        raise Exception(f"Could not get enum '{line[11:]}'")
                else:
                    currentDef.values.append(mapStrCType(line[6:]))
                    print(f"[ PYFFI GEN  ]     TYPE ARG: {line[6:]}")
            elif call.startswith("RET"):
                if currentDef.finish:
                    raise Exception(f"Def [{call}] Already Finished!")
                currentDef.res = mapStrCType(line[6:])
                currentDef.finish = True
                currentLibrary.data.append(currentDef)
                print(f"[ PYFFI GEN  ]     RETURN  : {line[6:]}")
                funcends+=1
        elif line.startswith("E."):
            call = line[2:].strip()
            if call.startswith("DEF"):
                currentEnum = en()
                currentEnum.name = call[4:]
                currentEnum.finish = False
                print(f"[ PYFFI GEN  ]    Begin Enum {currentEnum.name}")
                enumstarts+=1
            elif call.startswith("VAL"):
                if currentEnum.finish:
                    raise Exception(f"Enum [{call}] Already Finished!")
                if len(line[6:].split(' ')) != 3:
                    raise Exception(f"Enum [{call}] Has Invalid Length! (got {len(line[6:].split(' '))})")
                (valname, valtype, val) = line[6:].split(' ')
                valtype = mapStrCType(valtype)
                if valtype == None:
                    raise Exception(f"Value of enum enum '{currentEnum.name}' was None!")
                currentEnum.values[valname] = (valtype, val)
                print(f"[ PYFFI GEN  ]     ENUM VAL: {val}, {valtype}")
            elif call.startswith("END"):
                if currentEnum.finish:
                    raise Exception(f"Enum [{call}] Already Finished!")
                currentEnum.finish = True
                currentLibrary.data.append(currentEnum)
                print("[ PYFFI GEN  ]     ENUM END")
                enumends+=1
        line = file.readline()
        lineindex += 1

    if libstarts != libends:
        raise Exception(f"Libstarts {'>' if libstarts > libends else '<'} libends. starts: {libstarts} ends: {libends}")
    elif funcstarts != funcends:
        raise Exception(f"Funcstarts {'>' if funcstarts > funcends else '<'} funcends. starts: {funcstarts} ends: {funcends}")
    elif enumstarts != enumends:
        raise Exception(f"Enumstarts {'>' if enumstarts > enumends else '<'} enumends. starts: {enumstarts} ends: {enumends}")

    libs: dict[str, list[Union[__cdll_function_def, _cdll_enum]]] = {}

    print("[PYFFI BUILD ]  Begin Construct")
    for l in librs:
        libs[l.name] = []
        print(f"[PYFFI BUILD ]   Make Library {l.name}")
        for arg in l.data:
            if isinstance(arg, fun):
                _values = []
                print(f"[PYFFI BUILD ]    Begin Function {arg.name}")
                for a in arg.values:
                    if isinstance(a, en):
                        _values.append(_cdll_enum_arg(a.name))
                        print(f"[PYFFI BUILD ]     Added Enum Arg {a.name}")
                    else:
                        _values.append(a)
                        print(f"[PYFFI BUILD ]     Added Type Arg {a}")
                libs[l.name].append(__cdll_function_def(arg.name, _values, enum_storage, arg.res))
                print(f"[PYFFI BUILD ]    End Function {arg.name}")
            elif isinstance(arg, en):
                print(f"[PYFFI BUILD ]    Begin Enum {arg.name}")
                va = {nam: castCType(val, typ) for nam, (typ, val) in arg.values.items()}
                libs[l.name].append(_cdll_enum(arg.name, va))
                print(f"[PYFFI BUILD ]    End Enum {arg.name}")
    print(f"[ PYFFI INFO ]  Finished Loading {path}")
    sys.stdout = orig_stdout
    return libs
