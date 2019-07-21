FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB wall
ADD CreateWallDB.sql /docker-entrypoint-initdb.d/