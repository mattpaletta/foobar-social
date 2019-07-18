import logging
from concurrent import futures
from time import sleep
from typing import Iterator

import grpc
import psycopg2
import psycopg2.pool

from posts_pb2 import PostQuery, Post
from posts_pb2_grpc import PostServiceStub
from wall_pb2 import WallQuery
from wall_pb2_grpc import add_WallServiceServicer_to_server, WallServiceServicer


class WallService(WallServiceServicer):
    
    def __init__(self) -> None:
        self.posts_channel = grpc.insecure_channel('wall:2539')
        self.posts_stub = PostServiceStub(self.posts_channel)

        try:
            grpc.channel_ready_future(self.posts_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to Posts")

        for i in range(100):
            try:
                # Give the database a change to initialize
                self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(minconn = 1,
                                                                          maxconn = 20,
                                                                          user = "docker",
                                                                          password = "password",
                                                                          host = "walldb",
                                                                          port = "5432",
                                                                          database = "wall_serv")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)

            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)

    def fetch(self, request: WallQuery, context: grpc.RpcContext = None) -> Iterator[Post]:
        request_user = WallQuery.username
        request_start = WallQuery.starting_id
        request_limit = WallQuery.limit

        posts_request = PostQuery(request_user, request_start, request_limit)

        # posts = self.posts_stub.get_password(posts_request)
        # TODO: Make this call posts_stub
        posts = [Post(id = 1, msg = "hello world")]

        for post in posts:
            yield post


if __name__ == "__main__":
    wall_port = 4698
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_WallServiceServicer_to_server(servicer = WallService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(wall_port))
    print("Starting Auth Server")
    server.start()
    while True:
        sleep(1000)
