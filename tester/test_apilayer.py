from time import sleep
from unittest import TestCase
import grpc

from auth_pb2 import Auth, Token
from apilayer_pb2_grpc import ApiLayerServiceStub
from posts_pb2 import Post
from shared_pb2 import Location
from wall_pb2 import WallQuery


class TestApiLayer(TestCase):

    apilayer_host = "apilayer"

    def test_login(self):
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            auth = Auth(username = "student", password = "mypass")

            token: Token = s.login(auth)
            print("got back token")
            assert token.username == "student"
            assert token.token is not None and token.token != ""

    def test_login_empty_pass(self):
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            auth = Auth(username = "student", password = None)
            try:
                token: Token = s.login(auth)
                assert token.username == "student"
                assert token.token is None or token.token == ""
            except:
                assert False

    def test_login_empty_username(self):
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            auth = Auth(username = None, password = "my_pass")

            try:
                token: Token = s.login(auth)
                assert token.username is None or token.username == ""
                assert token.token is None or token.token == ""
            except:
                assert False

    # post, login, (logout), get_news_feed, get_wall, add_friend, remove_friend
    # TODO: Add/remove friend
    def test_post(self):
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            p = Post(username = "student",
                     msg = "hello world",
                     loc = Location(lat = 48.464051,
                                    long = -123.310215))

            try:
                s.post(p)
                assert True
            except:
                assert(False, "failed to post")

    def test_get_news_feed(self):
        for _ in range(10):
            self.test_post()

        sleep(5)
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            w = WallQuery(username = "student", starting_id = 0, limit = 10)
            nf = s.get_news_feed(w)
            assert len(list(nf)) == 10

    def test_get_wall(self):
        for _ in range(10):
            self.test_post()

        sleep(5)
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            w = WallQuery(username = "student", starting_id = 0, limit = 10)
            nf = s.get_wall(w)
            assert len(list(nf)) == 10
