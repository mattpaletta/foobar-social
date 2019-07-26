//
// Created by Matthew Paletta on 2019-07-25.
//

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>

#include "news_feed.grpc.pb.h"
#include "news_feed.pb.h"
#include "posts.grpc.pb.h"

#include "NewsFeedDataAccessClient.h"
#include "PostsClient.h"

class NewsFeedService final : public foobar::news_feed::NewsFeedService::Service {
public:
    NewsFeedService() : nf_client(grpc::CreateChannel("news_feed_data_access:9000", grpc::InsecureChannelCredentials())),
                        posts_client(grpc::CreateChannel("posts:9000", grpc::InsecureChannelCredentials())) {
    }

    grpc::Status get_news_feed(grpc::ServerContext *context, const foobar::wall::WallQuery *request,
                               grpc::ServerWriter<foobar::posts::Post> *writer) override {
        const auto request_user = request->username();
        const auto request_limit = request->limit();
        const auto request_start = request->starting_id() < 0 ? 0 : request->starting_id();

        if (request_limit == 0 || request_start < 0 || request_user.empty()) {
            return grpc::Status::OK;
        }

        auto posts = this->nf_client.get_news_feed(*request);
        foobar::posts::Post p;
        while (posts->Read(&p)) {
            auto post = this->posts_client.fetch(p);
            writer->Write(post);
        }

        auto status = posts->Finish();
        return status;
    }

private:
    NewsFeedDataAccessClient nf_client;
    PostsClient posts_client;
};

int main(int argc, char* argv[]) {
    std::string server_address("0.0.0.0:8080");
    NewsFeedService news_feed_service;

    grpc::ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&news_feed_service);

    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "News Feed server listening on " << server_address << std::endl;
    server->Wait();

    return 0;
}