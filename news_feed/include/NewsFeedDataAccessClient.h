//
// Created by Matthew Paletta on 2019-07-25.
//

#ifndef NEWS_FEED_NEWSFEEDDATAACCESSCLIENT_H
#define NEWS_FEED_NEWSFEEDDATAACCESSCLIENT_H


#include <memory>
#include <grpcpp/grpcpp.h>
#include <news_feed_data_access.grpc.pb.h>
#include <posts.grpc.pb.h>

class NewsFeedDataAccessClient {
public:
    NewsFeedDataAccessClient(const std::shared_ptr<grpc::Channel>& channel)
                : nfda_stub_(foobar::news_feed_data_access::NewsFeedDataAccessService::NewStub(channel)) {};

    std::unique_ptr<grpc::ClientReader<foobar::posts::Post>> get_news_feed(const foobar::wall::WallQuery& request) {
        grpc::ClientContext ctx;
        return this->nfda_stub_->get_news_feed(&ctx, request);
    }

private:
    std::unique_ptr<foobar::news_feed_data_access::NewsFeedDataAccessService::Stub> nfda_stub_;
//    std::unique_ptr<foobar::posts::PostService::Stub> posts_stub_;

};


#endif //NEWS_FEED_NEWSFEEDDATAACCESSCLIENT_H
