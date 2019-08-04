import logging
from concurrent import futures
from time import sleep
import grpc
import re
from pynotstdlib.logging import default_logging

from user_setting_pb2_grpc import add_UserSettingServiceServicer_to_server
from user_setting_pb2_grpc import UserSettingServiceServicer
from auth_pb2 import Auth

import psycopg2
import psycopg2.pool


class UserSettingService(UserSettingServiceServicer):
    
    def __init__(self):
        for i in range(100):
            try:
                # Give the database a change to initialize
                self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(minconn = 1,
                                                                          maxconn = 20,
                                                                          user = "docker",
                                                                          password = "password",
                                                                          host = "usersettingdb",
                                                                          port = "5432",
                                                                          database = "user_settings")
                if self.postgres_pool:
                    break
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error('Failure to connect to Postgres: ', error)
            sleep(2 * i)

        if not self.postgres_pool:
            logging.error('Failure to connect to Postgres')
            exit(1)
        self._create_temp_user()

    def _create_temp_user(self):
        logging.info("Creating temp user")
        with self.postgres_pool.getconn() as conn:
            ps_cursor = conn.cursor()
            ps_cursor.execute("""INSERT INTO user_settings
                (username, passw, phone_number, verification, private)
            SELECT 'student', 'password', '250-123-4567', true, false
            WHERE
                NOT EXISTS (
                    SELECT username, passw, phone_number, verification, private FROM user_settings WHERE username = 'student'
                );
            """)
            conn.commit()

    def get_password(self, request: Auth, context: grpc.RpcContext = None) -> Auth:

        request_username = request.username

        # Ensure username consists only of alphanumeric characters.
        validate = re.compile("[A-Za-z0-9]+$")
        valid_user = validate.match(request_username)
        if not valid_user:
            logging.debug("Invalid username")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid Username')
            return Auth()

        logging.debug("Getting connection")
        postgres_pool_conn = self.postgres_pool.getconn()
        if postgres_pool_conn:
            logging.debug("Got connection")

            with postgres_pool_conn.cursor() as ps_cursor:
                # Retrieve password for the provided username from user_setting
                # If we have more than 1, we don't really care how many more
                # ideally, we would only limit to the one row.
                ps_cursor.execute("""SELECT passw FROM user_settings WHERE username = %s LIMIT 2;""", (request_username, ))
                rows = ps_cursor.fetchall()
            self.postgres_pool.putconn(postgres_pool_conn)

            logging.debug("Got: {0} rows".format(len(rows)))

            # Should have one and only one password per username.
            if len(rows) != 1:
                logging.warning("Invalid number of rows")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('User Setting DB Error')
                return Auth()
            
            first_row = rows[0]
            retrieved_pass = first_row[0]
            return Auth(username = request_username, password = retrieved_pass)
        else:
            logging.error("Failed to connect to DB pool")
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
    default_logging(logging.DEBUG)
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_UserSettingServiceServicer_to_server(servicer = UserSettingService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    print("Started User Settings")
    server.start()
    while True:
        sleep(1000)
