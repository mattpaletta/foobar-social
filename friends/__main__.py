from concurrent import futures
from time import sleep
import grpc

from friends_pb2 import Friend
from friends_pb2_grpc import add_FriendsServiceServicer_to_server, FriendsServiceServicer



class FriendsService(FriendsServiceServicer):
    
    def __init__(self) -> None:
        try:
            self.postgres_pool = psycopg2.pool.SimpleConnectionPool(1, 20,user = "docker",
                                                  password = "docker",
                                                  host = "firendsdb",
                                                  port = "5432",
                                                  database = "friends_db")

            
        except (Exception, psycopg2.DatabaseError) as error :
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to Postgres: ', error)


    def get_friends(self, request: User, context: grpc.RpcContext = None) -> Iterator[Friend]:
        
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
                return Friend()

            
            ps_cursor.execute("SELECT friend FROM friends_db WHERE username = '{0}';".format(request_username))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            postgres_pool.putconn(postgres_pool_conn)

            for row in rows:
                yield Friend(username = request_username, password = row.friend)

    def top_friends(self, request: User, context: grpc.RpcContext = None) -> Iterator[Friend]:
        
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
                return Friend()

           
            ps_cursor.execute("SELECT friend FROM friends_db WHERE username = '{0}' ORDER BY added_date DESC LIMIT 10;".format(request_username))
            ps_cursor.close()
            rows = ps_cursor.fetchall()
            postgres_pool.putconn(postgres_pool_conn)

            for row in rows:
                yield Friend(username = request_username, password = retrieved_pass)
            



            
        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failure to connect to DB pool.')



if __name__ == "__main__":
    friends_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_FriendsServiceServicer_to_server(servicer = FriendsService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(friends_port))
    print("Starting Auth Server")
    server.start()
    while True:
        sleep(1000)
