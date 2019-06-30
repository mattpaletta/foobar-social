from concurrent import futures
from time import sleep
import grpc

from auth_pb2 import Token, Auth
from auth_pb2_grpc import add_AuthServiceServicer_to_server, AuthServiceServicer
from token_pb2_grpc import TokenDispenserServiceStub
from user_setting_pb2_grpc import UserSettingServiceStub


class AuthsService(AuthServiceServicer):
    
    def __init__(self) -> None:
        #TODO: Handle hosts through Docker or JSON

        self.token_channel = grpc.insecure_channel('token_dispenser:6969')
        self.token_stub = TokenDispenserServiceStub(self.token_channel)

        try:
            grpc.channel_ready_future(self.token_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to token_dispenser")

        self.settings_channel = grpc.insecure_channel('user_settings:2884')
        self.settings_stub = UserSettingServiceStub(self.settings_channel)
        try:
            grpc.channel_ready_future(self.settings_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to user settings")

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
            return Token(username = "", token = "")

        # Can't mutate the request, so we create a new token
        return self.token_stub.create_token(Token())


if __name__ == "__main__":
    auth_port = 2884
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_AuthServiceServicer_to_server(servicer = AuthsService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(auth_port))
    print("Starting Auth Server")
    server.start()
    while True:
        sleep(1000)
