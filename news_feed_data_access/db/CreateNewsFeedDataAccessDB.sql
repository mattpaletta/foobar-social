CREATE SCHEMA IF NOT EXISTS news_feed_data_access;

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

-- GRANT ALL PRIVILEGES ON SCHEMA news_feed_data_access TO docker;

-- CREATE DATABASE news_feed_data_access_serv WITH OWNER docker;

CREATE SEQUENCE IF NOT EXISTS nf_seq;

-- TODO: add table sharding based on range of datetime and username
CREATE TABLE IF NOT EXISTS nf_posts (
	-- The nf_post_id is incrementing, so that gives us an order
	nf_post_id BIGINT NOT NULL DEFAULT NEXTVAL ('nf_seq'),
	post_id BIGINT NOT NULL,
	datetime TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	-- store whose news feed are we using
	username VARCHAR(50) NOT NULL,
	PRIMARY KEY ( nf_post_id )
);
