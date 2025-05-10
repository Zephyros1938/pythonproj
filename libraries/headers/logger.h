#ifndef LOGGER_H
#define LOGGER_H

#include <csignal>
#include <iostream>
#include <map>
#include <string>

enum LEVELS { ERROR, WARN, INFO, DEBUG, TRACE };

void init(LEVELS targetLevel);
void error(int depth, const char *info);
void warn(int depth, const char *info);
void info(int depth, const char *info);
void debug(int depth, const char *info);
void trace(int depth, const char *info);
extern std::map<LEVELS, const char *> LEVEL_KEY;

#endif
