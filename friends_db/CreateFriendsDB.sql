-- CREATE SCHEMA IF NOT EXISTS friends_db;

--
-- DROP ROLE IF EXISTS docker;
-- CREATE ROLE docker LOGIN PASSWORD 'password';

-- DO
-- $body$
-- BEGIN
--    IF NOT EXISTS (
--       SELECT                       -- SELECT list can stay empty for this
--         FROM   pg_catalog.pg_roles
--         WHERE  rolname = 'docker') THEN
--      CREATE ROLE docker LOGIN PASSWORD 'password';
--    END IF;
-- END
-- $body$;

-- GRANT ALL PRIVILEGES ON SCHEMA friends_db TO docker;
-- GRANT ALL PRIVILEGES ON DATABASE friends_db TO docker;

-- CREATE DATABASE friends_serv WITH OWNER docker;

CREATE TABLE IF NOT EXISTS friends (
  friends_id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  friend VARCHAR(50) NOT NULL
);