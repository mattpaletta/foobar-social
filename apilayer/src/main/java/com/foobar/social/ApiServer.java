package com.foobar.social;

import java.io.IOException;

import foobar.apilayer.ApiLayerServiceGrpc;
import foobar.auth.Auth;
import foobar.auth.AuthServiceGrpc;
import foobar.auth.Token;
import foobar.post_importer.PostImporterServiceGrpc;
import foobar.posts.Post;
import foobar.shared.Empty;
import foobar.tokenizer.TokenDispenserServiceGrpc;
import foobar.wall.WallQuery;
import io.grpc.*;
import io.grpc.stub.StreamObserver;

import java.util.logging.Level;
import java.util.logging.Logger;

public class ApiServer {

    private static final Logger logger = Logger.getLogger(ApiServer.class.getName());

    private Server server;

    private void start() throws IOException {
        /* The port on which the server should run */
        int port = 50051;
        server = ServerBuilder.forPort(port)
                .addService(new APILayerImpl())
                .build()
                .start();
        logger.info("Server started, listening on " + port);
        Runtime.getRuntime().addShutdownHook(new Thread() {
            @Override
            public void run() {
                // Use stderr here since the logger may have been reset by its JVM shutdown hook.
                System.err.println("*** shutting down gRPC server since JVM is shutting down");
                ApiServer.this.stop();
                System.err.println("*** server shut down");
            }
        });
    }

    private void stop() {
        if (server != null) {
            server.shutdown();
        }
    }

    /**
     * Await termination on the main thread since the grpc library uses daemon threads.
     */
    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    // MARK: Main
    public static void main(String[] args) throws IOException, InterruptedException {
        final ApiServer server = new ApiServer();
        server.start();
        server.blockUntilShutdown();
    }

    static class APILayerImpl extends ApiLayerServiceGrpc.ApiLayerServiceImplBase{

        private final ManagedChannel authChannel;
        private final ManagedChannel tokenChannel;
        private final ManagedChannel postChannel;

        // TODO: Consider FutureStub
        private final AuthServiceGrpc.AuthServiceBlockingStub authStub;
        private final TokenDispenserServiceGrpc.TokenDispenserServiceBlockingStub tokenStub;
        private final PostImporterServiceGrpc.PostImporterServiceBlockingStub postStub;

        APILayerImpl() {
            this.authChannel = ManagedChannelBuilder
                    .forAddress("auth", 2884)
                    .usePlaintext()
                    .build();
            this.authStub = AuthServiceGrpc.newBlockingStub(this.authChannel);

            this.tokenChannel = ManagedChannelBuilder
                    .forAddress("token", 6969)
                    .usePlaintext()
                    .build();
            this.tokenStub = TokenDispenserServiceGrpc.newBlockingStub(this.tokenChannel);

            this.postChannel = ManagedChannelBuilder
                    .forAddress("postImporter", 9000)
                    .usePlaintext()
                    .build();
            this.postStub = PostImporterServiceGrpc.newBlockingStub(this.postChannel);
        }

        @Override
        public void login(Auth request, StreamObserver<Token> responseObserver) {
            Token token;
            try {
                token = authStub.checkAuth(request);
            } catch (StatusRuntimeException e) {
                logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
                responseObserver.onError(e);
                return;
            }

//            String username = token.getUsername();
//            String tok = token.getToken();

            responseObserver.onNext(token);
            responseObserver.onCompleted();
        }

        @Override
        public void post(Post request, StreamObserver<Post> responseObserver) {
            /*
                - Accept a post from the user
                - verify `username` with Auth service
                - if valid, send to PostService.create_post, return response
             */
            Token token = Token.newBuilder().setUsername(request.getUsername()).build();
            try {
                token = tokenStub.checkToken(token);
            } catch (StatusRuntimeException e) {
                logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
                responseObserver.onError(e);
                return;
            }

            if(token.getToken() == null){
                responseObserver.onError(new Exception("Invalid Token"));
                return;
            }

            try {
                Empty post = postStub.createPost(request);
            } catch (StatusRuntimeException e) {
                logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
                responseObserver.onError(e);
                return;
            }

            responseObserver.onCompleted();
        }

        @Override
        public void getWall(WallQuery request, StreamObserver<Post> responseObserver) {
            super.getWall(request, responseObserver);
        }

        @Override
        public void getNewsFeed(WallQuery request, StreamObserver<Post> responseObserver) {
            super.getNewsFeed(request, responseObserver);
        }
    }
}
