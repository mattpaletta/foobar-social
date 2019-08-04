from concurrent import futures
from time import sleep
from typing import Iterator

import grpc

from user_pb2 import User
from user_setting_pb2 import UserInfo
from wall_pb2 import WallQuery
from posts_pb2 import Post

from profile_pb2_grpc import add_ProfileServiceServicer_to_server, ProfileServiceServicer

from wall_pb2_grpc import WallServiceStub
from posts_pb2_grpc import PostServiceStub


class ProfileService(ProfileServiceServicer):
    
    def __init__(self) -> None:
        
        self.wall_channel = grpc.insecure_channel('wall:6969')
        self.wall_stub = WallServiceStub(self.wall_channel)

        try:
            grpc.channel_ready_future(self.wall_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to wall")

        self.posts_channel = grpc.insecure_channel('posts:2884')
        self.posts_stub = PostServiceStub(self.posts_channel)
        try:
            grpc.channel_ready_future(self.posts_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to posts")

    def get_friends(self, request: User, context: grpc.RpcContext = None) -> UserInfo:
        
        # Is this info from User Settings?
        return UserInfo()

    def get_wall(self, request: WallQuery, context: grpc.RpcContext = None) -> Iterator[Post]:
        
        # Right now profile just passes along from wall which just passes along from posts which just does an SQL query.
        # That is to say this is not production ready
        
        wall_posts = self.wall_stub.fetch(request)
        for post in wall_posts:
            yield post


if __name__ == "__main__":
    profile_port = 2885
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_ProfileServiceServicer_to_server(servicer = ProfileService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(profile_port))
    print("Starting Profile Server")
    server.start()
    while True:
        sleep(1000)
