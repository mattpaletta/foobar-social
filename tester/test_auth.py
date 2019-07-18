from unittest import TestCase
import grpc

from auth_pb2 import Auth, Token
from auth_pb2_grpc import AuthServiceStub


class TestAuth(TestCase):

    auth_host = "auth"

    def test_login(self):
        with grpc.insecure_channel(target = self.auth_host + ":2884") as channel:
            s = AuthServiceStub(channel = channel)

            auth = Auth(username = "student", password = "mypass")

            token: Token = s.check_auth(auth)
            print("got back token")
            assert token.username == "student"
            assert token.token is not None and token.token != ""

    def test_login_empty_pass(self):
        with grpc.insecure_channel(target = self.auth_host + ":2884") as channel:
            s = AuthServiceStub(channel = channel)

            auth = Auth(username = "student", password = None)

            # TODO: Should this throw, or just return quietly.
            try:
                token: Token = s.check_auth(auth)
                assert token.username == "student"
                assert token.token is None or token.token == ""
            except:
                assert False

    def test_login_empty_username(self):
        with grpc.insecure_channel(target = self.auth_host + ":2884") as channel:
            s = AuthServiceStub(channel = channel)

            auth = Auth(username = None, password = "my_pass")

            # TODO: Should this throw, or just return quietly.
            try:
                token: Token = s.check_auth(auth)
                assert token.username is None or token.username == ""
                assert token.token is None or token.token == ""
            except:
                assert False
