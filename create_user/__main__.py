from concurrent import futures
from time import sleep
import grpc

from auth_pb2 import Auth, Token
from create_user_pb2_grpc import add_CreateUserServiceServicer_to_server, CreateUserServiceServicer
from token_pb2_grpc import TokenDispenserServiceStub
from users_pb2_grpc import UsersServiceStub


class CreateUserService(CreateUserServiceServicer):
    
    def __init__(self) -> None:
        #TODO: Handle hosts through Docker or JSON

        self.token_channel = grpc.insecure_channel('tokendispenser:6969')
        self.token_stub = TokenDispenserServiceStub(self.token_channel)

        try:
            grpc.channel_ready_future(self.token_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to token_dispenser")
            exit(1)

        self.users_channel = grpc.insecure_channel('users:4477')
        self.users_stub = UsersServiceStub(self.users_channel)
        try:
            grpc.channel_ready_future(self.users_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to users")
            exit(1)

    def create_user(self, request: Auth, context: grpc.RpcContext = None) -> Token:
        user = request.username
        passw = request.password
        if user is None or passw is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Username or Password cannot be empty')
            return Token(username = user)

        created_user_future = self.users_stub.create_user.future(request)
        stored_username = created_user_future.result()
       
        # Can't mutate the request, so we create a new token
        return self.token_stub.create_token.future(Token(username = created_user_future)).result()


if __name__ == "__main__":
    users_port = 4477
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_CreateUserServiceServicer_to_server(servicer = CreateUserService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(users_port))
    print("Starting Users Server")
    server.start()
    while True:
        sleep(1000)
