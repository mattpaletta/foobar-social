import logging
from multiprocessing.dummy import Pool
from time import time, sleep
from typing import List

from essential_generators import DocumentGenerator
import grpc
from prettytable import PrettyTable
import humanfriendly

from apilayer_pb2_grpc import ApiLayerServiceStub
from auth_pb2 import Token, Auth
from posts_pb2 import Post
from wall_pb2 import WallQuery

apilayer_hostname = "localhost:30727"


def login(username: str, password: str, api: ApiLayerServiceStub) -> Token:
    try:
        auth = Auth(username = username,
                    password = password)
        logging.info("Sending Login")
        token = api.login(auth)
        return token
    except Exception as e:
        logging.error("Error logging in: ", e)


def post(post: Post, api: ApiLayerServiceStub) -> grpc.Future:
    try:
        return api.post.future(post)
    except Exception as e:
        logging.error("Error posting: " + str(e))


def print_wall(username: str, api: ApiLayerServiceStub):
    pt = PrettyTable(["Username", "ID", "Datetime", "Msg"])
    try:
        wq = WallQuery(username = username, starting_id = 0)
        for post in api.get_wall(wq):
            pt.add_row([post.username, post.id, post.datetime, post.msg])
        print(pt)
    except Exception as e:
        logging.error("error getting wall" + e)


def print_news_feed(username: str, api: ApiLayerServiceStub):
    pt = PrettyTable(["Username", "ID", "Datetime", "Msg"])
    try:
        wq = WallQuery(username = username, starting_id = 0)
        for post in api.get_news_feed(wq):
            pt.add_row([post.username, post.id, post.datetime, post.msg])
        print(pt)
    except Exception as e:
        logging.error("error getting news feed" + e)


def autologin() -> Token:
    try:
        token = login("student", "password", api)
        # logging.info("Logged in ({0}): ".format(token.username) + token.token)
        return token
    except:
        pass


def print_time_report(time: float, num: int):
    logging.info("Processed: {0} / Took: {1} / {2} TPS".format(humanfriendly.format_number(num),
                                                               humanfriendly.format_timespan(time),
                                                               humanfriendly.format_number(num / time, 3)))


def submit_posts(sentence: str):
    # logging.getLogger().setLevel(logging.INFO)

    apilayer_channel = grpc.insecure_channel(apilayer_hostname)
    api = ApiLayerServiceStub(channel = apilayer_channel)

    grpc.channel_ready_future(apilayer_channel).result()

    # gen.init_sentence_cache()

    token = autologin()
    while token is None or token.username is None or token.username == "":
        token = autologin()

    # print("Sending post")
    f = post(post = Post(username = token.username, msg = sentence), api = api)

    try:
        f.result(5)
    except grpc.FutureTimeoutError:
        print("Message timed out")
    except Exception as e:
        print("Unknown error occured:", e)

    return 1


def load_login(x: int):
    # logging.getLogger().setLevel(logging.INFO)
    # gen = DocumentGenerator()

    logging.info("Connecting to Api Layer")
    apilayer_channel = grpc.insecure_channel(apilayer_hostname)
    api = ApiLayerServiceStub(channel = apilayer_channel)

    grpc.channel_ready_future(apilayer_channel).result()
    logging.info("Connected to Api Layer")

    num_logged_in = 0
    while True:
        try:
            token: Token = autologin()
            num_logged_in += 1
        except Exception:
            pass

    return num_logged_in


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    gen = DocumentGenerator()

    logging.info("Connecting to Api Layer")
    apilayer_channel = grpc.insecure_channel(apilayer_hostname)
    api = ApiLayerServiceStub(channel = apilayer_channel)

    grpc.channel_ready_future(apilayer_channel).result()
    logging.info("Connected to Api Layer")

    token: Token = autologin()

    prompt = input(">> ")
    while prompt != "exit":
        if prompt == "autologin":
            token = autologin()

        elif prompt == "login":
            username = input("Username: ")
            password = input("Password: ")
            token = login(username, password, api)
            logging.info("Logged in: " + token.token)

        elif prompt == "wall":
            # Get the wall
            print_wall(username = token.username, api = api)

        elif prompt == "news_feed":
            # Get the news feed
            print_news_feed(username = token.username, api = api)

        elif prompt == "postrand":
            if token.username in [None, ""]:
                logging.error("Must login first")
            else:
                num_posts = input("#: ")
                if num_posts == "inf":
                    num_submitted = 0
                    start_time = time()
                    while True:
                        try:
                            p = Post(msg = gen.sentence(), username = token.username)
                            post(p, api).result()
                            num_submitted += 1
                        except KeyboardInterrupt:
                            break
                    end_time = time()
                    print_time_report(time = end_time - start_time, num = num_submitted)
                else:
                    num_posts = int(num_posts)

                    # num_threads = 20
                    # pool = Pool(processes = num_threads)

                    pieces = []

                    gen.init_sentence_cache()

                    for i in range(num_posts):
                        pieces.append(gen.sentence())
                    logging.info("Sending sentences")

                    start_time = time()

                    # pool.map(submit_posts, iterable = pieces, chunksize = 10)
                    # pool.close()
                    for sen in pieces:
                        p = Post(msg = sen, username = token.username)
                        post(p, api).result()

                    end_time = time()
                    if int(num_posts) >= 10:
                        print_time_report(time = end_time - start_time, num = int(num_posts))

        elif prompt == "post":
            if token.username in [None, ""]:
                logging.error("Must login first")
            else:
                # create a post
                msg = input("Post: ")
                p = Post(msg = msg, username = token.username)
                post(p, api).result()
        elif prompt == "help":
            print("Commands: [autologin, login, wall, news_feed, post, postrand, help]")
        else:
            logging.error("Invalid command.")
        prompt = input(">> ")
