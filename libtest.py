import lib
from lib import cstr
lib.init()
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "INFO"))
test = lib.getlib("test")
test.test(1938)
c = test.TestClass_New(1)
test.TestClass_doSomething(c, 3)
c2 = test.TestClass_New(1)
test.TestClass_doSomething(c, 3)
