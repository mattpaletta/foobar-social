FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB users1

ADD CreateUsersDB.sql /docker-entrypoint-initdb.d/
