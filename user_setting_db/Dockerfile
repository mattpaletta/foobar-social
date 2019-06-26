FROM postgres:9.3
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB user_settings_db
ADD CreateSettingsDB.sql /docker-entrypoint-initdb.d/