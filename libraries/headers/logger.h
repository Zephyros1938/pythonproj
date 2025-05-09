#ifndef LOGGER_H
#define LOGGER_H

#include <csignal>
#include <iostream>
#include <map>
#include <string>

enum LEVELS { ERROR, WARN, INFO, DEBUG, TRACE };

void init(LEVELS targetLevel);
void log(LEVELS level, int depth, const char *info);
extern std::map<LEVELS, const char *> LEVEL_KEY;

#endif
