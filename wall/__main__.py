from concurrent import futures
from time import sleep
import grpc

from posts_pb2 import PostQuery
from wall_pb2 import WallQuery
from wall_pb2_grpc import add_WallServiceServicer_to_server, WallServiceServicer

from posts_pb2_grpc import PostsServiceStub


class WallService(WallServiceServicer):
    
    def __init__(self) -> None:
        
        self.posts_channel = grpc.insecure_channel('wall:2539')
        self.posts_stub = PostsServiceStub(self.posts_channel)

        try:
            grpc.channel_ready_future(self.posts_channel).result(timeout = 20)
        except grpc.FutureTimeoutError:
            print("Failed to connect to Posts")


    def fetch(self, request: WallQuery, context: grpc.RpcContext = None) -> Iterator[Post]:
        
        request_user = WallQuery.username
        request_start = WallQuery.starting_id
        request_limit = WallQuery.limit

        posts_request = PostQuery(request_user, request_start, request_limit)

        posts = self.settings_stub.get_password(posts_request)

        for post in posts:
            yield post



if __name__ == "__main__":
    wall_port = 4698
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 4))
    add_WallServiceServicer_to_server(servicer = WallService(), server = server)
    server.add_insecure_port('[::]:{0}'.format(wall_port))
    print("Starting Auth Server")
    server.start()
    while True:
        sleep(1000)
