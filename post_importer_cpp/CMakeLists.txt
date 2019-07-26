cmake_minimum_required (VERSION 3.7.2)
project (post_importer CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/build/cmake/")
set(PROTOBUF_IMPORT_DIRS "${CMAKE_SOURCE_DIR}/")

include(build/cmake/redox.cmake)
add_definitions(-DNDEBUG)

find_package (Protobuf REQUIRED)
find_package (GRPC REQUIRED)

function(generate_proto FILENAME)
    PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS ${FILENAME})
    PROTOBUF_GENERATE_GRPC_CPP(GRPC_SRCS GRPC_HDRS ${FILENAME})
endfunction()

include_directories(${PROTOBUF_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR})

generate_proto(post_importer.proto)
generate_proto(posts.proto)
generate_proto(shared.proto)

add_executable(post_importer
        posts.pb
        shared.pb
        post_importer.grpc.pb
        post_importer.pb
        include/main.cpp)

target_link_libraries(post_importer ${PROTOBUF_LIBRARIES} ${GRPC_LIBRARIES})gi
#target_link_libraries(news_feed Protobuf::protolib GRPC::grpc)