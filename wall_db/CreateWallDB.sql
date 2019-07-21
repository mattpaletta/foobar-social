-- CREATE SCHEMA IF NOT EXISTS wall_db;

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

-- GRANT ALL PRIVILEGES ON SCHEMA wall_db TO docker;
-- CREATE DATABASE wall_serv WITH OWNER docker;

-- TODO: Complete filling in the required schema
CREATE TABLE IF NOT EXISTS wall (
  wall_id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  post_id BIGINT NOT NULL,
  datetime timestamp DEFAULT NOW()
);