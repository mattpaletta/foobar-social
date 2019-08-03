FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB friends
ADD CreateFriendsDB.sql /docker-entrypoint-initdb.d/