cmake_minimum_required (VERSION 3.7.2)
cmake_policy(SET CMP0042 NEW)
project (post_importer LANGUAGES CXX)
if (APPLE)
    set(CMAKE_MACOSX_RPATH ON)
endif ()

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/build/cmake/")
set(PROTOBUF_IMPORT_DIRS "${CMAKE_SOURCE_DIR}/")

SET(BUILD_SHARED_LIBS OFF)

add_subdirectory(include/pbjson)

add_definitions(-DNDEBUG)

find_package (Protobuf REQUIRED)
find_package (GRPC REQUIRED)
FIND_LIBRARY(Redox REQUIRED)
FIND_LIBRARY(ev REQUIRED)
FIND_LIBRARY(hiredis REQUIRED)
#FIND_LIBRARY(pb2json REQUIRED)

FIND_PACKAGE(Boost REQUIRED COMPONENTS program_options)
FIND_PACKAGE(CppKafka REQUIRED)

function(generate_proto FILENAME)
    PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS ${FILENAME})
    PROTOBUF_GENERATE_GRPC_CPP(GRPC_SRCS GRPC_HDRS ${FILENAME})
endfunction()

include_directories(${PROTOBUF_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR})

#add_subdirectory(cppkafka)

generate_proto(post_importer.proto)
generate_proto(posts.proto)
generate_proto(shared.proto)

add_executable(post_importer
        posts.pb
        shared.pb
        post_importer.grpc.pb
        post_importer.pb
        include/main.cpp
        include/redox_helper.h)

if (BUILD_STATIC_LIBS)
    link_libraries("-static")
    target_link_libraries(post_importer PUBLIC "-static")
endif()

target_link_libraries(post_importer ${PROTOBUF_LIBRARIES} ${GRPC_LIBRARIES} pbjson CppKafka::cppkafka ev redox_static hiredis)
#target_link_libraries(news_feed Protobuf::protolib GRPC::grpc)