
CREATE TABLE IF NOT EXISTS arena_stats (
arena_stat_id SERIAL,
user_id BIGINT,
date_set TIMESTAMP,
level SMALLINT,
trophies SMALLINT
);


CREATE table IF NOT EXISTS hangman (
user_id BIGINT PRIMARY KEY,
wins INTEGER
);


CREATE table IF NOT EXISTS servers (
server_id BIGINT PRIMARY KEY,
default_role BIGINT,
member_role BIGINT,
prefix VARCHAR(255)
);