from concurrent import futures
from time import sleep
import grpc
import re

from user_setting_pb2_grpc import add_UserSettingServiceServicer_to_server
from user_setting_pb2_grpc import UserSettingServiceServicer
from auth_pb2 import Auth

import psycopg2
from psycopg2 import pool


class UserSettingService(UserSettingServiceServicer):
    
    def __init__(self):
    
        try:
            self.postgres_pool = psycopg2.pool.SimpleConnectionPool(1, 20,user = "docker",
                                                  password = "docker",
                                                  host = "usersettingdb",
                                                  port = "5432",
                                                  database = "user_settings_db")

            
        except (Exception, psycopg2.DatabaseError) as error :
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to Postgres: ', error)


    def get_password(self, request: Auth, context: grpc.RpcContext = None) -> Auth:

        postgres_pool_conn  = self.postgres_pool.getconn()
        
        if(postgres_pool_conn):

            request_username = request.username

            ps_cursor = postgres_pool_conn.cursor()

            #Ensure username cosists only of alphanumeric characters.
            validate = re.compile("[A-Za-z0-9]+$")
            valid_user = validate.match(request_username)
            if(not valid_user):
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Invalid Username')
                return Auth()

            #Retrieve password for the proivided username from user_setting
            ps_cursor.execute("SELECT passw FROM user_setting_db WHERE username = '{0}';".format(request_username))
            ps_cursor.close()
            rows = ps_cursor.fetchall()

            #Should have one and only one password per username.
            if(len(rows) != 1):
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('User Setting DB Error')
                return Auth()
            
            retrieved_pass = rows[0]
            
            self.postgres_pool.putconn(postgres_pool_conn)

            return Auth(username = request_username, password = retrieved_pass)
        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to DB pool.')

    
    # finally:
    #     #closing database connection.
    #     # use closeall method to close all the active connection if you want to turn of the application
    #     if (postgres_pool):
    #         postgres_pool.closeall
    #     print("PostgreSQL connection pool is closed")

if __name__ == "__main__":
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_UserSettingServiceServicer_to_server(servicer = UserSettingService, server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    server.start()
    while True:
        sleep(1000)
