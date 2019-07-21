FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB user_settings

ADD CreateSettingsDB.sql /docker-entrypoint-initdb.d/