CREATE SCHEMA IF NOT EXISTS news_feed_data_access;

CREATE SEQUENCE IF NOT EXISTS news_feed_data_access.nf_seq;

-- TODO: add table sharding based on range of datetime and username
CREATE TABLE IF NOT EXISTS news_feed_data_access.nf_posts (
	-- The nf_post_id is incrementing, so that gives us an order
	nf_post_id BIGINT NOT NULL DEFAULT NEXTVAL ('news_feed_data_access.nf_seq'),
	post_id BIGINT NOT NULL,
	datetime TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	-- store whose news feed are we using
	username VARCHAR(50) NOT NULL,
	PRIMARY KEY ( nf_post_id )
);
