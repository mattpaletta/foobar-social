from concurrent import futures
from time import sleep
import grpc
import redis

from token_dispenser.token_pb2 import Token
from token_dispenser.token_pb2_grpc import add_TokenDispenserServicer_to_server
from token_dispenser.token_pb2_grpc import TokenDispenserServicer
from token_dispenser.auth_pb2 import Auth

host = "redis"
port = 6379
ONE_HOUR = 3600


class TokenService(TokenDispenserServicer):
    def __init__(self):
        self._redis_conn = redis.StrictRedis(host = host, port = port, encoding = "utf-8")

    def create_token(self, request: Auth, context: grpc.RpcContext = None) -> Token:
        # TODO: Generate string
        new_token = "hello world"
        user = request.username
        passw = request.password
        if user is None or passw is None:
            return Token()

        self._redis_conn.set(name = user + "_token", value = new_token, ex = ONE_HOUR)
        return Token(username = user, token = new_token)


if __name__ == "__main__":
    token_port = 6969
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_TokenDispenserServicer_to_server(servicer = TokenService, server = server)
    server.add_insecure_port('[::]:{0}'.format(token_port))
    server.start()
    while True:
        sleep(1000)
