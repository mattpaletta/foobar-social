from concurrent import futures
from time import sleep
import grpc

from auth.auth_pb2 import Token
from auth.auth_pb2_grpc import add_AuthsServicer_to_server
from auth.auth_pb2_grpc import AuthsServicer
from auth.auth_pb2 import Auth
from token_dispenser.token_pb2_grpc import TokenDispenserStub



class AuthsService(AUthsServicer):
    #def __init__(self):

    def check_auth(self, request: Auth, context: grpc.RpcContext = None) -> Token:

        channel = grpc.insecure_channel('localhost:6969')
        token_stub = TokenDispenserStub(channel)
        
        user = request.username
        passw = request.password
        if user is None or passw is None:
            #TODO: Handle error. For now handles in token_dispenser.
            return token_stub.create_token(request)

        correct_auth = user_settings.get_password(request)
        correct_pass = correct_auth.password

        if passw == correct_pass:
            return token_stub.create_token(request)
        
        #TODO: Handle error. For now handles in token_dispenser.
        request.username = None
        request.password = None
        return token_stub.create_token(request)


if __name__ == "__main__":
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_AuthsServicer_to_server(servicer = AuthsService, server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    server.start()
    while True:
        sleep(1000)
s