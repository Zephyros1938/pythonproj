#include <csignal>
#include <iostream>
#include <map>
#include <string>
#define LOGGER_H
#include "headers/logger.h"

enum LEVELS { ERROR, WARN, INFO, DEBUG, TRACE };

LEVELS TARGET_LEVEL = INFO; // info
bool INITIALIZED = false;

using namespace std;

extern "C" {

std::map<LEVELS, const char *> LEVEL_KEY = {{LEVELS::ERROR, "[ ERROR ]"},
                                            {LEVELS::WARN, "[ WARN  ]"},
                                            {LEVELS::INFO, "[ INFO  ]"},
                                            {LEVELS::DEBUG, "[ DEBUG ]"},
                                            {LEVELS::TRACE, "[ TRACE ]"}};

void init(LEVELS targetLevel) {
  TARGET_LEVEL = targetLevel;
  INITIALIZED = true;
}

void log(LEVELS level, int depth, const char *info) {
  if (!INITIALIZED) {
    raise(-1);
  }
  if (level == TARGET_LEVEL) {
    std::cout << LEVEL_KEY[level] << std::string(depth, ' ') << info
              << std::endl;
  }
}

int main() {
  std::cout << "Hello World!" << std::endl;
  return 0;
}
}
