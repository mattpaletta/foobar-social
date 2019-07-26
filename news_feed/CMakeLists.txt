cmake_minimum_required (VERSION 3.7.2)
project (news_feed CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/build/cmake/")
set(PROTOBUF_IMPORT_DIRS "${CMAKE_SOURCE_DIR}/")

add_definitions(-DNDEBUG)

find_package (Protobuf REQUIRED)
find_package (GRPC REQUIRED)

function(generate_proto FILENAME)
    PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS ${FILENAME})
    PROTOBUF_GENERATE_GRPC_CPP(GRPC_SRCS GRPC_HDRS ${FILENAME})
endfunction()

include_directories(${PROTOBUF_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR})

generate_proto(shared.proto)
generate_proto(posts.proto)
generate_proto(user.proto)
generate_proto(wall.proto)
generate_proto(news_feed.proto)
generate_proto(news_feed_data_access.proto)

add_executable(news_feed
        news_feed.pb
        news_feed.grpc.pb.h
        news_feed.grpc.pb.cc
        shared.pb.h
        shared.pb.cc
        user.pb
        posts.grpc.pb
        posts.pb.h
        posts.pb.cc
        wall.pb.h
        wall.pb.cc
        news_feed_data_access.grpc.pb
        news_feed_data_access.pb.h
        news_feed_data_access.pb.cc
        include/main.cpp
        include/NewsFeedDataAccessClient.h include/PostsClient.h)

target_link_libraries(news_feed ${PROTOBUF_LIBRARIES} ${GRPC_LIBRARIES})
#target_link_libraries(news_feed Protobuf::protolib GRPC::grpc)