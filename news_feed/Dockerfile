FROM debian:stretch as build

RUN apt-get update && apt-get install -y \
  autoconf \
  automake \
  build-essential \
  cmake \
  curl \
  g++ \
  git \
  libtool \
  make \
  pkg-config \
  unzip \
  && apt-get clean

ENV GRPC_RELEASE_TAG v1.16.0
ENV NEWS_FEED_BUILD_PATH /usr/local/news_feed

RUN git clone -b ${GRPC_RELEASE_TAG} https://github.com/grpc/grpc /var/local/git/grpc && \
    cd /var/local/git/grpc && \
    git submodule update --init --recursive

RUN echo "-- installing protobuf" && \
    cd /var/local/git/grpc/third_party/protobuf && \
    ./autogen.sh && ./configure --enable-shared && \
    make -j$(nproc) && make -j$(nproc) check && make install && make clean && ldconfig

RUN echo "-- installing grpc" && \
    cd /var/local/git/grpc && \
    make -j$(nproc) && make install && make clean && ldconfig

COPY . $NEWS_FEED_BUILD_PATH/src/news_feed/

RUN echo "-- building news_feed" && \
    mkdir -p $NEWS_FEED_BUILD_PATH/out/news_feed && \
    cd $NEWS_FEED_BUILD_PATH/out/news_feed && \
    cmake -DCMAKE_BUILD_TYPE=Release $NEWS_FEED_BUILD_PATH/src/news_feed && \
    make && \
    mkdir -p bin && \
    ldd news_feed | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v '{}' bin/ && \
    mv news_feed bin/news_feed && \
    echo "LD_LIBRARY_PATH=/opt/news_feed/:\$LD_LIBRARY_PATH ./news_feed" > bin/start.sh && \
    chmod +x bin/start.sh

WORKDIR $NEWS_FEED_BUILD_PATH
ENTRYPOINT ["/bin/bash"]
CMD ["-s"]

FROM debian:stretch as runtime
COPY --from=build /usr/local/news_feed/out/news_feed/bin/ /opt/news_feed/
EXPOSE 8080
WORKDIR /opt/news_feed/
ENTRYPOINT ["/bin/bash", "start.sh"]