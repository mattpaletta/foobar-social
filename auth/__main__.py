from concurrent import futures
from time import sleep
import grpc

from auth_pb2 import Token
from auth_pb2_grpc import add_AuthsServicer_to_server
from auth_pb2_grpc import AuthsServicer
from auth_pb2 import Auth
from token_pb2_grpc import TokenDispenserStub
from user_setting_pb2_grpc import UserSettingStub



class AuthsService(AuthsServicer):
    
    def __init__(self):

    #TODO: Handle hosts through Docker or JSON

        self.token_channel = grpc.insecure_channel('localhost:6969')
        self.token_stub = TokenDispenserStub(token_channel)

        self.settings_channel = grpc.insecure_channel('localhost:1234')
        self.settings_stub = UserSettingStub(settings_channel)

    def check_auth(self, request: Auth, context: grpc.RpcContext = None) -> Token:

        

        user = request.username
        passw = request.password
        if user is None or passw is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Username or Password cannot be empty')
            return Token()
        correct_auth = self.settings_stub.get_password(request)
        correct_pass = correct_auth.password

        if passw == correct_pass:
            return Token()

        request.username = None
        request.password = None
        return self.token_stub.create_token(request)


if __name__ == "__main__":
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_AuthsServicer_to_server(servicer = AuthsService, server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    server.start()
    while True:
        sleep(1000)
