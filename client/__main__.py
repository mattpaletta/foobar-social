import logging
from time import time

from essential_generators import DocumentGenerator
import grpc
from prettytable import PrettyTable
import humanfriendly

from apilayer_pb2_grpc import ApiLayerServiceStub
from auth_pb2 import Token, Auth
from posts_pb2 import Post
from wall_pb2 import WallQuery


def login(username: str, password: str, api: ApiLayerServiceStub) -> Token:
    try:
        auth = Auth(username = username,
                    password = password)
        token = api.login(auth)
        return token
    except Exception as e:
        logging.error("Error logging in: ", e)


def post(post: Post):
    try:
        api.post(post)
    except Exception as e:
        logging.error("Error logging in: " + str(e))


def print_wall(username: str):
    pt = PrettyTable(["Username", "ID", "Datetime", "Msg"])
    try:
        wq = WallQuery(username = username, starting_id = 0)
        for post in api.get_wall(wq):
            pt.add_row([post.username, post.id, post.datetime, post.msg])
        print(pt)
    except Exception as e:
        logging.error("error getting wall" + e)


def autologin() -> Token:
    token = login("student", "password", api)
    logging.info("Logged in ({0}): ".format(token.username) + token.token)
    return token


def print_time_report(time: float, num: int):
    logging.info("Processed: {0} / Took: {1} / {2} TPS".format(humanfriendly.format_number(num),
                                                               humanfriendly.format_timespan(time),
                                                               humanfriendly.format_number(num / time, 3)))

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    gen = DocumentGenerator()

    logging.info("Connecting to Api Layer")
    apilayer_channel = grpc.insecure_channel('apilayer:50051')
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
            print_wall(username = token.username)

        elif prompt == "news_feed":
            # Get the news feed
            pass
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
                            post(p)
                            num_submitted += 1
                        except KeyboardInterrupt:
                            break
                    end_time = time()
                    print_time_report(time = end_time - start_time, num = num_submitted)

                else:
                    # TODO: Split into 10 threads
                    start_time = time()
                    for _ in range(int(num_posts)):
                        p = Post(msg = gen.sentence(), username = token.username)
                        post(p)
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
                post(p)
        elif prompt == "help":
            print("Commands: [autologin, login, wall, news_feed, post, postrand, help]")
        else:
            logging.error("Invalid command.")
        prompt = input(">> ")
