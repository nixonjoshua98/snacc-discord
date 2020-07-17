
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
default_role BIGINT DEFAULT 0,
member_role BIGINT DEFAULT 0,
prefix VARCHAR DEFAULT "!",
display_joins BOOL DEFAULT True
);

CREATE table IF NOT EXISTS bank (
user_id BIGINT PRIMARY KEY,
money BIGINT DEFAULT 1000
);


CREATE TABLE IF NOT EXISTS empire (
user_id BIGINT PRIMARY KEY,
name VARCHAR DEFAULT 'My Empire',
last_income TIMESTAMP WITHOUT time zone default (now() at time zone 'utc'),
farmers SMALLINT DEFAULT 0,
butchers SMALLINT DEFAULT 0,
cooks SMALLINT DEFAULT 0,
bakers SMALLINT DEFAULT 0,
winemakers SMALLINT DEFAULT 0
);