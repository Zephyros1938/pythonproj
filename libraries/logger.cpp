#include <iostream>
#ifdef _WIN32
    #include <ncurses_dll.h>
#else
    #include <ncurses.h>
#endif

int main() {
    std::cout << "Hello World!" << std::endl;
    return 0;
}
