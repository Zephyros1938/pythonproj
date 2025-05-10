#include <csignal>
#include <iostream>
#include <map>
#include <string>
#define LOGGER_H
#include "headers/logger.h"

enum LEVELS { ERROR = 0, WARN, INFO, DEBUG, TRACE };

LEVELS TARGET_LEVEL = LEVELS::INFO; // info
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

void error(int depth, const char *info) {
  if (!INITIALIZED) {
    raise(-1);
  }
  if (LEVELS::ERROR <= TARGET_LEVEL) {
    std::cout << LEVEL_KEY[LEVELS::ERROR] << std::string(depth, ' ') << info
              << std::endl;
  }
}

void warn(int depth, const char *info) {
  if (!INITIALIZED) {
    raise(-1);
  }
  if (LEVELS::WARN <= TARGET_LEVEL) {
    std::cout << LEVEL_KEY[LEVELS::WARN] << std::string(depth, ' ') << info
              << std::endl;
  }
}

void info(int depth, const char *info) {
  if (!INITIALIZED) {
    raise(-1);
  }
  if (LEVELS::INFO <= TARGET_LEVEL) {
    std::cout << LEVEL_KEY[LEVELS::INFO] << std::string(depth, ' ') << info
              << std::endl;
  }
}

void debug(int depth, const char *info) {
  if (!INITIALIZED) {
    raise(-1);
  }
  if (LEVELS::DEBUG <= TARGET_LEVEL) {
    std::cout << LEVEL_KEY[LEVELS::DEBUG] << std::string(depth, ' ') << info
              << std::endl;
  }
}

void trace(int depth, const char *info) {
  if (!INITIALIZED) {
    raise(-1);
  }
  if (LEVELS::TRACE <= TARGET_LEVEL) {
    std::cout << LEVEL_KEY[LEVELS::TRACE] << std::string(depth, ' ') << info
              << std::endl;
  }
}

int main() {
  std::cout << "Hello World!" << std::endl;
  return 0;
}
}
