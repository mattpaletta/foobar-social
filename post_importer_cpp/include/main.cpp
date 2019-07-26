//
// Created by Matthew Paletta on 2019-07-25.
//

#include <grpcpp/grpcpp.h>
#include <iostream>
#include <memory>

#include "post_importer.grpc.pb.h"

class PostImporterService final : public foobar::post_importer::PostImporterService::Service {
public:
    PostImporterService() {

    }

    grpc::Status create_post(::grpc::ServerContext *context, const ::foobar::posts::Post *request,
                             ::foobar::shared::Empty *response) override {
        
        return Service::create_post(context, request, response);
    }

private:

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