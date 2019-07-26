//
// Created by Matthew Paletta on 2019-07-25.
//

#ifndef NEWS_FEED_POSTSCLIENT_H
#define NEWS_FEED_POSTSCLIENT_H

#include <memory>
#include <grpcpp/channel.h>
#include <posts.grpc.pb.h>

class PostsClient {
public:
    PostsClient(const std::shared_ptr<grpc::Channel>& channel)
            : posts_stub_(foobar::posts::PostService::NewStub(channel)) {};

    foobar::posts::Post fetch(const foobar::posts::Post& post) {

        grpc::ClientContext ctx;
        foobar::posts::Post reply;
        auto status = this->posts_stub_->fetch(&ctx, post, &reply);
        if (!status.ok()) {
            std::cout << status.error_code() << ": " << status.error_message() << std::endl;
        }

        return reply;
    }
private:
    std::unique_ptr<foobar::posts::PostService::Stub> posts_stub_;
};

#endif //NEWS_FEED_POSTSCLIENT_H
