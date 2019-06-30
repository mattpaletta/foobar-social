FROM swift:5.0.1 as builder
RUN apt-get update -y && apt-get install -y libssl-dev libz-dev unzip
WORKDIR /post_importer
ADD . /post_importer
RUN swift build --build-path build
ENTRYPOINT ["/post_importer/build/x86_64-unknown-linux/debug/post_importer"]
