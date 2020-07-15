
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
prefix VARCHAR,
display_joins BOOL
);

CREATE table IF NOT EXISTS bank (
user_id BIGINT PRIMARY KEY,
money BIGINT
);


CREATE TABLE IF NOT EXISTS empire (
user_id BIGINT PRIMARY KEY,
name VARCHAR,
peasants SMALLINT DEFAULT 0,
farmers SMALLINT DEFAULT 0,
butchers SMALLINT DEFAULT 0,
cooks SMALLINT DEFAULT 0
bakers SMALLINT DEFAULT 0,
winemakers SMALLINT DEFAULT 0,
tanners SMALLINT DEFAULT 0,
blacksmiths SMALLINT DEFAULT 0
);