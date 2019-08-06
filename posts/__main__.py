import logging
import re
from concurrent import futures
from time import sleep
from typing import Iterator

import grpc
import psycopg2
import psycopg2.pool

from posts_pb2 import Post, PostQuery
from shared_pb2 import Location, Empty
from posts_pb2_grpc import add_PostServiceServicer_to_server, PostServiceServicer


class PostsService(PostServiceServicer):
    
    def __init__(self) -> None:
        # TODO: https://stackoverflow.com/questions/48532301/python-postgres-psycopg2-threadedconnectionpool-exhausted
        for i in range(10):
            try:
                # Give the database a change to initialize
                self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(minconn = 1,
                                                                          maxconn = 20,
                                                                          user = "docker",
                                                                          password = "password",
                                                                          host = "postsdb",
                                                                          port = "5432",
                                                                          database = "posts")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)
            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)

    def get_posts(self, request: PostQuery, context: grpc.RpcContext = None) -> Iterator[Post]:
        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            request_username = request.username
            request_start = request.starting_id
            request_limit = request.limit

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
            ps_cursor.execute("""SELECT post_id, post_date, msg, lat, long FROM posts \
                               WHERE username = '{0}' ORDER BY post_date DESC LIMIT {1} OFFSET {2};"""
                              .format(request_username, request_limit, request_start))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            self.postgres_pool.putconn(postgres_pool_conn)

            for row in rows:
                post_location = Location(float(row.lat), float(row.long))
                yield Post(username = request_username, msg = row.msg, loc = post_location, datetime = post_date, id = post_id)

    def fetch(self, request: Post, context: grpc.RpcContext = None) -> Post:
        request_username = request.username

        # Ensure username cosists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_username)
        if not valid_user:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            return request

        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            post_id = request.id
            ps_cursor = postgres_pool_conn.cursor()

            # We are doing a query based on primary key, so it should be O(logn)
            ps_cursor.execute("""SELECT extract(epoch from post_date at time zone 'utc'), msg, lat, long FROM posts \
                                       WHERE post_id = {0} LIMIT 1;"""
                              .format(post_id))
            row = ps_cursor.fetchone()
            ps_cursor.close()

            print("Got Row: ", row)
            self.postgres_pool.putconn(postgres_pool_conn)

            if row is not None:
                # Fill in the post with the additional data
                resp = Post(datetime = int(row[0]),
                            msg = row[1],
                            username = request.username,
                            loc = Location(lat = row[2], long = row[3]))
                return resp

            return request

    def create_post(self, request: Post, context: grpc.RpcContext = None) -> Empty:
        request_username = request.username

        # Ensure username consists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_username)
        if not valid_user:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            logging.info("Invalid username")
            return Empty()

        logging.info("Inserting post")
        msg = request.msg.replace("'", "\"")

        # TODO: Finish validating posts
        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            ps_cursor = postgres_pool_conn.cursor()
            try:
                ps_cursor.execute("""INSERT INTO posts (post_id, username, msg, post_date, lat, long) 
                                     VALUES ({0}, '{1}', '{2}', to_timestamp({3}), {4}, {5});"""
                                    .format(request.id,
                                            request_username,
                                            msg,
                                            request.datetime,
                                            request.loc.lat,
                                            request.loc.long))
                postgres_pool_conn.commit()
            except Exception as e:
                logging.error("Failed to insert post: ", e)
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(e)

            ps_cursor.close()
            self.postgres_pool.putconn(postgres_pool_conn)
            return Empty()
        else:
            logging.error("Failed to get postgres connection")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    posts_port = 2885
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_PostServiceServicer_to_server(servicer = PostsService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(posts_port))
    print("Starting Posts Server")
    server.start()
    while True:
        sleep(1000)
