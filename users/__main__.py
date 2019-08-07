import logging
from concurrent import futures
from threading import Semaphore
from time import sleep
import grpc
import re

from users_pb2_grpc import add_UsersServiceServicer_to_server
from users_pb2_grpc import UsersServiceServicer
from auth_pb2 import Auth

import psycopg2
import psycopg2.pool


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


class UsersService(UsersServiceServicer):
    
    def __init__(self):
        for i in range(100):
            try:
                # Give the database a change to initialize
                self.postgres_pool = ReallyThreadedConnectionPool(minconn = 1,
                                                                  maxconn = 20,
                                                                  user = "docker",
                                                                  password = "password",
                                                                  host = "usersdb",
                                                                  port = "5432",
                                                                  database = "users1")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)
            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)

    def create_user(self, request: Auth, context: grpc.RpcContext = None) -> Auth:

        request_username = request.username

        # Ensure username consists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_username)
        if not valid_user:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            return Auth()

        print("Getting connection")
        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            print("Got connection")

            with postgres_pool_conn.cursor() as ps_cursor:

                ps_cursor.execute("INSERT INTO users(username) VALUES ('{0}');".format(request_username))
                postgres_pool_conn.commit()

            self.postgres_pool.putconn(postgres_pool_conn)

            return Auth(username = request_username, password = "")
        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to DB pool.')
            self.postgres_pool.putconn(postgres_pool_conn)

    def __del__(self):
        # closing database connection.
        # use closeall method to close all the active connection if you want to turn of the application
        try:
            if self.postgres_pool:
                self.postgres_pool.closeall()
            print("PostgreSQL connection pool is closed")
        except AttributeError:
            # This means we didn't allocate the resource, so nothing to do
            pass


if __name__ == "__main__":
    users_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_UsersServiceServicer_to_server(servicer = UsersService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(users_port))
    print("Started users")
    server.start()
    while True:
        sleep(1000)
