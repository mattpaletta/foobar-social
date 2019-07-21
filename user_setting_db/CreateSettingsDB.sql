-- CREATE SCHEMA IF NOT EXISTS user_settings_db;

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

-- CREATE DATABASE docker WITH OWNER docker;

CREATE TABLE IF NOT EXISTS user_settings (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  passw VARCHAR(50) NOT NULL,
  phone_number VARCHAR(50),
  verification BOOLEAN,
  private BOOLEAN
);