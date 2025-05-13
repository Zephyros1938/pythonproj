#include "headers/CWrapper.hpp"
#include <iostream>
int main() {
  std::cout << "test" << std::endl;
  return 0;
}

void test(int x) { std::cout << "Test:" << x << std::endl; }

class TestClass {
public:
  TestClass(int x) : val(x) {}
  void doSomething(int a) { std::cout << a << std::endl; }

private:
  int val;
};
