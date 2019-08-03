//
// Created by Matthew Paletta on 2019-07-25.
//

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>
#include <cstdlib>

//#include "cppkafka/producer.h"

#include "post_importer.grpc.pb.h"
#include "redox_helper.h"

class PostImporterService final : public foobar::post_importer::PostImporterService::Service {
public:
    PostImporterService() : rdx("post_importer_redis"),
            IMPORT_QUEUE(std::getenv("IMPORT_QUEUE")),
            POST_INCREMENT_KEY(std::getenv("POST_INCREMENT_KEY")) {
        if (POST_INCREMENT_KEY == nullptr || IMPORT_QUEUE == nullptr) {
            throw std::runtime_error("Failed to read env variables");
        }
    }

    grpc::Status create_post(::grpc::ServerContext *context, const ::foobar::posts::Post *request,
                             ::foobar::shared::Empty *response) override {

        auto has_msg = !request->msg().empty();
        auto has_username = !request->username().empty();
        auto has_location = request->has_loc() && PostImporterService::is_valid_loc(request->loc());

        if (!has_msg) {
            return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Missing message");
        }

        if (!has_username) {
            return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Missing username");
        }

        if (!has_location) {
            return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Invalid Location");
        }

        std::size_t next_index = this->rdx.incr(this->POST_INCREMENT_KEY);

        // Make a copy of request, so we can mutate it.
        foobar::posts::Post post = *request;

        // Add in the epoch time (according to the server)
        const auto now = std::chrono::system_clock::now();
        const auto epoch = now.time_since_epoch();
        const auto seconds = std::chrono::duration_cast<std::chrono::seconds>(epoch);
        post.set_datetime(seconds.count());

        // TODO: Turn post into json
        // TODO: Push json-post to redis


        return grpc::Status::OK;
    }

private:
    const char* IMPORT_QUEUE;
    const char* POST_INCREMENT_KEY;

    Redis rdx;

    static bool is_valid_loc(const foobar::shared::Location& loc) {
        return  loc.lat() > -90 &&
                loc.lat() < 90 &&
                loc.long_() > -180 &&
                loc.long_() < 180;
    }
};

int main(int argc, char* argv[]) {
    std::string server_address("0.0.0.0:8080");
    PostImporterService post_importer_service;

    grpc::ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&post_importer_service);

    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "Post Importer server listening on " << server_address << std::endl;
    server->Wait();

    return 0;
}