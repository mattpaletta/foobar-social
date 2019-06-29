from unittest import TestCase

import grpc

from apilayer_pb2_grpc import ApiLayerServiceStub
from auth_pb2 import Auth, Token


class TestApiLayer(TestCase):
    def _get_stub(self):
        channel = grpc.insecure_channel(target = "apilayer:50051")
        connected = grpc.channel_ready_future(channel)
        connected.result()
        return ApiLayerServiceStub(channel = channel)

    def test_login(self):
        s = self._get_stub()

        auth = Auth(username = "student", password = "mypass")

        token: Token = s.login(auth)
        assert token.username == "student"
        assert token.token is not None and token.token != ""
