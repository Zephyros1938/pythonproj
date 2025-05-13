#include <iostream>
#include"headers/CWrapper.hpp"
int main() {
    std::cout << "test" << std::endl;
    return 0;
}

C_WRAPPER_BEGIN

void test(int x)
{
    std::cout << "Test:" << x << std::endl;
}

C_WRAPPER_END

class TestClass {
    public:
    TestClass(int x) : val(x) {}
    void doSomething(int a) {std::cout << a << std::endl;}
    private:
    int val;
};

extern "C"
{
    TestClass* TestClass_New(int x) {return new TestClass(x);}
    void TestClass_doSomething(TestClass* obj, int a){obj->doSomething(a);}
    void TestClass_delete(TestClass* obj) { delete obj; }
}
