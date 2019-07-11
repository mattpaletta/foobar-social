from concurrent import futures
from time import sleep
import grpc
import re

from user_setting_pb2_grpc import add_UserSettingServiceServicer_to_server
from user_setting_pb2_grpc import UserSettingServiceServicer
from auth_pb2 import Auth

import psycopg2
import psycopg2.pool


class UserSettingService(UserSettingServiceServicer):
    
    def __init__(self):
        try:
            self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(minconn = 1,
                                                                      maxconn = 20,
                                                                      user = "docker",
                                                                      password = "password",
                                                                      host = "usersettingdb",
                                                                      port = "5432",
                                                                      database = "user_settings_db")
            if not self.postgres_pool:
                # context.set_code(grpc.StatusCode.INTERNAL)
                print('Failure to connect to Postgres')
                exit(1)
        except (Exception, psycopg2.DatabaseError) as error:
            # context.set_code(grpc.StatusCode.INTERNAL)
            print('Failure to connect to Postgres: ', error)
            exit(1)

    def get_password(self, request: Auth, context: grpc.RpcContext = None) -> Auth:

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

            ps_cursor = postgres_pool_conn.cursor()
            # Retrieve password for the provided username from user_setting
            # If we have more than 1, we don't really care how many more
            # ideally, we would only limit to the one row.
            ps_cursor.execute("SELECT passw FROM user_setting_db WHERE username = '{0} LIMIT 2';".format(request_username))
            rows = ps_cursor.fetchall()
            ps_cursor.close()
            self.postgres_pool.putconn(postgres_pool_conn)

            # Should have one and only one password per username.
            if len(rows) != 1:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('User Setting DB Error')
                return Auth()
            
            retrieved_pass = rows[0]
            
            return Auth(username = request_username, password = retrieved_pass)
        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to DB pool.')
            self.postgres_pool.putconn(postgres_pool_conn)

    def __del__(self):
        # closing database connection.
        # use closeall method to close all the active connection if you want to turn of the application
        if self.postgres_pool:
            self.postgres_pool.closeall()
        print("PostgreSQL connection pool is closed")


if __name__ == "__main__":
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_UserSettingServiceServicer_to_server(servicer = UserSettingService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    server.start()
    while True:
        sleep(1000)
