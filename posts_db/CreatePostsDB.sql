-- CREATE SCHEMA IF NOT EXISTS posts_db;

-- DROP ROLE IF EXISTS docker;
-- CREATE ROLE docker LOGIN PASSWORD 'password';

-- DO
-- $body$
-- BEGIN
--    IF NOT EXISTS (
--       SELECT                       -- SELECT list can stay empty for this
--         FROM   pg_catalog.pg_user
--         WHERE  usename = 'docker') THEN
--      CREATE ROLE docker LOGIN PASSWORD 'password';
--    END IF;
-- END
-- $body$;

-- CREATE DATABASE posts_serv WITH OWNER docker;

-- GRANT ALL PRIVILEGES ON SCHEMA posts_db TO docker;

CREATE TABLE IF NOT EXISTS posts (
  post_id BIGINT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  post_date TIMESTAMP,
  msg VARCHAR(1000),
  lat FLOAT,
  long FLOAT
);