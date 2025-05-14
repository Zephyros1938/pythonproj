#include <iostream>

int main() {
  std::cout << "test" << std::endl;
  return 0;
}

void test(int x) { std::cout << "Test:" << x << std::endl; }

class TestClass22 {
public:
  TestClass22(int x) : val(x) {}
  void doSomething(int a) { std::cout << a << std::endl; }
  int getVal() {return val;}
private:
  int val;
};

void cTest(TestClass22 t) {std::cout << t.getVal() << std::endl; }
void cTest2(TestClass22 t, int a) {t.doSomething(a);}

namespace layer1 {
    namespace layer2 {
        void cTest3(int a) {std::cout << a << std::endl;}
    }
}
