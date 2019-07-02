FROM postgres:alpine
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB news_feed_data_access
ADD CreateSettingsDB.sql /docker-entrypoint-initdb.d/
