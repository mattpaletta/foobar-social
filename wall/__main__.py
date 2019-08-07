import logging
import re
from concurrent import futures
from threading import Semaphore
from time import sleep
from typing import Iterator

import grpc
import psycopg2
import psycopg2.pool

from posts_pb2 import PostQuery, Post
from posts_pb2_grpc import PostServiceStub
from shared_pb2 import Empty
from user_pb2 import User
from wall_pb2 import WallQuery
from wall_pb2_grpc import add_WallServiceServicer_to_server, WallServiceServicer


class ReallyThreadedConnectionPool(psycopg2.pool.ThreadedConnectionPool):
    def __init__(self, minconn, maxconn, *args, **kwargs):
        self._semaphore = Semaphore(maxconn)
        super().__init__(minconn, maxconn, *args, **kwargs)

    def getconn(self, *args, **kwargs):
        self._semaphore.acquire()
        return super().getconn(*args, **kwargs)

    def putconn(self, *args, **kwargs):
        super().putconn(*args, **kwargs)
        self._semaphore.release()


class WallService(WallServiceServicer):
    def __init__(self) -> None:
        self.posts_channel = grpc.insecure_channel('posts:2885')
        self.posts_stub = PostServiceStub(self.posts_channel)

        try:
            grpc.channel_ready_future(self.posts_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to Posts")
            exit(1)

        for i in range(100):
            try:
                # Give the database a change to initialize
                self.postgres_pool = ReallyThreadedConnectionPool(minconn = 1,
                                                                  maxconn = 20,
                                                                  user = "docker",
                                                                  password = "password",
                                                                  host = "walldb",
                                                                  port = "5432",
                                                                  database = "wall")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)
            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)

    def fetch(self, request: WallQuery, context: grpc.RpcContext = None) -> Iterator[Post]:
        request_user = request.username
        request_limit = request.limit
        request_start = 0 if request.starting_id < 0 else request.starting_id

        # Ensure username consists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_user)
        if not valid_user:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            logging.info("Invalid username")
            yield from []
            return

        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            ps_cursor = postgres_pool_conn.cursor()

            limit_statement = "LIMIT {0}".format(request_limit) if request_limit > 0 else ""

            query = """SELECT post_id 
                        FROM wall 
                        WHERE username = '{0}' AND post_id >= {1} 
                        ORDER BY datetime DESC {2};""" \
                        .format(request_user, request_start, limit_statement)
            print(query)

            ps_cursor.execute(query)
            posts = ps_cursor.fetchall()

            print("Got rows: ", len(posts))

            for post in posts:
                try:
                    post_filled = self.posts_stub.fetch(Post(id = post[0], username = request_user))
                    yield post_filled
                except Exception as e:
                    logging.error("Failed to fetch post: ", e)

            ps_cursor.close()
            self.postgres_pool.putconn(postgres_pool_conn)
        else:
            logging.error("Failed to get postgres connection")
            yield from []
            return

    def put(self, request: Post, context: grpc.RpcContext = None) -> Empty:
        request_username = request.username

        # Ensure username consists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_username)
        if not valid_user:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            logging.info("Invalid username")
            return Empty()

        logging.info("Inserting into wall")
        # TODO: Finish validating posts
        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            ps_cursor = postgres_pool_conn.cursor()
            ps_cursor.execute("""INSERT INTO wall (username, post_id, datetime) 
                                         VALUES ('{0}',{1}, to_timestamp({2}));"""
                              .format(request_username, request.id, request.datetime))
            postgres_pool_conn.commit()
            ps_cursor.close()
            self.postgres_pool.putconn(postgres_pool_conn)
        else:
            logging.error("Failed to get postgres connection")
        return Empty()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    wall_port = 4698
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_WallServiceServicer_to_server(servicer = WallService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(wall_port))
    print("Starting Wall Server")
    server.start()
    while True:
        sleep(1000)
