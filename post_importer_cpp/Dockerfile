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

ENV GRPC_RELEASE_TAG v1.22.0
ENV BIN_NAME post_importer

ENV BIN_OPT /opt/$BIN_NAME
ENV BIN_BUILD_PATH /usr/local/$BIN_NAME

###################################
# Install GRPC
###################################
RUN git clone -b ${GRPC_RELEASE_TAG} https://github.com/grpc/grpc /var/local/git/grpc && \
    cd /var/local/git/grpc && \
    git submodule update --init --recursive

RUN echo '-- installing protobuf' && \
    cd /var/local/git/grpc/third_party/protobuf && \
    ./autogen.sh && ./configure --enable-shared && \
    make -j$(nproc) && make -j$(nproc) check && make install && make clean && ldconfig

RUN echo "-- installing grpc" && \
    cd /var/local/git/grpc && \
    make -j$(nproc) && make install && make clean && ldconfig

###################################
# Install additional C++ dependencies
###################################
RUN apt-get update && apt-get install -y libhiredis-dev libev-dev zlib1g-dev libssl-dev libsasl2-dev libzstd-dev libboost-all-dev

################################
# Update CMake
################################
ENV CMAKE_MAJOR_VERSION 3.9
ENV CMAKE_MINOR_VERSION 2
RUN curl https://cmake.org/files/v${CMAKE_MAJOR_VERSION}/cmake-${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}-Linux-x86_64.sh -o /cmake-${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}-Linux-x86_64.sh
RUN mkdir /opt/cmake
RUN sh /cmake-${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN cmake --version

###################################
# Install LibRDKafka (cppkafka deps)
####################################
ENV LIBRDKAFKA_VERSION 0.11.4
RUN curl -Lk -o /root/librdkafka-${LIBRDKAFKA_VERSION}.tar.gz https://github.com/edenhill/librdkafka/archive/v${LIBRDKAFKA_VERSION}.tar.gz && \
      tar -xzf /root/librdkafka-${LIBRDKAFKA_VERSION}.tar.gz -C /root && \
      cd /root/librdkafka-${LIBRDKAFKA_VERSION} && \
      ./configure --prefix /usr && make && make install && make clean && ./configure --clean

RUN git clone https://github.com/mfontanini/cppkafka && \
    mkdir -p cppkafka/build && \
    cd cppkafka/build && \
    cmake .. && \
    make install

###################################
# Install Redox (cpp redis client)
###################################
RUN git clone https://github.com/hmartiro/redox.git && \
    mkdir -p redox/build && \
    cd redox/build && \
    cmake .. && \
    make install

###################################
# Build binary
###################################
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
ENTRYPOINT ["/bin/bash"]
CMD ["-s"]

FROM debian:stretch as runtime
COPY --from=build /usr/local/post_importer/out/post_importer/bin/ /opt/post_importer/
WORKDIR /opt/post_importer

EXPOSE 8080
ENTRYPOINT ["/bin/bash", "start.sh"]
