import logging
import re
from concurrent import futures
from time import sleep
from typing import Iterator
import grpc
import psycopg2
import psycopg2.pool

from friends_pb2 import Friend
from friends_pb2_grpc import add_FriendsServiceServicer_to_server, FriendsServiceServicer
from user_pb2 import User


class FriendsService(FriendsServiceServicer):
    
    def __init__(self) -> None:
        for i in range(10):
            try:
                # Give the database a change to initialize
                self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(minconn = 1,
                                                                          maxconn = 20,
                                                                          user = "docker",
                                                                          password = "password",
                                                                          host = "friendsdb",
                                                                          port = "5432")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)
            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)

    def get_friends(self, request: User, context: grpc.RpcContext = None) -> Iterator[Friend]:
        request_username = request.username

        # Ensure username consists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_username)
        print("Getting friends")
        if not valid_user:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            print("Invalid username")
            yield from []
            return

        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            ps_cursor = postgres_pool_conn.cursor()

            ps_cursor.execute("SELECT friend FROM friends WHERE username = '{0}';".format(request_username))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            self.postgres_pool.putconn(postgres_pool_conn)

            print("Got friends")
            print("Len: ", len(rows))
            for row in rows:
                yield Friend(username = request_username, friend_username = row[0])
        else:
            print("did not get postgres conn")

    def top_friends(self, request: User, context: grpc.RpcContext = None) -> Iterator[Friend]:
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
                yield Friend()
                return

            ps_cursor.execute("SELECT friend FROM friends WHERE username = '{0}' ORDER BY added_date DESC LIMIT 10;".format(request_username))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            self.postgres_pool.putconn(postgres_pool_conn)

            for row in rows:
                yield Friend(username = request_username, friend_username = row[0])

        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to DB pool.')


if __name__ == "__main__":
    friends_port = 2885
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_FriendsServiceServicer_to_server(servicer = FriendsService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(friends_port))
    print("Starting Friends Server")
    server.start()
    while True:
        sleep(1000)
