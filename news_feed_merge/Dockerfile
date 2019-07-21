FROM swift:5.0.1 as builder
RUN apt-get update -y && apt-get install -y libssl-dev libz-dev unzip libpq-dev
WORKDIR /news_feed_merge
ADD . /news_feed_merge
RUN swift build --build-path build
ENTRYPOINT ["/news_feed_merge/build/x86_64-unknown-linux/debug/news_feed_merge"]
