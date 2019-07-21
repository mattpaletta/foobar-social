FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB posts
ADD CreatePostsDB.sql /docker-entrypoint-initdb.d/