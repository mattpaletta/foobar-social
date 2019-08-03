import random
import string
from concurrent import futures
from time import sleep
import grpc
import redis

from token_pb2_grpc import add_TokenDispenserServiceServicer_to_server
from token_pb2_grpc import TokenDispenserServiceServicer
from auth_pb2 import Auth, Token

host = "token-dispenser-redis"
port = 6379
ONE_HOUR = 3600


class TokenService(TokenDispenserServiceServicer):

    def __init__(self):
        self._redis_conn = redis.StrictRedis(host = host, port = port, encoding = "utf-8")

    def create_token(self, request: Auth, context: grpc.RpcContext = None) -> Token:
        print("Creating token")
        new_token = TokenService.randomString(16)
        user = request.username
        passw = request.password
        if user is None or passw is None:
            return Token()

        self._redis_conn.set(name = user + "_token", value = new_token, ex = ONE_HOUR)
        return Token(username = user, token = new_token)

    @staticmethod
    def randomString(length: int = 10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters
        return ''.join(random.choice(letters) for i in range(length))

    def check_token(self, request: Token, context: grpc.RpcContext = None) -> Token:
        print("Checking token")

        user = request.username
        if user is None:
            return Token(username = user)

        old_token = self._redis_conn.get(name = user + "_token")
        if old_token is None:
            return Token(username = user)
        else:
            return Token(username = user, token = old_token)

    def get_username(self, request, context):
        return super().get_username(request, context)


if __name__ == "__main__":
    token_port = 6969
    print("Staring token dispenser")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_TokenDispenserServiceServicer_to_server(servicer = TokenService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(token_port))
    print("Starting token dispenser")
    server.start()
    while True:
        sleep(1000)
