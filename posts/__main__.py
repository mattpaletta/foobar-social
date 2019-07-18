import logging
import re
from concurrent import futures
from time import sleep
from typing import Iterator

import grpc
import psycopg2
import psycopg2.pool

from posts_pb2 import Post, PostQuery
from shared_pb2 import Location
from posts_pb2_grpc import add_PostServiceServicer_to_server, PostServiceServicer


class PostsService(PostServiceServicer):
    
    def __init__(self) -> None:
        #TODO: Handle hosts through Docker or JSON
        for i in range(10):
            try:
                # Give the database a change to initialize
                self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(minconn = 1,
                                                                          maxconn = 20,
                                                                          user = "docker",
                                                                          password = "password",
                                                                          host = "postsdb",
                                                                          port = "5432",
                                                                          database = "posts_serv")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)
            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)

    def get_posts(self, request: PostQuery, context: grpc.RpcContext = None) -> Iterator[Post]:
        postgres_pool_conn  = self.postgres_pool.getconn()
        if postgres_pool_conn:
            
            request_username = PostQuery.username
            request_start = PostQuery.starting_id
            request_limit = PostQuery.limit

            ps_cursor = postgres_pool_conn.cursor()

            # Ensure username cosists only of alphanumeric characters.
            validate = re.compile("[A-Za-z0-9]+$")
            valid_user = validate.match(request_username)
            if not valid_user:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Invalid Username')
                yield Post()
                return

            # Retrieve password for the provided username from user_setting
            ps_cursor.execute("""SELECT post_id, post_date, msg, lat, long FROM posts_db.posts \
                               WHERE username = '{0}' ORDER BY post_date DESC LIMIT {1} OFFSET {2};""".format(request_username, request_limit, request_start))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            self.postgres_pool.putconn(postgres_pool_conn)

            for row in rows:
                post_location = Location(float(row.lat), float(row.long))
                yield Post(username = request_username, msg = row.msg, loc = post_location, datetime = post_date, id = post_id)
    
    def create_post(self, request: Post, context: grpc.RpcContext = None) -> Post:
        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            
            request_username = request.username
            ps_cursor = postgres_pool_conn.cursor()

            # Ensure username cosists only of alphanumeric characters.
            validate = re.compile("[A-Za-z0-9]+$")
            valid_user = validate.match(request_username)
            if not valid_user:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Invalid Username')
                return Post()
           
            ps_cursor.execute("INSERT INTO posts_db.posts (username, msg, datetime, lat, long) VALUES ('{0}','{1}','{2}','{3}','{4}');"
                                .format(request_username, request.msg, request.datetime, request.loc.lat, request.loc.long))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            self.postgres_pool.putconn(postgres_pool_conn)

            post_location = Location(float(row.lat), float(row.long))
            return Post(username = request_username, msg = request.msg, datetime = request.datetime, loc = post_location)


if __name__ == "__main__":
    posts_port = 2885
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_PostServiceServicer_to_server(servicer = PostsService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(posts_port))
    print("Starting Posts Server")
    server.start()
    while True:
        sleep(1000)
