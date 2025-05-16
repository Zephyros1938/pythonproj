# import lib
# from lib import cstr
# lib.init()
# test = lib.getlib("test")
# test.test(1938)
# c = test.TestClass_New(1)
# test.TestClass_doSomething(c, 3)
# c2 = test.TestClass_New(1)
# test.TestClass_doSomething(c, 3)
# demangleABI("libraries/compiled/test/test.so")
print("_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc")
import cxxfilt
print(cxxfilt.demangle("_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc"))
# for i in [ItaniumABITypes.CppCompoundTypes, ItaniumABITypes.CppNamePrefixes, ItaniumABITypes.CppOperators, ItaniumABITypes.CppQualifiers, ItaniumABITypes.CppSpecialForms, ItaniumABITypes.CppStandardNamespaces, ItaniumABITypes.CppTypes]:
#     t = []
#     k_ = i.__name__
#     for k, v in i.__members__.items():
#         t.append(v.value)
#     print(f"{k_}: ", t)
