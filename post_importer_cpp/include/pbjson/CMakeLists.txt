# Originally from https://github.com/yinqiwen/pbjson
add_library(pbjson pbjson.hpp pbjson.cpp bin2ascii.h)
target_include_directories(pbjson PRIVATE rapidjson)