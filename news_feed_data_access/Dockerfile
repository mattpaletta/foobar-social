FROM swift:5.0.1 as builder
RUN apt-get update -y && apt-get install -y libssl-dev libz-dev unzip
WORKDIR /news_feed_data_access
ADD . /news_feed_data_access
RUN swift build --build-path build
ENTRYPOINT ["/news_feed_data_access/build/x86_64-unknown-linux/debug/news_feed_data_access"]
