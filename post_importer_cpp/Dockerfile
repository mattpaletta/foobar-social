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
ENV BIN_NAME post_importer

ENV BIN_OPT /opt/$BIN_NAME
ENV BIN_BUILD_PATH /usr/local/$BIN_NAME

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

COPY . $BIN_BUILD_PATH/src/$BIN_NAME/

RUN echo "-- building $BIN_NAME" && \
    mkdir -p $BIN_BUILD_PATH/out/$BIN_NAME && \
    cd $BIN_BUILD_PATH/out/$BIN_NAME && \
    cmake -DCMAKE_BUILD_TYPE=Release $BIN_BUILD_PATH/src/$BIN_NAME && \
    make && \
    mkdir -p bin && \
    ldd $BIN_NAME | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp -v '{}' bin/ && \
    mv $BIN_NAME bin/$BIN_NAME && \
    echo "LD_LIBRARY_PATH=/$BIN_NAME/:\$LD_LIBRARY_PATH ./$BIN_NAME" > bin/start.sh && \
    chmod +x bin/start.sh

WORKDIR /usr/local/post_importer
RUN ls /usr/local/post_importer/out/post_importer/bin/
ENTRYPOINT ["/bin/bash"]
CMD ["-s"]

FROM debian:stretch as runtime
COPY --from=build /usr/local/post_importer/out/post_importer/bin/ /opt/post_importer/
WORKDIR /opt/post_importer

RUN ls /opt/post_importer
RUN cat start.sh
EXPOSE 8080
ENTRYPOINT ["/bin/bash", "start.sh"]
