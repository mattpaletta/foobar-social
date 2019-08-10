FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB posts

COPY postgresql.conf      /tmp/postgresql.conf
cOPY updateConfig.sh      /docker-entrypoint-initdb.d/_updateConfig.sh

ADD CreatePostsDB.sql /docker-entrypoint-initdb.d/
