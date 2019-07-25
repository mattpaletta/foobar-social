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
import foobar.wall.WallServiceGrpc;
import io.grpc.*;
import io.grpc.netty.NettyServerBuilder;
import io.grpc.stub.StreamObserver;
import io.prometheus.client.Histogram;

import java.util.Iterator;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class ApiServer {

    private static final Logger logger = Logger.getLogger(ApiServer.class.getName());

    private Server server;
    static private final Histogram requestDuration = Histogram.build()
            .name("request_duration_seconds").help("Request duration in seconds.").register();
//    static final Histogram postLatency = Histogram.build()
//            .name("post_duration_seconds").help("Post duration in seconds.").register();

    private void start() throws IOException {
        /* The port on which the server should run */
        int port = 50051;
        // TODO: Measure with/without Netty
        // https://groups.google.com/forum/#!topic/grpc-io/2uMTCA2D-x8

        server = NettyServerBuilder.forPort(port)
                .intercept(new ServerInterceptor() {
                    @Override
                    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(ServerCall<ReqT, RespT> call, Metadata headers,
                                                                         ServerCallHandler<ReqT, RespT> next) {
                        call.setCompression("gzip");
                        return next.startCall(call, headers);
                    }
                })
                .addService(new APILayerImpl())
                .executor(ForkJoinPool.commonPool())
                .build()
                .start();

//        server = ServerBuilder.forPort(port)
//                .intercept(new ServerInterceptor() {
//                    @Override
//                    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(ServerCall<ReqT, RespT> call, Metadata headers,
//                                                                                 ServerCallHandler<ReqT, RespT> next) {
//                        call.setCompression("gzip");
//                        return next.startCall(call, headers);
//                    }
//                })
//                .addService(new APILayerImpl())
//                .build()
//                .start();

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

        // TODO: Consider FutureStub
        private final AuthServiceGrpc.AuthServiceFutureStub authStub;
        private final TokenDispenserServiceGrpc.TokenDispenserServiceFutureStub tokenStub;
        private final PostImporterServiceGrpc.PostImporterServiceFutureStub postStub;
//        private final NewsFeedServiceGrpc.NewsFeedServiceBlockingStub nfStub;
        private final WallServiceGrpc.WallServiceBlockingStub wallStub;

        APILayerImpl() {
            final ManagedChannel authChannel;
            final ManagedChannel tokenChannel;
            final ManagedChannel postChannel;
            final ManagedChannel wallChannel;
            final ManagedChannel nfChannel;

            authChannel = ManagedChannelBuilder
                    .forAddress("auth", 2884)
                    .usePlaintext()
                    .build();
            this.authStub = AuthServiceGrpc.newFutureStub(authChannel);

            tokenChannel = ManagedChannelBuilder
                    .forAddress("token", 6969)
                    .usePlaintext()
                    .build();
            this.tokenStub = TokenDispenserServiceGrpc.newFutureStub(tokenChannel);

            postChannel = ManagedChannelBuilder
                    .forAddress("postImporter", 9000)
                    .usePlaintext()
                    .build();
            this.postStub = PostImporterServiceGrpc.newFutureStub(postChannel);

            // This has to be blocking, because it returns a stream
            wallChannel = ManagedChannelBuilder
                    .forAddress("wall", 4698)
                    .usePlaintext()
                    .build();
            this.wallStub = WallServiceGrpc.newBlockingStub(wallChannel);

//            nfChannel = ManagedChannelBuilder
//                    .forAddress("newsFeed", 9000)
//                    .usePlaintext()
//                    .build();
//            this.nfStub = NewsFeedServiceGrpc.newBlockingStub(nfChannel).withWaitForReady();
        }

        @Override
        public void login(Auth request, StreamObserver<Token> responseObserver) {
            Histogram.Timer t = ApiServer.requestDuration.labels("login").startTimer();

            Token token;
            System.out.println("Logging in");
            try {
                token = authStub.checkAuth(request).get(100, TimeUnit.MILLISECONDS);
            } catch (StatusRuntimeException e) {
                logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
                responseObserver.onError(e);
                t.close();
                return;
            } catch (TimeoutException e) {
                responseObserver.onError(new RuntimeException("Timeout Occured"));
                t.close();
                return;
            }  catch (InterruptedException|java.util.concurrent.ExecutionException e) {
                responseObserver.onError(e);
                t.close();
                return;
            }

            responseObserver.onNext(token);
            t.close();
            responseObserver.onCompleted();
        }

        @Override
        public void post(Post request, StreamObserver<Post> responseObserver) {
            /*
                - Accept a post from the user
                - verify `username` with Auth service
                - if valid, send to PostService.create_post, return response
             */
            Histogram.Timer t = ApiServer.requestDuration.labels("post").startTimer();

            Token token = Token.newBuilder().setUsername(request.getUsername()).build();
            System.out.println("Getting token");
            try {
                token = tokenStub.checkToken(token).get(100, TimeUnit.MILLISECONDS);
            } catch (StatusRuntimeException e) {
                logger.log(Level.WARNING, "Check Token RPC failed: {0}", e.getStatus());
                responseObserver.onError(e);
                t.close();
                return;
            } catch (TimeoutException e) {
                logger.log(Level.WARNING, "Timeout: {0}", e.getMessage());
                responseObserver.onError(new RuntimeException("Timeout Occured"));
                t.close();
                return;
            } catch (InterruptedException | ExecutionException e) {
                logger.log(Level.WARNING, "Unknown Exception: {0}", e.getMessage());
                responseObserver.onError(e);
                t.close();
                return;
            }

            System.out.println("Validating token");
            if (token.getToken() == null) {
                responseObserver.onError(new Exception("Invalid Token"));
                t.close();
                return;
            }

            System.out.println("Creating Post");
            try {
                Empty post = postStub.createPost(request).get();
            } catch (StatusRuntimeException e) {
                logger.log(Level.WARNING, "Create Post RPC failed: {0}", e.getMessage());
                responseObserver.onError(e);
                t.close();
                return;
//            } catch (TimeoutException e) {
//                logger.log(Level.WARNING, "Timeout: {0}", e.getMessage());
//                responseObserver.onError(new RuntimeException("Timeout Occured"));
//                return;
            } catch (InterruptedException | ExecutionException e) {
                logger.log(Level.WARNING, "Unknown Exception: {0}", e.getMessage());
                responseObserver.onError(e);
                t.close();
                return;
            }

            responseObserver.onNext(request);
            t.close();

            responseObserver.onCompleted();
        }

        @Override
        public void getWall(WallQuery request, StreamObserver<Post> responseObserver) {
            Iterator<Post> posts;
            try {
                System.out.println("Fetching wall");
                posts = this.wallStub.fetch(request);

                // Forward all posts to user
                while (posts.hasNext()) {
                    Post nextPost = posts.next();
                    responseObserver.onNext(nextPost);
                }
            } catch (Exception e) {
                System.err.println(e);
            }

            responseObserver.onCompleted();
        }

        @Override
        public void getNewsFeed(WallQuery request, StreamObserver<Post> responseObserver) {
//            Iterator<Post> posts = this.nfStub.getNewsFeed(request);
//
//            // Forward all posts to user
//            while (posts.hasNext()) {
//                Post nextPost = posts.next();
//                responseObserver.onNext(nextPost);
//            }
            responseObserver.onCompleted();
        }
    }
}
