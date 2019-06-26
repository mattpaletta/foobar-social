from concurrent import futures
from time import sleep
import grpc
import re

from user_setting.user_setting_pb2_grpc import add_UserSettingServicer_to_server
from user_setting.user_setting_pb2_grpc import UserSettingServicer
from user_setting.auth_pb2 import Auth

import psycopg2
from psycopg2 import pool




class UserSettingService(UserSettingServicer):
    
    #def __init__(self):
    
    try:
        postgres_pool = psycopg2.pool.SimpleConnectionPool(1, 20,user = "docker",
                                                  password = "docker",
                                                  host = "127.0.0.1",
                                                  port = "5432",
                                                  database = "user_settings_db")

            
    except (Exception, psycopg2.DatabaseError) as error :
        context.set_code(grpc.StatusCode.INTERNAL)
        context.set_details('Failure to connect to Postgres: ', error)


    def get_password(self, request: Auth, context: grpc.RpcContext = None) -> Auth:

        postgres_pool_conn  = postgres_pool.getconn()
        if(postgres_pool_conn):

            ps_cursor = postgres_pool_conn.cursor()

            username = request.username
            validate = re.compile("[A-Za-z0-9]+$")
            if(! validate.match(username)):
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Failure to connect to Postgres: ', error)
                return Auth()


            ps_cursor.execute("SELECT passw FROM user_setting_db WHERE username = '{0}';".format(username))


            ps_cursor.close()

            postgres_pool.putconn(postgres_pool_conn)

    
    # finally:
    #     #closing database connection.
    #     # use closeall method to close all the active connection if you want to turn of the application
    #     if (postgres_pool):
    #         postgres_pool.closeall
    #     print("PostgreSQL connection pool is closed")


        

        


if __name__ == "__main__":
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_UserSettingServicer_to_server(servicer = UserSettingService, server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    server.start()
    while True:
        sleep(1000)