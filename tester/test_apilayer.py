from unittest import TestCase
import grpc

from auth_pb2 import Auth, Token
from apilayer_pb2_grpc import ApiLayerServiceStub


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

            token: Token = s.login(auth)
            assert token.username == "student"
            assert token.token is None or token.token == ""

    def test_login_empty_username(self):
        with grpc.insecure_channel(target = self.apilayer_host + ":50051") as channel:
            s = ApiLayerServiceStub(channel = channel)

            auth = Auth(username = None, password = "my_pass")

            token: Token = s.login(auth)
            assert token.username is None or token.username == ""
            assert token.token is None or token.token == ""