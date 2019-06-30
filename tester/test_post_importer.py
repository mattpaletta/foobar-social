import time
from unittest import TestCase
import grpc

from post_importer_pb2_grpc import PostImporterServiceStub
from posts_pb2 import Post
from shared_pb2 import Location


class TestPostImporter(TestCase):

    post_importer_host = "postImporter"

    def test_create_post_empty(self):
        with grpc.insecure_channel(target = self.post_importer_host + ":9000") as channel:
            s = PostImporterServiceStub(channel = channel)

            post = Post()
            try:
                s.create_post(post)
                assert False, "Accepted invalid post"
            except:
                assert True

    def test_create_post_empty_msg(self):
        with grpc.insecure_channel(target = self.post_importer_host + ":9000") as channel:
            s = PostImporterServiceStub(channel = channel)

            post = Post(username = "student",
                        datetime = int(time.time() * 1000))
            try:
                s.create_post(post)
                assert False, "Accepted invalid post"
            except:
                assert True

    def test_create_post_invalid_id(self):
        with grpc.insecure_channel(target = self.post_importer_host + ":9000") as channel:
            s = PostImporterServiceStub(channel = channel)

            post = Post(username = "student",
                        datetime = int(time.time() * 1000),
                        msg = "here is my msg",
                        id = -1)
            # Shouldn't throw an exception, should replace id
            s.create_post(post)

    def test_create_post_invalid_loc(self):
        with grpc.insecure_channel(target = self.post_importer_host + ":9000") as channel:
            s = PostImporterServiceStub(channel = channel)

            post = Post(username = "student",
                        datetime = int(time.time() * 1000),
                        msg = "here is my msg",
                        id = -1,
                        loc = Location(lat = -100, long = -200))
            try:
                s.create_post(post)
                assert False, "Accepted invalid post"
            except:
                assert True
