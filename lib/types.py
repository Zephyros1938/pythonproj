from typing import Union
from enum import EnumMeta
from typing import Any
from dataclasses import dataclass


@dataclass(init=False)
class CEnumMeta(type):
    _enumtype_: Union[EnumMeta, None]
    _values_ : dict[str, Any]
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

# Enum

class _cdll_enum_arg:
    """Used when using an enum in a __cdll_function_def"""
    def __init__ (self, enumName: str):
        self.enumName = enumName

class _cdll_enum:
    """A container for C-Style Enums"""
    def __init__(self, enumName: str, enumValues: Union[dict[str, Any], list[str]] = {}):
        self.enumName = enumName
        self.enumValues = enumValues

# Function

class __cdll_function_def:
    """Used to define functions for CDLL\nThis should be placed after any _cdll_enum definitions if they are used in argtypes"""
    def __init__(self, fname: str, argtypes: list[Union[Any, _cdll_enum_arg]], localstorage: dict[str, Any], restype: Any = None):
        self.name = fname
        _argtypes: list[Any] = []
        for a in argtypes:
            if isinstance(a, _cdll_enum):
                _argtypes.append(localstorage[a.enumName])
            else:
                _argtypes.append(a)
        self.argtypes = _argtypes
        self.restype = restype

# Class

class _cdll_class_method:
    name: str
    argtypes: list[Any] = []
    restype: Any = None
    def __init__(self, name: str, args: list[Any], restype: Any):
        self.name = name
        self.argtypes = args
        self.restype = restype

class _cdll_class_constructor:
    args: list[Any] = []
    def __init__(self, args: list[Any]):
        self.args = args

class __cdll_class:
    name: str
    methods: list[_cdll_class_method]
    constructor: _cdll_class_constructor
    def __init__(self, name: str, methods: list[_cdll_class_method], constructor: _cdll_class_constructor):
        self.name = name
        self.methods = methods
        self.constructor = constructor
