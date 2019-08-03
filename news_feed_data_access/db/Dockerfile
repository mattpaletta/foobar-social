FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB news_feed_data_access
ADD CreateNewsFeedDataAccessDB.sql /docker-entrypoint-initdb.d/
