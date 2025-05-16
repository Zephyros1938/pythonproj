# import lib
# from lib import cstr
# lib.init()
# test = lib.getlib("test")
# test.test(1938)
# c = test.TestClass_New(1)
# test.TestClass_doSomething(c, 3)
# c2 = test.TestClass_New(1)
# test.TestClass_doSomething(c, 3)
from lib.demangle import demangleABI, ItaniumABITypes
demangleABI("libraries/compiled/test/test.so")
# for i in [ItaniumABITypes.CppCompoundTypes, ItaniumABITypes.CppNamePrefixes, ItaniumABITypes.CppOperators, ItaniumABITypes.CppQualifiers, ItaniumABITypes.CppSpecialForms, ItaniumABITypes.CppStandardNamespaces, ItaniumABITypes.CppTypes]:
#     t = []
#     k_ = i.__name__
#     for k, v in i.__members__.items():
#         t.append(v.value)
#     print(f"{k_}: ", t)
